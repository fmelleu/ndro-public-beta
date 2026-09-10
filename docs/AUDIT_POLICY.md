# Community audit policy

NDRO invites researchers to report a possible classification problem or suggest
a missing PubMed article. A community submission is an audit candidate only.
It never alters the displayed snapshot or the canonical database automatically.

## Required provenance

The form requires the reporter's name, email address and ORCID. Reports about
an existing record carry the PMID, association identifier, current disease,
current classification and snapshot version automatically. A missing-article
suggestion requires a PMID or PubMed URL.

## Controlled reporting vocabulary

Problem type and suggested reason use controlled dropdowns. This reduces
reporter effort, supports consistent triage and avoids collecting unnecessary
free text.

## Review workflow

1. submission received;
2. identity and record context checked;
3. scientific issue triaged;
4. report accepted, rejected or held for clarification;
5. accepted change applied to the canonical workflow;
6. correction released in a later versioned snapshot.

## Privacy

Fernando Melleu, as the NDRO project lead, is the controller of the reporter
data. Reporter identity is collected by consent only to establish provenance,
review the report, request clarification when necessary and send one closing
message with the outcome and thanks. It is not used for marketing, profiling,
public attribution or unrelated contact.

Privacy, access, correction or deletion requests may be sent to
[ndro.project@proton.me](mailto:ndro.project@proton.me).

In the hosted beta, Formspree temporarily processes the submitted fields and
delivers them to the NDRO Proton Mail inbox. Once the audit reaches a final
decision and the closing message has been sent, NDRO deletes the identifiable
submission from both operational services. The corrected scientific record and
its normal snapshot/version history remain, but they are not linked to the
reporter. Only aggregate counts of community corrections are retained as a
community-contribution metric. Reporters must not submit sensitive personal or
health information.

The complete production notice is available in `PRIVACY_NOTICE.md`. The
Formspree-to-Proton delivery route and the case-closing deletion procedure were
verified end to end on 2026-09-04.
