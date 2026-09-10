"""Snapshot downloads, checksums and provisional citation guidance."""

from __future__ import annotations

import io
import json
import zipfile

import streamlit as st

from ..config import DOCS_ROOT
from ..data_loader import Snapshot
from ..ui import info_card


@st.cache_data(show_spinner=False)
def _snapshot_zip(snapshot_dir: str) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        from pathlib import Path

        root = Path(snapshot_dir)
        for path in sorted(root.iterdir()):
            if path.is_file():
                archive.write(path, arcname=f"{root.name}/{path.name}")
    return buffer.getvalue()


def render(snapshot: Snapshot) -> None:
    st.subheader("Downloads & Citation")
    st.caption(
        "Download and cite a named immutable snapshot. The live interface can change; "
        "the snapshot version is the reproducible analytical object."
    )

    cols = st.columns(3)
    info_card(cols[0], "Snapshot", snapshot.snapshot_version)
    info_card(cols[1], "Cutoff date", snapshot.cutoff_date)
    info_card(cols[2], "Data contract", str(snapshot.metadata.get("contract_version", "—")))

    archive_name = f"{snapshot.snapshot_version}.zip"
    st.download_button(
        "Download complete public snapshot (ZIP)",
        data=_snapshot_zip(str(snapshot.snapshot_dir)),
        file_name=archive_name,
        mime="application/zip",
        type="primary",
    )
    st.download_button(
        "Download snapshot metadata (JSON)",
        data=json.dumps(snapshot.metadata, ensure_ascii=False, indent=2),
        file_name=f"{snapshot.snapshot_version}_metadata.json",
        mime="application/json",
    )

    citation_path = DOCS_ROOT / "CITATION_AND_REUSE.md"
    citation = citation_path.read_text(encoding="utf-8")
    citation = citation.replace("{snapshot_version}", snapshot.snapshot_version)
    citation = citation.replace("{cutoff_date}", snapshot.cutoff_date)
    citation = citation.replace(
        "{contract_version}", str(snapshot.metadata.get("contract_version", "not reported"))
    )
    st.markdown(citation)

    with st.expander("Release changelog"):
        st.markdown((DOCS_ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))
