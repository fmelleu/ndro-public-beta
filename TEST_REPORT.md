# Test Report

## Public beta packaging addendum (Windows, 2026-09-09)

The Streamlit source and its allowlisted public package each completed the full
automated suite with **91 passed, 0 failed**. Both runs reported only the known
upstream Altair 5.5 deprecation warning. `pyflakes` returned no findings for
`app.py`, `ndro_app`, `scripts` and `tests`.

The immutable public snapshot `ndro-mvp-v0.1.2-20260823` passed checksum,
metadata, coverage, duplicate-key and orphan-record reconciliation. Reference
metrics remain 425 candidate associations, 423 distinct publications, 151 core
associations, 15 separate-view associations, 239 exclusions, 20 pending
associations, 166 semantically complete associations and 1,380 evidence spans.

The paired canonical Power BI project references the same public snapshot. All
**135** project JSON files parsed successfully, all **8** page-order references
resolved, and all **49** public mobile visual configurations passed width,
height and per-page tab-order checks. Page 99 remains intentionally
desktop-only.

The public Streamlit release was generated from an explicit allowlist. The
builder refused overwrite, excluded secrets, caches, local audit submissions
and private snapshots, and passed its e-mail, production-endpoint, secret and
personal-workstation-path scans. A real hosted deployment and its
post-deployment acceptance test remain external actions and are not claimed by
this report.

## Disease labels, roadmap and review-protocol addendum (Windows, 2026-09-08)

Public disease controls and charts now use full disease names while retaining
stable disease codes internally. Streamlit adds **Review Protocol** and
**Planned Updates** pages; the protocol exposes the recorded PubMed query
strings, acquisition, duplicate handling, deterministic eligibility, planned
semantic workflow, canonical storage, retraction handling, snapshot publication
and community-audit loop. The Power BI project adds the synchronized **07
Planned Updates** page and uses full disease names in public fields.

Automated Streamlit result: **91 passed, 0 failed** in 6.16 seconds, with one
upstream Altair deprecation warning. Python compilation passed. All **86** JSON
files in the Power BI project parsed successfully, and all **8** page-order
entries resolved to an existing page definition. A final visual inspection in
Power BI Desktop remains required after opening the modified project.

## Overview and public-export addendum (Windows, 2026-09-03)

The Overview now presents a source-linked scientific rationale, NDRO mission
and concise usage path. The longer Introduction document uses the same scope
and sources. A separate public-export utility was added to mask published
correspondence e-mails without editing the canonical database or the bundled
immutable snapshot; it assigns a new version, records the transformation and
rebuilds the checksum manifest.

Automated result: **82 passed, 0 failed** in 4.50 seconds with the same single
upstream Altair deprecation warning. The new release tests confirm that the
current snapshot contains 28 recognizable e-mail occurrences, that all 28 are
removed from a generated derivative, that the derivative remains loadable and
that every regenerated checksum matches. `pyflakes` returned no findings.

The Overview was rendered in the in-app browser. Purpose, Mission and How to
use NDRO were all visible with working source links, the scientific copy
wrapped correctly, and the browser reported no console errors. The current
immutable pilot snapshot was not modified and no production derivative was
created.

## Public-release hardening addendum (Windows, 2026-08-31)

The automatic corrections from the public-release readiness audit were
implemented without modifying the snapshot, scientific classifications or
analytical calculations. Snapshot-derived badge text is now HTML-escaped and
covered by an injection-regression test. Runtime and development dependencies
are exactly pinned, Python 3.12 is selected for deployment, stale audit-control
and package-license documentation was corrected, and the default-snapshot
configuration comment now describes the real pilot snapshot.

The Overview candidate-landscape chart now explicitly disables unnecessary
automatic stacking. The browser continues to emit transient Vega infinite-
extent warnings while initializing embedded datasets, but both charts render
and remain interactive; no browser error or Streamlit exception was observed.

Final automated result after these changes: **76 passed, 0 failed** with the
same single upstream Altair deprecation warning. `pyflakes` returned no
findings. The exact Apache-2.0 text was verified against a local authoritative
copy. The default snapshot was not changed.

