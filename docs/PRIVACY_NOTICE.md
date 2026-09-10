# Community audit privacy notice

**Status:** approved for the NDRO public beta. The controller, public contact,
consent basis, processing route and event-based deletion procedure were
confirmed in an end-to-end test on 2026-09-04.

## What the audit form collects

For classification reports, NDRO collects the reporter's name, e-mail address
and ORCID together with the selected problem type, suggested reason and the
prefilled publication context (such as PMID, disease, current classification
and snapshot version). A missing-article suggestion also includes the supplied
PMID or PubMed URL.

Do not submit confidential information, health information or personal data
about another person. Free text is intentionally minimized through controlled
dropdowns.

## Why these data are collected

The information is used only to authenticate the provenance of a community
report, assess the alleged scientific or classification issue, contact the
reporter if clarification is necessary, document the review decision and
protect the audit channel against abuse. A submission is an audit candidate;
it never changes the canonical database or a published snapshot automatically.

## Processing route

In the planned hosted beta, the form will transmit the submitted fields over
HTTPS to Formspree. Formspree stores submissions in the form owner's account
and sends a notification to the designated NDRO Proton Mail inbox. This means
the submitted personal data may be processed by both Formspree and Proton under
their respective terms and privacy policies.

In local development mode, test submissions are written to a git-ignored JSONL
outbox on the developer workstation. Test records must use non-sensitive data
and must never be included in a release package.

## Consent and permitted use

The processing is based on the reporter's explicit consent. NDRO uses the
identifying fields only to review the report, request clarification when
necessary, and send one closing message communicating the outcome and thanking
the reporter. They are not used for marketing, profiling, public attribution,
mailing lists, or any purpose unrelated to the submitted audit report.

## Access and publication

Access should be limited to the NDRO reviewers responsible for audit triage.
Reporter names, e-mail addresses and ORCID identifiers must not be included in
public snapshots, public issue trackers or aggregate reports. The corrected
scientific record and its normal snapshot/version history may remain public,
but they must not identify or be linked to the reporter.

## Deletion after the audit decision

Identifiable reporter information is retained only while the audit is open.
After NDRO reaches a final decision—whether the report is accepted or not—and
sends the single closing message, the identifiable submission is deleted from
the Formspree account, the Proton Mail inbox and any operational working copy.
There is no additional fixed retention period.

NDRO retains only:

- the scientific record as corrected, when a correction is accepted;
- the ordinary non-personal snapshot and version history; and
- aggregate counts of corrections contributed by the community.

No retained metric or version record identifies the reporter.

## Reporter rights and contact

Reporters may request access, correction or deletion, subject to applicable law
and legitimate record-keeping exceptions, by writing to the public NDRO privacy
contact.

- **Data controller:** Fernando Melleu, NDRO project lead
- **Public privacy/audit contact:** [ndro.project@proton.me](mailto:ndro.project@proton.me)
- **Applicable lawful basis:** explicit consent
- **Retention rule:** until final audit decision and one closing message; then deletion
- **Form processor:** Formspree
- **Destination mailbox provider:** Proton Mail

## Operational verification

The Formspree endpoint is configured outside source control, the NDRO Proton
Mail destination is confirmed, and the end-to-end workflow was tested on
2026-09-04. NDRO verified submission, notification delivery, field completeness
and deletion from both Formspree and Proton Mail. The same deletion procedure
must be followed after every closed audit case.

Reference material: [LGPD principles published by the Brazilian Ministry of
Health](https://www.gov.br/saude/pt-br/acesso-a-informacao/lgpd/principios),
[ANPD data-subject rights](https://www.gov.br/anpd/pt-br/assuntos/titular-de-dados-1/direito-dos-titulares),
[Formspree form handling documentation](https://help.formspree.io/articles/building-your-form/building-an-html-form),
and [Proton Mail privacy information](https://proton.me/mail/privacy-policy).

This notice is a transparency and implementation document, not legal advice.
