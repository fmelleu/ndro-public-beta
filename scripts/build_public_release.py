"""Build a privacy-minimized NDRO Streamlit public release from an allowlist.

The builder refuses to overwrite an existing destination. It copies only the
files declared below, scans the result for local secrets and personal paths,
and writes a SHA-256 file manifest plus a machine-readable build report.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path


RELEASE_NAME = "NDRO_Streamlit_Public_Beta_v0.2.0"
PUBLIC_SNAPSHOT = "ndro-mvp-v0.1.2-20260823"
SYNTHETIC_FIXTURE = "synthetic-ui-fixture-v0.1"

ROOT_FILES = (
    ".gitignore",
    ".python-version",
    "app.py",
    "ASSET_AND_LICENSE_NOTES.md",
    "DATA_LICENSE.md",
    "DEPLOYMENT_GUIDE.md",
    "IMPLEMENTATION_DECISIONS.md",
    "LICENSE",
    "LOCAL_BETA_REPORT.md",
    "NOTICE",
    "PUBLIC_RELEASE_READINESS_AUDIT.md",
    "README.md",
    "requirements-dev.txt",
    "requirements-lock.txt",
    "requirements.txt",
    "runtime.txt",
    "TEST_REPORT.md",
)

EXPLICIT_FILES = (
    ".streamlit/config.toml",
    ".streamlit/secrets.example.toml",
)

TREE_RULES = {
    "contracts": {".md"},
    "docs": {".md"},
    "ndro_app": {".py"},
    "scripts": {".py"},
    "tests": {".py"},
}

SNAPSHOT_FILES = (
    "articles.csv",
    "coverage.csv",
    "evidence_spans.csv",
    "interventions_outcomes.csv",
    "SHA256SUMS.csv",
    "snapshot_metadata.json",
    "study_facts.csv",
    "validation_report.json",
)

FIXTURE_FILES = (
    "articles.csv",
    "coverage.csv",
    "evidence_spans.csv",
    "interventions_outcomes.csv",
    "snapshot_metadata.json",
    "study_facts.csv",
)

PROHIBITED_PARTS = {
    ".git",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "local_audit_outbox",
}
PROHIBITED_FILES = {"secrets.toml"}
TEXT_SUFFIXES = {".bat", ".csv", ".json", ".md", ".py", ".toml", ".txt"}
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
FORMSPREE_RE = re.compile(r"https://formspree\.io/f/([A-Za-z0-9_-]+)")
LOCAL_PATH_RE = re.compile(
    r"(?i)(?:[A-Z]:[\\/]Users[\\/](?!USERNAME\b|<user>\b)[^\\/\s]+|"
    r"/(?:Users|home)/(?!USERNAME\b|<user>\b)[^/\s]+)"
)
SECRET_PATTERNS = {
    "OpenAI-style secret": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "GitHub-style token": re.compile(r"\bgh[oprsu]_[A-Za-z0-9]{20,}\b"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_allowlisted(source: Path) -> list[Path]:
    files: set[Path] = set()
    files.update(source / name for name in ROOT_FILES)
    files.update(source / name for name in EXPLICIT_FILES)

    for directory, suffixes in TREE_RULES.items():
        tree_root = source / directory
        files.update(path for path in tree_root.rglob("*") if path.is_file() and path.suffix in suffixes)

    snapshot_root = source / "snapshots" / PUBLIC_SNAPSHOT
    files.update(snapshot_root / name for name in SNAPSHOT_FILES)
    fixture_root = source / "snapshots" / SYNTHETIC_FIXTURE
    files.update(fixture_root / name for name in FIXTURE_FILES)

    missing = [path.relative_to(source).as_posix() for path in files if not path.is_file()]
    if missing:
        raise RuntimeError("Allowlisted source files are missing: " + ", ".join(sorted(missing)))
    return sorted(files, key=lambda path: path.relative_to(source).as_posix().lower())


def scan_release(root: Path) -> dict:
    errors: list[str] = []
    emails: set[str] = set()
    scanned_files = 0

    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root)
        lowered_parts = {part.lower() for part in relative.parts}
        if lowered_parts & PROHIBITED_PARTS:
            errors.append(f"Prohibited path: {relative.as_posix()}")
        if path.name.lower() in PROHIBITED_FILES or path.suffix.lower() == ".pyc":
            errors.append(f"Prohibited file: {relative.as_posix()}")
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue

        scanned_files += 1
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        if LOCAL_PATH_RE.search(text):
            errors.append(f"Personal workstation path: {relative.as_posix()}")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{label}: {relative.as_posix()}")
        for endpoint_id in FORMSPREE_RE.findall(text):
            if endpoint_id not in {"REPLACE_WITH_FORM_ID", "example"}:
                errors.append(f"Production Formspree endpoint: {relative.as_posix()}")
        emails.update(match.group(0).lower() for match in EMAIL_RE.finditer(text))

    unexpected_emails = sorted(
        email
        for email in emails
        if email != "ndro.project@proton.me" and not email.endswith("@example.org")
    )
    if unexpected_emails:
        errors.append("Unexpected e-mail address(es): " + ", ".join(unexpected_emails))

    return {
        "passed": not errors,
        "scanned_text_files": scanned_files,
        "recognized_email_addresses": sorted(emails),
        "unexpected_email_addresses": unexpected_emails,
        "errors": errors,
    }


def write_manifest(root: Path) -> tuple[Path, int]:
    manifest = root / "PUBLIC_RELEASE_FILE_MANIFEST.csv"
    files = sorted(path for path in root.rglob("*") if path.is_file() and path != manifest)
    with manifest.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("file", "bytes", "sha256"))
        writer.writeheader()
        for path in files:
            writer.writerow(
                {
                    "file": path.relative_to(root).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
    return manifest, len(files)


def build(source: Path, destination: Path, archive: Path | None) -> dict:
    if destination.exists():
        raise FileExistsError(f"Destination already exists; refusing overwrite: {destination}")
    if archive is not None and archive.exists():
        raise FileExistsError(f"Archive already exists; refusing overwrite: {archive}")

    allowlisted = iter_allowlisted(source)
    destination.mkdir(parents=True)
    for source_file in allowlisted:
        relative = source_file.relative_to(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, target)

    scan = scan_release(destination)
    report = {
        "release_name": RELEASE_NAME,
        "application_version": "v0.2.0",
        "public_snapshot": PUBLIC_SNAPSHOT,
        "snapshot_contract": "public-snapshot-v0.1",
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "allowlisted_source_files": len(allowlisted),
        "privacy_and_secret_scan": scan,
    }
    report["manifest"] = {"file": "PUBLIC_RELEASE_FILE_MANIFEST.csv"}
    report_path = destination / "PUBLIC_RELEASE_BUILD_REPORT.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _, manifest_entries = write_manifest(destination)

    if not scan["passed"]:
        raise RuntimeError("Release scan failed: " + "; ".join(scan["errors"]))

    archive_created = None
    if archive is not None:
        archive.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zip_handle:
            for path in sorted(item for item in destination.rglob("*") if item.is_file()):
                zip_handle.write(path, arcname=f"{RELEASE_NAME}/{path.relative_to(destination).as_posix()}")
        archive_created = str(archive)

    return {
        "destination": str(destination),
        "archive": archive_created,
        "files": manifest_entries + 1,
        "scan": scan,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    try:
        result = build(args.source.resolve(), args.destination.resolve(), args.archive.resolve() if args.archive else None)
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print(f"Release: {RELEASE_NAME}")
    print(f"Files: {result['files']}")
    print("Privacy/secret scan: PASS")
    print(f"Directory: {result['destination']}")
    if result["archive"]:
        print(f"Archive: {result['archive']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
