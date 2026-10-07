# Changelog

## 5.6.269 (2026-10-07)

### Fixed
- The signed-in user badge no longer overlaps the version label. It is in the sidebar footer, Sign out is on its own line, and the role shows only when it differs from the username.

## 5.6.268 (2026-10-06)

### Added
- **More Active IQ data.** How long each open risk has been open and the versions that fix it (Service History), Active IQ's own risk counts by severity and impact area (`risksCount`), support case counts and trend (`caseSummary`, Support Cases tab), forecast power, carbon and heat, and used capacity split into NAS, SAN and snapshots (platform sections of the reports).
- **Second batch of Active IQ data.** Aggregate RAID and storage types and offline volumes, volume counts and capacity by workload (`workloadSummary`), the StorageGRID capacity forecast (`StorageGridCapacityExceededForecast`), ONTAP feature usage by customer (`quarterlyOntapFeatureUsageStats`; Service History), and each support case's resolution, linked bugs and replacement parts. The case resolution was already shown but had never been requested.
- **Context in the documents.** The QBR Pack and MSP Service Report carry the last six months of service outcomes (availability, unplanned downtime, risks found and resolved, ARP coverage) and the support case trend; the QBR, MSP report and Risk & Remediation Brief show how long serious risks have been open and which aggregates will fill within 12 months; the Sustainability Report adds forecast power and carbon; the Sales Proposals add the customer's most and least used ONTAP features.

### Changed
- The **Download All** button and the explanation of the deliverables are in the Customer Deliverables bar, which shows on every deliverables tab, instead of in a box on the Risk & Remediation tab only.
- **Word documents.** Choosing Word for the Technical Risks, Security Advisories, Support Cases, OS Upgrade and TAM Recommendations downloads now gives the purpose-built Word report (it was only reached from a separate Word button; the main button produced a conversion of the text report). Technical Risks lists systems with the same findings once (42k to 37k characters), Security Advisories writes each mitigation once for the advisories that share it (47k to 18k), and HTML and line-break debris in Active IQ's text no longer shows in the Word reports.
  - The "How to read this document" note is two sentences and appears only in documents that contain general guidance.
- **Documents trimmed and de-duplicated** (checked on a 44-system customer; sizes before and after): the Customer Success Plan 56k to 30k characters, the Security Posture Brief 63k to 26k, the MSP Service Report 34k to 21k, the Handover Brief 40k to 28k, the QBR Pack 27k to 18k, Solution Proposals 18k to 9k, Problem Statements 22k to 11k; for a 185-system customer the change tickets fall from 3.3 MB to 0.8 MB and the implementation plans from 4.9 MB to 1.0 MB.
  - The configuration and best-practice findings list appears in full once (Risk & Remediation Brief); other documents carry a five-line summary that points to it.
  - The vendor knowledge-base reference lists stay in the change tickets, implementation plans, Security Posture Brief and Risk & Remediation Brief only.
  - The CVE matrix groups CVEs that share a fix; the Success Plan lists the eight most severe advisories and points to the Security Posture Brief for the rest; the cross-customer CVE exposure no longer appears in the customer-facing Security Posture Brief.
  - Change tickets and implementation plans for systems with identical changes are merged into one entry that names the systems.
  - Lines that repeat for many systems ("AutoSupport not reporting") become one line listing them; the ranking of systems by issue severity leaves out systems with nothing open; the MSP report no longer repeats the switch inventory and platform insights that the Handover Brief carries; the empty "transition notes" placeholder is gone.
  - Site Logistics is one table instead of a block per system, and a record-update request is written only where a record really differs; the Prioritized Technical Risks and Security Advisories text reports list each distinct item once with its systems.
- **Active IQ is the only source of figures.** An upgrade target is shown only when Active IQ reports one (its recommended version, or for E-Series its minimum recommended version); ARIA no longer works one out from the version number. Recommendation counts for a customer are those measured on that customer's systems; a count is no longer extrapolated from an account-wide score.

