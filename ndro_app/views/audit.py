"""Community audit form with prefilled, immutable article context."""

from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from .. import copy
from ..audit import (
    MISSING_ARTICLE_REASONS,
    PROBLEM_REASONS,
    AuditDeliveryError,
    AuditValidationError,
    build_submission,
    save_local_submission,
    send_formspree,
)
from ..config import AUDIT_OUTBOX_PATH
from ..data_loader import Snapshot
from ..metrics import corpus_bucket


SUBMISSION_TYPES = ("Report incorrect classification", "Suggest a missing article")


def _clean(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value).strip()


def _query_value(name: str) -> str:
    value = st.query_params.get(name, "")
    if isinstance(value, list):
        return str(value[0]) if value else ""
    return str(value)


def _find_target(snapshot: Snapshot):
    association_id = _query_value("association_id")
    pmid = _query_value("pmid")
    articles = snapshot.articles
    if association_id:
        matches = articles[articles["association_id"].astype(str) == association_id]
        if not matches.empty:
            return matches.iloc[0]
    if pmid:
        matches = articles[articles["pmid"].astype(str) == pmid]
        if len(matches) == 1:
            return matches.iloc[0]
        if len(matches) > 1:
            labels = {
                f"{copy.disease_name(row['disease_code'])} — {_clean(row['association_id'])}": idx
                for idx, row in matches.iterrows()
            }
            selected = st.selectbox("Select the publication–disease association", list(labels))
            return matches.loc[labels[selected]]
    return None


def _audit_settings() -> tuple[str, str]:
    endpoint = os.getenv("NDRO_FORMSPREE_ENDPOINT", "").strip()
    environment = os.getenv("NDRO_ENVIRONMENT", "local").strip().lower()
    try:
        audit_secrets = st.secrets.get("audit", {})
        endpoint = str(audit_secrets.get("formspree_endpoint", endpoint)).strip()
        environment = str(audit_secrets.get("environment", environment)).strip().lower()
    except (FileNotFoundError, KeyError):
        pass
    return endpoint, environment


def _existing_record_fields(snapshot: Snapshot, target) -> dict:
    if target is None:
        identifier = st.text_input("PMID or PubMed URL", placeholder="e.g. 21127706")
        pmid = ""
        if identifier:
            digits = "".join(ch for ch in identifier if ch.isdigit())
            pmid = digits
            matches = snapshot.articles[snapshot.articles["pmid"].astype(str) == pmid]
            if not matches.empty:
                target = matches.iloc[0]
        if target is None:
            st.info("Open this form from an article card to prefill and lock the record context.")
            return {"pmid": pmid, "article_identifier": identifier}

    bucket = corpus_bucket(target.get("corpus_status"))
    cols = st.columns([1, 1, 3])
    cols[0].text_input("PMID", value=_clean(target.get("pmid")), disabled=True)
    cols[1].text_input(
        "Disease", value=copy.disease_name(target.get("disease_code")), disabled=True
    )
    cols[2].text_input("Current NDRO status", value=copy.CORPUS_BUCKET_LABELS[bucket], disabled=True)
    st.markdown(f"**Article:** {_clean(target.get('title'))}")

    problem_type = st.selectbox("Problem type", list(PROBLEM_REASONS))
    suggested_reason = st.selectbox("Suggested reason", list(PROBLEM_REASONS[problem_type]))
    suggested_disease = ""
    if problem_type == "Incorrect disease assignment":
        disease_options = sorted(snapshot.articles["disease_code"].dropna().unique().tolist())
        suggested_disease = st.selectbox(
            "Suggested disease", disease_options, format_func=copy.disease_name
        )

    return {
        "association_id": _clean(target.get("association_id")),
        "pmid": _clean(target.get("pmid")),
        "pubmed_url": _clean(target.get("pubmed_url")),
        "title": _clean(target.get("title")),
        "disease_code": _clean(target.get("disease_code")),
        "current_corpus_status": _clean(target.get("corpus_status")),
        "current_classification_status": _clean(target.get("classification_status")),
        "problem_type": problem_type,
        "suggested_reason": suggested_reason,
        "suggested_disease": suggested_disease,
    }


def render(snapshot: Snapshot) -> None:
    st.subheader("Audit & Corrections")
    st.info(copy.AUDIT_SCIENTIFIC_GUARDRAIL)

    target = _find_target(snapshot)
    default_type = "Report incorrect classification" if target is not None else SUBMISSION_TYPES[0]
    endpoint, environment = _audit_settings()

    with st.form("community_audit_form", clear_on_submit=False):
        submission_type = st.selectbox(
            "What would you like to report?",
            SUBMISSION_TYPES,
            index=SUBMISSION_TYPES.index(default_type),
        )

        report_details: dict
        if submission_type == "Report incorrect classification":
            report_details = _existing_record_fields(snapshot, target)
        else:
            article_identifier = st.text_input(
                "Missing article PMID or PubMed URL",
                placeholder="e.g. 21127706 or https://pubmed.ncbi.nlm.nih.gov/21127706/",
            )
            disease_options = sorted(snapshot.articles["disease_code"].dropna().unique().tolist())
            disease_code = st.selectbox(
                "Target disease", disease_options, format_func=copy.disease_name
            )
            suggested_reason = st.selectbox("Reason for inclusion", MISSING_ARTICLE_REASONS)
            report_details = {
                "article_identifier": article_identifier,
                "disease_code": disease_code,
                "suggested_reason": suggested_reason,
            }

        st.markdown("#### Reporter identification")
        identity_cols = st.columns(3)
        reporter_name = identity_cols[0].text_input("Name")
        reporter_email = identity_cols[1].text_input("Email")
        reporter_orcid = identity_cols[2].text_input(
            "ORCID",
            placeholder="0000-0002-1825-0097 or orcid.org/...",
            help=(
                "Enter the 16-digit ORCID iD or its orcid.org URL. "
                "The check digit is validated before submission."
            ),
        )

        st.caption(copy.AUDIT_PRIVACY_NOTICE)
        consent = st.checkbox(copy.AUDIT_CONSENT_LABEL)
        submitted = st.form_submit_button("Submit audit report", type="primary", use_container_width=True)

    if not submitted:
        if not endpoint:
            st.caption(
                "Local preview mode: valid test submissions are written only to the git-ignored local audit outbox."
            )
        return

    if not consent:
        st.error("Confirm that you have read the notice before submitting.")
        return

    payload = {
        "submission_type": submission_type,
        "snapshot_version": snapshot.snapshot_version,
        "snapshot_cutoff_date": snapshot.cutoff_date,
        "reporter_name": reporter_name,
        "reporter_email": reporter_email,
        "reporter_orcid": reporter_orcid,
        "consent_confirmed": True,
        "privacy_notice_version": copy.AUDIT_PRIVACY_NOTICE_VERSION,
        **report_details,
    }
    try:
        record = build_submission(payload)
        if endpoint:
            send_formspree(record, endpoint)
        elif environment == "production":
            raise AuditDeliveryError(
                "Audit delivery is not configured. The report was not stored or sent."
            )
        else:
            save_local_submission(record, AUDIT_OUTBOX_PATH)
    except (AuditValidationError, AuditDeliveryError) as exc:
        st.error(str(exc))
        return

    st.success(
        "Thank you. Your audit report has been received and will be reviewed by the "
        "NDRO team. We will contact you only if clarification is required and once "
        "more to communicate the outcome."
    )
    st.caption(
        f"Reference ID: {record['audit_id']}. Keep this identifier if you need to "
        "refer to the submission later."
    )
