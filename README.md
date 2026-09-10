# NDRO Streamlit public beta candidate v0.2.0

A local Streamlit beta candidate for the NDRO (Neurodegenerative Disease
Research Observatory). It reads local, versioned
CSV/JSON snapshot files described in
`contracts/NDRO_Public_Snapshot_Data_Contract_v0.1.md` and renders eleven pages:
**Overview**, **Article Explorer**, **Disease Trends**, **Geographic Coverage**,
**Scientific Documentation**, **Review Protocol**, **Methods & Data Quality**,
**Planned Updates**, **Audit & Corrections**, **Downloads & Citation**, and
**About**.

The snapshot remains read-only: the app does not connect to the canonical
database, scrape PubMed, alter scientific classifications or generate
scientific prose at runtime. Community reports are kept outside the snapshot.
In local mode they are appended to a git-ignored JSONL outbox; after deployment
an optional Formspree endpoint can deliver them to the NDRO audit mailbox.

The default dataset is the immutable, privacy-minimized public pilot snapshot
`snapshots/ndro-mvp-v0.1.2-20260823/`. It is a redacted derivative of the
restricted `ndro-mvp-v0.1.1-20260823` export: published correspondence e-mail
addresses are masked while the canonical source and provenance remain intact.
A five-row synthetic fixture remains bundled only for tests. The app displays
a warning whenever a selected snapshot declares `"synthetic_fixture": true`.

The 2026-08-31 local polish revision adds responsive cards, compact filters,
mobile-safe navigation and clarified geographic semantics without changing the
snapshot, scientific classifications or analytical calculations.

---

## 1. What's in this package

```
NDRO_Streamlit_MVP_v0.2.0/
├── app.py                      Streamlit entry point
├── requirements.txt             Runtime dependencies (pinned)
├── requirements-lock.txt        Complete tested runtime dependency closure
├── requirements-dev.txt         + pytest, for running tests/
├── .python-version              Exact Python build used for validation
├── runtime.txt                  Python 3.12 deployment-family selection
├── README.md                    This file
├── LICENSE                      Apache License 2.0 for application code
├── NOTICE                       NDRO software attribution and scope boundary
├── DATA_LICENSE.md              CC BY 4.0 and third-party field boundary
├── DEPLOYMENT_GUIDE.md          Public beta deployment and rollback protocol
├── ASSET_AND_LICENSE_NOTES.md
├── TEST_REPORT.md
├── IMPLEMENTATION_DECISIONS.md
├── .streamlit/config.toml       Theme + server settings
├── contracts/                   Copy of the data contract (for reference)
├── docs/                        Versioned scientific documentation
├── snapshots/
│   ├── ndro-mvp-v0.1.2-20260823/  Default redacted public pilot snapshot
│   └── synthetic-ui-fixture-v0.1/  Five-row test fixture
├── ndro_app/                    Application code (see below)
├── scripts/                     Release-preparation utilities
└── tests/                       Automated tests (pytest)
```

Inside `ndro_app/`:

- `config.py` — paths, supported contract versions, pagination defaults.
- `schema.py` — column lists transcribed from the data contract.
- `exceptions.py` — typed, user-safe error classes.
- `data_loader.py` — reads and validates a snapshot directory; the only
  module that touches disk.
- `metrics.py` — pure pandas calculations (corpus bucketing, headline
  counts, coverage, trends). No Streamlit calls, fully unit-testable.
- `filters.py` — search, filter and pagination logic for the Article
  Explorer. No Streamlit calls.
- `copy.py` — every scientific label, status explanation and fixed
  question used anywhere in the UI, in one place.
- `charts.py` — Altair chart builders.
- `cards.py` — the PubMed-like article card and plain-language panel.
- `audit.py` — validation, local append-only outbox and optional Formspree delivery.
- `views/` — all eleven public pages.

## 2. Requirements

- Python 3.12 for the public beta. The exact validated Windows build is recorded
  in `.python-version`; `runtime.txt` selects the same Python minor family for
  deployment platforms that support it.
- Exact direct package versions are pinned in `requirements.txt`. Use
  `requirements-lock.txt` when reproducing the complete validated environment.

## 3. Run it locally on Windows

On the configured NDRO workstation, double-click `Start_NDRO_Streamlit.bat`.
It uses the existing Anaconda Python installation and opens the local server.
Press `Ctrl+C` in that window to stop it.

For a clean installation on another computer, use the steps below.

Open **PowerShell** (or Command Prompt) and run, from the folder that
contains this README:

```powershell
# 1. Create and activate a virtual environment
py -3 -m venv .venv
.venv\Scripts\Activate.ps1

# If PowerShell blocks the activation script, run this once first:
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

Streamlit will print a local URL (typically `http://localhost:8501`) and
should also open it in your default browser automatically. If it does not,
open that URL manually.

To stop the app, go back to the PowerShell window and press `Ctrl+C`.

### Running the automated tests (optional, for developers)

