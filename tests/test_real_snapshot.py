"""Release-level reconciliation tests for the bundled NDRO MVP snapshot."""

import json

from ndro_app.data_loader import load_snapshot
from ndro_app.metrics import coverage_summary, headline_counts


def test_real_snapshot_loads_and_reconciles(real_snapshot_dir):
    snapshot = load_snapshot(real_snapshot_dir)
    metadata = json.loads((real_snapshot_dir / "snapshot_metadata.json").read_text(encoding="utf-8-sig"))

    counts = headline_counts(snapshot.articles)
    coverage = coverage_summary(snapshot.coverage)

    assert counts["candidate_associations"] == 425
    assert counts["distinct_publications"] == 423
    assert counts["core_associations"] == 151
    assert counts["separate_associations"] == 15
    assert counts["excluded_associations"] == 239
    assert counts["pending_associations"] == 20
    assert counts["integrity_flagged_associations"] == 5
    assert counts["retracted_associations"] == 2
    assert coverage["eligible_associations"] == 186
    assert coverage["semantically_complete_associations"] == 166
    assert coverage["semantic_coverage_percent"] == 89.24731182795699
    assert len(snapshot.study_facts) == 166
    assert len(snapshot.evidence_spans) == 1380
    assert metadata["counts"]["article_associations"] == counts["candidate_associations"]


def test_real_snapshot_corrections_are_not_automatically_excluded(real_snapshot_dir):
    snapshot = load_snapshot(real_snapshot_dir)
    corrected = snapshot.articles[snapshot.articles["integrity_status"] == "corrected"]
    retracted = snapshot.articles[snapshot.articles["integrity_status"] == "retracted"]

    assert len(corrected) == 3
    assert len(retracted) == 2
