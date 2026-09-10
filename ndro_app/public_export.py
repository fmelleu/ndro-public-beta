"""Create a privacy-preserving public derivative of an NDRO snapshot.

The source snapshot is never edited. A new versioned directory is created,
published e-mail addresses are masked in text fields, and the checksum
manifest is rebuilt. This transformation is deliberately separate from the
canonical PostgreSQL workflow so internal provenance can be retained.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EMAIL_REDACTION_TOKEN = "[email redacted from public snapshot]"
# Published correspondence strings are not consistently restricted to ASCII
# mailbox syntax. Match a compact non-whitespace token around ``@`` while
# stopping at the punctuation that normally delimits an address in prose.
# Requiring an alphanumeric final character preserves a sentence-ending full
# stop outside the replacement token.
EMAIL_PATTERN = re.compile(
    r"[^\s,;<>()[\]{}@]+@[^\s,;<>()[\]{}@]*[A-Za-z0-9]",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class RedactionReport:
    source_snapshot_version: str
    public_snapshot_version: str
    email_occurrences_redacted: int
    files_changed: tuple[str, ...]


def redact_email_addresses(value: str) -> tuple[str, int]:
    """Return masked text and the number of address occurrences removed."""
    return EMAIL_PATTERN.subn(EMAIL_REDACTION_TOKEN, value)


def _redact_json_value(value: Any) -> tuple[Any, int]:
    if isinstance(value, str):
        return redact_email_addresses(value)
    if isinstance(value, list):
        output: list[Any] = []
        count = 0
        for item in value:
            cleaned, item_count = _redact_json_value(item)
            output.append(cleaned)
            count += item_count
        return output, count
    if isinstance(value, dict):
        output_dict: dict[str, Any] = {}
        count = 0
        for key, item in value.items():
            cleaned, item_count = _redact_json_value(item)
            output_dict[key] = cleaned
            count += item_count
        return output_dict, count
    return value, 0


def scan_snapshot_for_email_addresses(snapshot_dir: Path) -> dict[str, int]:
    """Count recognizable e-mail addresses without exposing their values."""
    findings: dict[str, int] = {}
    for path in sorted(snapshot_dir.iterdir()):
        if path.name == "SHA256SUMS.csv" or path.suffix.lower() not in {".csv", ".json"}:
            continue
        text = path.read_text(encoding="utf-8-sig")
        count = len(EMAIL_PATTERN.findall(text))
        if count:
            findings[path.name] = count
    return findings


def _rewrite_csv(path: Path, old_version: str, new_version: str) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        if not fieldnames:
            return 0
        rows = list(reader)

    redactions = 0
    for row in rows:
        for field, value in row.items():
            if value is None:
                continue
            cleaned, count = redact_email_addresses(value)
            if field == "snapshot_version" and cleaned == old_version:
                cleaned = new_version
            row[field] = cleaned
            redactions += count

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return redactions


def _rewrite_json(path: Path, old_version: str, new_version: str) -> int:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    cleaned, redactions = _redact_json_value(payload)
    if isinstance(cleaned, dict) and cleaned.get("snapshot_version") == old_version:
        cleaned["snapshot_version"] = new_version
    path.write_text(json.dumps(cleaned, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return redactions


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_checksum_manifest(snapshot_dir: Path, filenames: list[str]) -> None:
    with (snapshot_dir / "SHA256SUMS.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["file", "sha256"])
        for filename in filenames:
            writer.writerow([filename, _sha256(snapshot_dir / filename)])


def create_redacted_public_snapshot(
    source_dir: Path,
    destination_dir: Path,
    public_snapshot_version: str,
    *,
    generated_at: str | None = None,
) -> RedactionReport:
    """Create a new masked snapshot, refusing to overwrite any directory."""
    source_dir = source_dir.resolve()
    destination_dir = destination_dir.resolve()
    if source_dir == destination_dir:
        raise ValueError("Source and destination snapshot directories must be different.")
    if destination_dir.exists():
        raise FileExistsError(f"Destination already exists: {destination_dir}")
    if not public_snapshot_version.strip():
        raise ValueError("A non-empty public snapshot version is required.")

    metadata_path = source_dir / "snapshot_metadata.json"
    if not metadata_path.is_file():
        raise FileNotFoundError(f"Missing snapshot metadata: {metadata_path}")
    source_metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    source_version = str(source_metadata.get("snapshot_version", "")).strip()
    if not source_version:
        raise ValueError("Source snapshot metadata has no snapshot_version.")
    if public_snapshot_version == source_version:
        raise ValueError("The public derivative must use a new snapshot version.")

    shutil.copytree(source_dir, destination_dir)
    changed_files: list[str] = []
    total_redactions = 0
    try:
        manifest_path = destination_dir / "SHA256SUMS.csv"
        manifest_filenames: list[str] = []
        if manifest_path.is_file():
            with manifest_path.open("r", encoding="utf-8-sig", newline="") as handle:
                manifest_filenames = [row["file"] for row in csv.DictReader(handle)]

        for path in sorted(destination_dir.iterdir()):
            if path.name == "SHA256SUMS.csv":
                continue
            count = 0
            if path.suffix.lower() == ".csv":
                count = _rewrite_csv(path, source_version, public_snapshot_version)
            elif path.suffix.lower() == ".json":
                count = _rewrite_json(path, source_version, public_snapshot_version)
            if count:
                changed_files.append(path.name)
                total_redactions += count

        public_metadata_path = destination_dir / "snapshot_metadata.json"
        public_metadata = json.loads(public_metadata_path.read_text(encoding="utf-8"))
        public_metadata["snapshot_version"] = public_snapshot_version
        public_metadata["source_snapshot_version"] = source_version
        public_metadata["generated_at"] = generated_at or datetime.now(timezone.utc).isoformat()
        public_metadata["public_export_transformations"] = [
            {
                "type": "email_redaction",
                "replacement": EMAIL_REDACTION_TOKEN,
                "occurrences": total_redactions,
                "files_changed": changed_files,
            }
        ]
        public_metadata_path.write_text(
            json.dumps(public_metadata, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        if not manifest_filenames:
            manifest_filenames = sorted(
                path.name
                for path in destination_dir.iterdir()
                if path.is_file() and path.name != "SHA256SUMS.csv"
            )
        _write_checksum_manifest(destination_dir, manifest_filenames)
    except Exception:
        shutil.rmtree(destination_dir)
        raise

    return RedactionReport(
        source_snapshot_version=source_version,
        public_snapshot_version=public_snapshot_version,
        email_occurrences_redacted=total_redactions,
        files_changed=tuple(changed_files),
    )
