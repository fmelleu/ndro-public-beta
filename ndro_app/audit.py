"""Validation and delivery helpers for community audit submissions.

The public snapshot remains immutable. Audit submissions are separate
candidate records. Locally, they are appended to a git-ignored JSONL outbox;
when a Formspree endpoint is configured, they are delivered over HTTPS.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
ORCID_RE = re.compile(
    r"^(?:(?:https?://)?(?:www\.)?orcid\.org/)?"
    r"(\d{4})-?(\d{4})-?(\d{4})-?(\d{3}[\dXx])/?$",
    re.IGNORECASE,
)
PMID_URL_RE = re.compile(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", re.IGNORECASE)


PROBLEM_REASONS = {
    "Incorrect inclusion": (
        "Not about the target disease",
        "Review or meta-analysis",
        "Case report or case series",
        "Background mention only",
        "Comparative mention only",
    ),
    "Incorrect exclusion": (
        "Should be included in the core corpus",
        "Should be placed in the separate view",
    ),
    "Incorrect disease assignment": (
        "Wrong disease assigned",
        "Additional target disease should be assigned",
    ),
    "Incorrect publication type": (
        "Original research misclassified",
        "Review or meta-analysis misclassified",
        "Case report or case series misclassified",
    ),
    "Duplicate record": ("Same publication appears more than once",),
    "Retracted or corrected publication": (
        "Known retraction is not represented",
        "Known correction is not represented",
    ),
    "Incorrect or missing metadata": (
        "Missing abstract",
        "Incorrect abstract",
        "Incorrect title, year, journal or author metadata",
    ),
}

MISSING_ARTICLE_REASONS = (
    "Primary research about the target disease",
    "Clinical study",
    "Experimental model",
    "Intervention or treatment study",
    "Biomarker or diagnostic study",
    "Epidemiological study",
)


class AuditValidationError(ValueError):
    """A safe, user-facing audit form validation error."""


class AuditDeliveryError(RuntimeError):
    """A safe, user-facing delivery failure."""


def normalize_email(value: str) -> str:
    email = str(value or "").strip().lower()
    if not EMAIL_RE.fullmatch(email):
        raise AuditValidationError("Enter a valid email address.")
    return email


def normalize_orcid(value: str) -> str:
    """Validate and normalize an ORCID iD, including its check digit."""
    match = ORCID_RE.fullmatch(str(value or "").strip())
    if not match:
        raise AuditValidationError("Enter a valid ORCID iD, for example 0000-0002-1825-0097.")
    compact = "".join(match.groups()).upper()
    total = 0
    for char in compact[:15]:
        total = (total + int(char)) * 2
    remainder = total % 11
    result = (12 - remainder) % 11
    expected = "X" if result == 10 else str(result)
    if compact[-1] != expected:
        raise AuditValidationError("The ORCID check digit is not valid.")
    formatted = f"{compact[0:4]}-{compact[4:8]}-{compact[8:12]}-{compact[12:16]}"
    return f"https://orcid.org/{formatted}"


def extract_pmid(value: str) -> str:
    raw = str(value or "").strip()
    if raw.isdigit():
        return raw
    match = PMID_URL_RE.search(raw)
    if match:
        return match.group(1)
    raise AuditValidationError("Enter a PMID or a valid PubMed article URL.")


def new_audit_id(now: Optional[datetime] = None) -> str:
    timestamp = now or datetime.now(timezone.utc)
    return f"AUD-{timestamp:%Y%m%d}-{uuid.uuid4().hex[:8].upper()}"


def build_submission(payload: Mapping[str, object]) -> dict:
    """Return a validated, serializable audit record."""
    name = str(payload.get("reporter_name", "")).strip()
    if len(name) < 2:
        raise AuditValidationError("Enter your name.")
    submission_type = str(payload.get("submission_type", "")).strip()
    if submission_type not in {"Report incorrect classification", "Suggest a missing article"}:
        raise AuditValidationError("Choose a valid submission type.")

    record = dict(payload)
    record["reporter_name"] = name
    record["reporter_email"] = normalize_email(str(payload.get("reporter_email", "")))
    record["reporter_orcid"] = normalize_orcid(str(payload.get("reporter_orcid", "")))
    record["audit_id"] = str(payload.get("audit_id") or new_audit_id())
    record["submitted_at"] = str(
        payload.get("submitted_at") or datetime.now(timezone.utc).isoformat()
    )

    if submission_type == "Suggest a missing article":
        record["pmid"] = extract_pmid(str(payload.get("article_identifier", "")))
        record["pubmed_url"] = f"https://pubmed.ncbi.nlm.nih.gov/{record['pmid']}/"
    elif not str(record.get("pmid", "")).strip():
        raise AuditValidationError("The existing record has no PMID.")
    return record


def save_local_submission(record: Mapping[str, object], outbox_path: Path) -> None:
    outbox_path = Path(outbox_path)
    outbox_path.parent.mkdir(parents=True, exist_ok=True)
    with outbox_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(record), ensure_ascii=False, sort_keys=True) + "\n")


def send_formspree(record: Mapping[str, object], endpoint: str, timeout: int = 15) -> None:
    endpoint = str(endpoint or "").strip()
    if not endpoint.startswith("https://formspree.io/"):
        raise AuditDeliveryError("The configured form endpoint is not valid.")
    body = json.dumps(dict(record), ensure_ascii=False).encode("utf-8")
    request = Request(
        endpoint,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            # Formspree's Cloudflare policy rejects Python's default
            # ``Python-urllib`` signature with HTTP 403 / Error 1010.
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/140.0 Safari/537.36 "
                "NDRO-Streamlit/0.2"
            ),
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            if not 200 <= response.status < 300:
                raise AuditDeliveryError("The audit service did not accept the submission.")
    except HTTPError as exc:
        raise AuditDeliveryError(f"The audit service returned HTTP {exc.code}.") from exc
    except URLError as exc:
        raise AuditDeliveryError("The audit service could not be reached.") from exc
