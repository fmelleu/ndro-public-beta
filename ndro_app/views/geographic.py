"""Reported study-context geography derived from completed study facts."""

from __future__ import annotations

import streamlit as st

from .. import copy
from ..charts import reported_country_chart
from ..data_loader import Snapshot
from ..metrics import reported_country_tally


def render(snapshot: Snapshot) -> None:
    st.subheader("Geographic Coverage")
    st.warning(copy.GEOGRAPHIC_SCOPE_NOTICE)
    st.caption(copy.GEOGRAPHIC_FUTURE_SCOPE)

    country_df = reported_country_tally(snapshot.study_facts)
    if country_df.empty:
        st.info("No country values are available in completed study facts for this snapshot.")
        return

    diseases = sorted(country_df["disease_code"].unique().tolist())
    selected = st.multiselect(
        "Disease",
        diseases,
        default=diseases,
        format_func=copy.disease_name,
        key="geo_disease_filter",
    )
    filtered = country_df[country_df["disease_code"].isin(selected)]
    if filtered.empty:
        st.info("No country values match the selected diseases.")
        return

    unique_countries = int(filtered["country"].nunique())
    association_mentions = int(filtered["association_count"].sum())
    cols = st.columns(2)
    cols[0].metric(
        "Study-context countries",
        unique_countries,
        help="Unique countries extracted from completed study-context records after filtering.",
    )
    cols[1].metric(
        "Association–country links",
        association_mentions,
        help="One publication–disease association may report more than one country.",
    )

    st.altair_chart(reported_country_chart(filtered, limit=12), use_container_width=True)
    matrix = filtered.pivot_table(
        index="country",
        columns="disease_code",
        values="association_count",
        aggfunc="sum",
        fill_value=0,
    )
    matrix = matrix.rename(columns=copy.disease_name)
    matrix["Total"] = matrix.sum(axis=1)
    matrix = matrix.sort_values("Total", ascending=False)
    matrix.index.name = "Study-context country"
    st.markdown("#### Study-context country by disease")
    st.caption(
        "Cells count publication–disease associations, not unique publications or author affiliations."
    )
    st.dataframe(matrix, use_container_width=True, height=400)
