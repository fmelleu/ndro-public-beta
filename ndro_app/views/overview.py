"""Overview page: living-corpus status banner, headline counts, disease
filter, and the core-only publication trend alongside the explicitly
candidate landscape.
"""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from .. import copy
from ..charts import candidate_landscape_chart, publication_year_trend_chart
from ..data_loader import Snapshot
from ..metrics import coverage_summary, headline_counts, publication_year_trend, candidate_landscape_by_status
from ..ui import info_card


def _status_banner(status_indicator: str) -> None:
    info = copy.STATUS_BANNER.get(str(status_indicator).lower(), copy.STATUS_BANNER_UNKNOWN)
    st.markdown(
        f"""
        <div style="background-color:{info['background']}; color:{info['color']};
                    border:1px solid {info['color']}33; border-radius:10px;
                    padding:14px 18px; margin-bottom:12px;">
            <div style="font-size:1.05rem; font-weight:700;">{info['icon']} {info['label']}</div>
            <div style="margin-top:4px;">{info['description']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _display_timestamp(raw_value: object) -> str:
    raw = str(raw_value or "").strip()
    if not raw:
        return "—"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return raw
    offset = parsed.strftime("%z")
    offset_label = f"UTC{offset[:3]}:{offset[3:]}" if offset else "local time"
    return f"{parsed:%Y-%m-%d %H:%M} ({offset_label})"


def render(snapshot: Snapshot) -> None:
    st.subheader("Overview")

    metadata = snapshot.metadata
    _status_banner(metadata.get("status_indicator", ""))

    if metadata.get("synthetic_fixture"):
        st.warning(copy.SYNTHETIC_DATA_BANNER)

    cov = coverage_summary(snapshot.coverage)
    coverage_display = (
        f"{cov['semantic_coverage_percent']:.1f}%" if cov["semantic_coverage_percent"] is not None else "n/a"
    )
    release_cols = st.columns([1.25, 0.8, 1.35, 0.8])
    info_card(release_cols[0], "Snapshot version", snapshot.snapshot_version or "—")
    info_card(release_cols[1], "Cutoff date", snapshot.cutoff_date or "—")
    info_card(
        release_cols[2],
        "Generated at",
        _display_timestamp(metadata.get("generated_at")),
        help_text=str(metadata.get("generated_at", "")),
    )
    info_card(
        release_cols[3],
        "Semantic coverage",
        coverage_display,
        help_text=(
            f"{cov['semantically_complete_associations']} of {cov['eligible_associations']} "
            "eligible associations are semantically complete. "
            + copy.DENOMINATOR_DISCLOSURE
        ),
    )

    st.caption(copy.LIVING_CORPUS_EXPLANATION)

    with st.container(border=True):
        st.markdown("### Purpose")
        st.markdown(copy.PURPOSE_TEXT)
        st.caption(copy.PURPOSE_SOURCES)

        purpose_cols = st.columns([1, 1.15])
        with purpose_cols[0]:
            st.markdown("#### Mission")
            st.markdown(copy.MISSION_TEXT)
        with purpose_cols[1]:
            st.markdown("#### How to use NDRO")
            st.markdown(copy.HOW_TO_USE_STEPS)

    st.divider()

    disease_options = [""] + sorted(snapshot.articles["disease_code"].dropna().unique().tolist())
    selected_disease = st.selectbox(
        "Filter by disease",
        disease_options,
        format_func=lambda code: "All diseases" if not code else copy.disease_name(code),
        key="overview_disease_filter",
    )

    articles = snapshot.articles
    coverage = snapshot.coverage
    if selected_disease:
        articles = articles[articles["disease_code"] == selected_disease]
        coverage = coverage[coverage["disease_code"] == selected_disease]

    counts = headline_counts(articles)
    cov_filtered = coverage_summary(coverage) if not coverage.empty else {
        "candidate_associations": 0,
        "eligible_associations": 0,
        "semantically_complete_associations": 0,
        "semantic_coverage_percent": None,
    }

    st.markdown("**Candidate landscape** — every known publication-disease association, including pending and excluded records.")
    candidate_cols = st.columns(3)
    candidate_cols[0].metric("Candidate associations", counts["candidate_associations"])
    candidate_cols[1].metric("Distinct publications", counts["distinct_publications"])
    disease_coverage_display = (
        f"{cov_filtered['semantic_coverage_percent']:.1f}%"
        if cov_filtered["semantic_coverage_percent"] is not None
        else "n/a"
    )
    selected_disease_name = copy.disease_name(selected_disease) if selected_disease else ""
    coverage_label = (
        f"Semantic coverage — {selected_disease_name}"
        if selected_disease
        else "Semantic coverage"
    )
    coverage_scope = f" for {selected_disease_name}" if selected_disease else ""
    candidate_cols[2].metric(
        coverage_label,
        disease_coverage_display,
        help=(
            f"{cov_filtered['semantically_complete_associations']} of "
            f"{cov_filtered['eligible_associations']} eligible associations{coverage_scope} "
            "are semantically complete."
        ),
    )

    st.markdown("**Analytical corpus breakdown** — the same associations, split by current NDRO placement.")
    bucket_cols = st.columns(4)
    bucket_cols[0].metric(
        "Core", counts["core_associations"], help=copy.CORPUS_BUCKET_EXPLANATION["core"]
    )
    bucket_cols[1].metric(
        "Separate view",
        counts["separate_associations"],
        help=copy.CORPUS_BUCKET_EXPLANATION["separate"],
    )
    bucket_cols[2].metric(
        "Excluded",
        counts["excluded_associations"],
        help=copy.CORPUS_BUCKET_EXPLANATION["excluded"],
    )
    bucket_cols[3].metric(
        "Pending",
        counts["pending_associations"],
        help=copy.CORPUS_BUCKET_EXPLANATION["pending"],
    )
    if counts.get("unrecognized_associations"):
        st.caption(
            f"{counts['unrecognized_associations']} record(s) have a corpus_status value this "
            "app build does not recognize; they are excluded from every headline count above "
            "pending review."
        )

    st.caption(
        "Candidate counts above are the full candidate landscape. They are shown separately "
        "from the semantic-completion denominator (eligible vs. semantically complete) so the "
        "two are never mixed without labeling, per the data contract."
    )

    st.divider()

    chart_cols = st.columns(2)
    with chart_cols[0]:
        st.markdown("**Core analytical publications by year**")
        st.altair_chart(
            publication_year_trend_chart(publication_year_trend(articles)),
            use_container_width=True,
        )
        st.caption(
            "This trend counts core-analytical publications after confirmed retractions are removed. "
            "Separate, excluded and pending records are not included; corrected publications remain visible."
        )
    with chart_cols[1]:
        st.markdown("**Candidate landscape by status**")
        st.altair_chart(
            candidate_landscape_chart(candidate_landscape_by_status(articles)),
            use_container_width=True,
        )
        st.caption(
            "This chart intentionally includes every status (the candidate landscape), "
            "unlike the core-only trend to its left."
        )
