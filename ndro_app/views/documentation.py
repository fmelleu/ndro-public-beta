"""Versioned scientific documentation rendered from Markdown sources."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from ..config import DOCS_ROOT
from ..data_loader import Snapshot


DOCUMENTS = {
    "Introduction": "INTRODUCTION.md",
    "Methodology": "METHODOLOGY.md",
    "Review protocol": "REVIEW_PROTOCOL.md",
    "Data dictionary": "DATA_DICTIONARY.md",
    "Community audit policy": "AUDIT_POLICY.md",
}


def _render_markdown(path: Path) -> None:
    if not path.exists():
        st.error("This documentation file is not available in the application package.")
        return
    st.markdown(path.read_text(encoding="utf-8"))


def render(snapshot: Snapshot) -> None:
    st.subheader("Scientific Documentation")
    st.caption(
        f"Documentation displayed with snapshot {snapshot.snapshot_version}. "
        "Scientific source text is versioned with the application rather than generated at runtime."
    )
    tabs = st.tabs(list(DOCUMENTS))
    for tab, filename in zip(tabs, DOCUMENTS.values()):
        with tab:
            _render_markdown(DOCS_ROOT / filename)
