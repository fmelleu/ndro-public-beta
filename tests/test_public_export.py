import csv
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from ndro_app.data_loader import load_snapshot
from ndro_app.public_export import (
    EMAIL_REDACTION_TOKEN,
    create_redacted_public_snapshot,
    redact_email_addresses,
    scan_snapshot_for_email_addresses,
)


def test_redact_email_addresses_preserves_surrounding_text():
    cleaned, count = redact_email_addresses("Contact jane.doe+lab@example.org for details.")
    assert count == 1
    assert cleaned == f"Contact {EMAIL_REDACTION_TOKEN} for details."


def test_public_snapshot_email_scan_is_clean(real_snapshot_dir):
    findings = scan_snapshot_for_email_addresses(real_snapshot_dir)
    assert findings == {}


def _copy_with_synthetic_email(source: Path, destination: Path) -> Path:
    """Create a non-sensitive source fixture for exercising public redaction."""
    shutil.copytree(source, destination)
    evidence_path = destination / "evidence_spans.csv"
    with evidence_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        rows = list(reader)
    assert fieldnames
    rows[0]["evidence_text"] += " Contact jane.doe+ndro@example.org."
    with evidence_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return destination


def test_redacted_public_snapshot_is_loadable_and_has_valid_checksums(
    tmp_path: Path, real_snapshot_dir: Path
):
    source = _copy_with_synthetic_email(real_snapshot_dir, tmp_path / "source-with-fake-email")
    destination = tmp_path / "ndro-public-redacted-test"
    report = create_redacted_public_snapshot(
        source,
        destination,
        "ndro-public-redacted-test",
        generated_at="2026-09-03T12:00:00+00:00",
    )

    assert report.email_occurrences_redacted == 1
    assert report.files_changed == ("evidence_spans.csv",)
    assert scan_snapshot_for_email_addresses(destination) == {}
    loaded = load_snapshot(destination)
    assert loaded.snapshot_version == "ndro-public-redacted-test"

    metadata = json.loads((destination / "snapshot_metadata.json").read_text(encoding="utf-8"))
    assert metadata["source_snapshot_version"] == "ndro-mvp-v0.1.2-20260823"
    assert metadata["public_export_transformations"][0]["occurrences"] == 1

    with (destination / "SHA256SUMS.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            digest = hashlib.sha256((destination / row["file"]).read_bytes()).hexdigest()
            assert digest == row["sha256"]


def test_redacted_export_refuses_to_overwrite(tmp_path: Path, real_snapshot_dir: Path):
    destination = tmp_path / "already-there"
    destination.mkdir()
    with pytest.raises(FileExistsError):
        create_redacted_public_snapshot(real_snapshot_dir, destination, "new-version")


def test_redacted_export_requires_a_distinct_version(tmp_path: Path, real_snapshot_dir: Path):
    with pytest.raises(ValueError, match="new snapshot version"):
        create_redacted_public_snapshot(
            real_snapshot_dir,
            tmp_path / "output",
            "ndro-mvp-v0.1.2-20260823",
        )
