# NDRO Public Snapshot Data Contract v0.1

**Contract version:** `public-snapshot-v0.1`  
**Language:** English-first field names and product text; PubMed source text remains verbatim.  
**Encoding:** UTF-8 CSV with header row.  
**Null representation:** empty CSV field.  
**Primary grain:** one publication-disease association identified by `association_id`.

## Shared rules

- `snapshot_version` and `cutoff_date` identify the immutable release represented by every file.
- `association_id` is the stable join key across files.
- `pmid` is text, not a number.
- lists stored in a single CSV field use `; ` as the display delimiter; consumers must not use these strings as authoritative normalized relations.
- pending classification has blank `corpus_status`; it is not exclusion.
- `integrity_status = no_pubmed_integrity_signal` means only that the last PubMed integrity check found no supported retraction/correction signal.
- Streamlit and Power BI must display `snapshot_metadata.json` release and limitation information.
- Consumers must tolerate new nullable columns but must reject missing required columns or a changed `contract_version`.

## `articles.csv`

One row per association, including core, separate, excluded and pending records.

Required identity/publication fields:

`snapshot_version`, `cutoff_date`, `association_id`, `disease_code`, `pmid`, `pubmed_url`, `title`, `publication_year`, `journal`.

Public display fields:

`authors`, `abstract`, `keywords`, `publication_types`.

Classification/audit fields:

`language_eligibility_status`, `eligibility_status`, `classification_status`, `semantic_status`, `relevance_class`, `decision_code`, `corpus_status`, `final_label_source`, `classification_version`, `integrity_status`, `integrity_last_checked_at`, `plain_language_explanation`, `eligibility_reason`, `language_exclusion_reason`, `association_updated_at`.

Required non-null values per row: `snapshot_version`, `cutoff_date`, `association_id`, `disease_code`, `pmid`, `pubmed_url`, `title`, `publication_year`, `classification_status`, `semantic_status`, `integrity_status`.

## `study_facts.csv`

One row per association with a complete accepted semantic study profile. It includes:

`association_id`, `disease_code`, `corpus_status`, `pmid`, `publication_year`, `publication_form`, `population_description`, `sample_size_total`, `overall_treatment_signal`, `extraction_confidence`, `design_codes`, `objective_codes`, `context_codes`, `methods`, `models`, `countries`.

Only non-retracted core/separate analytical associations may appear.

## `evidence_spans.csv`

One row per accepted literal evidence span:

`association_id`, `disease_code`, `pmid`, `subject_type`, `subject_id`, `source_field`, `evidence_text`, `evidence_start`, `evidence_end`, `confidence`.

The `evidence_text` must be a literal substring of the stored source field after the normalization rules used by the semantic validator.

## `interventions_outcomes.csv`

One row per intervention-outcome pair. Outcomes without an intervention remain valid rows. Fields include intervention name/type/intent, dose/route/duration/comparator and outcome domain, direction, significance, summary and confidence.

This file is supporting structured data. MVP v0.1 must not present it as a causal effectiveness estimate.

## `coverage.csv`

One row per disease containing:

- `candidate_associations`: all current association records through cutoff;
- `eligible_associations`: records deterministically eligible for semantic classification, including those still pending final relevance placement;
- `semantically_complete_associations`;
- `semantic_coverage_percent` = complete / eligible;
- `core_associations`, `separate_associations`, `excluded_associations`, `pending_final_classification`;
- `last_updated_at`.

Candidate, final analytical and semantically complete denominators must never be mixed in a chart without explicit labeling.

## Versioning policy

- Backward-compatible nullable fields increment the patch version.
- Renamed/removed columns, changed meanings or changed file grains require a new major/minor contract version and consumer changes.
- A snapshot directory is immutable after publication. Corrections create a new snapshot version.

