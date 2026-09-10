# Methodology

## Unit of observation

The primary grain is one publication–disease association, identified by a
stable `association_id`. A single PMID can therefore contribute more than one
association when it is evaluated in relation to more than one target disease.
Counts labelled as associations must not be interpreted automatically as
counts of unique publications.

## Evidence boundary

The public snapshot uses PubMed metadata and adequate English-language
scientific abstracts. PubMed title, abstract and source metadata are retained
as source material. The interface does not generate scientific prose at
runtime and does not infer a missing explanation when the snapshot field is
blank.

## Classification stages

1. **Candidate identification** records a potential publication–disease
   association.
2. **Eligibility screening** evaluates document and language requirements.
3. **Scientific-relevance classification** distinguishes direct analytical
   relevance from background or comparative mentions.
4. **Corpus placement** assigns a final record to the core corpus, a separate
   analytical view, exclusion, or pending placement.
5. **Semantic extraction** creates structured study facts and literal evidence
   spans for eligible records.
6. **Integrity checking** reports supported PubMed correction or retraction
   signals. A clean signal means only that no supported signal was found at the
   most recent check.

## Corpus placements

- **Core analytical corpus:** the disease relationship is the primary focus
  and the association passed eligibility and relevance classification.
- **Separate analytical view:** preserved evidence outside the core analytical
  indicators; it is not treated as rejection.
- **Excluded:** the association did not meet eligibility or scientific
  relevance criteria.
- **Pending:** no final placement is available. Pending is never counted as
  excluded.

## Semantic denominators

Semantic coverage is calculated as semantically complete eligible associations
divided by all associations eligible for semantic processing. Candidate,
core-analytical and semantically complete counts are distinct denominators.

## Geographic interpretation

The current geographic view uses countries extracted from study descriptions
in PubMed metadata for completed semantic records. These countries may describe
study populations or scientific contexts. They must not be interpreted as the
countries of the authors or their institutions.

Future snapshot contracts may add **author-affiliation country** and
**responsible institution** as separate dimensions. NDRO does not combine
these concepts into one generic country field. Confirmed recruitment or study
sites are not part of the planned public scope.

## Reproducibility and versioning

Each snapshot carries a version, cutoff date, generation timestamp and data
contract version. Snapshot directories are immutable after publication.
Corrections create a new snapshot rather than silently rewriting a published
release.

## Methodological items required before the final public release

The current public snapshot contract does not contain the complete PubMed query,
retrieval dates by disease, deduplication implementation or reviewer-level
adjudication log. These must be published as release artifacts before NDRO is
described as a fully reproducible search and screening protocol.
