"""End-to-end smoke tests that actually run the Streamlit app (via
streamlit.testing.v1.AppTest) against the bundled synthetic fixture
snapshot, rather than only unit-testing the underlying functions.

These confirm the app boots without exceptions on each page, that an empty
search on the Article Explorer does not crash, and that a PMID search
actually surfaces a matching article card.
"""

from pathlib import Path

import pytest

from streamlit.testing.v1 import AppTest

from ndro_app.config import DEFAULT_SNAPSHOT_DIR_NAME, SNAPSHOTS_ROOT

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=30)
    return at


def test_app_boots_on_overview_without_exception():
    at = _fresh_app()
    assert not at.exception


def test_navigating_to_article_explorer_without_exception():
    at = _fresh_app()
    at.sidebar.radio[0].set_value("Article Explorer")
    at.run(timeout=30)
    assert not at.exception


def test_navigating_to_methods_page_without_exception():
    at = _fresh_app()
    at.sidebar.radio[0].set_value("Methods & Data Quality")
    at.run(timeout=30)
    assert not at.exception


@pytest.mark.parametrize(
    "page",
    [
        "Disease Trends",
        "Geographic Coverage",
        "Scientific Documentation",
        "Review Protocol",
        "Planned Updates",
        "Audit & Corrections",
        "Downloads & Citation",
        "About",
    ],
)
def test_new_public_beta_pages_render_without_exception(page):
    at = _fresh_app()
    at.sidebar.radio[0].set_value(page)
    at.run(timeout=30)
    assert not at.exception


def _apply_filters_button(at: AppTest):
    matches = [b for b in at.button if b.label == "Apply search & filters"]
    assert len(matches) == 1, "expected exactly one 'Apply search & filters' form submit button"
    return matches[0]


def test_article_explorer_empty_search_submit_does_not_crash():
    at = _fresh_app()
    at.sidebar.radio[0].set_value("Article Explorer")
    at.run(timeout=30)
    assert not at.exception
    _apply_filters_button(at).click().run(timeout=30)
    assert not at.exception


def test_article_explorer_pmid_search_surfaces_a_result():
    at = _fresh_app()
    at.sidebar.radio[0].set_value("Article Explorer")
    at.run(timeout=30)
    text_inputs = at.text_input
    assert len(text_inputs) >= 1
    import pandas as pd

    first_pmid = str(pd.read_csv(SNAPSHOTS_ROOT / DEFAULT_SNAPSHOT_DIR_NAME / "articles.csv", dtype=str).iloc[0]["pmid"])
    text_inputs[0].set_value(first_pmid)
    _apply_filters_button(at).click().run(timeout=30)
    assert not at.exception
    all_text = " ".join(md.value for md in at.markdown)
    assert "**1** matching association(s)" in all_text
    assert first_pmid in all_text
    all_captions = " ".join(caption.value for caption in at.caption)
    assert "From PubMed metadata" in all_captions
    assert "not relicensed by NDRO" in all_captions


def test_overview_disease_filter_does_not_crash():
    at = _fresh_app()
    disease_select = [s for s in at.selectbox if s.label == "Filter by disease"][0]
    disease_select.set_value("AD").run(timeout=30)
    assert not at.exception
    metric_labels = [m.label for m in at.metric]
    assert "Semantic coverage — Alzheimer's disease" in metric_labels


def test_overview_always_shows_semantic_coverage_metric():
    at = _fresh_app()
    metric_labels = [metric.label for metric in at.metric]
    assert "Semantic coverage" in metric_labels


def test_overview_explains_project_purpose_mission_and_use():
    at = _fresh_app()
    rendered_text = " ".join(md.value for md in at.markdown) + " ".join(
        caption.value for caption in at.caption
    ) + " ".join(info.value for info in at.info)
    assert "### Purpose" in rendered_text
    assert "3.4 billion people" in rendered_text
    assert "#### Mission" in rendered_text
    assert "#### How to use NDRO" in rendered_text
    assert "snapshot version and cutoff date" in rendered_text


def test_geographic_scope_keeps_future_dimensions_separate():
    at = _fresh_app()
    at.sidebar.radio[0].set_value("Geographic Coverage")
    at.run(timeout=30)
    assert not at.exception
    rendered_text = " ".join(md.value for md in at.markdown) + " ".join(
        caption.value for caption in at.caption
    )
    assert "author-affiliation country" in rendered_text
    assert "responsible institution" in rendered_text
    assert "study site" not in rendered_text.lower()


def test_planned_updates_documents_semantics_enrichment_and_ms_scope():
    at = _fresh_app()
    at.sidebar.radio[0].set_value("Planned Updates")
    at.run(timeout=30)
    assert not at.exception
    rendered_text = " ".join(md.value for md in at.markdown) + " ".join(
        caption.value for caption in at.caption
    ) + " ".join(info.value for info in at.info)
    assert "Validated semantic layer" in rendered_text
    assert "citation networks" in rendered_text
    assert "Multiple sclerosis" in rendered_text
    assert "fixed delivery dates" in rendered_text


def test_review_protocol_documents_search_screening_semantics_and_release():
    at = _fresh_app()
    at.sidebar.radio[0].set_value("Review Protocol")
    at.run(timeout=30)
    assert not at.exception
    rendered_text = " ".join(md.value for md in at.markdown) + " ".join(
        caption.value for caption in at.caption
    )
    assert "NDRO review protocol v0.1" in rendered_text
    assert "Versioned search protocol" in rendered_text
    assert "Deterministic eligibility screen" in rendered_text
    assert "Deep semantic extraction" in rendered_text
    assert "Synchronized presentation" in rendered_text


@pytest.mark.parametrize(
    "page",
    [
        "Overview",
        "Article Explorer",
        "Disease Trends",
        "Geographic Coverage",
        "Scientific Documentation",
        "Review Protocol",
        "Methods & Data Quality",
        "Planned Updates",
        "Audit & Corrections",
        "Downloads & Citation",
        "About",
    ],
)
def test_no_page_leaks_a_local_filesystem_path(page):
    at = _fresh_app()
    at.sidebar.radio[0].set_value(page)
    at.run(timeout=30)
    assert not at.exception
    rendered_text = " ".join(md.value for md in at.markdown) + " ".join(c.value for c in at.caption)
    assert "/tmp/" not in rendered_text
    assert str(Path.home()) not in rendered_text