## Streamlit v0.2.0 visual-polish addendum (Windows, 2026-08-31)

The current beta completed a new local validation pass after responsive and
layout improvements. The automated suite returned **74 passed, 0 failed**;
Streamlit reported one upstream Altair deprecation warning that does not affect
rendering or calculations.

All nine pages were rendered in the in-app browser at 1440 × 900 with no
Streamlit exceptions or horizontal document overflow. Five interaction-heavy
pages were also checked at 390 × 844; the sidebar remained collapsed by
default and no horizontal overflow was detected. Direct screenshot review
covered Overview, Article Explorer, Geographic Coverage, Methods & Data
Quality and an audit form opened with a prefilled article.

The Overview candidate-landscape chart was subsequently changed to a
horizontal, directly labelled layout after the original vertical plot area
collapsed at intermediate widths. It was rechecked at 1085 × 800 and
390 × 844: both charts retained their intended 260-pixel drawing height and
the document had no horizontal overflow.

The two Overview chart titles were moved out of the Altair canvases and into
the Streamlit layout after the layered publication chart continued to clip its
canvas title. A browser render confirmed that both titles are complete and
aligned.

Excluded-record panels now expose the stored exclusion layer and row-level
criterion instead of relying on the generic snapshot explanation alone.
Browser checks covered one eligibility exclusion and one relevance exclusion;
the displayed criteria matched their source fields.

The package scan found no configured Formspree endpoint, committed Streamlit
secrets file, local audit outbox or personal workstation path in public-facing
documentation. Literal PubMed affiliation evidence in the immutable snapshot
can contain published correspondence addresses; whether those addresses remain
in the final public export requires a release-level policy decision.

The historical acceptance and construction reports below are retained for
provenance and describe their own earlier test states. They do not supersede
this addendum.

## NDRO acceptance addendum — v0.1.1 (Windows, 2026-08-23)

The original Claude report below is retained as provenance for v0.1. Nora's
acceptance pass ran the corrected v0.1.1 build on the NDRO Windows workstation
with Python 3.12.12, Streamlit 1.45.1, pandas 2.2.3, Altair 5.5.0 and pytest
8.3.4. Result: **49 passed, 0 failed** in 2.23 seconds (one upstream Altair
deprecation warning). This includes the full immutable pilot snapshot:
425 associations, 423 distinct PMIDs, 151 core, 15 separate, 239 excluded,
20 pending, 186 eligible, 166 semantically complete, 1,380 evidence spans,
3 corrected publications and 2 retractions. Snapshot loading produced no
contract warnings. Local load time was 0.0486 seconds and an all-field search
for "Alzheimer" was 0.0039 seconds on this machine.

The acceptance pass fixed three issues not covered by the original synthetic
fixture: Windows UTF-8 BOM handling for JSON, Streamlit 1.45 widget-width
compatibility, and the distinction between corrected publications (retained)
and retracted publications (excluded from analytics). A local Streamlit server
also passed the `/_stcore/health` endpoint.

---

This report lists exactly what was executed against this package, in the
build/test environment used to produce it, and what was **not** verified.
Nothing in this report is claimed without having actually been run.

## Environment actually used

- Python 3.11.15, Linux (the cloud sandbox this MVP was built in).
- `pip install streamlit>=1.32,<2 altair>=5.0,<6 pytest>=7.4,<9` resolved to:
  streamlit `1.62.0`, altair `5.5.0`, pandas `3.0.2` (already present),
  pytest `8.4.2`.
- `requirements.txt` was written to match these tested versions.
- **Not tested**: Windows. The README's Windows run steps are written from
  the standard, documented Streamlit/pip/venv behavior on Windows, but the
  app itself was only actually executed on Linux in this environment —
  there is no Windows machine available here to confirm the exact
  PowerShell steps end-to-end.

## 1. Automated test suite

Command run:

```
python -m pytest tests/ -v
```

Result: **47 passed, 0 failed**, in 4.71s (last full run). Full listing:

