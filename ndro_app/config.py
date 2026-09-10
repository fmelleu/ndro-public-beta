"""Static configuration for the NDRO MVP.

Keeping these values in one module makes it easy to point the app at a new
snapshot directory (e.g. when a real NDRO snapshot replaces the synthetic
fixture) without touching application logic.
"""

from pathlib import Path

# Root directory that contains one sub-directory per snapshot version, e.g.
# snapshots/synthetic-ui-fixture-v0.1/{articles.csv, coverage.csv, ...}
APP_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOTS_ROOT = APP_ROOT / "snapshots"
DOCS_ROOT = APP_ROOT / "docs"
AUDIT_OUTBOX_PATH = APP_ROOT / "local_audit_outbox" / "submissions.jsonl"

APP_VERSION = "0.2.0"

# The default snapshot directory shown on startup. This points at the immutable
# real pilot snapshot. Future releases can be added under SNAPSHOTS_ROOT and
# selected here or through the sidebar without changing application logic.
DEFAULT_SNAPSHOT_DIR_NAME = "ndro-mvp-v0.1.2-20260823"

# Contract versions this build of the app knows how to read. A snapshot
# whose snapshot_metadata.json declares any other contract_version is
# rejected with a friendly diagnostic rather than guessed at.
SUPPORTED_CONTRACT_VERSIONS = {"public-snapshot-v0.1"}

# Pagination default for the Article Explorer.
DEFAULT_PAGE_SIZE = 10
PAGE_SIZE_OPTIONS = (5, 10, 20, 50)

# The exact string the data contract uses for a clean integrity check.
# Anything else is displayed as a reported signal. Only the canonical
# ``retracted`` value is automatically excluded from analytics.
INTEGRITY_CLEAN_STATUS = "no_pubmed_integrity_signal"
