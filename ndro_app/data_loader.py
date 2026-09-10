"""Loads and validates one NDRO public snapshot directory.

This module is the only place that touches disk. It never opens a database
connection, never asks for credentials, and never fetches anything from the
network -- it reads a small set of local, versioned CSV/JSON files as
described in ``contracts/NDRO_Public_Snapshot_Data_Contract_v0.1.md``.

Validation follows the contract's own rules:

- an unsupported (or missing) ``contract_version`` is rejected;
- a missing required column is rejected;
- ``articles.csv`` and ``study_facts.csv`` must be unique per
  ``association_id`` (their stated grain);
- required-non-null fields in ``articles.csv`` must actually be present;
- ``snapshot_version`` / ``cutoff_date`` must agree across every file and
  the metadata document.

Every failure raises one of the typed exceptions in ``ndro_app.exceptions``
carrying a short, user-safe diagnostic string -- no stack traces, file
system paths, or credentials are ever surfaced to the UI.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

import pandas as pd

from . import schema
from .config import SUPPORTED_CONTRACT_VERSIONS
from .exceptions import (
    ContractVersionError,
    DuplicateKeyError,
    MissingFileError,
    RequiredValueError,
    SchemaValidationError,
    SnapshotConsistencyError,
)

_MAX_EXAMPLES_IN_DIAGNOSTIC = 8

_FILES: Dict[str, List[str]] = {
    "articles.csv": schema.ARTICLES_REQUIRED_COLUMNS,
    "coverage.csv": schema.COVERAGE_REQUIRED_COLUMNS,
    "study_facts.csv": schema.STUDY_FACTS_REQUIRED_COLUMNS,
    "evidence_spans.csv": schema.EVIDENCE_SPANS_REQUIRED_COLUMNS,
    "interventions_outcomes.csv": schema.INTERVENTIONS_OUTCOMES_REQUIRED_COLUMNS,
}

_NUMERIC_COLUMNS: Dict[str, List[str]] = {
    "articles.csv": schema.ARTICLES_NUMERIC_COLUMNS,
    "coverage.csv": schema.COVERAGE_NUMERIC_COLUMNS,
    "study_facts.csv": schema.STUDY_FACTS_NUMERIC_COLUMNS,
    "evidence_spans.csv": schema.EVIDENCE_SPANS_NUMERIC_COLUMNS,
    "interventions_outcomes.csv": [],
}


@dataclass
class Snapshot:
    """A fully validated, in-memory view of one snapshot directory."""

    snapshot_dir: Path
    metadata: dict
    articles: pd.DataFrame
    coverage: pd.DataFrame
    study_facts: pd.DataFrame
    evidence_spans: pd.DataFrame
    interventions_outcomes: pd.DataFrame
    warnings: List[str] = field(default_factory=list)

    @property
    def snapshot_version(self) -> str:
        return str(self.metadata.get("snapshot_version", ""))

    @property
    def cutoff_date(self) -> str:
        return str(self.metadata.get("cutoff_date", ""))


def _read_csv_as_text(path: Path) -> pd.DataFrame:
    """Read a snapshot CSV with every column as text.

    Reading everything as text first (rather than letting pandas guess
    types) keeps ``pmid`` as text per the contract and prevents accidental
    float coercion of identifier-like columns. Numeric columns are cast
    explicitly afterwards by the caller.
    """
    return pd.read_csv(
        path,
        dtype=str,
        keep_default_na=True,
        na_values=[""],
        na_filter=True,
    )


def _diagnostic_list(values, limit: int = _MAX_EXAMPLES_IN_DIAGNOSTIC) -> str:
    values = list(values)
    shown = values[:limit]
    text = ", ".join(str(v) for v in shown)
    if len(values) > limit:
        text += f", and {len(values) - limit} more"
    return text


def _validate_columns(df: pd.DataFrame, required: List[str], filename: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SchemaValidationError(
            f"'{filename}' is missing required column(s): "
            f"{_diagnostic_list(missing)}. This snapshot cannot be loaded "
            "until the file matches the published data contract."
        )


def _validate_required_nonnull(df: pd.DataFrame, filename: str) -> None:
    if filename != "articles.csv":
        return
    problems = []
    for col in schema.ARTICLES_REQUIRED_NONNULL:
        if col not in df.columns:
            continue  # already reported by _validate_columns
        blank_mask = df[col].isna() | (df[col].astype(str).str.strip() == "")
        if blank_mask.any():
            ids = df.loc[blank_mask, schema.ARTICLES_PRIMARY_KEY] if schema.ARTICLES_PRIMARY_KEY in df.columns else blank_mask[blank_mask].index
            problems.append(
                f"'{col}' is blank in {int(blank_mask.sum())} row(s) "
                f"(association_id: {_diagnostic_list(ids)})"
            )
    if problems:
        raise RequiredValueError(
            f"'{filename}' has required fields left blank: " + "; ".join(problems)
        )


def _validate_unique_association_id(df: pd.DataFrame, filename: str) -> None:
    if filename not in schema.FILES_REQUIRING_UNIQUE_ASSOCIATION_ID:
        return
    if "association_id" not in df.columns or df.empty:
        return
    dup_mask = df["association_id"].duplicated(keep=False)
    if dup_mask.any():
        dup_ids = sorted(set(df.loc[dup_mask, "association_id"]))
        raise DuplicateKeyError(
            f"'{filename}' has duplicate association_id value(s), but this "
            f"file must have exactly one row per association: "
            f"{_diagnostic_list(dup_ids)}."
        )


def _cast_numeric(df: pd.DataFrame, columns: List[str], filename: str, warnings: List[str]) -> None:
    for col in columns:
        if col not in df.columns:
            continue
        original_non_null = df[col].notna()
        coerced = pd.to_numeric(df[col], errors="coerce")
        newly_null = original_non_null & coerced.isna()
        if newly_null.any():
            warnings.append(
                f"'{filename}' column '{col}' had {int(newly_null.sum())} "
                "value(s) that could not be read as numbers; they were "
                "treated as missing."
            )
        df[col] = coerced


def _validate_consistency(
    metadata: dict, frames: Dict[str, pd.DataFrame]
) -> None:
    expected_version = str(metadata.get("snapshot_version", ""))
    expected_cutoff = str(metadata.get("cutoff_date", ""))
    for filename, df in frames.items():
        if df.empty:
            continue
        for col, expected in (
            ("snapshot_version", expected_version),
            ("cutoff_date", expected_cutoff),
        ):
            if col not in df.columns:
                continue
            distinct = set(df[col].dropna().astype(str).unique())
            distinct.discard("")
            if not distinct:
                continue
            if distinct != {expected}:
                raise SnapshotConsistencyError(
                    f"'{filename}' reports {col} value(s) "
                    f"{_diagnostic_list(sorted(distinct))}, which does not "
                    f"match snapshot_metadata.json ({expected!r}). A "
                    "snapshot directory must represent a single immutable "
                    "release."
                )


def _soft_check_metadata_counts(
    metadata: dict, frames: Dict[str, pd.DataFrame], warnings: List[str]
) -> None:
    """Cross-check snapshot_metadata.json's declared counts against what the
    CSVs actually contain, and coverage.csv's candidate_associations sum
    against articles.csv's row count. Disagreement is surfaced as a
    data-quality warning, not a hard failure -- the app still renders using
    the CSVs (the authoritative source for row-level data) but flags the
    mismatch on the Methods & Data Quality page so it is never silently
    hidden.
    """
    counts = metadata.get("counts") or {}
    articles = frames.get("articles.csv")
    coverage = frames.get("coverage.csv")
    study_facts = frames.get("study_facts.csv")
    evidence_spans = frames.get("evidence_spans.csv")

    def _check(label: str, declared, actual) -> None:
        if declared is None:
            return
        try:
            if int(declared) != int(actual):
                warnings.append(
                    f"snapshot_metadata.json declares {label} = {declared}, "
                    f"but the snapshot files contain {actual}."
                )
        except (TypeError, ValueError):
            return

    if articles is not None:
        _check("counts.article_associations", counts.get("article_associations"), len(articles))
        _check(
            "counts.distinct_pmids",
            counts.get("distinct_pmids"),
            articles["pmid"].nunique(dropna=True) if "pmid" in articles.columns else None,
        )
    if study_facts is not None:
        _check("counts.study_facts", counts.get("study_facts"), len(study_facts))
    if evidence_spans is not None:
        _check("counts.evidence_spans", counts.get("evidence_spans"), len(evidence_spans))

    if articles is not None and coverage is not None and "candidate_associations" in coverage.columns:
        candidate_from_coverage = int(
            pd.to_numeric(coverage["candidate_associations"], errors="coerce").fillna(0).sum()
        )
        if candidate_from_coverage != len(articles):
            warnings.append(
                "coverage.csv candidate_associations sums to "
                f"{candidate_from_coverage}, but articles.csv has {len(articles)} rows. "
                "The candidate denominator shown in the app uses articles.csv."
            )


def load_snapshot(snapshot_dir: Path) -> Snapshot:
    """Load and validate one snapshot directory.

    Raises a subclass of :class:`ndro_app.exceptions.ContractError` on any
    contract violation. Never raises a bare exception for expected
    validation failures.
    """
    snapshot_dir = Path(snapshot_dir)
    warnings: List[str] = []

    metadata_path = snapshot_dir / "snapshot_metadata.json"
    if not metadata_path.exists():
        raise MissingFileError(
            "This snapshot directory has no snapshot_metadata.json file, "
            "so its release and limitation information cannot be shown."
        )
    try:
        # ``utf-8-sig`` accepts both ordinary UTF-8 and Windows-generated
        # UTF-8 files carrying a BOM, without changing immutable snapshots.
        metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise MissingFileError(
            "snapshot_metadata.json could not be parsed as JSON "
            f"(line {exc.lineno}, column {exc.colno})."
        ) from exc

    contract_version = metadata.get("contract_version")
    if contract_version not in SUPPORTED_CONTRACT_VERSIONS:
        supported = _diagnostic_list(sorted(SUPPORTED_CONTRACT_VERSIONS))
        raise ContractVersionError(
            f"This snapshot declares contract_version "
            f"{contract_version!r}, which this app build does not support "
            f"(supported: {supported}). Please use a compatible snapshot "
            "or an updated app build."
        )

    frames: Dict[str, pd.DataFrame] = {}
    for filename, required_columns in _FILES.items():
        path = snapshot_dir / filename
        if not path.exists():
            raise MissingFileError(
                f"Required snapshot file '{filename}' was not found in "
                "this snapshot directory."
            )
        df = _read_csv_as_text(path)
        _validate_columns(df, required_columns, filename)
        _validate_required_nonnull(df, filename)
        _validate_unique_association_id(df, filename)
        _cast_numeric(df, _NUMERIC_COLUMNS.get(filename, []), filename, warnings)
        frames[filename] = df

    _validate_consistency(metadata, frames)
    _soft_check_metadata_counts(metadata, frames, warnings)

    return Snapshot(
        snapshot_dir=snapshot_dir,
        metadata=metadata,
        articles=frames["articles.csv"],
        coverage=frames["coverage.csv"],
        study_facts=frames["study_facts.csv"],
        evidence_spans=frames["evidence_spans.csv"],
        interventions_outcomes=frames["interventions_outcomes.csv"],
        warnings=warnings,
    )


def list_available_snapshots(snapshots_root: Path) -> List[str]:
    """Return the names of sub-directories that look like snapshot dirs."""
    snapshots_root = Path(snapshots_root)
    if not snapshots_root.exists():
        return []
    return sorted(
        p.name
        for p in snapshots_root.iterdir()
        if p.is_dir() and (p / "snapshot_metadata.json").exists()
    )
