"""NDRO Streamlit public beta — entry point.

Reads a local, versioned public snapshot (CSV + JSON files) and renders a
read-only browsing interface. This app never connects to a database, never
asks for or stores credentials, never calls a paid API, and never scrapes
PubMed. It also never generates new scientific prose -- every scientific
label and explanation is fixed copy from ndro_app/copy.py or a value stored
verbatim in the snapshot itself.

Run locally with:

    streamlit run app.py

See README.md for full Windows setup and deployment instructions.
"""

from __future__ import annotations

import logging

import streamlit as st

from ndro_app import copy
from ndro_app.config import APP_VERSION, DEFAULT_SNAPSHOT_DIR_NAME, SNAPSHOTS_ROOT
from ndro_app.data_loader import Snapshot, list_available_snapshots, load_snapshot
from ndro_app.exceptions import ContractError
from ndro_app.styles import GLOBAL_STYLES
from ndro_app.views import (
    about,
    audit,
    documentation,
    downloads,
    explorer,
    geographic,
    methods,
    overview,
    protocol,
    roadmap,
    trends,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ndro_app")

st.set_page_config(
    page_title="NDRO Observatory",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown(GLOBAL_STYLES, unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading snapshot…")
def _load(snapshot_dir_str: str) -> Snapshot:
    return load_snapshot(snapshot_dir_str)


def main() -> None:
    st.title(copy.APP_TITLE)
    st.caption(copy.APP_SUBTITLE)

    available = list_available_snapshots(SNAPSHOTS_ROOT)
    with st.sidebar:
        st.header("Snapshot")
        if not available:
            st.error(
                "No snapshot directories were found under snapshots/. This "
                "app cannot display anything until a valid snapshot is "
                "present."
            )
            st.stop()
        default_index = available.index(DEFAULT_SNAPSHOT_DIR_NAME) if DEFAULT_SNAPSHOT_DIR_NAME in available else 0
        chosen = st.selectbox("Snapshot directory", available, index=default_index)

        st.divider()
        st.header("Navigate")
        pages = [
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
        ]
        requested_page = str(st.query_params.get("page", ""))
        requested_index = pages.index(requested_page) if requested_page in pages else 0
        page = st.radio(
            "Page",
            pages,
            index=requested_index,
            label_visibility="collapsed",
        )

    try:
        snapshot = _load(str(SNAPSHOTS_ROOT / chosen))
    except ContractError as exc:
        st.error(
            "This snapshot could not be loaded because it does not satisfy "
            f"the NDRO public snapshot data contract:\n\n**{exc.diagnostic}**"
        )
        st.stop()
        return
    except Exception:  # pragma: no cover - defensive: never leak internals
        logger.exception("Unexpected error while loading snapshot")
        st.error(
            "This snapshot could not be loaded due to an unexpected error. "
            "Please check the snapshot files and try again."
        )
        st.stop()
        return

    if page == "Overview":
        overview.render(snapshot)
    elif page == "Article Explorer":
        explorer.render(snapshot)
    elif page == "Disease Trends":
        trends.render(snapshot)
    elif page == "Geographic Coverage":
        geographic.render(snapshot)
    elif page == "Scientific Documentation":
        documentation.render(snapshot)
    elif page == "Review Protocol":
        protocol.render(snapshot)
    elif page == "Methods & Data Quality":
        methods.render(snapshot)
    elif page == "Planned Updates":
        roadmap.render(snapshot)
    elif page == "Audit & Corrections":
        audit.render(snapshot)
    elif page == "Downloads & Citation":
        downloads.render(snapshot)
    else:
        about.render(snapshot)

    st.divider()
    st.caption(
        f"Snapshot `{snapshot.snapshot_version}` · cutoff `{snapshot.cutoff_date}` · "
        f"NDRO Streamlit v{APP_VERSION} · snapshot data are read-only."
    )


if __name__ == "__main__":
    main()
