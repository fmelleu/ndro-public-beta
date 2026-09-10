# Public snapshot data dictionary

The authoritative field-level specification is the bundled
`NDRO_Public_Snapshot_Data_Contract_v0.1.md`.

## Files

- **articles.csv:** one row per publication–disease association, including
  publication metadata, classification, audit and integrity fields.
- **coverage.csv:** disease-level candidate, analytical and semantic counts.
- **study_facts.csv:** one completed accepted semantic study profile per
  association.
- **evidence_spans.csv:** literal source spans supporting structured semantic
  fields.
- **interventions_outcomes.csv:** descriptive abstract-level intervention and
  outcome pairs; these are not causal effectiveness estimates.
- **snapshot_metadata.json:** release identity, source, status, counts and
  scientific limitations.
- **SHA256SUMS.csv:** checksums used to verify file integrity where supplied.

## Important identifiers

- `association_id` is the stable cross-file join key.
- `pmid` is text, not a numerical measure.
- `snapshot_version` and `cutoff_date` identify an immutable release.
- `disease_code` identifies the target disease evaluated for an association.

## Null and list representation

An empty CSV field represents null. Semicolon-delimited display fields are not
authoritative normalized relations. A blank `corpus_status` means pending final
classification, not exclusion.

## Geographic dimensions

In the current contract, `study_facts.countries` contains semicolon-delimited
study-context country values extracted for completed semantic records. The
field is not an author-affiliation field.

Planned future fields for author-affiliation country and responsible
institution must be represented separately. A generic merged `Country` field
and a study-site country field are outside the approved scope.
