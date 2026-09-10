# Implementation Decisions

This file records every place where the authoritative inputs (the data
contract, the UI scientific requirements, and the master prompt) left a
judgment call to the implementer, what was decided, and why. Nothing here
overrides the authoritative inputs; where a decision below conflicts with
them, the authoritative inputs win and this file is wrong.

## 1. Multi-snapshot directory layout (`snapshots/<version>/...`)

The contract describes a single "snapshot directory" without specifying a
folder layout for an application that may need to hold more than one
release over time (the README-First note says a real snapshot will later
replace the synthetic one). This app introduces
`snapshots/<snapshot_version>/{articles.csv, coverage.csv, ...}` as its own
convention and offers a sidebar selector over whatever sub-directories are
present. This is additive scaffolding, not part of the data contract
itself — a real snapshot only needs to be dropped into a new sub-directory,
no code change required.

## 2. Integrity signals are displayed broadly; only retractions are automatically excluded

The contract only defines the meaning of `integrity_status =
no_pubmed_integrity_signal`. It implies other values exist (the master
prompt refers to "known retracted records") but never enumerates them.
`ndro_app/metrics.py::integrity_is_flagged` treats any value other than
`no_pubmed_integrity_signal` as a signal that must be displayed. Analytical
exclusion is narrower: `integrity_is_retracted` excludes only the canonical
`retracted` status. A `corrected` publication remains analytical unless a
separate scientific decision changes its corpus placement. The article card
therefore distinguishes clean, corrected, retracted, expression-of-concern
and unknown statuses instead of collapsing them into one warning. Tests
cover both corrected-core retention and retracted-core exclusion.

## 3. A fifth corpus bucket: "unrecognized"

`corpus_status` per the contract is blank (pending), `core`, `separate`, or
some `excluded_*` value (`excluded_eligibility`, `excluded_relevance` are
the two seen in the fixture). Rather than assuming every possible future
non-blank, non-core, non-separate value starts with `excluded` and
silently lumping anything else into "excluded", `corpus_bucket()` in
`ndro_app/metrics.py` puts any value it does not recognize into an explicit
`unrecognized` bucket, which is shown (with a count) but excluded from
every headline metric until a human reviews it. This favors "fail loud in
a visible corner of the UI" over "silently miscount" if the contract is
patched with a new status value this app build does not yet know about.
The bundled fixture never triggers this path (all five records map
cleanly to core/separate/excluded/pending).

## 4. `interventions_outcomes.csv`'s exact required-column list

The contract describes this file's fields narratively ("dose/route/
duration/comparator", "outcome domain, direction, significance, summary
and confidence") rather than as a literal column list, unlike the other
four files. `ndro_app/schema.py::INTERVENTIONS_OUTCOMES_REQUIRED_COLUMNS`
uses the exact header row shipped in `sample_snapshot/interventions_outcomes.csv`
as the concrete contract for this file. The fixture file has zero data
rows (header only); the app and its tests both handle an empty-but-valid
file without error.

## 5. Uniqueness (duplicate `association_id`) is enforced only where the contract states a one-row-per-association grain

`articles.csv` ("One row per association...") and `study_facts.csv` ("One
row per association with a complete accepted semantic study profile")
both state a one-row-per-association grain, so both are checked for
duplicate `association_id` and rejected with `DuplicateKeyError` if
violated. `evidence_spans.csv` (one row per evidence span — many spans per
association is expected) and `interventions_outcomes.csv` (one row per
intervention-outcome pair — likewise many per association) are not
uniqueness-checked, since duplication of `association_id` there is normal,
not an error.

## 6. Semantic coverage percent is recomputed, not averaged

`coverage_summary()` in `ndro_app/metrics.py` sums
`eligible_associations` and `semantically_complete_associations` across
every disease in scope, then computes `complete / eligible * 100`, rather
than averaging each disease's own `semantic_coverage_percent` column. This
avoids a well-known distortion (averaging percentages with different
denominators misrepresents overall coverage) and keeps the headline number
mathematically consistent with the two counts displayed alongside it, per
the requirement that status must always be paired with its denominators.
Per-disease percentages from `coverage.csv` are still shown verbatim in the
Methods & Data Quality coverage table.

## 7. Candidate vs. analytical vs. semantic denominators are kept in visually separate blocks

The Overview page renders three visually distinct groups: (a) "Candidate
landscape" (candidate associations, distinct publications — the full
candidate surface), (b) "Analytical corpus breakdown" (core/separate/
excluded/pending counts), and (c) a semantic-coverage metric with an
explicit "X of Y eligible" tooltip. The two Overview charts are similarly
split: a core-only trend and an explicitly-labeled "candidate landscape"
bar chart including every status. This directly implements "candidate and
analytical denominators must remain visibly distinct" and "must never be
mixed in a chart without explicit labeling."

