# NDRO Review Protocol v0.1

**Status:** public-beta protocol candidate  
**Unit of review:** publication–disease association  
**Primary source:** public PubMed records  
**Evidence boundary:** title, abstract, structured PubMed metadata and affiliations; systematic full-text retrieval is outside the current scope

## 1. Purpose

The Neurodegenerative Disease Research Observatory (NDRO) maintains a living, versioned and auditable evidence corpus. The protocol is systematic-review-like: searches are reproducible, screening rules are explicit, exclusions retain reasons, and each public release has a fixed version and cutoff. Unlike a conventional review with one final publication date, NDRO is designed for incremental updates.

The central unit is not simply an article. It is the relationship between one PubMed publication and one target disease. The same PMID may therefore have separate, legitimate associations with more than one disease.

## 2. Current PubMed candidate searches

Each run records the exact query, PubMed date field, date window, execution time and retrieved identifiers in a run manifest.

| Disease | Candidate query |
|---|---|
| Alzheimer's disease | `"Alzheimer Disease"[MeSH Terms] OR Alzheimer*[Title/Abstract]` |
| Amyotrophic lateral sclerosis | `"Amyotrophic Lateral Sclerosis"[MeSH Terms] OR "amyotrophic lateral sclerosis"[Title/Abstract]` |
| Frontotemporal dementia | `"Frontotemporal Dementia"[MeSH Terms] OR "Frontotemporal Lobar Degeneration"[MeSH Terms] OR frontotemporal*[Title/Abstract]` |
| Huntington's disease | `"Huntington Disease"[MeSH Terms] OR Huntington*[Title/Abstract]` |
| Parkinson's disease | `"Parkinson Disease"[MeSH Terms] OR Parkinson*[Title/Abstract]` |

These expressions define the candidate landscape. A search match is not an inclusion decision. MeSH terms recover indexed records; Title/Abstract expressions recover explicit free-text mentions. Date restrictions are added per update run rather than silently embedded in these base expressions.

## 3. Acquisition and raw preservation

1. PubMed ESearch retrieves candidate PMIDs for each disease and update window.
2. A result set above 10,000 records is recursively partitioned by publication date so the retrieval frame is not restricted to the first 10,000 identifiers.
3. PubMed EFetch retrieves complete XML for the selected identifiers.
4. Raw responses and the query manifest are preserved before flattening or classification.
5. Both `PubmedArticle` and `PubmedBookArticle` structures are supported. A batch fails closed if requested PMIDs are missing, unexpected or parsed more than once.

## 4. Normalization and duplicate handling

The XML parser extracts source identifiers, dates, title, abstract variants, publication types, keywords, MeSH headings, affiliations, grant fields and PubMed integrity relations. Source hashes support idempotent updates and provenance checks.

A PMID is stored once as a publication. Each PMID–disease pair is stored once as a publication–disease association. Repeated retrieval of the same PMID for the same disease is reconciled deterministically. A PMID matching two diseases remains associated with both; cross-disease multiplicity is scientific context, not an accidental duplicate. Raw source records are not deleted during this process.

## 5. Deterministic eligibility screen

Eligibility is evaluated from PubMed XML and structured metadata before semantic relevance screening.

| Rule | Decision |
|---|---|
| `E_ABS_01` | Exclude when a PubMed abstract is missing. |
| `E_ABS_02` | Exclude when the available abstract is explicitly truncated. |
| `E_LANG_01` | Exclude when no adequate English scientific abstract is available. An English plain-language summary alone is insufficient. |
| `E_DESIGN_01` | Exclude when the publication is not original empirical research. |
| `I1` | Pass to relevance screening when original empirical research has an adequate English scientific abstract. |

Publication-form exclusions include reviews, systematic reviews, meta-analyses, case reports or case series, editorials, letters, comments and protocols without original results. A language-detector disagreement is a data-quality flag and cannot silently override authoritative PubMed element provenance.

## 6. Relevance classification and analytical placement

Eligible records are classified according to the role of the target disease:

- primary or co-primary focus → **core analytical corpus**;
- shared mechanism, secondary disease context or defined comparative context → **separate analytical view**;
- background mention, comparison-only mention or no relevant relationship → **relevance exclusion**;
- uncertain → **human adjudication** before final placement.

Eligibility and relevance exclusions are different decisions and remain separately countable. Pending records have no final corpus placement and are never counted as exclusions.

## 7. Semantic layer

The current public snapshot contains pilot semantic classifications. The full production semantic worker is planned but is not yet operating across the complete candidate corpus.

The planned workflow first performs a short relevance screen on deterministically eligible records. Only final core and separate records proceed to deep extraction of study design, population or experimental model, biological mechanisms, interventions and outcomes. Every accepted assertion must retain literal evidence from the title, abstract or affiliation, together with confidence, contract version, model or reviewer provenance and validation status. Invalid or incomplete batches write nothing to the canonical database.

## 8. Retractions, corrections and record preservation

PubMed relationships for retractions, expressions of concern, corrections, errata, updates and republications are stored and checked. A confirmed retraction is excluded from analytical indicators by default, but NDRO does not erase the publication. Its source record, warning, classification and audit history remain inspectable. Corrections remain visible unless a separate scientific review changes their analytical placement.

## 9. Canonical storage and revisions

PostgreSQL is the canonical source of truth. Raw source observations, canonical publication metadata, semantic assertions, analytical views and audit events occupy separate schemas. Classification history is immutable: an accepted change creates a revision linked to the previous decision rather than silently replacing it.

## 10. Public release and audit

A release freezes its version, cutoff date, status, counts and semantic-coverage denominators. The public CSV/JSON derivative is privacy-minimized, validated against the public data contract and accompanied by SHA-256 checksums. Streamlit and the read-only Power BI report must use the same immutable snapshot.

Streamlit community reports enter a separate audit workflow. They do not change the displayed snapshot or canonical data automatically. A curator reviews the evidence; an accepted correction is recorded as a revision and becomes public only in a later versioned release.

## 11. Current limitations

- The complete production-scale semantic layer is not yet deployed.
- The current geography view is derived from reported study-context text in completed pilot semantic records; author-country and responsible-institution country are planned as distinct future fields.
- Systematic full-text retrieval, causal inference, clinical recommendations and definitive author or institution disambiguation are outside the current scope.
- Expansion to additional diseases requires a separately documented and validated search protocol. Multiple sclerosis is the final currently planned expansion and will receive an explicit scientific-scope note.

## 12. Source documentation

- [NCBI PubMed data documentation](https://www.ncbi.nlm.nih.gov/books/NBK3828/)
- [NLM PubMed `Abstract` element](https://dtd.nlm.nih.gov/ncbi/pubmed/doc/out/250101/el-Abstract.html)
- [NLM PubMed `OtherAbstract` element](https://dtd.nlm.nih.gov/ncbi/pubmed/doc/out/250101/el-OtherAbstract.html)
