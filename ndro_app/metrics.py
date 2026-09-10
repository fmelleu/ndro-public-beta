"""Pure, Streamlit-free calculations over a loaded :class:`Snapshot`.

Keeping these as plain pandas functions (no ``st.*`` calls) is what lets the
critical counts be unit tested directly, without spinning up Streamlit.

Corpus-status bucketing
------------------------
``corpus_status`` in ``articles.csv`` is blank for records still awaiting
final relevance placement. Per the data contract ("pending classification
has blank corpus_status; it is not exclusion") a blank value must never be
folded into "excluded". :func:`corpus_bucket` implements that rule.

Publication integrity
---------------------
The public snapshot distinguishes a reported integrity signal from a
confirmed retraction. Every non-clean value is displayed transparently, but
only ``retracted`` publications are automatically removed from core
analytical indicators. Corrected publications remain analytical unless a
separate scientific decision changes their corpus status.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd

from .config import INTEGRITY_CLEAN_STATUS

BUCKET_CORE = "core"
BUCKET_SEPARATE = "separate"
BUCKET_EXCLUDED = "excluded"
BUCKET_PENDING = "pending"
BUCKET_UNRECOGNIZED = "unrecognized"


def _is_blank(value) -> bool:
    return value is None or (isinstance(value, float) and pd.isna(value)) or pd.isna(value) or str(value).strip() == ""


def corpus_bucket(corpus_status) -> str:
    """Map a raw corpus_status value to one of the five analytical buckets.

    Blank/NaN -> ``pending`` (never ``excluded``); an exact ``core`` or
    ``separate`` match maps directly; any other non-blank value that starts
    with ``excluded`` maps to ``excluded``; anything else is flagged as
    ``unrecognized`` rather than silently guessed at, so a future new status
    value cannot be miscounted without anyone noticing.
    """
    if _is_blank(corpus_status):
        return BUCKET_PENDING
    value = str(corpus_status).strip()
    if value == "core":
        return BUCKET_CORE
    if value == "separate":
        return BUCKET_SEPARATE
    if value.startswith("excluded"):
        return BUCKET_EXCLUDED
    return BUCKET_UNRECOGNIZED


def integrity_is_flagged(integrity_status) -> bool:
    """True when the stored integrity_status reports something other than
    a clean check (i.e. a retraction/correction signal was found, or the
    check reported an unrecognized non-clean state)."""
    if _is_blank(integrity_status):
        # Required-non-null per contract; treated conservatively as flagged
        # rather than silently assumed clean if it is ever missing.
        return True
    return str(integrity_status).strip() != INTEGRITY_CLEAN_STATUS


def integrity_is_retracted(integrity_status) -> bool:
    """True only for the canonical confirmed-retraction status."""
    if _is_blank(integrity_status):
        return False
    return str(integrity_status).strip().lower() == "retracted"


def is_core_analytical(row) -> bool:
    """A record counts toward "core" analytical indicators only when it is
    in the core bucket AND is not retracted."""
    return corpus_bucket(row.get("corpus_status")) == BUCKET_CORE and not integrity_is_retracted(
        row.get("integrity_status")
    )


def add_bucket_columns(articles_df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of articles_df with helper columns
    ``corpus_bucket``, ``integrity_flagged`` and retraction helpers attached."""
    out = articles_df.copy()
    out["corpus_bucket"] = out["corpus_status"].apply(corpus_bucket)
    out["integrity_flagged"] = out["integrity_status"].apply(integrity_is_flagged)
    out["integrity_retracted"] = out["integrity_status"].apply(integrity_is_retracted)
    out["is_core_analytical"] = out["corpus_bucket"].eq(BUCKET_CORE) & ~out["integrity_retracted"]
    return out


def headline_counts(articles_df: pd.DataFrame) -> dict:
    """Candidate-landscape counts computed directly from articles.csv (one
    row per association, per the contract's stated grain).

    These are the *candidate* denominators: every known association,
    including pending and excluded ones. They must be shown alongside, but
    never merged with, the analytical (core-only) or semantic (complete-only)
    denominators computed elsewhere in this module.
    """
    df = add_bucket_columns(articles_df)
    bucket_counts = df["corpus_bucket"].value_counts().to_dict()
    return {
        "candidate_associations": int(len(df)),
        "distinct_publications": int(df["pmid"].nunique(dropna=True)),
        "core_associations": int(bucket_counts.get(BUCKET_CORE, 0)),
        "separate_associations": int(bucket_counts.get(BUCKET_SEPARATE, 0)),
        "excluded_associations": int(bucket_counts.get(BUCKET_EXCLUDED, 0)),
        "pending_associations": int(bucket_counts.get(BUCKET_PENDING, 0)),
        "unrecognized_associations": int(bucket_counts.get(BUCKET_UNRECOGNIZED, 0)),
        "integrity_flagged_associations": int(df["integrity_flagged"].sum()),
        "retracted_associations": int(df["integrity_retracted"].sum()),
    }