- `tests/test_data_contract.py` (9 tests) — contract loading and rejection:
  - `test_fixture_contract_passes` — the bundled synthetic fixture loads
    cleanly with zero warnings.
  - `test_missing_required_column_fails` — dropping `title` from
    `articles.csv` raises `SchemaValidationError` naming the file and
    column.
  - `test_missing_required_column_in_coverage_fails` — same, for
    `coverage.csv` / `semantic_coverage_percent`.
  - `test_duplicate_association_id_fails` — a duplicated `association_id`
    row in `articles.csv` raises `DuplicateKeyError`.
  - `test_unsupported_contract_version_fails` — a `contract_version` of
    `public-snapshot-v9.9` raises `ContractVersionError` naming the
    unsupported value.
  - `test_required_nonnull_field_blank_fails` — blanking
    `classification_status` on one row raises `RequiredValueError`.
  - `test_missing_snapshot_file_fails` — deleting `evidence_spans.csv`
    raises with the filename named in the message.
  - `test_metadata_count_mismatch_is_a_warning_not_a_failure` — a wrong
    `counts.article_associations` in `snapshot_metadata.json` loads
    successfully but produces a `Snapshot.warnings` entry.
  - `test_pending_corpus_status_is_not_coerced_to_excluded` — the
    Parkinson (PD) fixture row's blank `corpus_status` survives loading as
    blank, not as `excluded`.

- `tests/test_metrics.py` (15 tests) — critical metric calculations:
  - `test_headline_counts_reconcile_with_fixture_metadata` — candidate
    associations (5) and distinct publications (5) match
    `snapshot_metadata.json`'s own `counts`; core/separate/excluded/pending
    = 1/1/2/1, matching the fixture by hand-inspection (AD=core,
    ALS=separate, FTD=excluded_eligibility, HD=excluded_relevance,
    PD=pending).
  - `test_coverage_summary_reconciles_with_fixture` — eligible=3,
    complete=2, coverage=66.67%, matching `coverage.csv`'s summed columns.
  - `test_corpus_bucket_mapping` (8 parametrized cases) — every raw
    `corpus_status` value maps to the correct bucket, including blank/None/
    NaN → `pending` and an unrecognized string → `unrecognized` (never
    `excluded`).
  - `test_pending_is_never_counted_as_excluded` — a synthetic 2-row frame
    with blank `corpus_status` produces `pending_associations == 2`,
    `excluded_associations == 0`.
  - `test_integrity_flag_detection` — `no_pubmed_integrity_signal` is
    clean; any other value (including `None`) is flagged.
  - `test_core_trend_excludes_separate_excluded_pending_and_retracted` — a
    synthetic 5-row frame (one clean core, one integrity-flagged core, one
    separate, one excluded, one pending, all same year) produces a
    publication-year trend containing exactly 1 count for that year (the
    clean core row only).
  - `test_candidate_landscape_includes_every_bucket` — the explicitly
    "candidate" chart data includes all 4 present buckets and sums to the
    full row count.
  - `test_publication_year_trend_empty_input_does_not_crash` — an empty
    input frame returns an empty trend frame rather than raising.

- `tests/test_filters_and_search.py` (14 tests) — Article Explorer logic:
  - PMID search (`test_search_finds_by_pmid`), abstract-text search
    (`test_search_finds_by_abstract_text`), title search
    (`test_search_finds_by_title`), and case-insensitivity
    (`test_search_is_case_insensitive`) each confirmed against the real
    fixture rows.
  - `test_empty_search_returns_everything` — blank/None/whitespace-only
    query returns the full frame, unfiltered.
  - `test_search_with_no_match_returns_empty_not_crash` — a query with no
    matches returns an empty frame without raising.
  - `test_apply_filters_with_all_empty_does_not_restrict` — every filter
    left at its default (`None` or `[]`) leaves the frame unchanged (an
    empty multiselect is "no restriction," not "hide everything").
  - `test_apply_filters_by_disease`, `..._by_corpus_bucket_separate_only`,
    `..._pending_not_confused_with_excluded` — filters correctly isolate
    the intended subset using the fixture's known composition.
  - `test_search_then_filter_combo_can_return_empty_without_crash` —
    chaining a search and a filter to an empty result does not raise.
  - `test_pagination_basic`, `..._out_of_range_is_clamped_not_crashing`,
    `..._empty_dataframe_does_not_crash` — pagination math and edge cases.

