"""Article Explorer search/filter/pagination tests, including the required
empty-search / empty-filter robustness checks."""

from pathlib import Path

import pandas as pd
import pytest

from ndro_app.data_loader import load_snapshot
from ndro_app.filters import apply_filters, paginate, search_articles
from ndro_app.metrics import add_bucket_columns


@pytest.fixture(scope="module")
def articles_df(valid_snapshot_dir: Path) -> pd.DataFrame:
    snapshot = load_snapshot(valid_snapshot_dir)
    return add_bucket_columns(snapshot.articles)


def test_search_finds_by_pmid(articles_df):
    result = search_articles(articles_df, "90000001")
    assert len(result) == 1
    assert result.iloc[0]["disease_code"] == "AD"


def test_search_finds_by_abstract_text(articles_df):
    result = search_articles(articles_df, "Alzheimer disease")
    assert len(result) >= 1
    assert (result["disease_code"] == "AD").any()


def test_search_finds_by_title(articles_df):
    result = search_articles(articles_df, "case report")
    assert len(result) == 1
    assert result.iloc[0]["disease_code"] == "FTD"


def test_search_is_case_insensitive(articles_df):
    result_lower = search_articles(articles_df, "parkinson")
    result_upper = search_articles(articles_df, "PARKINSON")
    assert len(result_lower) == len(result_upper) == 1


def test_empty_search_returns_everything(articles_df):
    assert len(search_articles(articles_df, "")) == len(articles_df)
    assert len(search_articles(articles_df, None)) == len(articles_df)
    assert len(search_articles(articles_df, "   ")) == len(articles_df)


def test_search_with_no_match_returns_empty_not_crash(articles_df):
    result = search_articles(articles_df, "no such term exists anywhere xyz123")
    assert result.empty


def test_apply_filters_with_all_empty_does_not_restrict(articles_df):
    result = apply_filters(articles_df)
    assert len(result) == len(articles_df)
    result = apply_filters(
        articles_df,
        disease_codes=[],
        year_range=None,
        corpus_buckets=[],
        classification_statuses=[],
        semantic_statuses=[],
        integrity_states=[],
    )
    assert len(result) == len(articles_df)


def test_apply_filters_by_disease(articles_df):
    result = apply_filters(articles_df, disease_codes=["AD"])
    assert len(result) == 1
    assert result.iloc[0]["disease_code"] == "AD"


def test_apply_filters_by_corpus_bucket_separate_only(articles_df):
    result = apply_filters(articles_df, corpus_buckets=["separate"])
    assert len(result) == 1
    assert result.iloc[0]["disease_code"] == "ALS"


def test_apply_filters_pending_not_confused_with_excluded(articles_df):
    pending_only = apply_filters(articles_df, corpus_buckets=["pending"])
    excluded_only = apply_filters(articles_df, corpus_buckets=["excluded"])
    assert set(pending_only["disease_code"]) == {"PD"}
    assert set(excluded_only["disease_code"]) == {"FTD", "HD"}


def test_search_then_filter_combo_can_return_empty_without_crash(articles_df):
    result = search_articles(articles_df, "Alzheimer")
    result = apply_filters(result, corpus_buckets=["excluded"])
    assert result.empty


def test_pagination_basic():
    df = pd.DataFrame({"x": range(25)})
    page1, total_pages = paginate(df, page=1, page_size=10)
    assert len(page1) == 10
    assert total_pages == 3
    page3, _ = paginate(df, page=3, page_size=10)
    assert len(page3) == 5


def test_pagination_out_of_range_is_clamped_not_crashing():
    df = pd.DataFrame({"x": range(5)})
    page, total_pages = paginate(df, page=999, page_size=10)
    assert total_pages == 1
    assert len(page) == 5
    page, total_pages = paginate(df, page=0, page_size=10)
    assert len(page) == 5


def test_pagination_empty_dataframe_does_not_crash():
    df = pd.DataFrame({"x": []})
    page, total_pages = paginate(df, page=1, page_size=10)
    assert page.empty
    assert total_pages == 1
