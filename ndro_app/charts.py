"""Altair chart builders. Kept separate from page rendering so the
underlying data (already computed by ndro_app.metrics) is the only thing
these functions touch -- no filtering or bucketing logic lives here.
"""

from __future__ import annotations

import altair as alt
import pandas as pd

from . import copy

_ACCESSIBLE_CORE_COLOR = "#2f6f4f"  # readable on white, distinguishable without relying on hue alone
_DISEASE_ORDER = list(copy.DISEASE_NAMES.values())
_DISEASE_COLORS = ["#2F6F4F", "#0B3D91", "#8A6100", "#842029", "#495057"]


def publication_year_trend_chart(trend_df: pd.DataFrame) -> alt.Chart:
    """Bar chart of core-analytical publications by year. Caller is
    responsible for having already restricted the input to core-analytical
    rows (see ndro_app.metrics.publication_year_trend)."""
    if trend_df.empty:
        return (
            alt.Chart(pd.DataFrame({"publication_year": [], "count": []}))
            .mark_bar()
            .properties(height=260)
        )
    chart = (
        alt.Chart(trend_df)
        .mark_bar(color=_ACCESSIBLE_CORE_COLOR)
        .encode(
            x=alt.X("publication_year:O", title="Publication year"),
            y=alt.Y("count:Q", title="Core-analytical publications", axis=alt.Axis(tickMinStep=1)),
            tooltip=[
                alt.Tooltip("publication_year:O", title="Year"),
                alt.Tooltip("count:Q", title="Core-analytical publications"),
            ],
        )
    )
    labels = (
        alt.Chart(trend_df)
        .mark_text(dy=-8)
        .encode(x="publication_year:O", y="count:Q", text="count:Q")
    )
    return (chart + labels).properties(height=260)


def candidate_landscape_chart(landscape_df: pd.DataFrame) -> alt.Chart:
    """Bar chart of every corpus bucket (candidate view: core, separate,
    excluded, pending, unrecognized). Explicitly labeled as the candidate
    landscape, never merged visually with the core-only trend."""
    if landscape_df.empty:
        return (
            alt.Chart(pd.DataFrame({"corpus_bucket": [], "count": []}))
            .mark_bar()
            .properties(height=260)
        )
    df = landscape_df.copy()
    df["label"] = df["corpus_bucket"].map(copy.CORPUS_BUCKET_SHORT_BADGE).fillna(df["corpus_bucket"])
    order = ["core", "separate", "excluded", "pending", "unrecognized"]
    label_order = [copy.CORPUS_BUCKET_SHORT_BADGE.get(bucket, bucket) for bucket in order]
    color_scale = alt.Scale(
        domain=order,
        range=[
            copy.CORPUS_BUCKET_COLORS.get(bucket, {"fg": "#495057"})["fg"]
            for bucket in order
        ],
    )
    max_count = float(df["count"].max()) if not df.empty else 0.0
    x_domain_max = max(1.0, max_count * 1.12)

    bars = (
        alt.Chart(df)
        .mark_bar(size=24, cornerRadiusEnd=3)
        .encode(
            x=alt.X(
                "count:Q",
                title="Associations",
                stack=None,
                scale=alt.Scale(domain=[0, x_domain_max]),
                axis=alt.Axis(tickMinStep=1),
            ),
            y=alt.Y(
                "label:N",
                title=None,
                sort=label_order,
                axis=alt.Axis(labelLimit=130, labelPadding=8),
            ),
            color=alt.Color("corpus_bucket:N", scale=color_scale, legend=None),
            tooltip=[
                alt.Tooltip("label:N", title="Status"),
                alt.Tooltip("count:Q", title="Associations"),
            ],
        )
    )
    labels = (
        alt.Chart(df)
        .mark_text(align="left", baseline="middle", dx=6, color="#343a40")
        .encode(
            x=alt.X("count:Q", scale=alt.Scale(domain=[0, x_domain_max])),
            y=alt.Y("label:N", sort=label_order),
            text=alt.Text("count:Q", format="d"),
        )
    )
    return (bars + labels).properties(height=260)


def disease_trend_chart(trend_df: pd.DataFrame, cumulative: bool = False) -> alt.Chart:
    display_df = trend_df.copy()
    display_df["disease_name"] = display_df["disease_code"].map(copy.disease_name)
    value_field = "cumulative_count" if cumulative else "count"
    title = (
        "Cumulative core analytical publications by disease"
        if cumulative
        else "Annual core analytical publications by disease"
    )
    y_title = "Cumulative publications" if cumulative else "Annual publications"
    return (
        alt.Chart(display_df)
        .mark_line(point=True, strokeWidth=2.5)
        .encode(
            x=alt.X("publication_year:O", title="Publication year"),
            y=alt.Y(f"{value_field}:Q", title=y_title, axis=alt.Axis(tickMinStep=1)),
            color=alt.Color(
                "disease_name:N",
                title="Disease",
                scale=alt.Scale(domain=_DISEASE_ORDER, range=_DISEASE_COLORS),
                sort=_DISEASE_ORDER,
            ),
            tooltip=[
                alt.Tooltip("disease_name:N", title="Disease"),
                alt.Tooltip("publication_year:O", title="Year"),
                alt.Tooltip(f"{value_field}:Q", title=y_title),
            ],
        )
        .properties(height=340, title=title)
    )


def reported_country_chart(country_df: pd.DataFrame, limit: int = 15) -> alt.Chart:
    totals = (
        country_df.groupby("country", as_index=False)["association_count"]
        .sum()
        .sort_values("association_count", ascending=False)
        .head(limit)
    )
    return (
        alt.Chart(totals)
        .mark_bar(color=_ACCESSIBLE_CORE_COLOR)
        .encode(
            x=alt.X("association_count:Q", title="Publication–disease associations"),
            y=alt.Y("country:N", title="Study-context country", sort="-x"),
            tooltip=[
                alt.Tooltip("country:N", title="Country"),
                alt.Tooltip("association_count:Q", title="Associations"),
            ],
        )
        .properties(height=360, title=f"Top {limit} study-context countries")
    )
