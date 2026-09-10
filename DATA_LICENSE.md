# NDRO data license and third-party rights notice

## 1. NDRO-authored material

To the extent that NDRO Project contributors hold the applicable rights, the
following material is offered under the **Creative Commons Attribution 4.0
International license (CC BY 4.0)**:

- NDRO-created eligibility, relevance, corpus-placement and semantic-status
  classifications;
- controlled labels, decision codes and plain-language explanations authored
  by NDRO;
- aggregate coverage and corpus metrics;
- NDRO-created structured study, intervention and outcome annotations; and
- annotation identifiers, confidence values, provenance coordinates and
  validation metadata created by NDRO.

License: https://creativecommons.org/licenses/by/4.0/

Recommended attribution:

> NDRO Project contributors. Neurodegenerative Disease Research Observatory
> public snapshot, version {snapshot_version}, cutoff {cutoff_date}, CC BY 4.0
> for NDRO-authored annotations only. Changes, if any, must be indicated.

## 2. Material not relicensed by NDRO

CC BY 4.0 does **not** apply to third-party or source-derived content merely
because it appears in an NDRO snapshot. This exclusion includes:

- article titles and abstracts;
- author names, affiliations, journal metadata, keywords and publication types;
- PubMed identifiers, links and PubMed- or publisher-supplied metadata;
- verbatim `evidence_text` spans and other quoted source passages; and
- any publisher-authored wording retained in a structured field.

Those elements remain subject to the rights of their authors, publishers or
other rights holders and to applicable National Library of Medicine terms.
NDRO grants no additional permission to reproduce or redistribute them.

The NLM notes that abstracts originating from publications may be protected by
copyright. See:
https://www.nlm.nih.gov/databases/download.html

## 3. Field-level interpretation

The license follows the **origin of the content**, not merely the CSV filename.
For example:

- NDRO classification columns in `articles.csv` may fall within section 1;
- PubMed display fields in the same file fall within section 2;
- structural annotation columns in `evidence_spans.csv` may fall within section
  1, while the verbatim `evidence_text` field falls within section 2; and
- an NDRO-authored normalized label may fall within section 1, while copied or
  closely reproduced publisher wording remains outside the NDRO license.

When uncertain, preserve PubMed/publisher attribution, link to the source
record and do not assume that CC BY 4.0 applies.

## 4. No warranty

The snapshot and NDRO-authored annotations are provided as-is, without warranty
of completeness, fitness for a particular purpose or absence of third-party
rights. Users are responsible for assessing whether their intended reuse of
third-party material is permitted.