## 8. Evidence-span heading relabeling

`evidence_spans.csv`'s `subject_type` values in the fixture
(`study_context`, `population`, `study_objective`) don't exactly match the
example heading list in the UI requirements ("disease focus; human/animal/
in vitro context; intervention; outcome; result direction"). `ndro_app/copy.py::EVIDENCE_HEADING_MAP`
maps the fixture's actual values to a friendlier heading, and includes the
example headings from the requirements text for values that might appear
in a future snapshot (`disease_focus`, `intervention`, `outcome`,
`result_direction`). Any `subject_type` not in the map falls back to a
title-cased version of the raw value — this only relabels an existing
field, it never invents new evidence or drops a span.

## 9. Community reports remain separate from the scientific snapshot

The original v0.1 preview used a disabled button because no submission path
existed. In v0.2.0, each article card links to a prefilled **Audit &
Corrections** form. Local development writes valid reports to an append-only,
git-ignored JSONL outbox. A hosted deployment sends them only when a valid
Formspree endpoint is supplied through Streamlit secrets; production mode
fails closed when that endpoint is absent. In every mode, a report is only an
audit candidate and never edits the snapshot or canonical database
automatically.

## 10. Metadata/CSV count mismatches are warnings, not load failures

The contract's hard-failure list is: unsupported `contract_version`,
missing required column, and (per this app's own interpretation, see #5)
duplicate `association_id` where the grain forbids it. A mismatch between
`snapshot_metadata.json`'s declared `counts` and what the CSVs actually
contain, or between `coverage.csv`'s summed `candidate_associations` and
`articles.csv`'s row count, is not in that list, so it does not block
loading. Instead it is collected into `Snapshot.warnings` and surfaced on
the Methods & Data Quality page. The CSVs (not the metadata JSON's summary
counts) are always the source of truth for every number shown elsewhere in
the app.

## 11. Filtering happens via an explicit "Apply" step, not live-reactive widgets

The Article Explorer's search box and filters are inside an `st.form`
rather than wired to fire a rerun on every keystroke. This bounds how often
the (potentially large, in a real snapshot) article table is re-filtered
and re-rendered, and keeps the results view from partially updating mid-
type. It also satisfies "paginated or bounded results" more robustly: the
page only ever renders `page_size` (5/10/20/50, selectable) article cards
at a time, never "thousands of full abstracts."

## 12. Streamlit 1.45 compatibility retained

Claude's original build used the newer `width="stretch"` API from Streamlit
1.62. The NDRO Windows workstation currently runs Streamlit 1.45.1, where
that keyword causes page failures. The accepted build uses
`use_container_width=True`, which works on the actual workstation and keeps
the application usable without a dependency upgrade.

## 13. Numeric parsing failures are warnings, not load failures

`_cast_numeric` in `ndro_app/data_loader.py` coerces columns like
`publication_year` and `sample_size_total` to numbers with
`pd.to_numeric(errors="coerce")`. A value that fails to parse becomes
missing and is recorded in `Snapshot.warnings`, rather than aborting the
whole snapshot load — a single malformed numeric cell is a data-quality
issue to flag, not grounds to refuse the entire release (the contract does
not list this as a rejection condition).

## 14. New nullable columns are tolerated by construction

Per "Consumers must tolerate new nullable columns but must reject missing
required columns," `_validate_columns` only checks that every column in the
required list is present — it never checks for an exact/closed column set.
A future patch version that adds an optional column will load without any
code change.
