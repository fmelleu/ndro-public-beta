# NDRO Streamlit v0.2.0 — local beta implementation report

Initial implementation: 2026-08-27  
Visual-polish and responsive-QA revision: 2026-08-31  
Community-audit integration verification: 2026-09-04

## Implemented

- preserved the accepted v0.1.1 package unchanged;
- promoted an active v0.2.0 working copy;
- added nine-page navigation and versioned Markdown documentation;
- added annual and cumulative core disease trends;
- added reported study-context country summaries with explicit limitations;
- enabled per-record prefilled audit links;
- added controlled correction and missing-article forms;
- required name, email and checksum-valid ORCID;
- added local append-only JSONL delivery and optional Formspree HTTPS delivery;
- added snapshot ZIP/metadata downloads and provisional citation guidance;
- added secret templates and git exclusions for credentials and personal data.
- added responsive styling, compact wrapping cards and automatic mobile sidebar behavior;
- simplified the Article Explorer filter hierarchy and Methods page navigation;
- clarified that current geography is study-context geography, while future
  author-affiliation country and responsible-institution dimensions remain separate;
- enabled minimal public toolbar mode and removed local workstation paths from this report.
- replaced the cramped candidate-status plot with a stable horizontal bar
  chart using direct category labels, visible status colors and value labels.
- added auditable row-level exclusion details to article cards, separating the
  exclusion layer from its recorded eligibility or relevance criterion.

## Automated verification

Command: `python -m pytest tests -q`

Result: **91 passed, 0 failed**. One upstream Altair deprecation warning was
reported by Streamlit and does not affect application behavior.

## Browser-based verification

- all nine pages rendered without a Streamlit exception at a 1440 × 900 viewport;
- no horizontal document overflow was detected on any page;
- Overview, Article Explorer, Geographic Coverage, Audit & Corrections and
  Downloads & Citation were also checked at 390 × 844;
- the sidebar remained collapsed by default on the narrow viewport;
- Overview, Geographic Coverage, Article Explorer, Methods & Data Quality and
  the prefilled audit route received direct screenshot inspection;
- the local Streamlit toolbar was reduced to public-viewer controls.
- the corrected Overview chart was rechecked at 1085 × 800 and 390 × 844;
  both chart canvases retained a 260-pixel height and neither viewport showed
  horizontal document overflow.
- both Overview chart titles were moved outside their Altair canvases after a
  live render exposed persistent clipping of the layered publication title.
- eligibility and relevance exclusion panels were opened against real snapshot
  records and displayed the expected stored criterion.

## Community-audit delivery verified

- the real Formspree endpoint is configured through git-ignored Streamlit
  secrets and delivers to `ndro.project@proton.me`;
- diagnostic and representative submissions were received with complete
  fields on 2026-09-04;
- the user confirmation message and flexible ORCID normalization were tested;
- the test submission was deleted from Formspree and Proton Mail, leaving no
  submitted personal data in the test workflow.

## Deliberately pending

- public GitHub repository and Streamlit Community Cloud deployment;
- contributor ORCIDs;
- exact PubMed query and remaining protocol artifacts;
- a release decision on whether correspondence email addresses embedded in
  literal PubMed affiliation evidence spans should be retained or redacted in
  the final public export.
