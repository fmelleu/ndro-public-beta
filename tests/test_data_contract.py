"""Data-contract validation tests: fixture must pass; each documented
failure mode must be rejected with the correct typed diagnostic."""

import json
from pathlib import Path

import pandas as pd
import pytest

from ndro_app.data_loader import load_snapshot
from ndro_app.exceptions import (
    ContractVersionError,
    DuplicateKeyError,
    RequiredValueError,
    SchemaValidationError,
)
from tests.conftest import read_csv_text


def test_fixture_contract_passes(valid_snapshot_dir: Path):
    snapshot = load_snapshot(valid_snapshot_dir)
    assert snapshot.snapshot_version == "synthetic-ui-fixture-v0.1"
    assert snapshot.cutoff_date == "2026-08-22"
    assert len(snapshot.articles) == 5
    assert snapshot.warnings == []


def test_missing_required_column_fails(tmp_snapshot_dir: Path):
    articles_path = tmp_snapshot_dir / "articles.csv"
    df = read_csv_text(articles_path)
    df = df.drop(columns=["title"])
    df.to_csv(articles_path, index=False)

    with pytest.raises(SchemaValidationError) as excinfo:
        load_snapshot(tmp_snapshot_dir)
    assert "title" in excinfo.value.diagnostic
    assert "articles.csv" in excinfo.value.diagnostic


def test_missing_required_column_in_coverage_fails(tmp_snapshot_dir: Path):
    coverage_path = tmp_snapshot_dir / "coverage.csv"
    df = read_csv_text(coverage_path)
    df = df.drop(columns=["semantic_coverage_percent"])
    df.to_csv(coverage_path, index=False)

    with pytest.raises(SchemaValidationError) as excinfo:
        load_snapshot(tmp_snapshot_dir)
    assert "semantic_coverage_percent" in excinfo.value.diagnostic


def test_duplicate_association_id_fails(tmp_snapshot_dir: Path):
    articles_path = tmp_snapshot_dir / "articles.csv"
    df = read_csv_text(articles_path)
    duplicated_row = df.iloc[[0]].copy()
    df = pd.concat([df, duplicated_row], ignore_index=True)
    df.to_csv(articles_path, index=False)

    with pytest.raises(DuplicateKeyError) as excinfo:
        load_snapshot(tmp_snapshot_dir)
    assert "association_id" in excinfo.value.diagnostic


def test_unsupported_contract_version_fails(tmp_snapshot_dir: Path):
    metadata_path = tmp_snapshot_dir / "snapshot_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["contract_version"] = "public-snapshot-v9.9"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    with pytest.raises(ContractVersionError) as excinfo:
        load_snapshot(tmp_snapshot_dir)
    assert "public-snapshot-v9.9" in excinfo.value.diagnostic


def test_required_nonnull_field_blank_fails(tmp_snapshot_dir: Path):
    articles_path = tmp_snapshot_dir / "articles.csv"
    df = read_csv_text(articles_path)
    df.loc[0, "classification_status"] = ""
    df.to_csv(articles_path, index=False)

    with pytest.raises(RequiredValueError) as excinfo:
        load_snapshot(tmp_snapshot_dir)
    assert "classification_status" in excinfo.value.diagnostic


def test_missing_snapshot_file_fails(tmp_snapshot_dir: Path):
    (tmp_snapshot_dir / "evidence_spans.csv").unlink()
    with pytest.raises(Exception) as excinfo:
        load_snapshot(tmp_snapshot_dir)
    assert "evidence_spans.csv" in str(excinfo.value)


def test_metadata_count_mismatch_is_a_warning_not_a_failure(tmp_snapshot_dir: Path):
    metadata_path = tmp_snapshot_dir / "snapshot_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["counts"]["article_associations"] = 999
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    snapshot = load_snapshot(tmp_snapshot_dir)  # must not raise
    assert any("article_associations" in w for w in snapshot.warnings)


def test_pending_corpus_status_is_not_coerced_to_excluded(valid_snapshot_dir: Path):
    """The Parkinson (PD) fixture row has a blank corpus_status. Loading
    must preserve that blank rather than silently filling it."""
    snapshot = load_snapshot(valid_snapshot_dir)
    pd_row = snapshot.articles[snapshot.articles["disease_code"] == "PD"].iloc[0]
    assert pd.isna(pd_row["corpus_status"]) or str(pd_row["corpus_status"]).strip() == ""
