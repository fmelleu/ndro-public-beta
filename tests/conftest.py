import shutil
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ndro_app.config import SNAPSHOTS_ROOT  # noqa: E402


@pytest.fixture(scope="session")
def valid_snapshot_dir() -> Path:
    """Small synthetic fixture used by mutation-oriented unit tests."""
    return SNAPSHOTS_ROOT / "synthetic-ui-fixture-v0.1"


@pytest.fixture(scope="session")
def real_snapshot_dir() -> Path:
    return SNAPSHOTS_ROOT / "ndro-mvp-v0.1.2-20260823"


@pytest.fixture
def tmp_snapshot_dir(tmp_path: Path, valid_snapshot_dir: Path) -> Path:
    """A mutable copy of the bundled valid snapshot for tests that need to
    break it on purpose. The original files under snapshots/ are never
    touched."""
    dest = tmp_path / "snapshot"
    shutil.copytree(valid_snapshot_dir, dest)
    return dest


def read_csv_text(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=True, na_values=[""])