```powershell
pip install -r requirements-dev.txt
python -m pytest tests -v
```

## 4. Pointing the app at a different snapshot

The sidebar's **Snapshot directory** selector lists every sub-directory of
`snapshots/` that contains a `snapshot_metadata.json`. To add a new
snapshot (for example, a real NDRO release replacing the synthetic
fixture):

1. Create a new folder under `snapshots/`, named after the new
   `snapshot_version` (e.g. `snapshots/ndro-2026-09-01/`).
2. Copy in `articles.csv`, `coverage.csv`, `study_facts.csv`,
   `evidence_spans.csv`, `interventions_outcomes.csv` and
   `snapshot_metadata.json` for that release.
3. Restart the app (or use the sidebar selector if it is already running)
   and choose the new directory.

If a snapshot's `snapshot_metadata.json` declares a `contract_version`
other than `public-snapshot-v0.1`, or is missing a required column, the app
will refuse to load it and show a plain-language diagnostic instead of a
stack trace — see `ndro_app/data_loader.py` and
`ndro_app/exceptions.py`.

## 5. Audit form configuration

No configuration is needed for local testing. A valid local submission is
written to `local_audit_outbox/submissions.jsonl`, which is excluded by
`.gitignore`.

For live delivery:

1. Create a Formspree form and connect its notification address to the NDRO
   Proton Mail inbox: `ndro.project@proton.me`.
2. Copy `.streamlit/secrets.example.toml` to `.streamlit/secrets.toml` locally,
   or paste equivalent values into Streamlit Community Cloud's Secrets panel.
3. Replace `REPLACE_WITH_FORM_ID` with the real Formspree form ID.
4. Never commit `.streamlit/secrets.toml`.

With `environment = "production"`, the app refuses to accept a report when no
delivery endpoint is configured; it never silently pretends that a submission
was sent.

## 6. Deployment notes

The analytical interface is stateless and snapshot-backed. The optional audit
form makes one HTTPS request to the configured form endpoint.

Use `DEPLOYMENT_GUIDE.md` for the allowlisted release-build procedure,
post-deployment acceptance test and rollback protocol. Do not deploy the
development directory directly.

- **Streamlit Community Cloud**: push this directory to a Git repository,
  then point Streamlit Community Cloud at `app.py`. `requirements.txt` is
  picked up automatically. Add the audit endpoint in the Secrets panel.
- **A private server / container**: install `requirements.txt` and run
  `streamlit run app.py --server.port <port> --server.address 0.0.0.0`
  behind your normal reverse proxy / TLS termination. `.streamlit/config.toml`
  already sets `headless = true` and disables anonymous usage stats.
- **Docker**: a minimal Dockerfile would be
  `FROM python:3.12-slim`, `COPY . /app`, `WORKDIR /app`,
  `RUN pip install -r requirements.txt`,
  `CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]`.
  (No Dockerfile is included in this package; add one if your deployment
  target requires it.)

This package has **not** been deployed to any of the above by the author of
this MVP — see `TEST_REPORT.md` for exactly what was and was not verified.

### Preparing a public snapshot without correspondence e-mails

The canonical database and the bundled pilot snapshot remain unchanged. To
create a new public derivative that masks recognizable e-mail addresses,
assigns a distinct snapshot version and rebuilds `SHA256SUMS.csv`, run:

```powershell
python scripts/prepare_public_snapshot.py `
  <restricted-snapshot-root>/ndro-mvp-v0.1.1-20260823 `
  snapshots/ndro-mvp-v0.1.2-20260823 `
  --version ndro-mvp-v0.1.2-20260823
```

The destination must not already exist and must use a version different from
the source. The utility records the source version and redaction count in the
new `snapshot_metadata.json`. To scan without writing anything, run:

```powershell
python scripts/prepare_public_snapshot.py `
  <restricted-snapshot-root>/ndro-mvp-v0.1.1-20260823 `
  --scan-only
```

Never run this transformation in place. Keep the unredacted canonical source
under restricted internal governance and publish only the newly validated
derivative.

## 7. Licensing and third-party rights

- Application source code: Apache License 2.0 (`LICENSE` and `NOTICE`).
- NDRO-authored structured annotations: CC BY 4.0 to the extent defined in
  `DATA_LICENSE.md`.
- Titles, abstracts, author/publisher metadata and verbatim source evidence are
  not relicensed by NDRO. Their original rights and applicable NLM terms remain
  in force. Every abstract panel identifies PubMed as its source and links both
  to the PubMed record and the NLM copyright information page.

## 8. Scope reminders

- Snapshot data are read-only. Audit submissions are separate candidates and
  never write back to canonical classifications.
- English-first UI copy; PubMed title/abstract text is shown verbatim.
- `no_pubmed_integrity_signal` means only that the last supported PubMed
  check found no retraction/correction signal — see the Methods & Data
  Quality page.
- Candidate, core-analytical and semantically-complete counts are
  different denominators and are always labeled separately.
