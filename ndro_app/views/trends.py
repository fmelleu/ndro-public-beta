"""Disease-specific annual and cumulative core analytical trends."""

from __future__ import annotations

import streamlit as st

from .. import copy
from ..charts import disease_trend_chart
from ..data_loader import Snapshot
from ..metrics import core_publications_by_year_and_disease, cumulative_core_publications


def render(snapshot: Snapshot) -> None:
    st.subheader("Disease Trends")
    st.caption(
        "These charts count publication–disease associations in the core analytical corpus. "
        "Separate-view, excluded, pending and confirmed retracted records are not included."
    )

    annual = core_publications_by_year_and_disease(snapshot.articles)
    cumulative = cumulative_core_publications(snapshot.articles)
    diseases = sorted(annual["disease_code"].unique().tolist())
    selected = st.multiselect(
        "Disease", diseases, default=diseases, format_func=copy.disease_name
    )
    annual = annual[annual["disease_code"].isin(selected)]
    cumulative = cumulative[cumulative["disease_code"].isin(selected)]

    if annual.empty:
        st.info("No core analytical publications match the selected diseases.")
        return

    st.altair_chart(disease_trend_chart(annual), use_container_width=True)
    st.caption(
        "Annual values show the number of core publication–disease associations in each publication year."
    )
    st.altair_chart(disease_trend_chart(cumulative, cumulative=True), use_container_width=True)
    st.caption(
        "Cumulative values are running totals within this snapshot; they can change in a later snapshot "
        "if a record is added, corrected, reclassified or retracted."
    )
