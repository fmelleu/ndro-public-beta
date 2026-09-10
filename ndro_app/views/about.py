"""Project identity, governance and contact placeholders."""

from __future__ import annotations

import streamlit as st

from .. import copy
from ..data_loader import Snapshot


def render(snapshot: Snapshot) -> None:
    st.subheader("About NDRO")
    st.markdown(
        f"""
        The Neurodegenerative Disease Research Observatory is an independent
        scientific data project designed to make PubMed-based classification,
        evidence boundaries and release provenance inspectable rather than
        hidden behind aggregate charts.

        #### Governance principles

        - public snapshots are immutable and versioned;
        - automated processing does not replace scientific adjudication;
        - community reports cannot write directly to canonical classifications;
        - candidate, analytical and semantic denominators remain distinct;
        - limitations and missing release artifacts are disclosed explicitly.

        #### Contact and contributors

        Project lead and community-audit data controller: **Fernando Melleu**.  
        Public audit and privacy contact:
        [{copy.AUDIT_CONTACT_EMAIL}](mailto:{copy.AUDIT_CONTACT_EMAIL}).
        Contributor ORCID identifiers and the repository URL will be added
        before deployment. NDRO software is
        licensed under Apache-2.0. NDRO-authored structured annotations are
        offered under CC BY 4.0, subject to the field-level exclusions described
        in `DATA_LICENSE.md`.
        """
    )
    st.caption(
        f"Current data release: {snapshot.snapshot_version} · cutoff {snapshot.cutoff_date}."
    )
