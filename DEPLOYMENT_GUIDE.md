# NDRO public beta deployment guide

**Application:** NDRO Streamlit v0.2.0  
**Public snapshot:** `ndro-mvp-v0.1.2-20260823`  
**Snapshot contract:** `public-snapshot-v0.1`  
**Paired visualization:** Power BI v0.2.1 canonical desktop/mobile layout

This guide covers the first public beta. The deployed Streamlit application is
read-only with respect to scientific data. Community audit submissions are sent
to the configured form processor; they never modify the public snapshot.

## 1. Build the public package

From the active Streamlit source directory, run:

```powershell
python scripts/build_public_release.py <empty-release-directory> `
  --archive <new-release-zip>
```

The builder uses an explicit allowlist, refuses to overwrite an existing
destination, excludes local secrets and audit submissions, scans for personal
workstation paths and production credentials, and creates:

- `PUBLIC_RELEASE_BUILD_REPORT.json`;
- `PUBLIC_RELEASE_FILE_MANIFEST.csv`; and
- the optional ZIP archive.

Do not deploy if the build or privacy scan reports `FAIL`.

## 2. Create the public repository

1. Create an empty public repository for the NDRO Streamlit beta.
2. Upload the contents of the generated release directory, not the development
   workspace and not its parent folder.
3. Confirm that `.streamlit/secrets.toml`, `local_audit_outbox/`, cache folders
   and private snapshots are absent.
4. Preserve the release commit identifier in the NDRO release record.

## 3. Configure Streamlit Community Cloud

1. Create a new application from the public repository.
2. Select the repository branch containing the release.
3. Set the main file path to `app.py`.
4. In the application's Secrets panel, enter the production audit settings
   using `.streamlit/secrets.example.toml` as the template.
5. Replace the placeholder with the real Formspree endpoint only inside the
   protected Secrets panel. Never commit it to the repository.
6. Deploy the application.

## 4. Post-deployment acceptance test

Verify the following before announcing the beta:

- the application loads without an exception;
- the displayed snapshot is `ndro-mvp-v0.1.2-20260823` with cutoff
  `2026-08-23`;
- headline counts are 425 candidate associations, 423 distinct publications,
  166 analytical associations and 239 exclusions;
- the Overview, Article Explorer, Disease Trends, Geographic Coverage,
  Methods, Planned Updates, Audit and About pages open correctly;
- a 390-pixel-wide mobile viewport has no document-level horizontal overflow;
- PubMed links open the expected records;
- a non-sensitive audit test reaches the NDRO mailbox with the expected fields;
- the test submission is deleted from Formspree and Proton Mail after the
  closing confirmation, leaving no reporter identity in NDRO records.

## 5. Power BI pairing

Power BI is a read-only communication product for non-scientists, funding
agencies and decision makers. It does not host the community audit workflow.
Before publishing it, confirm that its snapshot card and headline metrics match
the Streamlit deployment and the beta synchronization manifest.

## 6. Rollback

If deployment fails, restore the last accepted repository commit. Do not edit
the immutable snapshot in place. A data correction or update must generate a
new snapshot version, pass reconciliation, and then be promoted to Streamlit
and Power BI together. A layout-only correction may retain the same data
snapshot but must be recorded separately.
