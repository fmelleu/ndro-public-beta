"""Command-line wrapper for creating a redacted NDRO public snapshot."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ndro_app.public_export import (  # noqa: E402
    create_redacted_public_snapshot,
    scan_snapshot_for_email_addresses,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Create a new versioned NDRO snapshot with published e-mail addresses "
            "masked. The source directory is never edited."
        )
    )
    parser.add_argument("source", type=Path, help="Existing immutable snapshot directory")
    parser.add_argument(
        "destination",
        type=Path,
        nargs="?",
        help="New output directory (required unless --scan-only; must not exist)",
    )
    parser.add_argument("--version", help="New public snapshot_version (required for creation)")
    parser.add_argument(
        "--scan-only",
        action="store_true",
        help="Report counts by filename without writing an output snapshot",
    )
    args = parser.parse_args()

    if args.scan_only:
        findings = scan_snapshot_for_email_addresses(args.source)
        print(json.dumps({"files": findings, "total": sum(findings.values())}, indent=2))
        return 0

    if args.destination is None or not args.version:
        parser.error("destination and --version are required unless --scan-only is used")

    report = create_redacted_public_snapshot(args.source, args.destination, args.version)
    print(json.dumps(report.__dict__, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