def coverage_summary(coverage_df: pd.DataFrame) -> dict:
    """Semantic-completion denominators drawn from coverage.csv, summed
    across all diseases currently in the snapshot.

    ``semantic_coverage_percent`` is recomputed here from the summed
    numerator/denominator (rather than averaging the per-disease
    percentages) so it is mathematically consistent with the disclosed
    counts.
    """
    eligible = int(pd.to_numeric(coverage_df["eligible_associations"], errors="coerce").fillna(0).sum())
    complete = int(
        pd.to_numeric(coverage_df["semantically_complete_associations"], errors="coerce").fillna(0).sum()
    )
    candidate = int(pd.to_numeric(coverage_df["candidate_associations"], errors="coerce").fillna(0).sum())
    coverage_percent: Optional[float] = (complete / eligible * 100.0) if eligible > 0 else None
    return {
        "candidate_associations": candidate,
        "eligible_associations": eligible,
        "semantically_complete_associations": complete,
        "semantic_coverage_percent": coverage_percent,
    }


def publication_year_trend(articles_df: pd.DataFrame, disease_code: Optional[str] = None) -> pd.DataFrame:
    """Core-analytical publication counts by year.

    Per the behavioral rules, core charts exclude separate, excluded,
    pending, and confirmed retracted records unless a
    visual explicitly says otherwise. This function is that core-only
    trend; use :func:`candidate_landscape_by_status` for the
    explicitly-candidate view.
    """
    df = add_bucket_columns(articles_df)
    df = df[df["is_core_analytical"]]
    if disease_code and disease_code != "All diseases":
        df = df[df["disease_code"] == disease_code]
    if df.empty:
        return pd.DataFrame({"publication_year": [], "count": []})
    grouped = (
        df.dropna(subset=["publication_year"])
        .groupby("publication_year", as_index=False)
        .size()
        .rename(columns={"size": "count"})
        .sort_values("publication_year")
    )
    grouped["publication_year"] = grouped["publication_year"].astype(int)
    return grouped


def candidate_landscape_by_status(articles_df: pd.DataFrame, disease_code: Optional[str] = None) -> pd.DataFrame:
    """Candidate-landscape counts by corpus bucket (core/separate/excluded/
    pending/unrecognized). Explicitly a *candidate* view: it intentionally
    includes every bucket, unlike the core-only trend above."""
    df = add_bucket_columns(articles_df)
    if disease_code and disease_code != "All diseases":
        df = df[df["disease_code"] == disease_code]
    counts = df["corpus_bucket"].value_counts().rename_axis("corpus_bucket").reset_index(name="count")
    return counts


def core_publications_by_year_and_disease(articles_df: pd.DataFrame) -> pd.DataFrame:
    """Core analytical association counts by disease and publication year."""
    df = add_bucket_columns(articles_df)
    df = df[df["is_core_analytical"]].dropna(subset=["publication_year", "disease_code"])
    if df.empty:
        return pd.DataFrame(columns=["publication_year", "disease_code", "count"])
    out = (
        df.groupby(["publication_year", "disease_code"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
        .sort_values(["disease_code", "publication_year"])
    )
    out["publication_year"] = out["publication_year"].astype(int)
    return out


def cumulative_core_publications(articles_df: pd.DataFrame) -> pd.DataFrame:
    """Year-by-year cumulative core counts, separately for each disease."""
    annual = core_publications_by_year_and_disease(articles_df)
    if annual.empty:
        return annual.assign(cumulative_count=pd.Series(dtype=int))
    min_year = int(annual["publication_year"].min())
    max_year = int(annual["publication_year"].max())
    diseases = sorted(annual["disease_code"].unique())
    complete_index = pd.MultiIndex.from_product(
        [range(min_year, max_year + 1), diseases],
        names=["publication_year", "disease_code"],
    )
    out = (
        annual.set_index(["publication_year", "disease_code"])["count"]
        .reindex(complete_index, fill_value=0)
        .rename("count")
        .reset_index()
    )
    out["cumulative_count"] = out.groupby("disease_code")["count"].cumsum()
    return out


def reported_country_tally(study_facts_df: pd.DataFrame) -> pd.DataFrame:
    """Association-country counts from the semicolon-delimited public field.

    The result describes reported study context, not author affiliation or
    recruitment-site geography.
    """
    if study_facts_df is None or study_facts_df.empty or "countries" not in study_facts_df:
        return pd.DataFrame(columns=["country", "disease_code", "association_count"])
    rows = study_facts_df[["association_id", "disease_code", "countries"]].dropna(subset=["countries"]).copy()
    rows["country"] = rows["countries"].astype(str).str.split(r";\s*")
    rows = rows.explode("country")
    rows["country"] = rows["country"].astype(str).str.strip()
    # The public field stores values such as ``USA — United States``.
    # Charts use the human-readable part while retaining the source field
    # unchanged in the immutable snapshot.
    rows["country"] = rows["country"].str.replace(
        r"^[A-Z]{3}\s+\S+\s+", "", regex=True
    )
    rows = rows[rows["country"] != ""]
    if rows.empty:
        return pd.DataFrame(columns=["country", "disease_code", "association_count"])
    return (
        rows.groupby(["country", "disease_code"], as_index=False)["association_id"]
        .nunique()
        .rename(columns={"association_id": "association_count"})
    )
