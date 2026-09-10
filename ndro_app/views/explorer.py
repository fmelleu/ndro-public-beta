"""Article Explorer page: search, filter, paginate and render article cards."""

from __future__ import annotations

import streamlit as st

from .. import copy
from ..cards import render_article_card
from ..config import DEFAULT_PAGE_SIZE, PAGE_SIZE_OPTIONS
from ..data_loader import Snapshot
from ..filters import apply_filters, paginate, search_articles
from ..metrics import add_bucket_columns


def render(snapshot: Snapshot) -> None:
    st.subheader("Article Explorer")
    st.caption(
        "Search and filter every known publication-disease association in this "
        "snapshot, including separate-view, excluded and pending records. "
        + copy.EVIDENCE_BOUNDARY_TEXT
    )

    df = add_bucket_columns(snapshot.articles)

    with st.form("explorer_filters"):
        query = st.text_input(
            "Search PMID, title, authors, abstract or keywords",
            value="",
            placeholder="e.g. Alzheimer, biomarker, 90000001 …",
        )

        filter_cols = st.columns([1, 1.15, 1, 0.7])
        disease_choices = sorted(df["disease_code"].dropna().unique().tolist())
        diseases = filter_cols[0].multiselect(
            "Disease", disease_choices, format_func=copy.disease_name
        )

        years = df["publication_year"].dropna()
        if not years.empty:
            year_min, year_max = int(years.min()), int(years.max())
        else:
            year_min, year_max = 0, 0
        if year_min < year_max:
            year_range = filter_cols[1].slider(
                "Publication year", min_value=year_min, max_value=year_max, value=(year_min, year_max)
            )
        else:
            filter_cols[1].caption(f"Publication year: {year_min or '—'} (only one year in this snapshot)")
            year_range = (year_min, year_max) if year_min else None

        bucket_choices = [b for b in ["core", "separate", "excluded", "pending", "unrecognized"] if (df["corpus_bucket"] == b).any()]
        bucket_labels = {b: copy.CORPUS_BUCKET_LABELS[b] for b in bucket_choices}
        selected_bucket_labels = filter_cols[2].multiselect(
            "NDRO corpus status", list(bucket_labels.values())
        )
        selected_buckets = [b for b, label in bucket_labels.items() if label in selected_bucket_labels]

        page_size = filter_cols[3].selectbox(
            "Per page",
            options=list(PAGE_SIZE_OPTIONS),
            index=list(PAGE_SIZE_OPTIONS).index(DEFAULT_PAGE_SIZE),
        )

        with st.expander("Advanced filters"):
            filter_cols2 = st.columns(3)
            classification_choices = sorted(df["classification_status"].dropna().unique().tolist())
            classification_selected = filter_cols2[0].multiselect(
                "Classification status", classification_choices
            )

            semantic_choices = sorted(df["semantic_status"].dropna().unique().tolist())
            semantic_selected = filter_cols2[1].multiselect("Semantic status", semantic_choices)

            integrity_choices = sorted(df["integrity_status"].dropna().unique().tolist())
            integrity_selected = filter_cols2[2].multiselect("Integrity status", integrity_choices)

        st.form_submit_button("Apply search & filters", type="primary", use_container_width=True)

    filtered = search_articles(df, query)
    filtered = apply_filters(
        filtered,
        disease_codes=diseases or None,
        year_range=year_range,
        corpus_buckets=selected_buckets or None,
        classification_statuses=classification_selected or None,
        semantic_statuses=semantic_selected or None,
        integrity_states=integrity_selected or None,
    )

    st.markdown(f"**{len(filtered)}** matching association(s) out of {len(df)} in this snapshot.")

    if filtered.empty:
        st.info("No records match this search and filter combination. Try widening a filter or clearing the search box.")
        return

    page_key = "explorer_page"
    if page_key not in st.session_state:
        st.session_state[page_key] = 1

    page_slice, total_pages = paginate(filtered, st.session_state[page_key], page_size)

    nav_cols = st.columns([1, 2, 1])
    if nav_cols[0].button("◀ Previous", disabled=st.session_state[page_key] <= 1, use_container_width=True):
        st.session_state[page_key] = max(1, st.session_state[page_key] - 1)
        st.rerun()
    nav_cols[1].markdown(
        f"<div style='text-align:center;'>Page {min(st.session_state[page_key], total_pages)} of {total_pages}</div>",
        unsafe_allow_html=True,
    )
    if nav_cols[2].button("Next ▶", disabled=st.session_state[page_key] >= total_pages, use_container_width=True):
        st.session_state[page_key] = min(total_pages, st.session_state[page_key] + 1)
        st.rerun()

    page_slice, total_pages = paginate(filtered, st.session_state[page_key], page_size)

    for _, row in page_slice.iterrows():
        render_article_card(row, snapshot.evidence_spans)
