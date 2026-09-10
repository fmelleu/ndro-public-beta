"""Rendering helpers for a single article: the PubMed-like card, the
collapsed plain-language selection panel, and the evidence-span grouping.

These functions do call Streamlit (``st.*``) -- unlike metrics/filters,
rendering is inherently tied to the widget tree. Keeping them in one module
still centralizes *how* an article is displayed, even though the *words*
used live in ``ndro_app.copy``.
"""

from __future__ import annotations

from html import escape
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st

from . import copy
from .metrics import corpus_bucket


def _badge_html(text: str, fg: str, bg: str) -> str:
    safe_text = escape(str(text), quote=True)
    return (
        f'<span style="background-color:{bg}; color:{fg}; padding:2px 10px; '
        f'border-radius:999px; font-size:0.82rem; font-weight:600; '
        f'border:1px solid {fg}22; white-space:nowrap;">{safe_text}</span>'
    )


def status_badge_html(bucket: str) -> str:
    colors = copy.CORPUS_BUCKET_COLORS.get(bucket, {"fg": "#41464b", "bg": "#e2e3e5"})
    label = copy.CORPUS_BUCKET_SHORT_BADGE.get(bucket, bucket.title())
    return _badge_html(label, colors["fg"], colors["bg"])


def integrity_badge_html(integrity_status) -> str:
    status = _clean(integrity_status).lower()
    if status == "retracted":
        return _badge_html("Retracted — excluded from analytics", "#842029", "#f8d7da")
    if status == "corrected":
        return _badge_html("Corrected publication", "#084298", "#cfe2ff")
    if status == "expression_of_concern":
        return _badge_html("Expression of concern", "#664d03", "#fff3cd")
    if status == "no_pubmed_integrity_signal":
        return _badge_html("No PubMed integrity signal", "#0f5132", "#d1e7dd")
    return _badge_html("Integrity status needs review", "#41464b", "#e2e3e5")


def _clean(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value).strip()


def _keywords_list(raw_keywords: str) -> list:
    raw = _clean(raw_keywords)
    if not raw:
        return []
    return [k.strip() for k in raw.split(";") if k.strip()]


def _criterion_label(raw_value, labels: dict[str, str]) -> str:
    raw = _clean(raw_value)
    if not raw:
        return "No criterion is stored for this record."
    return labels.get(raw.casefold(), raw)


def _abstract_source_notice(pubmed_url: str) -> str:
    links = []
    if pubmed_url:
        links.append(f"[View in PubMed ↗]({pubmed_url})")
    links.append(
        f"[NLM copyright information]({copy.NLM_COPYRIGHT_INFORMATION_URL})"
    )
    return (
        f"**From PubMed metadata.** {copy.PUBMED_DERIVED_RIGHTS_NOTICE} "
        + " · ".join(links)
    )


def exclusion_reason_details(row: pd.Series) -> dict[str, str]:
    """Return row-level exclusion details without inferring new evidence."""
    status = _clean(row.get("corpus_status")).lower()
    if status == "excluded_eligibility":
        details = {
            "layer": "Eligibility",
            "criterion": _criterion_label(
                row.get("eligibility_reason"), copy.ELIGIBILITY_EXCLUSION_CRITERIA
            ),
        }
        additional_note = _clean(row.get("language_exclusion_reason"))
        if additional_note:
            details["additional_note"] = additional_note
        return details
    if status == "excluded_relevance":
        return {
            "layer": "Relevance",
            "criterion": _criterion_label(
                row.get("relevance_class"), copy.RELEVANCE_EXCLUSION_CRITERIA
            ),
        }
    return {}


