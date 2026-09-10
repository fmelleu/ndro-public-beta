"""Public, versioned explanation of the NDRO evidence-review protocol."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from .. import copy
from ..data_loader import Snapshot


def render(snapshot: Snapshot) -> None:
    st.subheader("Review Protocol")
    st.caption(
        f"{copy.PROTOCOL_VERSION} · applied to the architecture supporting "
        f"snapshot {snapshot.snapshot_version}."
    )
    st.write(
        "This page follows the logic of a systematic-review protocol, while "
        "preserving NDRO's defining unit: the publication–disease association."
    )

    flow_tab, search_tab, rules_tab, release_tab = st.tabs(
        ["Flowchart", "Search strategy", "Screening rules", "Versioning & audit"]
    )

    with flow_tab:
        st.markdown(copy.PROTOCOL_FLOW_HTML, unsafe_allow_html=True)
        st.caption(copy.PROTOCOL_STATUS_NOTE)

    with search_tab:
        st.markdown("### PubMed candidate queries")
        st.info(copy.SEARCH_PROTOCOL_NOTE)
        queries = pd.DataFrame(copy.SEARCH_QUERIES).rename(
            columns={"disease": "Disease", "query": "Current candidate query"}
        )
        st.dataframe(queries, hide_index=True, use_container_width=True)
        st.markdown(
            "**Acquisition and preservation.** ESearch retrieves identifiers and "
            "EFetch retrieves PubMed XML. Result sets above 10,000 are recursively "
            "partitioned by publication date. NDRO preserves the complete raw XML "
            "and the executed-query manifest before creating analytical tables."
        )
        st.markdown("### Duplicate handling")
        st.write(copy.DEDUPLICATION_NOTE)

    with rules_tab:
        st.markdown("### Deterministic eligibility")
        rules = pd.DataFrame(
            copy.DETERMINISTIC_RULES, columns=["Rule", "Current routing"]
        )
        st.dataframe(rules, hide_index=True, use_container_width=True)
        st.markdown("### Relevance placement")
        routing = pd.DataFrame(
            copy.RELEVANCE_ROUTING, columns=["Relevance class", "Analytical placement"]
        )
        st.dataframe(routing, hide_index=True, use_container_width=True)
        st.warning(
            "The production semantic screen and deep-extraction worker are planned, "
            "not yet active at full corpus scale. Semantic claims will require literal "
            "evidence from title, abstract or affiliation and will be validated before import."
        )

    with release_tab:
        st.markdown("### Storage and provenance")
        st.write(
            "PostgreSQL is the canonical source of truth. Source observations, current "
            "publication metadata, semantic assertions and audit events occupy separate "
            "schemas. Classification history is revision-based: an accepted correction "
            "does not silently overwrite the previous decision."
        )
        st.markdown("### Retractions and corrections")
        st.write(copy.RETRACTION_PROTOCOL)
        st.markdown("### Publication")
        st.write(
            "A release freezes its version, cutoff, status and denominators. A public "
            "CSV/JSON derivative is privacy-minimized, validated against the data contract "
            "and accompanied by SHA-256 checksums. Streamlit and Power BI must be rebuilt "
            "from that same immutable snapshot. Community reports enter a separate review "
            "workflow and can affect only a later release."
        )
