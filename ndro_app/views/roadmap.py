"""Public roadmap for planned NDRO releases."""

from __future__ import annotations

import streamlit as st

from .. import copy
from ..data_loader import Snapshot


def render(snapshot: Snapshot) -> None:
    st.subheader("Planned Updates")
    st.caption(
        f"Roadmap associated with snapshot {snapshot.snapshot_version}; priorities may "
        "be refined when validation evidence becomes available."
    )
    st.info(copy.ROADMAP_INTRO)

    for item in copy.ROADMAP_PHASES:
        with st.container(border=True):
            heading, status = st.columns([4, 1.2])
            heading.markdown(f"### {item['phase']}. {item['title']}")
            status.caption(item["status"])
            st.write(item["description"])

    st.warning(
        "Multiple sclerosis is planned only after the infrastructure, update workflow "
        "and semantic validation are stable. Its inclusion will be accompanied by a "
        "documented scientific-scope justification."
    )

