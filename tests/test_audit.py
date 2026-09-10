"""Audit validation and local-delivery regression tests."""

from __future__ import annotations

import json

import pytest

from ndro_app import audit
from ndro_app.audit import (
    AuditValidationError,
    build_submission,
    extract_pmid,
    normalize_orcid,
    save_local_submission,
    send_formspree,
)


def _valid_payload(**overrides):
    payload = {
        "submission_type": "Report incorrect classification",
        "snapshot_version": "test-snapshot",
        "pmid": "21127706",
        "reporter_name": "Jane Researcher",
        "reporter_email": "jane@example.org",
        "reporter_orcid": "0000-0002-1825-0097",
        "problem_type": "Incorrect inclusion",
        "suggested_reason": "Review or meta-analysis",
    }
    payload.update(overrides)
    return payload


def test_orcid_is_normalized_and_checksum_validated():
    canonical = "https://orcid.org/0000-0002-1825-0097"
    accepted_formats = (
        "0000-0002-1825-0097",
        "orcid.org/0000-0002-1825-0097",
        "https://orcid.org/0000-0002-1825-0097",
        "https://orcid.org/0000-0002-1825-0097/",
    )
    assert all(normalize_orcid(value) == canonical for value in accepted_formats)
    with pytest.raises(AuditValidationError):
        normalize_orcid("0000-0002-1825-0098")


def test_pubmed_url_is_reduced_to_pmid():
    assert extract_pmid("https://pubmed.ncbi.nlm.nih.gov/21127706/") == "21127706"


def test_missing_article_builds_canonical_pubmed_url():
    record = build_submission(
        _valid_payload(
            submission_type="Suggest a missing article",
            article_identifier="https://pubmed.ncbi.nlm.nih.gov/21127706/",
        )
    )
    assert record["pmid"] == "21127706"
    assert record["pubmed_url"] == "https://pubmed.ncbi.nlm.nih.gov/21127706/"


def test_local_submission_is_append_only_jsonl(tmp_path):
    path = tmp_path / "outbox" / "submissions.jsonl"
    first = build_submission(_valid_payload(audit_id="AUD-TEST-1"))
    second = build_submission(_valid_payload(audit_id="AUD-TEST-2"))
    save_local_submission(first, path)
    save_local_submission(second, path)
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert [row["audit_id"] for row in rows] == ["AUD-TEST-1", "AUD-TEST-2"]


def test_formspree_request_uses_cloudflare_compatible_user_agent(monkeypatch):
    captured = {}

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr(audit, "urlopen", fake_urlopen)
    send_formspree({"message": "test"}, "https://formspree.io/f/example")

    assert captured["request"].get_header("User-agent").endswith("NDRO-Streamlit/0.2")
    assert captured["request"].get_header("Content-type") == "application/json"
    assert captured["timeout"] == 15
