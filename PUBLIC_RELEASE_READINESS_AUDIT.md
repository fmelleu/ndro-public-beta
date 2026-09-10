# NDRO Streamlit v0.2.0 — Public release readiness audit

**Audit date:** 2026-08-31; updated 2026-09-09  
**Scope:** `NDRO_Streamlit_MVP_v0.2.0` application, documentation, public snapshot, runtime configuration and release hygiene  
**Default snapshot:** `ndro-mvp-v0.1.2-20260823`  
**Assessment:** **GO for public-beta packaging and deployment**

The application is technically healthy and the immutable snapshot is internally
consistent. Public deployment should wait until the release gates below are
closed. None of the gates requires a redesign of the dashboard or a change to
the scientific counts.

### Automatic remediation completed on 2026-08-31

The corrections that did not require a policy choice or external credential
were completed after the initial audit:

- corrected third-party license and community-audit documentation;
- added Apache-2.0 software licensing, a NOTICE file and a field-scoped CC BY
  4.0 data notice;
- updated the default-snapshot configuration note;
- HTML-escaped snapshot-derived badge text and added a regression test;
- pinned the tested Python and dependency versions;
- disabled unnecessary automatic stacking in the candidate-landscape chart;
- re-ran automated, static and browser checks successfully.

All four public-release gates are closed. The default snapshot is now a
validated, privacy-minimized public derivative; its restricted source remains
unchanged.

## 1. Checks that passed

| Area | Result | Evidence |
|---|---:|---|
| Automated test suite | Pass | 91 tests passed; one dependency deprecation warning |
| Static Python check | Pass | `pyflakes` returned no findings |
| Browser smoke test | Pass | Overview and Disease Trends loaded locally without a Streamlit exception |
| Snapshot validation | Pass | `validation_report.json` reports `passed`; no missing required files/columns, duplicates, orphan records or invalid layers |
| Snapshot checksums | Pass | All seven entries in `SHA256SUMS.csv` match their files |
| Secret scan | Pass | No credentials, API keys, private keys or production Formspree endpoint found |
| Local-path scan | Pass | No personal workstation paths found in application or documentation |
| Audit-submission storage | Pass | No `local_audit_outbox/` or submitted form data present in the package |
| PubMed links | Pass | Snapshot article URLs follow the expected PMID URL pattern |
| Streamlit security configuration | Pass | XSRF protection and CORS are enabled; usage statistics are disabled |

## 2. Public-release gates

Gates A, B, C and D are closed.

### Gate A — licenses — resolved

- Application source code is licensed under Apache-2.0 (`LICENSE` and
  `NOTICE`).
- NDRO-authored structured annotations are offered under CC BY 4.0 to the
  extent defined in `DATA_LICENSE.md`.
- PubMed- and publisher-derived titles, abstracts, metadata and verbatim source
  text are explicitly excluded from the NDRO data license.
- Every abstract panel identifies PubMed as its source, links to the source
  record and links to the NLM copyright information page.

### Gate B — published correspondence e-mails — resolved

The restricted source snapshot contains **28 e-mail occurrences in 27 evidence
rows**, covering **25 publication–disease associations**. Although those
addresses are already available in the original publications, NDRO does not
need to redistribute them to provide its public analytical service. The release
therefore applies preventive data minimization.

`ndro-mvp-v0.1.2-20260823` was generated as a distinct immutable derivative of
`ndro-mvp-v0.1.1-20260823`. All 28 occurrences were replaced in
`evidence_spans.csv`; the source snapshot and canonical database were not
modified. The transformation, source version, replacement token, affected file
and occurrence count are recorded in `snapshot_metadata.json`.

Post-generation validation found zero recognizable e-mail addresses in the
public derivative. All seven manifest checksums match, and the complete
application test suite passes (91 tests; one upstream Altair deprecation
warning).

### Gate C — community-audit privacy notice — resolved

The form collects a reporter's name, e-mail address and ORCID. The present
policy says that identity is not published, but a public form also needs a
clear operational notice covering:

- who controls the submitted data and how to contact NDRO;
- the hosted form processor and destination mailbox;
- the purpose of collection;
- retention/deletion policy and access controls; and
- a reminder not to submit confidential or health information.

