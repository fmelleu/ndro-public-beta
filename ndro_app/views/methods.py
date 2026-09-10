"""Methods & Data Quality page: evidence boundary, exclusions, living-corpus
explanation, status legend, and the snapshot coverage table.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from .. import copy
from ..data_loader import Snapshot


def render(snapshot: Snapshot) -> None:
    st.subheader("Methods & Data Quality")
    st.caption(
        "Scope, classification semantics, release coverage and integrity notes for the selected snapshot."
    )

    scope_tab, status_tab, release_tab = st.tabs(
        ["Scope & corpus", "Status definitions", "Coverage & release"]
    )

    with scope_tab:
        scope_cols = st.columns(2)
        with scope_cols[0].container(border=True):
            st.markdown("#### Evidence boundary")
            st.write(copy.EVIDENCE_BOUNDARY_TEXT)
            st.write(copy.NON_ENGLISH_EXPLANATION)
            st.write(copy.INTERVENTIONS_OUTCOMES_DISCLAIMER)
        with scope_cols[1].container(border=True):
            st.markdown("#### Living corpus")
            st.write(copy.LIVING_CORPUS_EXPLANATION)
            st.markdown("#### Exclusions")
            st.write(copy.EXCLUSIONS_EXPLANATION)

        with st.expander("PubMed integrity signals"):
            st.write(copy.INTEGRITY_CLEAN_EXPLANATION)
            st.write(copy.INTEGRITY_FLAGGED_EXPLANATION)

    with status_tab:
        legend_rows = [
            {
                "Status": copy.CORPUS_BUCKET_LABELS[bucket],
                "Meaning": copy.CORPUS_BUCKET_EXPLANATION[bucket],
            }
            for bucket in ["core", "separate", "excluded", "pending", "unrecognized"]
        ]
        st.dataframe(
            pd.DataFrame(legend_rows),
            use_container_width=True,
            hide_index=True,
            height=360,
        )

        with st.expander("Raw classification and semantic status values"):
            classification_rows = [
                {
                    "Value": v,
                    "Meaning": copy.CLASSIFICATION_STATUS_LABELS.get(
                        v, "(not described by this app build)"
                    ),
                }
                for v in sorted(snapshot.articles["classification_status"].dropna().unique())
            ]
            semantic_rows = [
                {
                    "Value": v,
                    "Meaning": copy.SEMANTIC_STATUS_LABELS.get(
                        v, "(not described by this app build)"
                    ),
                }
                for v in sorted(snapshot.articles["semantic_status"].dropna().unique())
            ]
            st.markdown("**classification_status**")
            st.dataframe(pd.DataFrame(classification_rows), use_container_width=True, hide_index=True)
            st.markdown("**semantic_status**")
            st.dataframe(pd.DataFrame(semantic_rows), use_container_width=True, hide_index=True)

    with release_tab:
        st.markdown("#### Snapshot coverage by disease")
        st.caption(copy.DENOMINATOR_DISCLOSURE)
        coverage_display = snapshot.coverage.copy()
        coverage_display["disease_code"] = coverage_display["disease_code"].map(
            copy.disease_name
        )
        coverage_display = coverage_display.rename(
            columns={
                "disease_code": "Disease",
                "candidate_associations": "Candidate",
                "eligible_associations": "Eligible (semantic)",
                "semantically_complete_associations": "Semantically complete",
                "semantic_coverage_percent": "Semantic coverage %",
                "core_associations": "Core",
                "separate_associations": "Separate",
                "excluded_associations": "Excluded",
                "pending_final_classification": "Pending",
                "last_updated_at": "Last updated",
            }
        )
        display_columns = [
            "Disease",
            "Candidate",
            "Core",
            "Separate",
            "Excluded",
            "Pending",
            "Eligible (semantic)",
            "Semantically complete",
            "Semantic coverage %",
            "Last updated",
        ]
        st.dataframe(
            coverage_display[display_columns],
            use_container_width=True,
            hide_index=True,
            height=290,
        )

        with st.expander("Release metadata"):
            st.json(snapshot.metadata, expanded=True)

        if snapshot.warnings:
            st.markdown("#### Data-quality notes for this snapshot")
            for warning in snapshot.warnings:
                st.warning(warning)
