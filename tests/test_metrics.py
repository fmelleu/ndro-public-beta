"""Critical metric-calculation tests: headline counts reconcile with the
fixture's own snapshot_metadata.json, pending is never counted as excluded,
and the core trend excludes separate/excluded/pending/integrity-flagged
records."""

import json
from pathlib import Path

import pandas as pd
import pytest

from ndro_app.data_loader import load_snapshot
from ndro_app.metrics import (
    add_bucket_columns,
    candidate_landscape_by_status,
    corpus_bucket,
    coverage_summary,
    cumulative_core_publications,
    headline_counts,
    integrity_is_flagged,
    integrity_is_retracted,
    publication_year_trend,
    reported_country_tally,
)


@pytest.fixture(scope="module")
def loaded_snapshot(valid_snapshot_dir: Path):
    return load_snapshot(valid_snapshot_dir)


@pytest.fixture(scope="module")
def fixture_metadata(valid_snapshot_dir: Path) -> dict:
    return json.loads((valid_snapshot_dir / "snapshot_metadata.json").read_text(encoding="utf-8"))


def test_headline_counts_reconcile_with_fixture_metadata(loaded_snapshot, fixture_metadata):
    counts = headline_counts(loaded_snapshot.articles)
    assert counts["candidate_associations"] == fixture_metadata["counts"]["article_associations"]
    assert counts["distinct_publications"] == fixture_metadata["counts"]["distinct_pmids"]
    # Fixture: AD=core, ALS=separate, FTD=excluded_eligibility, HD=excluded_relevance, PD=pending
    assert counts["core_associations"] == 1
    assert counts["separate_associations"] == 1
    assert counts["excluded_associations"] == 2
    assert counts["pending_associations"] == 1
    assert counts["unrecognized_associations"] == 0
    total = (
        counts["core_associations"]
        + counts["separate_associations"]
        + counts["excluded_associations"]
        + counts["pending_associations"]
        + counts["unrecognized_associations"]
    )
    assert total == counts["candidate_associations"]


def test_coverage_summary_reconciles_with_fixture(loaded_snapshot):
    cov = coverage_summary(loaded_snapshot.coverage)
    # coverage.csv: eligible sums to 1+1+0+0+1=3, complete sums to 1+1+0+0+0=2
    assert cov["eligible_associations"] == 3
    assert cov["semantically_complete_associations"] == 2
    assert cov["candidate_associations"] == 5
    assert cov["semantic_coverage_percent"] == pytest.approx(2 / 3 * 100, rel=1e-6)


@pytest.mark.parametrize(
    "raw_value,expected_bucket",
    [
        (None, "pending"),
        ("", "pending"),
        (float("nan"), "pending"),
        ("core", "core"),
        ("separate", "separate"),
        ("excluded_eligibility", "excluded"),
        ("excluded_relevance", "excluded"),
        ("something_new", "unrecognized"),
    ],
)
def test_corpus_bucket_mapping(raw_value, expected_bucket):
    assert corpus_bucket(raw_value) == expected_bucket


def test_pending_is_never_counted_as_excluded():
    df = pd.DataFrame(
        {
            "association_id": ["a1", "a2"],
            "disease_code": ["AD", "AD"],
            "pmid": ["1", "2"],
            "publication_year": [2024, 2024],
            "corpus_status": [None, ""],
            "integrity_status": ["no_pubmed_integrity_signal", "no_pubmed_integrity_signal"],
        }
    )
    counts = headline_counts(df)
    assert counts["pending_associations"] == 2
    assert counts["excluded_associations"] == 0


def test_integrity_flag_detection():
    assert integrity_is_flagged("no_pubmed_integrity_signal") is False
    assert integrity_is_flagged("retraction_confirmed") is True
    assert integrity_is_flagged(None) is True  # required field; missing treated conservatively
    assert integrity_is_retracted("retracted") is True
    assert integrity_is_retracted("corrected") is False
    assert integrity_is_retracted("no_pubmed_integrity_signal") is False


def test_core_trend_keeps_corrected_but_excludes_separate_excluded_pending_and_retracted():
    df = pd.DataFrame(
        {
            "association_id": ["core-clean", "core-corrected", "core-retracted", "separate-1", "excluded-1", "pending-1"],
            "disease_code": ["AD", "AD", "AD", "AD", "AD", "AD"],
            "pmid": ["1", "2", "3", "4", "5", "6"],
            "publication_year": [2020, 2020, 2020, 2020, 2020, 2020],
            "corpus_status": ["core", "core", "core", "separate", "excluded_relevance", None],
            "integrity_status": [
                "no_pubmed_integrity_signal",
                "corrected",
                "retracted",
                "no_pubmed_integrity_signal",
                "no_pubmed_integrity_signal",
                "no_pubmed_integrity_signal",
            ],
        }
    )
    trend = publication_year_trend(df)
    assert list(trend["publication_year"]) == [2020]
    assert list(trend["count"]) == [2]  # clean and corrected core records count

    bucketed = add_bucket_columns(df)
    assert bucketed.set_index("association_id")["is_core_analytical"].to_dict() == {
        "core-clean": True,
        "core-corrected": True,
        "core-retracted": False,
        "separate-1": False,
        "excluded-1": False,
        "pending-1": False,
    }


def test_candidate_landscape_includes_every_bucket():
    df = pd.DataFrame(
        {
            "association_id": ["a", "b", "c", "d"],
            "disease_code": ["AD", "AD", "AD", "AD"],
            "pmid": ["1", "2", "3", "4"],
            "publication_year": [2020, 2020, 2020, 2020],
            "corpus_status": ["core", "separate", "excluded_eligibility", None],
            "integrity_status": ["no_pubmed_integrity_signal"] * 4,
        }
    )
    landscape = candidate_landscape_by_status(df)
    assert set(landscape["corpus_bucket"]) == {"core", "separate", "excluded", "pending"}
    assert landscape["count"].sum() == 4


def test_publication_year_trend_empty_input_does_not_crash():
    df = pd.DataFrame(
        {
            "association_id": [],
            "disease_code": [],
            "pmid": [],
            "publication_year": [],
            "corpus_status": [],
            "integrity_status": [],
        }
    )
    trend = publication_year_trend(df)
    assert trend.empty


def test_cumulative_core_trend_fills_missing_years_per_disease():
    df = pd.DataFrame(
        {
            "association_id": ["a", "b"],
            "disease_code": ["AD", "AD"],
            "pmid": ["1", "2"],
            "publication_year": [2020, 2022],
            "corpus_status": ["core", "core"],
            "integrity_status": ["no_pubmed_integrity_signal"] * 2,
        }
    )
    trend = cumulative_core_publications(df)
    assert trend["publication_year"].tolist() == [2020, 2021, 2022]
    assert trend["cumulative_count"].tolist() == [1, 1, 2]


def test_reported_country_tally_uses_human_readable_name():
    facts = pd.DataFrame(
        {
            "association_id": ["a", "b"],
            "disease_code": ["AD", "ALS"],
            "countries": ["USA — United States", "USA — United States; CAN — Canada"],
        }
    )
    tally = reported_country_tally(facts)
    assert set(tally["country"]) == {"United States", "Canada"}