Local preview submissions are written as plain JSONL in a git-ignored folder.
That is acceptable for development, but the folder must remain excluded from
every release artifact and access to it must remain restricted.

The final notice is available in `docs/PRIVACY_NOTICE.md`. Fernando Melleu is
identified as controller,
explicit consent is the selected basis, and identifiable data will be deleted
after the final audit decision and one closing message. Only the corrected
scientific record, its non-personal version history and aggregate community-
correction counts remain. The public audit/privacy contact is
`ndro.project@proton.me`. Delivery, field completeness and deletion from both
Formspree and Proton Mail were verified on 2026-09-04.

### Gate D — production audit delivery — resolved

The production Formspree endpoint is configured through the git-ignored local
Streamlit secrets file and routes notifications to the designated Proton Mail
inbox. A diagnostic submission and a representative end-to-end audit were
accepted on 2026-09-04; receipt, field completeness, the user confirmation and
the deletion procedure were verified. No submitted personal data remains from
the test. The application refuses to present the hosted submission path as
working when the endpoint is absent.

## 3. Automatically corrected findings

### Documentation drift — resolved

- `ASSET_AND_LICENSE_NOTES.md` now records BSD-3-Clause for pandas and describes
  the current local/Formspree audit paths.
- `IMPLEMENTATION_DECISIONS.md`, section 9, now distinguishes the historical
  disabled preview from the v0.2.0 form.
- `ndro_app/config.py` now describes the configured real pilot snapshot.

### Escape snapshot-derived badge text — resolved

`ndro_app/cards.py` now escapes badge text before inserting it into HTML. A
regression test verifies that an HTML-like keyword is displayed as text rather
than interpreted as markup.

### Freeze the tested environment — resolved

The public beta now publishes exact pins for the tested environment:

- Streamlit 1.45.1
- pandas 2.2.3
- Altair 5.5.0
- pytest 8.3.4 and pyflakes 3.2.0 for development validation
- Python 3.12.12 in `.python-version`, with the Python 3.12 deployment family
  selected in `runtime.txt`

### Build a clean release artifact — resolved offline

Runtime/test caches are covered by `.gitignore` and are removed after local
validation. A manual ZIP or copied release must continue to exclude
`__pycache__/`, `.pytest_cache/`, `*.pyc`, `.streamlit/secrets.toml` and
`local_audit_outbox/`.

On 2026-09-09, `scripts/build_public_release.py` generated the public beta from
an explicit allowlist and created a SHA-256 file manifest plus a machine-readable
build report. The clean package passed the full 91-test suite, static analysis,
snapshot reconciliation and privacy/secret scans. It has not yet been uploaded
to a public repository or deployed.

## 4. Non-blocking technical observations

- The test suite emits one Altair 5.5 deprecation warning from Streamlit's
  Vega chart integration. It does not currently break rendering.
- The browser console reports transient Vega warnings about infinite extents
  while embedded count datasets initialize. Unnecessary chart stacking was
  disabled, but the upstream initialization warnings remain. The inspected
  charts remain visible and usable, and no browser error or Streamlit exception
  was observed. Recheck after dependency upgrades.
- The production form should use the processor's abuse controls or equivalent
  rate limiting. This is operational hardening rather than a current data error.

## 5. Reproducibility items for the scientific release

`docs/METHODOLOGY.md` already identifies the remaining protocol artifacts:

- complete PubMed search strings;
- retrieval dates by disease;
- deduplication implementation; and
- reviewer-level adjudication log.

Their absence does not prevent a transparently labelled exploratory beta, but
NDRO should not be described as a **fully reproducible search and screening
protocol** until these artifacts are published.

## 6. Recommended release sequence

1. Upload only the generated allowlisted release directory to the public
   repository.
2. Configure the protected Streamlit Cloud audit secret and deploy.
3. Perform the post-deployment desktop, mobile and non-sensitive audit test in
   `DEPLOYMENT_GUIDE.md`.
4. Publish the paired read-only Power BI artifact from the same snapshot and
   record both public release identifiers.

## 7. Final decision

The **application and snapshot are sound enough to proceed toward publication**.
All public-release gates are closed. The remaining work is clean packaging,
cross-product reconciliation and deployment rather than analytical repair.