- `tests/test_app_smoke.py` (9 tests) — actually runs the Streamlit app
  in-process via `streamlit.testing.v1.AppTest` against the bundled
  fixture (not just its underlying functions):
  - App boots on Overview with no exception.
  - Navigating to Article Explorer and to Methods & Data Quality each
    raise no exception.
  - Submitting the Article Explorer filter form with an empty search box
    does not crash.
  - Searching `90000001` (a PMID) and submitting surfaces exactly the one
    matching article ("**1** matching association(s)" and the PMID text
    both present in the rendered output).
  - Selecting a specific disease (`AD`) on the Overview page's filter does
    not crash and renders the expected per-disease semantic-coverage
    metric.
  - Across all three pages, the rendered text does not contain `/tmp/` or
    the sandbox's home directory path (a basic check against leaking local
    filesystem paths into the UI).

## 2. Manual, non-pytest verification actually performed

- **Real server boot**: `streamlit run app.py --server.headless true
  --server.port 8765` was started as a background process. `curl -s -o
  /dev/null -w "%{http_code}" http://localhost:8765/` returned `200`, and
  `http://localhost:8765/_stcore/health` returned `ok` (HTTP 200). The
  process log was checked and contained no error or traceback lines. The
  process was then stopped. This confirms the app actually starts and
  serves HTTP under a real Streamlit server process, not only under the
  `AppTest` bare-mode harness used above.
- **Static analysis**: `python -m pyflakes app.py ndro_app tests` was run
  and returned no warnings (no unused imports, no unused locals) after two
  small cleanups (an unused `typing.Optional` import and an unused form
  variable).

## 3. What was NOT verified (explicit limitations)

- **No visual/screenshot inspection.** No browser screenshot or manual
  visual review of layout, spacing, color contrast ratios, or the
  1366×768 layout claim was performed. The CSS in `app.py` (`max-width:
  1280px`, tighter top padding) was written to be usable at that
  resolution but was not measured against it.
- **No accessibility audit.** No contrast-ratio tool (e.g. axe, WAVE) or
  screen-reader pass was run. Status colors are always paired with a text
  label as a design choice, but this was not independently verified
  against WCAG contrast thresholds.
- **No deployment.** This app was not deployed to Streamlit Community
  Cloud, a container, or any server beyond the local, temporary smoke-test
  process described above. The deployment steps in README.md are standard
  documented procedure, not a verified-successful deployment log.
- **No Windows execution.** The exact PowerShell steps in README.md were
  not run on a Windows machine in this session.
- **No large-snapshot / performance testing.** The bundled fixture has 5
  article rows. Pagination, search, and chart code were written to scale
  (they operate on the full DataFrame with vectorized pandas operations
  and only render one page of cards at a time), but no load test with a
  larger synthetic dataset was performed.
- **No test for a snapshot whose `snapshot_version`/`cutoff_date` disagree
  across files** (`SnapshotConsistencyError` in `ndro_app/data_loader.py`
  is implemented but has no dedicated automated test — the bundled fixture
  is internally consistent, so this path was only exercised by manual code
  review, not a test run).
- **No security review** beyond confirming no credentials, database
  connection strings, or paid-API calls exist anywhere in the code (verified
  by reading every module, not by an automated scanner).
- **`interventions_outcomes.csv` has zero data rows in the bundled
  fixture.** Loading and schema validation of this file were exercised
  (including the empty-file case), but no test exercises what the UI does
  with actual intervention/outcome rows, because the fixture does not
  contain any and the master prompt says MVP v0.1 must not present this
  data as a causal effectiveness estimate — no UI surface for this file
  was built beyond the disclaimer text in Methods & Data Quality, which is
  a scope decision, not an untested feature.