def render_article_card(row: pd.Series, evidence_df: pd.DataFrame) -> None:
    """Render one PubMed-like article card with a collapsed plain-language
    panel and grouped evidence spans, following the UI scientific
    requirements exactly (never inventing a reason from a blank field)."""
    bucket = corpus_bucket(row.get("corpus_status"))
    integrity_status = row.get("integrity_status")

    title = _clean(row.get("title")) or "(untitled record)"
    pmid = _clean(row.get("pmid"))
    pubmed_url = _clean(row.get("pubmed_url"))
    authors = _clean(row.get("authors")) or "Authors not reported"
    journal = _clean(row.get("journal")) or "Journal not reported"
    year = _clean(row.get("publication_year")) or "Year not reported"
    abstract = _clean(row.get("abstract")) or "No abstract available in this snapshot."
    disease_display = copy.disease_name(row.get("disease_code"))
    keywords = _keywords_list(row.get("keywords"))

    with st.container(border=True):
        header_cols = st.columns([5, 2])
        with header_cols[0]:
            if pubmed_url:
                st.markdown(f"##### [{title}]({pubmed_url})")
            else:
                st.markdown(f"##### {title}")
            st.caption(f"{authors} — *{journal}*, {year}")
        with header_cols[1]:
            st.markdown(
                f'<div style="text-align:right; line-height:2.1;">'
                f"{status_badge_html(bucket)}<br/>{integrity_badge_html(integrity_status)}"
                f"</div>",
                unsafe_allow_html=True,
            )

        meta_cols = st.columns([1, 1, 2])
        meta_cols[0].markdown(f"**PMID:** {pmid or '—'}")
        meta_cols[1].markdown(f"**Disease:** {disease_display}")
        if pubmed_url:
            meta_cols[2].markdown(f"[View on PubMed ↗]({pubmed_url})")

        with st.expander("Abstract", expanded=False):
            st.caption(_abstract_source_notice(pubmed_url))
            st.write(abstract)

        if keywords:
            st.markdown(
                " ".join(_badge_html(k, "#0b3d91", "#eef2ff") for k in keywords),
                unsafe_allow_html=True,
            )

        question = copy.plain_language_question(bucket)
        with st.expander(question, expanded=False):
            exclusion_details = exclusion_reason_details(row)
            if exclusion_details:
                st.markdown(f"**Exclusion layer:** {exclusion_details['layer']}")
                st.markdown(f"**Recorded criterion:** {exclusion_details['criterion']}")
                if exclusion_details.get("additional_note"):
                    st.markdown(
                        f"**Additional recorded note:** {exclusion_details['additional_note']}"
                    )
            else:
                explanation = _clean(row.get("plain_language_explanation"))
                if explanation:
                    st.write(explanation)
                else:
                    # Never invent a reason from a blank field.
                    st.write(
                        "No plain-language explanation is stored for this "
                        "record in this snapshot."
                    )
            st.caption(copy.CORPUS_BUCKET_EXPLANATION.get(bucket, ""))

            _render_evidence_groups(evidence_df, row.get("association_id"))

        st.markdown(
            f'<span style="font-size:0.85rem; color:#495057;">{copy.COMMUNITY_INVITATION_TEXT}</span>',
            unsafe_allow_html=True,
        )
        association_id = _clean(row.get("association_id"))
        audit_url = (
            "?page=Audit%20%26%20Corrections"
            f"&pmid={quote_plus(pmid)}"
            f"&association_id={quote_plus(association_id)}"
        )
        st.link_button(
            "Report a possible classification issue",
            audit_url,
            help=copy.COMMUNITY_INVITATION_DISABLED_NOTE,
        )


def _render_evidence_groups(evidence_df: pd.DataFrame, association_id) -> None:
    if evidence_df is None or evidence_df.empty or association_id is None:
        return
    rows = evidence_df[evidence_df["association_id"] == association_id]
    if rows.empty:
        return
    st.markdown("**Available evidence**")
    for subject_type, group in rows.groupby("subject_type", sort=False):
        heading = copy.evidence_heading(subject_type)
        spans = [f"“{_clean(t)}”" for t in group["evidence_text"] if _clean(t)]
        if not spans:
            continue
        st.markdown(f"*{heading}:* " + "; ".join(spans))