### Fixed
- The Action Planner downloads were named like `executive_summary_System__NAME.docx`; they now use a descriptive title, the scope and the date, like the Deliverables Suite files (for example `Executive Summary - Customer Name - 06 October 2026.docx`).
- **Download All** covers every document on the Deliverables page, not just the 15 suite documents, and saves the As-Built sheet as an Excel workbook; the button shows the real count.
- Toggle switches next to long labels were squeezed narrower than the knob, so the knob stuck out of its track.
- With sign-in on, a page left open after its session lapsed showed empty lists and dead buttons; it now goes to the sign-in page.

### Removed
- The Value Reporting setting (cost per TiB per month) and every dollar figure built from it, plus the unused support-cost and incident-cost constants. Savings are shown as terabytes saved.

## 5.6.267 (2026-10-05)

### Added
- **Team deployment.** Dockerfile, docker-compose.yml and Kubernetes manifests (`deploy/k8s`), one data volume, a `/healthz` probe. See `docs/DEPLOY.md`.
- **Sign-in and roles.** `ARIA_AUTH=local` (login page, scrypt-hashed accounts, signed session cookies, throttling) or `ARIA_AUTH=header` (single sign-on through a proxy). Roles: administrator and viewer. A default administrator (`admin` / `Changeme1!`) must choose a new password at the first sign-in.
- **User administration in Settings > Access**, with a switch to turn sign-in on or off (applies at the next start).
- **Desktop program (ARIA.exe)** now runs the full server: sync, cache, reports and optional sign-in (`ARIA.exe --sign-in` / `--no-sign-in`).
- **Service History tab** (Action Planner): Active IQ monthly uptime and downtime, ARP coverage, risks found and resolved, auto-resolved cases; per-volume protection gaps; Active IQ's aggregate capacity forecast; and the kind of change (and whether disruptive) that fixes each open risk.
- **`api_queries.json`**: every Active IQ query, endpoint and mutation in one editable file that the server and the browser read. `tools/validate_api_queries.py` validates the queries against the public schema reference.
- `docs/DATA_SOURCES.md`: where every piece of data comes from.
- `tools/audit_formatting.js`: formatting audit of the deliverables, run from the browser console.
- `tools/guard_sensitive.py` and the commit and push hooks: block customer or other sensitive data from reaching the repository.

### Changed
- **Settings** is seven tabs with two-column cards. The subgroup creator moved into the Custom Subgroups card (Fleet tab).
- Keys and tokens (refresh token, NVD key, GitHub token, webhook URL) save when you leave the field, show as saved after a reload and can be cleared.
- Contact roles `retentionSpecialist` / `solutionEngineerSpecialist` and lifecycle `eventDate` (replacing the deprecated `csm` and `daysToEvent`) are fetched in a separate pass; the deprecated fields stay as the fallback.
- Static files are sent with `Cache-Control: no-cache` and the page stamps each of them with its modification time, so a browser always loads a changed style sheet or script.
- File pickers use the dark theme.
- Reference tables are read from an optional local file; the repository holds source code and documentation only.
- The local server answers only this machine unless `ARIA_ALLOWED_HOSTS` is set, and sends fixed content types.

### Fixed
- **AutoSupport "stopped sending" was wrong for many systems.** ARIA used the `latestAsup` field, which is often an older regular message, while newer management-log, performance, user-triggered or E-Series AutoSupports had arrived (median 9 days newer on a real fleet). The newest AutoSupport of any type is now used, so systems that are still sending no longer show as stale; Active IQ's own latest is kept as `latestRegularAsupDate`.
- **Deliverable formatting** (checked across 58 customers): "Benefit: undefined" and a "TBD" placeholder removed; upgrade steps, recommendations and caveats are bullet lists instead of broken tables; contract rows are a table with a header; a sentence or list item above a rule is no longer a heading; decision items sit one level under their heading; no heading over an empty section; HTML stripped from advisory titles.
- The write-back mutations and the firmware probe queries selected output fields that are not in the schema.
- The SAN & NAS table failed for a system with no data volumes.
- A heading such as "SYSTEMS RANKED BY ISSUE SEVERITY (Worst First)" kept "BY" in capitals in Word exports.
- A blank page with "JavaScript error detected / Message: undefined" when the Windows registry mapped `.js` or `.css` to `text/plain`.

### Removed
- The System Metadata & Logistics Editor.
