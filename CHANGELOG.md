# Changelog

## 5.6.354 (2026-10-17)

### Added
- SANtricity (E-Series) and StorageGRID procedures, written from NetApp's own documentation pages (read this session) and shipped in tools/playbooks.json: SANtricity OS and NVSRAM upgrade for the advisories a newer controller release fixes (one procedure per array, grouped by target release, with the 11.70.5 prerequisite, the Recovery Guru check, signed-firmware rule, transfer-now/activate-later option and the post-upgrade inventory check); drive firmware upgrade (online and offline, the prerequisites, the errors that stop it); media scan frequency; hot spare coverage; drawer loss protection; Recovery Guru entries; drives past six years (logical replace); remote login (SSH), now written from the page itself. StorageGRID: software upgrade (version check, hotfix first, recovery package, prechecks, primary Admin Node, approving nodes, completion checks), NTP servers, stored object compression (with the FabricPool and range-read cautions), Object Lock for versioned buckets, and site capacity (adding volumes, shelves or nodes).
- Coverage on the large test fleet: 31,074 of 32,946 findings (94.3%); E-Series 70% (from 0% for most kinds), StorageGRID 42%. The rest are optimisation suggestions (use flash), bugs whose fix is in a support article that is not public (DBM corruption, the SANtricity upgrade-failure bulletin), and a few kinds not yet written; they are listed in Settings > Data & Sync > Procedure coverage.
- The playbook format gained: {name|text} (a default for a value the finding does not give), built-in values {target} (the release the finding or Active IQ asks for), {finding}, {advisory}, {cve}, {detail}, {recommended}, family 'any', and groupKey / compact / advisoryRef so one upgrade procedure serves all of an array's advisories (SANtricity and StorageGRID, as ONTAP). The Implementation Plans, Change Tickets, Handover Brief and Risk & Remediation Brief say 'systems' instead of 'clusters' for these. Findings the tool raises itself after a system is enriched (StorageGRID site capacity) now get their procedure too.

## 5.6.353 (2026-10-17)

### Added
- Remediation playbooks are now data. tools/playbooks.json (shipped) and data/playbooks_local.json (yours, never overwritten by an update) hold procedures in a documented format (docs/PLAYBOOKS.md): the finding to match, the names to take from the system and the finding, the steps with commands, options, a ticket with risk, window and rollback, and the NetApp pages it was written from. A new entry applies on the next load with no release. Only entries marked approved are used; a draft waits for a person, a local rejected entry switches off a shipped one, and an invalid entry is reported (never used). Procedures for E-Series and StorageGRID can be added the same way; the first is E-Series Remote Login, written from NetApp's SANtricity documentation.
- The tool now knows what it has no procedure for. After each load it reports the findings that got none (data/playbook_gaps.json); Settings > Data & Sync > Procedure coverage shows the share covered (92.4% on the large test fleet), the kinds of finding with none, drafts waiting for approval and invalid entries, and the 25 largest gaps are added to the reference updater's review queue as 'playbook-gap' items. A kind that later gets a procedure leaves the record and its queue item closes. Nothing is written or fetched by the tool itself, so it still runs where no AI or internet is allowed; the weekly maintenance job (docs/LIBRARY_HARVEST_ROUTINE.md, new section) drafts entries from NetApp's documentation and a person approves them.
- Six ONTAP procedures written in code (automatic giveback, NTP redundancy and unresponsive servers, single DNS server, FabricPool certificate validation, cluster peering encryption, license files) moved into the data file; the others stay in code until they are moved. Tests: tests/test_playbooks_data.py (14): loading, approval, validation, the gap record and queue, and the data engine under node.

## 5.6.352 (2026-10-17)

### Added
- More procedures: security advisories and bugs that a newer ONTAP release fixes (the largest group, about 15,000 findings on a large fleet) now carry the full upgrade procedure for the cluster: read the fix, choose the target release (a patch on the same release line where one contains the fix, which is flagged when the advisory's target is on another line), check health, load the image, validate and estimate, rolling update, watch, confirm, with a MetroCluster variant. In the documents one cluster is in one upgrade group, for the highest release any of its advisories asks for, with the list of advisories that upgrade closes, so a cluster with forty advisories gets one procedure, not forty.
- Also covered now: inactive data reporting and FabricPool tiering, FlexCache, FlexClone, the disk qualification package, NFS in-flight operation limits (the client addresses from the finding and the slot-table setting for Linux clients), inline efficiency on the named volumes, a second intercluster LIF, 64-bit NFSv3 identifiers for FlexGroup SVMs, the diagnostic-login boot argument, snapshots on every data volume, volumes near full, disk, service processor and shelf firmware, switch monitoring, and releases past end of engineering support.
- End-of-availability and version-range advisory findings that the tool builds from its reference data now get the same procedure as the findings Active IQ reports (they did not before). Coverage on the large test fleet: 30,410 of 32,945 findings (92%) carry a procedure written for their own system, up from 9,866 (30%); the generic fallback is 846 findings (2.6%).
- The per-system sections of the Change Tickets and Implementation Plans show a one-line upgrade for an advisory and point at the group procedure, so the documents do not repeat the upgrade steps for every advisory. The procedure sections list up to 30 procedures, then name the rest.

## 5.6.351 (2026-10-17)

### Added
- The procedures are also in the Change Tickets and the Handover Brief. The Change Tickets end with a ticket per finding type (CHG-P01 and on), each covering every cluster it applies to, with the reason, the risk of the change and the window, the pre-check, the change (commands written for the first cluster), the verification and a rollback: a specific command where ONTAP has one (FIPS, SMB signing, export rules, AES Kerberos, gateways, certificates, cluster peering encryption) and a plain statement where it has not (tamperproof snapshots, encryption conversion, platform refresh). The Handover Brief carries the same procedures as the Implementation Plans, so the team taking over has the commands as well as the findings.

## 5.6.350 (2026-10-17)

### Added
- Remediation procedures written for the system: the findings that occur most often now carry a documented procedure with the exact ONTAP commands, built from the cluster, node and SVM or policy the finding names (multi-admin verification, configuration backup to a remote server, log forwarding, tamperproof snapshots, native FPolicy, FIPS, data-at-rest encryption and NSE drives, export rules open to 0.0.0.0/0, anti-ransomware, SMB signing and AES Kerberos, default gateways, Vscan, auto giveback, NTP and DNS redundancy, FabricPool certificate validation, intercluster peer addresses, license files, compaction, compression and deduplication, consolidation, end-of-availability platform refresh, Cloud Insights and BlueXP discovery, switch log collection, expired certificates, broadcast domain reachability, cluster peering encryption, continuously-available shares). Commands are gated by release (for example multi-admin verification needs 9.11.1) and left as <placeholders> where the finding does not say; none are invented for E-Series or StorageGRID. Active IQ's own guidance links follow the procedure.
- Before this, 35% of the risks in a large fleet (11,678 of 32,939) fell back to a generic three-line plan; with the procedures it is 4% (1,404), and 9,866 risks carry a procedure for their own system. The remediation window, the Risk & Remediation Brief, the Implementation Plans and the Security Brief show them: a procedure per finding type with the commands for the first cluster, and a table of every cluster it applies to with what the finding says about each.
- Tests: tests/test_playbooks.py (5) runs the real function under node: names from the finding, release gate, no template text, not for E-Series.

## 5.6.349 (2026-10-17)

### Fixed
- Model names on screen: every tab shows the name a system is sold under instead of the code Active IQ reports ('AFF-A800' is 'AFF A800', 'FDvM300' is 'ONTAP Select (FDvM300)', 'CDvM200' is 'Cloud Volumes ONTAP (CDvM200)', an E-Series array reported as '2806' or '5700' is 'NetApp E2800' or 'NetApp E5700'), including tooltips. Cluster and host names that contain a model (for example a cluster called after its AFF model) are left as they are, in the tabs and in the documents; the document rewrite had been changing them.

## 5.6.348 (2026-10-17)

### Fixed
- Model names in the other documents: E-Series arrays that Active IQ reports as a bare number now carry their name in the model column of the system tables ('[E-Series] | 6000' is 'EF600'), after 'Platform:' ('Platform: 2806' is 'E2800') and in the platform age list ('- 600: 4'). Every Action Planner document and deliverable was generated for two customers and scanned for any code that is still unnamed: none is left.

## 5.6.347 (2026-10-17)

### Fixed
- TAM Success Plan: the account health score appeared as the last bullet of the list of platforms and node counts (it was a line starting with an asterisk, which the Word converter read as another list item). It is now its own sentence under the list: 'Account health score: 49/100 (Grade F), calculated from the findings, support, lifecycle and capacity data collected from Active IQ.'
- Platform lists in the documents say what a model code is. Active IQ reports some models as a bare number or a code: an E-Series array as '3000', '5700' or '2806' is now 'E-Series 3000' and so on, 'CDvM200' is 'CDvM200 (Cloud Volumes ONTAP)', 'FDvM300' is 'FDvM300 (ONTAP Select)', and 'SG6060' as an E-Series record is 'SG6060 (E-Series array of a StorageGRID appliance)'.
- Platform lists in the documents use the names the systems are sold under, not the product codes Active IQ reports: 'AFF-A800' is 'AFF A800', 'C190' is 'AFF C190', 'FDvM300' is 'ONTAP Select (FDvM300)', 'CDvM200' is 'Cloud Volumes ONTAP (CDvM200)', and an E-Series array reported as '5700', '3000', '6000' or '2806' is 'NetApp E5700', 'EF300', 'EF600' or 'E2800' (E-Series). The rewrite runs on every document and deliverable, so a code in a table or a sentence is named the same way.

## 5.6.346 (2026-10-17)

### Fixed
- Action Planner tabs checked one by one against the same problems found in the earlier documents (a fact that belongs to a cluster repeated for every node, counts that did not agree between tabs, labels that said something other than the figure). Fixed:
- DR and Replication Health: the SnapMirror relationship count is the cluster's total, which every node of the cluster reports, and it was listed once per node (a 2-node cluster with 166 relationships showed 166 twice and the coverage figures counted nodes). One row per ONTAP cluster now, with the largest node figure, and the coverage tiles count clusters.
- Contracts and Lifecycle: a lifecycle event shared by the nodes of a cluster was listed once per node (four identical rows for two clusters), the renewal pipeline had a row with no system name, the tiles counted nodes, and the fourth tile described renewals as 'EOA / EOS milestones'. One row per cluster, grid or array, the tiles count them, an unnamed row shows its serial number, and the tile reads 'Renewals, EOA and EOS milestones'.
- Account Intelligence: the account team was listed once for every node of a StorageGRID grid, and the 'Systems' tile counted nodes. One row per cluster, grid or array, the tile shows the count with the number of nodes beside it, and a replacement character from Active IQ's site data no longer appears in site names.
- Contract Compliance: one row per cluster, grid or array (earliest contract end, worst status, earliest warranty end), warranty and service-tier tiles count them, and the Licensed Feature Adoption table could show more 'confirmed active' than 'licensed' (4 / 2 and 6 / 2) because it counted every license record of every node; it now counts each cluster once (2 / 2).
- Feature Adoption and Operational Health: ransomware protection, SnapMirror and HA are cluster settings and are counted once per cluster (0 of 2 clusters, not 0 of 4 nodes), the recommendation names the clusters, and AutoSupport, which each node sends, stays per node; the per-node matrix says so.
- Sustainability: the whole-account Active IQ score was labelled 'Fleet Sustainability Score' with the explanation only in a tooltip, which a Word document loses. The label and the weekly trend heading now say it is Active IQ's whole-account score, not specific to the scope.

## 5.6.345 (2026-10-17)

### Fixed
- Fixed: the risk trend chart was not correct. It added up whatever systems a day's snapshot happened to hold, so the line fell to zero from 28 September to 2 October (harvests that stored no risks were counted as 'no risks'), jumped on 3 October when risk capture began, and dipped on 11 October (a partial harvest). The trend now counts the same systems on every day, and a day is left out when fewer than 70% of those systems were captured or when most of them have no risks recorded; the chart says how many earlier days are not shown and why. On the current data only 12 October onward is comparable. The 30/60/90 day Better / Unchanged / Worse scorecard in the documents uses the same comparable days, so it can no longer report a change that is only a gap in the data. Nine tests cover it.
- Fixed: the Capacity Breakdown table could not be reconciled. Active IQ reports raw capacity, usable capacity, used capacity and a utilization percentage per node, on different bases: the percentage is often neither used / raw nor used / usable (one cluster shows 86% where used / usable is 52%), and 'used' can exceed usable when it includes capacity outside the local aggregates, such as an object-store tier. The table showed raw, used and the percentage side by side as if they agreed, and its total row used yet another formula. It now shows Raw, Usable, Used, Used / usable (calculated, so the columns reconcile, with a flag above 100%) and Active IQ's own utilization labelled as Active IQ's; the total row shows used / usable and no longer averages Active IQ's percentages.
- Documents and deliverables are unbranded: they no longer name the tool, and say instead that they are an interpretation of the data collected from NetApp Active IQ. Every document carries one basis line under its title (Active IQ's own figures are labelled as Active IQ's; anything derived from them is marked as derived), the wording that named the tool is rewritten ('no firmware baseline is held for this switch', 'derived comparison', 'measured from the collected data'), the 'Generated By' line is replaced, and the Word and PowerPoint properties and the PowerPoint footer no longer carry the product name. Applies to every download and to the on-screen previews of the deliverables.
- Contents and headings: the change tickets and runbooks were headed 'System 4: 10 systems with identical changes', which told the reader nothing, and the contents filed them under 'Estate and platform'. A group is now named after its clusters ('cluster-a, cluster-b (2 clusters with identical changes)', 'cluster-c (2 nodes with identical changes)'), a single entry says which node, and these sections are listed under 'Actions, plans and handover'.
- Site Logistics, Contacts and Customer Health: every system was reported as having 'pending record updates' with a ticket template (393 of them for one customer) because nothing ever records the original values to compare with. A change is now reported only when a recorded original exists. The document is one row per cluster, grid or array (it was a block per node, 6 MB in Word for one customer), with a summary of what is missing, the logistics alerts, and a short section on updating the records.

## 5.6.344 (2026-10-17)

### Added
- Full sweep of the Action Planner and the deliverables: the 28 documents of a 245-system customer were generated and checked for which topics each carries, for raw Markdown or code leaking into the Word text, and (with tools/audit_deliverables.py, 38 scopes) for placeholders, invented figures and other customers' names.
- Word: a Markdown table inside a plain-text document (the hardening scorecard, known-exploited-vulnerability and configuration tables appended to the Security Posture Brief and the MSP Service Report) was printed as literal pipes and dashes; it is now a table. After the fix no document leaks Markdown, code fences or placeholder values into the Word text.
- When a topic is too long to list in a document but is covered in another, the document now says so and names the document that has the complete list. A new section 'Related Findings, and Where the Complete List Is' (a table in Markdown documents, lines in plain text) lists, for the scope, known exploited vulnerabilities, hardening gaps, configuration findings, unowned drives, SnapMirror findings, switches needing attention, risks first raised in the last 30 days and hardware end of support, each with its count and where the full list is; a topic the document already has a section for is left out. It is in the Executive Risk Assessment, Solution Proposals, TAM Success Plan, QBR Pack, MSP report, Handover Brief, Risk & Remediation Brief, Security Posture Brief, Customer Health report, and the Technical Risks and Security Advisories sections. Lists that were cut (the system ranking, StorageGRID nodes and tenants, platform insights, switches, upgrade order, contracts, per-system risks, the Executive Summary and Next Steps lists) now end with where the rest is.
- Better / Unchanged / Worse: the 30, 60 and 90 day view is now a scorecard. Each measure (critical, high and medium risks, open severity 1 and 2 cases, systems with ransomware protection on and off, systems with a lapsed contract, average efficiency ratio, system records in scope) is compared with the same measure 30, 60 and 90 days ago and marked Better, Unchanged or Worse, with a count of each per window. The server computes the new measures from the daily snapshots it already keeps, so the history is complete from the first snapshot (four tests). Where fewer days of history exist than the window asks for, the note says so.
- What changed and the scorecard are now in the documents that report on a period: the Executive Risk Assessment, TAM Success Plan, QBR Pack (90 days), MSP report, Handover Brief, Risk & Remediation Brief, Security Posture Brief, Customer Health report, the Customer Value Report, the Executive Summary and the Technical Risks section; the Configuration Review gains a count of findings first raised in the last 30, 60 and 90 days. The what-changed table shows the 10 most serious kinds of new risk and points to the Customer Value Report for the full list.
- The Security Advisories section and document now report the known exploited (CISA KEV) vulnerabilities, and the Configuration Review now also covers MetroCluster mediator and automatic switchover findings, card firmware with a known issue (NetApp KB rule) and a summary of the security configuration gaps of the hardening scorecard with a pointer to the scorecard.

## 5.6.343 (2026-10-17)

### Added
- Fixed: a harvest could be saved as complete when its systems list had stopped early. If the request for page 2 or later of the systems query timed out, dropped, hit a proxy error page or got a 429/5xx answer, the paging loop ended quietly and the partial fleet was saved over the good cache (255 systems of 1,697 in one real harvest, shown until the next harvest). Such a page is now retried (3, 6 and 12 seconds apart); if it still fails the harvest is marked incomplete, the systems of the previous harvest that it lacks are kept and marked, and the warning in Settings says so. Ten tests cover it.
- New Configuration Review tab in the Action Planner (its tab shows the number of findings) and a new deliverable, P. Configuration Review: every misconfiguration and wrong placement with what to do, the commands, and the clusters; findings are grouped by area (high availability, cluster network, hardware, disks, management), ordered by severity, with the unowned drives in detail and the clusters that have more than one finding. Word and text downloads like the other documents.
- Rebuilt from the customer's own data, as proper documents in Word and text: the Executive Summary (overall position, estate at a glance, decisions needed with owner and timing, risk and security with where the risk is concentrated, support, contracts and lifecycle, capacity, data protection, configuration; it was five counts and a sentence), Operational Guidelines and Next Steps (the priority actions grouped now / next / later, the ONTAP upgrade order, the checks before and after a change with the cluster-specific cautions for MetroCluster, ASA, StorageGRID, E-Series, VMware, Kubernetes and switches, change control and the review cadence; it was a fixed block of generic text that named VMware and Trident whether or not the customer had them) and Network Switch and Fabric Validation (each physical switch once instead of once per node, with a summary, the switches that need action and what to do, the inventory and firmware by model).
- Word documents: a numbered action no longer puts its whole sentence into a dark banner. A long title keeps its first clause as the banner headline and the full text moves into the card body; an item with no detail rows is a numbered paragraph, not an empty banner. Longest banner in the proposal, communications, security and review documents is now 87 characters.
- Platform findings: drive end-of-support and drive-firmware findings are one finding per cluster with the drive models added up across its nodes, instead of one line per node and per model (16 lines became 13 in the Technical Solution Proposal of a two-cluster customer).

## 5.6.342 (2026-10-17)

### Added
- Unowned drives are now a risk and a recommendation in the reports and deliverables, not only in the Security Posture Brief. A section 'Unowned Drives (risk and recommendation)' states the risk (unowned drives cannot serve as spares or hold data, so spare coverage and usable capacity are lower than the drive count suggests; Active IQ's severity, the count and how long it has been open), the recommendation, and the commands to list, assign and verify. It is in the Executive Risk Assessment, the Customer Advisory, the Technical Solution Proposals, the TAM Success Plan, the QBR Pack, the MSP Service Report, the Account Handover Brief, the Customer Health and Lifecycle Report and the Risk & Remediation Brief (full table); the Change Control tickets get one change per cluster (pre-check, change, verify, rollback), and the CLI Runbooks the commands. A document for a customer with no unowned drives is unchanged.
- New Configuration review, on the Overview (a card folded to one line) and in the documents, for the configuration problems that sit beside unowned drives. It groups what Active IQ already flags: a card in an unsupported slot, NS224 shelf cabling that does not follow best practice, takeover not possible, automatic giveback off, two cluster LIFs on one port, a cluster network port offline, intercluster LIFs below best practice, a Service Processor with no address, AutoSupport sent by SMTP, and unowned drives. For each: what to do and the commands that show and fix it, with the clusters and Active IQ's own evidence. On the current fleet: 151 findings on 123 clusters.
- Three comparisons Active IQ does not raise, derived by ARIA from the inventory Active IQ reports and labelled 'ARIA comparison' (confirm them on the array): the two nodes of an HA pair with different cards in the same slot (found on 3 of 213 two-node clusters, for example a card or Flash Cache present on one node only), ports of one broadcast domain with different MTUs (data ports against each other; the fixed 1500 management port e0M is excluded, which removed every hit on the current fleet), and AutoSupport over plain HTTP. A card's slot is deliberately not judged against the documentation: NetApp's slot rules differ by platform (an Ethernet card in a storage slot is correct for NS224 shelves), so only Active IQ's own unsupported-slot finding is used.
- In the documents the review is a table of the checks with the recommendation (and the evidence for ARIA's own comparisons), the full per-cluster list in the Risk & Remediation Brief and the Security Posture Brief, and the commands in the CLI Runbooks.

## 5.6.341 (2026-10-16)

### Changed
- Documentation brought up to date with everything shipped since 5.6.262. README: version badge; the new analysis (cluster-level reporting, known exploited vulnerabilities with their evidence rule, the security hardening scorecard, SnapMirror health, unowned drives, What changed, automatic update settings); the Success Plans use case, dashboard section, 19-template trigger table (Best Practice & Configuration Hardening was missing) and the new write chain, progress sync and manual form; light theme, Connection check and Reference updater in Settings; three background timers; repository layout, component sizes, development workflow and release rule; new troubleshooting rows (401 through a proxy, empty first sync, account warning, partial Success Plan, plans not updating). CONTEXT.md: current version, corrected file inventory (paths under tools/, sizes, new data files and documents) and a new addendum for 5.6.276 to 5.6.340 describing how the code is organised. docs: DEPLOY (role table, ARIA_NO_PROXY, outbound access, automatic plan updates, image tag, Settings > Access), DATA_SOURCES (plan write-backs, the library updater's pages), OFFLINE (dark-site reference data), data/README, PLATFORM_COVERAGE (installed cards, verification tools, what Active IQ does not give) and a historical note on ARIA_FIX_PLAN.
- The automatic Success Plan update now skips a signed-in viewer's session (the server would refuse the write on every harvest); an administrator's open session, or a single-user install, does the update. The Success Plans tab says so.

## 5.6.340 (2026-10-16)

### Added
- Success Plans now follow the data. After every harvest ARIA re-measures each active plan it created and, when the measure has moved, a milestone or action changes status, or the health changes, writes the update to Active IQ itself: the plan's health, the status of each milestone and action, and one dated progress note (for example 'Open critical findings 16 -> 10, 50% of the way, 20% of the time elapsed'). A plan whose measure has not changed is not written to, and closed plans are left alone. The Success Plans tab shows when the last check ran and what it updated, and a checkbox there turns the automatic updates off (the update button on a plan still works).
- Health is no longer lowered by a harvest that shows no change: a plan opened RED stays RED until it improves or the date passes.
- The New Success Plan form now captures what a well-shaped plan holds: title, customer challenges and goals, summary, objectives, Active IQ success metrics (chosen from the list Active IQ accepts), success measures with baseline, target and date, key stakeholders (name, e-mail, role), the NetApp team, notes, and milestones with dated actions, owners and statuses. It is written to Active IQ the same way as a composed plan (plan, then milestones, then actions), and anything Active IQ refuses is listed. Editing a plan can now change its title, challenges and goals and stakeholders as well. The window is wider and scrolls.

## 5.6.339 (2026-10-16)

### Added
- Success Plans are now drafted the way a well-shaped customer success plan reads, and written to Active IQ in full. Each plan has a one-line summary, challenges and goals (what was found, why it matters, the scope with every cluster and its nodes), the Essential or Elite tier, a lifecycle stage, up to three objectives named for the outcome, and a success measure with a baseline, interim targets and a final target with dates. ARIA sets the opening health from the findings (RED, YELLOW or GREEN).
- The plan structure is created in Active IQ, not only the text: five milestones (confirm scope and baseline, first measurable result, halfway target, target reached, verified and handed over), each with its actions, owner, due date and status, written with the milestone and action mutations in that order. Key stakeholders and the internal team are listed, and the plan notes carry the full scope, the measure, the review cadence and a [template] marker so a plan is never created twice. If Active IQ rejects the objectives the plan is retried with Other plus a description; if it rejects the long text a shorter text is sent and the complete list goes into the notes; anything it still refuses is reported and kept for later.
- The preview before adopting shows the complete plan as it will be written. After adoption ARIA keeps the plan's structure, and the plan window gains 'Update Active IQ from ARIA's measurement' (re-measures from the live data, sets each milestone and action status by its own rule, sets the plan's health from progress against time, and adds a dated progress note) and 'Complete missing items' (creates what Active IQ did not accept the first time). Both ask before writing to the customer's account.
- Checked against Active IQ's own input definitions for all 17 templates (323 create and 3 update payloads, no problems); the writes have not yet been exercised against a live account.

## 5.6.338 (2026-10-16)

### Added
- The weekly library routine is now built into the ARIA engine (tools/library_updater.py), so reference data and the NetApp library are kept current without anyone running a job. Each sweep (four minutes after start-up, then every 24 hours; 'Sweep now' in Settings > Data & Sync) reads the key official pages (release lists, What's new pages, end-of-availability, TR indexes) and the stalest of the 160 source pages the library's documents name, one request a second and public pages only, keeps a searchable copy of each page, and compares it with the last read: a newer release number, new KB, CVE or advisory ids, or lines added and removed.
- Every new release or id is looked up in ARIA's own data; what ARIA holds is covered, the rest goes to a review queue in Settings with the page, the changed lines and, for known-issue ids, a ready rules stub. A change to a release, end-of-availability, advisory or What's new page runs the existing scanners straight away. The library's unseen CHANGELOG entries are read the same way, and one that says no material changes and names nothing ARIA lacks is recorded as harvested by itself.
- The Curated reference tables row no longer says 'static (manual)': Settings lists all 21 tables as kept up to date by a scanner (9), partly by a scanner (5) or by hand (7), and for the hand-kept ones names the official pages that changed since the file was compiled. A compatibility range, a prose best-practice fact or a new kind of check is never written by the updater; those stay with a person. Eleven tests cover it (65 in all).

## 5.6.337 (2026-10-14)

### Added
- New Overview card 'SnapMirror health' (folded to a summary line, and a section in the Security Posture Brief). Active IQ's API gives only the number of relationships per cluster (checked against the live schema: no source, destination, policy or lag), so health is built from the findings Active IQ raises, in four classes: updates failing, destination disrupted, MetroCluster, and cluster peering or intercluster network. On your data: 101 clusters report relationships (20,225 in all), 460 report none, 140 clusters have a replication finding and 16 of them have updates failing; each row shows what Active IQ says (it names the source volumes), how long the most serious class has been open and the next step.
- The Support Cases and Firmware Currency documents now list per cluster, grid or array. A case on both nodes of a cluster is one case naming the nodes; firmware updates that apply to every node are one line, on some nodes only they name them (86 node lines became 8), a cluster's drive inventory is counted once, and the status table has one row per cluster, grid or array. The as-built workbook and the systems CSV keep one row per node (serial numbers are the point of an inventory) and gain three columns: Cluster / Grid / Array, Unit Type and Nodes in Unit.
- StorageGRID grids can now be chosen as a scope on the Support & Ops and Customer Success tabs ('Grid: name (N nodes)'), and clicking a grid in the Overview opens it with that scope. The Technical Audit node strip titles an E-Series box 'E-Series array: name' instead of presenting it as a cluster, and the 'node-specific' marker in the Overview table no longer wraps.

## 5.6.336 (2026-10-14)

### Fixed
- Capacity is now shown the same way everywhere. One formatter (TB below 1,000, PB from 1,000 up, with thousands separators; PB is TB divided by 1,000, so a number never changes meaning from one screen to another) now drives the Overview donut, bar and capacity charts and their tooltips, the Value and ROI tiles, the Customer Success capacity cards and tables, the per-system capacity tables, the StorageGRID and E-Series capacity text, the StorageGRID licence capacity, every document (capacity, savings, growth, headroom, LUN and volume sizes) and the customer PowerPoint. The Value tile that showed '9.92 PiB' next to '10154.7 TB' now shows '10.15 PB' with the TB figure beneath it, and the StorageGRID and E-Series figures that said TiB now say TB or PB like the rest.
- Figures held in the data are KiB divided by 1024 cubed, which is strictly TiB; ARIA has always labelled them TB, and keeps doing so, so the PB figure is the TB figure divided by 1,000. Text that Active IQ itself writes (for example a risk saying a site is 84% full (3442.79 of 4077.3 TB)) is shown as Active IQ wrote it.

## 5.6.335 (2026-10-14)

### Fixed
- Sorting the Capacity Breakdown table by Runway (or Growth/day) was wrong: it compared only the number in the text, so '1.3 Yrs' sorted next to '1.3 days' and '21.8 Yrs' came after '36 days' in the wrong place. Each cell now carries its own sort value in days: an over-limit system sorts first, '> 10 Yrs' last of the known runways, and 'Not available' always at the end, in both directions.
- Correction to 5.6.334: raw capacity is NOT filed per HA pair. Checked against Active IQ's own cluster total (a 12-node cluster reports 3,071.18 TB, and its nodes' raw figures add up to exactly 3,071.18 TB; used capacity matches the same way), so the nodes' figures are added up. The pair rule introduced in 5.6.334 halved raw capacity in the Capacity Breakdown table and in the platform-headroom and power-per-TB figures of the deliverables; it is removed and those figures are back to the sum of the nodes. The fleet-wide capacity totals were never changed and were right.

## 5.6.334 (2026-10-14)

### Fixed
- The Capacity Breakdown table showed '> 10 Yrs' in green for systems that were at or over 90% full. Two causes: a system with no measured capacity history (no projection at all) was treated as having a runway of 9999 days, and a system already past the 90% threshold (0 days left) was also turned into 9999 days because 0 counted as 'no value'. The runway now reads 'Not available' (grey, source '-') when Active IQ reports no capacity history, 'Over 90% limit' or 'At 90% limit' when there is no room left, and '> 10 Yrs' only when growth was measured and the limit is more than ten years away.
- The same table now has one row per cluster, grid or array, titled 'Capacity Breakdown by Cluster, Grid or Array': used capacity and growth are added up over the nodes, utilisation is the worst node's, the runway the shortest. Raw capacity is counted once per HA pair (Active IQ files it per pair, so both nodes of a pair report the same figure; a 12-node cluster showed 3,071 TB where its six pairs add up to 1,536 TB), while a StorageGRID grid's nodes and an E-Series array are added up. The platform-capacity headroom and power-per-TB figures in the deliverables use the same rule.

## 5.6.333 (2026-10-13)

### Fixed
- The StorageGRID card on the Technical Audit tab (and the Action Planner StorageGRID tab) no longer runs to hundreds of rows on a large grid. Tenants and buckets are one summary line (for example 560 tenants, 3,152 buckets, 570 versioned, 0 immutable, 24 CloudMirror) with the table folded, largest tenants first and scrolling inside a 260-pixel box with a fixed header when opened. A grid with 12 tenants or fewer stays open. The node and ILM rule tables also scroll inside their own box on a large grid.

## 5.6.332 (2026-10-12)

### Added
- Every deliverable now reports per cluster, grid or array and names individual nodes only where that matters. The risk, upgrade and contract lists the documents are built from have one entry per unit (a risk on both nodes of a pair is one entry; a hardware or node-firmware risk on only some nodes reads 'cluster (node only)'); the CVE matrix, the configuration and best-practice findings, the non-CVE critical issues, the oldest findings, the risk, advisory and upgrade documents, the customer report's estate table, the sustainability scores and the Security Posture, Handover, Success Plan, Problem Statement and Risk Remediation documents all list each cluster, grid or array once. Where a unit's nodes run different releases, the fix lines name the node. When two nodes of one cluster carry the same name, the serial number tells them apart.
- Figures that belong to the cluster are no longer repeated per node: platform capacity headroom and drive inventory (shown once when identical on every node, added up when the nodes differ), the NAS/SAN/snapshot split, platform files and upgrade history; power draw and heat (node figures) are added up per unit. DR, HA and feature-adoption coverage and the ransomware-protection count are per cluster. Genuinely node-level data stays per node: contracts and renewals, adapters, SP/BMC and BIOS firmware, LIFs and health scores.

## 5.6.331 (2026-10-12)

### Added
- Cluster-level reporting carried through the rest of the interface and the documents. Technical Audit: the risk list is grouped per cluster, grid or array, each risk appears once, and a risk on only some nodes says '⚑ node-specific: only on <node>'; the system picker lists one entry per cluster, grid or array (its nodes only when there is more than one) and the Support & Ops and Customer Success pickers list single-node units once, as 'Array: ...' or 'Grid: ...'. The Selected line, the contracts tile and the customer portfolio count clusters, grids and arrays and give the node count.
- Documents: scope counts read '556 clusters, 16 grids, 321 arrays (1,808 nodes in all)'; the ranking of systems by issue severity, the Technical Risks, Security Advisories and OS Upgrade Roadmaps documents list each cluster, grid or array once instead of once per node.

## 5.6.330 (2026-10-12)

### Added
- The Overview now reports one row per cluster, grid or array instead of one row per node: 1,808 node records become 556 ONTAP clusters, 16 StorageGRID grids, 321 E-Series arrays and 84 StorageGRID nodes that cannot be placed in a grid. A StorageGRID grid or E-Series array carries a badge and is never called a cluster; the KPI tiles, the table, Needs Attention, What changed, Known exploited vulnerabilities and Unowned drives all count and list these units. A risk found on both nodes of a pair counts once, a contract shows its most urgent node, and the table defaults to the units with the most critical and high risks (50 rows, with a button for the rest).
- Node-specific issues stay visible: a unit with a hardware or node-firmware finding on only some nodes, nodes on different releases, or nodes of different models is marked 'node-specific' with the detail in the tooltip, and a click on a multi-node row lists its nodes. Known exploited CVEs say 'N of M nodes' where only some nodes are affected. Unowned drives are counted per cluster (nodes of a cluster share their drives, so the count is the largest a node reports, 59 rather than 121).
- The Technical Audit node strip no longer files StorageGRID nodes under 'No cluster name reported' (it says 'StorageGRID nodes (grid not identified)'). What changed, Known exploited vulnerabilities and Unowned drives fold to a header and one summary line (the choice is remembered), to make the Overview less busy.

## 5.6.329 (2026-10-12)

### Fixed
- Switching between light and dark mode left the charts with the old theme's text colours: the efficiency doughnut and the capacity, risk trend and projection charts kept dark labels and values on the dark background (and the reverse) until their data changed. Every chart is now recoloured when the theme changes, and the doughnut's centre text and legend follow the theme.

## 5.6.328 (2026-10-12)

### Added
- The Unowned drives card and brief section now carry full detail per system: cluster and serial, customer and site, model, release and HA configuration, the number of unowned drives or partitions (Active IQ's risk text states it: 121 across the 21 systems), severity, first and last seen dates, days open, support contract state and end date, last AutoSupport, health score, and a link to NetApp's storage disk assign documentation. This corrects the card's earlier statement that Active IQ gives no count.

## 5.6.327 (2026-10-12)

### Added
- New Overview card 'Unowned drives': lists the systems for which Active IQ raises 'Unowned drives or partitions present' (21 in the current cache), with customer, model, release and how long the risk has been open, a note where the DS460 ownership rule is also broken, and a copy button. It also prints as a section in the Security Posture Brief. Active IQ's API has no drive owner, container type or auto-assign field (checked against the live schema), so the card says that it knows only that unowned drives exist and gives the array command to list them.
- The hardening scorecard's 'check on the array' table gains disk auto-assign: storage disk option show -fields autoassign; storage disk show -container-type unassigned.

## 5.6.326 (2026-10-12)

### Fixed
- Findings about the Unified Manager installation itself (for example OCUM end-of-version-support, ONTAP not supported by the detected Unified Manager, AIQUM database issues) are no longer listed against storage controllers; they move to the not-applicable list with the other findings that concern a different product. The pattern is data (otherProductFindings in resolution_rules.json).

## 5.6.325 (2026-10-12)

### Fixed
- Only what applies to a system is flagged against it. An advisory that lists no affected product but has NetApp's not-affected table (for example the September 2026 IBM Cognos advisory) was attached to 980 systems; it is now treated as not applicable. The known exploited vulnerabilities check no longer counts the SANtricity ActiveMQ CVE (CVE-2023-46604) on 27 E-Series and StorageGRID systems: that advisory concerns Web Services Proxy and the vCenter plug-in, not the controller software, so such products are no longer matched to SANtricity OS. Findings Active IQ reports are checked against the advisory's product list in the known exploited view too.
- The header chip now shows the number of distinct advisories (it counted duplicates), and its KEV figure is the number of known exploited CVEs affecting your systems, the same as the Overview card, with a tooltip saying so. The card's fix note now reads 'lowest fixed release on its own line, else the next line up'.

## 5.6.324 (2026-10-12)

### Added
- The known exploited vulnerabilities check now covers every KEV CVE that NetApp has an advisory for, not only the 13 ARIA happened to have loaded: NetApp's advisory index names 84 of the 1,739 CISA KEV CVEs, and ARIA now requests all of them. Result on the current fleet: 9 known exploited CVEs on 392 systems (it was 4 on 365). New confirmed exposures: CVE-2023-46604 (Apache ActiveMQ) on 27 SANtricity systems, fixed in SANtricity OS 11.81, and five Linux kernel CVEs on the BMC firmware (CVE-2023-0266, CVE-2021-22600, CVE-2022-0185, CVE-2022-0847, CVE-2024-1086) on 6 to 20 systems each.
- BMC firmware advisories are now decided per system: the fixed firmware is read from the advisory's download file names (such as BMC_FW_308-04160_13.10P1.zip) for the system's own model, and the system is listed when its BMC firmware is older.
- The card and the Security Posture Brief list the other KEV CVEs NetApp has advisories for (75) and why each is not counted: cannot be confirmed because the advisory publishes no fixed release for the product, no usable advisory data, already fixed or fixed only on older release lines, or no system in scope runs an affected product.
- Product matching: "Data ONTAP Edge" (the old virtual edition) and components such as the Antivirus Connector, SMI-S Provider, Manageability SDK, VASA Provider and 7-Mode are no longer treated as ONTAP the array. That removed 1,296 false matches for CVE-2017-1000253 and most of the Heartbleed matches.

## 5.6.323 (2026-10-12)

### Added
- New "Known exploited vulnerabilities (CISA KEV)" card on the Overview tab, and the same section in the Security Posture Brief. For the systems in scope it lists each CISA KEV CVE with when it was added and its federal due date (and how many days past), the products, the number of systems and customers, the evidence, and the fixed release on each system's own release line. "Show systems" lists the systems grouped by customer (each opens in Technical Audit) and "Copy" copies the list.
- A system is listed against a KEV CVE only on evidence: Active IQ reported the CVE on it, or NetApp's advisory lists a fixed release for its product and the installed release is below the fix on its line. Advisories that name other products, releases that are already fixed, and advisories that publish no fixed release for the system's product are not counted as exposure; the card says how many were left out.
- The "No CISA KEV Active Exploitation Alerts" check, and the per-system version of it, now use the same evidence. Before, they matched nearly every ONTAP system (1,285 of 1,296) to three KEV CVEs, two of which are about other NetApp products (the ONTAP Select Deploy utility and Cloud Backup); the evidence-based result is 4 CVEs on 365 systems. Scores that include this check will rise accordingly.
- The CVE index no longer marks every CVE in a multi-CVE advisory as known exploited because one of them is.

## 5.6.322 (2026-10-12)

### Fixed
- The risk count beside each customer and group in the sidebar now says what it counts. Its tooltip gives the number of open risks, the systems they are on and the split by severity (critical, high, medium, low, best practice), and clicking it opens Technical Audit for that customer or group. Risks acknowledged in Active IQ are not counted, because they have been accepted; the tooltip says how many were left out.
- The counts beside customers and groups used to go stale: the sidebar redrew only when its lists changed, so risks and cases that arrived afterwards (advisory matching, generated StorageGRID findings, an acknowledgement) left the pills out of date (48 of 56 differed from the data 15 seconds after load). It now redraws when the totals change.
- The customer and group pills no longer put a name inside the text of a click handler, so a customer name with a quote cannot break them.

## 5.6.321 (2026-10-12)

### Fixed
- The support-case counts beside customers and groups in the sidebar, and the "Open" badge on each system in the systems table, counted every case ever raised, closed ones included (one customer showed 619 where 12 are open; across the fleet 1,605 cases of which 49 are open). They now count only open cases, using the same definition as the documents: not closed, resolved or cancelled, and not still being set up. Statuses such as Open - Active, Open - Customer Action, Open - Awaiting TSE and Solution Proposed count as open.

## 5.6.320 (2026-10-12)

### Fixed
- A JavaScript error ("Invalid or unexpected token") appeared on the Technical Risks tab. The Acknowledge and Mark Mitigated buttons wrote the risk title inside the text of an onclick handler, and 22 risk titles contain a double quote (for example AutoSupport "-to" parameter includes ...), which cut the handler short. The buttons now carry the title in data- attributes, which hold any character, in the Technical Risks tab and in the Technical Audit risk detail. Checked by compiling every inline event handler (about 65,000) on every tab, with none failing, and by clicking a button whose title holds a double quote, an apostrophe, angle brackets, an ampersand and a line break.

## 5.6.319 (2026-10-12)

### Added
- Risk acknowledgement, rebuilt. The write is now made by the server, with the token of the Active IQ account that owns each system, instead of from the browser (which only held one token and could write with the wrong account). Acknowledging a risk now offers Active IQ's own five justifications (resolution planned, system to be decommissioned, risk allowed for this system, workaround applied, other), a comment, and an optional expiry date. One risk can be acknowledged on several systems in one go, with a checklist of the systems in scope, a "this customer" shortcut, a count of customers in the confirmation, and a limit of 500 systems at a time.
- An acknowledgement can be withdrawn from ARIA (the same mutation with the flag off), from the Technical Risks tab and from the risk detail in Technical Audit. Acknowledged risks show a badge with who, when, why and the expiry. Every change is recorded in a log (Acknowledgements made from ARIA) with an Undo button. POST /api/risk/ack has a dry-run mode that checks the owning account's token without changing anything, and is administrator-only.

## 5.6.318 (2026-10-12)

### Fixed
- Light theme readability pass, found with an automated contrast audit that reads every visible piece of text and its background on every tab. Headings, values and port or SVM names that were written in white on the card background (invisible on a white card) now use a strong-text colour that is white in dark mode and near-black in light mode. Amber, green and badge text that scripts write into style attributes now maps to readable shades in light mode. The case-count badge in the system table (orange text on a blue fill) is legible in both themes. Dark grey inset panels become a soft tint. Small text on tinted status badges is now at least 4.2:1 against its background, and almost everything is above the 4.5:1 AA level.

## 5.6.317 (2026-10-12)

### Added
- Light theme. The sun/moon button in the header switches between dark and light, and Settings > Connection > Appearance offers Dark, Light or Match system. Dark stays the default and looks exactly as before (checked by comparing screenshots of the main tabs before and after: the only differences are the new button and the Appearance card). Light uses a soft cool-grey page, white cards with gentle shadows, a deeper sky-blue accent and darker status colours that stay readable on white. Charts, dialogs, badges and the header follow the theme. The rear-panel drawings keep their dark hardware colours in both themes. The choice is remembered, and it is applied before the page paints so there is no flash of the wrong theme.
- Support & Ops and Value & ROI no longer write every system name into the page header when a large scope is selected (1,808 names, 33,000 characters, which pushed the page apart); they show the first six and the count, with the first sixty in the tooltip.
- Repository guard (tools/guard_sensitive.py): ordinary technical words (for example "storage" or "primary") are no longer treated as sensitive harvested terms. A harvested field that was literally "Storage" made the guard match ordinary text in hundreds of places and block commits until the term list was next rebuilt.

## 5.6.316 (2026-10-12)

### Added
- New tool tools/verify_rear_panels_reverse.py: draws each platform with nothing reported and lists every fixed port the drawing shows that NetApp's install, cabling and setup pages for that platform never mention. It complements tools/verify_rear_panels.py, which checks the other direction (every documented port has a place on the drawing). It reads only public NetApp documentation.

## 5.6.315 (2026-10-12)

### Added
- New page docs/OFFLINE.md describing the offline and dark-site path (importing an AutoSupport bundle for a customer who does not send AutoSupport to NetApp): how to use it, what the importer reads, and what it does not give (Active IQ's own risk engine, health score, cases and contracts).
- The hardening scorecard's "not reported by Active IQ" list gains the isolated recovery copy (a vault SnapMirror relationship or SnapLock) and a tested restore, with the commands that show them on the array.

## 5.6.314 (2026-10-12)

### Added
- New "Connection check" card in Settings. It tests, without changing anything: the configured accounts, the system proxy, name lookup and TLS to the Active IQ REST and GraphQL services, the clock against Active IQ's, the last harvest of each account and any harvest warnings, and whether a local reference file is present. "Also test the tokens" asks Active IQ to accept each refresh token and reports only the HTTP status. Each failure comes with a plain-language fix: a rejected token, a proxy that answers for Active IQ, a security gateway re-signing HTTPS, or a wrong clock.
- The sync-failure message no longer tells you to restart the launcher; it points to the connection check.

## 5.6.313 (2026-10-12)

### Added
- Automatic update settings are now shown. Active IQ reports, for each system, whether security files, storage firmware, SP/BMC firmware and system files (such as the disk qualification package) are installed automatically or only notified. ARIA collected these but never displayed them. The hardening scorecard has three new controls for them: a system set to notify-only counts as a gap (an administrator has to act), a system set to automatic does not, and a system that reports nothing is counted apart as not reported, never as a pass.

## 5.6.312 (2026-10-12)

### Added
- New security hardening scorecard on the Technical Audit tab and in the Security Posture Brief. Ten controls (ransomware protection, snapshots on all data volumes, Vscan, open NFS export rules, self-encrypting drive locking, cluster peering encryption, remote configuration backups, NTP and DNS redundancy, open critical or high advisories) each tied to the Active IQ check that evidences a gap, with the systems that have one and the NetApp reference.
- The wording is exact: "no gap raised" means Active IQ ran its check and raised nothing; it does not confirm the setting. Controls Active IQ does not report (multi-admin verification, administrator authentication, TLS and FIPS settings, audit logging, login banner and timeouts) are listed separately with the command that shows their state on the array, and are never scored.

## 5.6.311 (2026-10-12)

### Added
- Success Plans now show measured outcomes. When a suggested plan is adopted, ARIA stores the systems it covers next to the baseline metric. The Success Plans tab then shows, per plan, how many of those systems are no longer affected, whether the finding that triggered the plan no longer applies ("target met: consider closing"), and plans not updated for 60 days or more.
- The plan dialog has an outcome panel: the metric from baseline to now, and the systems no longer affected, still affected, no longer in the data, and newly affected. "Add this evidence to the notes" puts a dated evidence sentence in the notes field; nothing is sent to Active IQ until you save the plan, as before.
- Closing a plan now keeps its record with the result at closing instead of deleting it, so closed plans still show their outcome.
- Account documents that list the account's Success Plans now include a table of outcomes: metric at adoption and now, systems no longer affected, and the result.
- Plans adopted before this version have the metric only; the covered systems are recorded from now on.

## 5.6.310 (2026-10-12)

### Added
- New "What changed" card on the Overview tab, with a 7, 14, 30, 60 or 90 day window, for whatever scope is selected. Newly raised risks come from the live data (Active IQ dates every risk on every system), listed by risk with the number of systems. Under it, a comparison of the latest daily snapshot with an earlier one: OS and SP/BMC version changes, contract and ransomware-protection flag changes, risks that went away, and watchlist moves.
- The comparison is honest about its data. Earlier harvests covered different systems and watchlists, and some stored no risks, so it picks a snapshot with comparable coverage when one exists and says how many systems are in both. Added or removed systems and risk count changes are reported only when the coverage supports it; otherwise a note says why.
- Daily snapshots now also record each system's risk ids, SP/BMC version and watchlists, so "risks resolved" and "moved between watchlists" fill in from 12 October 2026 onward.
- The Value report carries the same section, "Progress, What Changed", with the complete list of newly raised risks.

## 5.6.309 (2026-10-12)

### Fixed
- A system proxy that cannot be authenticated to (common on macOS: VPN and security gateways) answered the Active IQ token request with HTTP 401, which looked like a rejected refresh token and left the app with no data. A 401 or 407 that comes back through a proxy is now retried once without the proxy; when that works, ARIA keeps going direct (a log line says so). Setting ARIA_NO_PROXY=1 forces direct connections from the start. Resolved watchlist names are now merged into aiq_config.json across accounts instead of one account overwriting the other's.

## 5.6.308 (2026-10-11)

### Fixed
- Action Plan generation crashed with "Cannot read properties of undefined (reading 'findIndex')" in calculateUpgradePath — same root cause as 5.6.307's MetroCluster ISL fix: the server's reference-file overlay only adds a platform to SOFTWARE_VERSION_DATABASES once version_catalog.json has entries for it, so on a new/early install a StorageGRID or SANtricity system in the fleet could have no catalog key at all (not an empty list — missing outright), crashing the whole plan. ontap/storagegrid/santricity now always exist as arrays; a platform with no catalog yet falls back to the existing generic upgrade-steps text instead of throwing.

## 5.6.307 (2026-10-11)

### Fixed
- A new install failed its first sync with "Cannot read properties of undefined (reading 'maxPacketLoss')". Without the local reference file, the server supplies only part of the MetroCluster requirements (no ISL block), and the remediation text for a MetroCluster ISL risk read the missing block. The ISL block now always exists, and the text falls back to the figures it already states (0.01% packet loss, 3 ms jitter, MTU 9216). Checked by loading the app with no local reference file and building the remediation plan for every risk of the fleet (28,781 risks, no errors).

## 5.6.306 (2026-10-11)

### Fixed
- A first harvest on a new install no longer ends in an empty page. The page used to stop watching after 20 minutes; on a large fleet the harvest was still running, the cache was still empty, so it showed nothing and never looked again until the page was reloaded. It now keeps watching with no time limit, shows what the harvest is doing (account N of M, current step, elapsed time), loads the first account as soon as it is cached, and refreshes itself when the remaining accounts finish. /api/sync-status carries a progress block for this.

## 5.6.305 (2026-10-11)

### Added
- New check: known issues of network and I/O card firmware. A rule names the card by part number, the model families and the affected firmware (first rule: CFDIAGS-40, the X60132A 4-port CX7 25GbE module on firmware 28.49.1014, where boot_diags fails to initialize the card). The adapter inventory is checked on every system; a match shows in the installed-cards table and in the Firmware Currency deliverable, which also says how many cards were checked and that none was affected when that is the case. Family names match exactly (A30 does not match A300).

## 5.6.304 (2026-10-11)

### Fixed
- Installed cards table: the onboard devices are no longer each flagged as 'N of M ports reported' (slot 0 is every onboard device together, and storage-shelf, service-processor and internal ports are in the inventory but not in ONTAP's network port list); one note gives the onboard totals. A numbered slot whose card has no port in the network port list is now described as that, not as a disagreement, with the reasons it can be normal.

## 5.6.303 (2026-10-11)

### Fixed
- The Enrichment Log now shows the date as well as the time each entry was fetched (cached entries date from an earlier day), and under each summary says what was added: the CVE, advisory and bug identifiers, and the first known-issue and what's-new titles. The catalogue entry says what it is.

## 5.6.302 (2026-10-11)

### Fixed
- A refresh token with a trailing newline, spaces, quotes or a 'Bearer ' prefix (easy to pick up when pasting) was sent as it stood and Active IQ answered 401. The token is now cleaned before use.
- A rejected token exchange now logs the server's reason (status, host, token length, response text, never the token) instead of only 'HTTP 401'.
- An account whose harvest fails (most often a refresh token Active IQ no longer accepts) is now shown as a warning in Settings > Data & Sync until a harvest of that account succeeds; before, its old data was shown as if it were current.
- Rear panel: a table of the installed cards from Active IQ's adapter inventory (slot, card, type, ports, firmware, documented role of the slot) with a check where the inventory and the reported ports disagree, or a note when Active IQ reports no inventory.

## 5.6.301 (2026-10-08)

### Fixed
- Opening or reloading the app started a full background harvest whatever the cache age. A page load now re-syncs only when the cache is older than the auto-refresh interval (an hour when auto-refresh is off).
- The cache metadata has its own table (`harvest_cache_meta`): it sat after the 140 MB result in the same row, which cost about 8 seconds per status poll and page load.
- `/api/harvest` is built once per cache version and sent gzip-compressed (about 180 MB becomes 22 MB).
- A harvest records the seconds per phase (log line and `phaseSeconds` in the result).

## 5.6.300 (2026-10-08)

### Added
- The minimum safe release per ONTAP line is used: fleet and per-system checklist item, Minimum safe column and summary in the OS Upgrade Roadmap, a note on the upgrade card and a text-report section. Upgrade targets are never below it (125 raised, including systems Active IQ reports as up to date).
- Firmware and upgrade-path known issues in `resolution_rules.json` (`firmwareKnownIssues`, `upgradePathKnownIssues`): CFBMC-8277, CFBMC-6454, CFBMC-2358, CONTAP-799924, from the NetApp Reference Library.
- `docs/LIBRARY_HARVEST_ROUTINE.md` and a weekly scheduled job; `tools/library_manager.py --unharvested / --mark-harvested`; Settings > Data & Sync shows the library entries not yet harvested.

### Fixed
- The "recommended is never below the highest installed" firmware rule ignores a lone far-higher backup-image reading.

## 5.6.299 (2026-10-08)

### Fixed
- Code audit (ESLint, pyflakes, tests, a smoke run of all 21 documents): StorageGRID software node rear panel ReferenceError; duplicated `end_headers` (API answers had no cache header); version text sorted as text in two firmware lookups and several version lists; viewers can use the library status, search and document routes; library `Source:` links accept only http(s); dead fix-floor code and a duplicate field removed.

## 5.6.298 (2026-10-08)

### Added
- `tools/netapp_docs_versions.py` also reads the newest ONTAP tools for VMware vSphere version (10.6) from NetApp's release-notes page; Settings > Data & Sync lists it as ahead of the compatibility table (10.3).

## 5.6.297 (2026-10-08)

### Fixed
- A system on ONTAP 9.16.1 was told to upgrade to at least 9.13.1P20 in the remediation plan: the plan passes a copy of each finding that had lost its link to its system, so the installed release was unknown and the lowest fixed release was picked. The system is found by serial number now, and an unknown release lists the first fixed release of each line. No finding in the fleet (32,539 checked) recommends a lower release or another line.

### Added
- `tools/derived_reference.py` derives the remaining hand-kept reference tables from data ARIA collects: latest release per ONTAP line, minimum safe release per line (advisory fixed releases), current platforms, upgrade caveats and MetroCluster feature versions (release notes), Trident note. Harvests record `data/fleet_evidence.json`.

## 5.6.296 (2026-10-08)

### Fixed
- The advisory scanner now also reads the NetApp list ordered by publication date. After NetApp re-dated thousands of old advisories on 7 October, the 400 most recently updated were all old ones and new advisories were missed (20 added at once).
- Recommended SP/BMC and BIOS versions are never lower than the highest version installed on that model in the fleet (a stale hand-kept baseline overrode Active IQ; 495 cases of installed-newer-than-recommended), and release versions are compared numerically.
- The Trident interoperability check no longer skips silently when the recommended version (26.06.1) is more precise than the table's key (26.06).

### Added
- `tools/eoa_list.py` reads the end-of-availability platform list from docs.netapp.com (16 platforms were missing).
- `tools/netapp_docs_versions.py` reads the newest Host Utilities, SnapCenter, Veeam, Proxmox VE and vSphere versions and Settings > Data & Sync lists the integrations whose newest release is ahead of the compatibility table.

## 5.6.295 (2026-10-08)

### Fixed
- CISA KEV status is read from CISA's catalog by CVE id. It was read from a field the per-system advisories never carry, so the KEV check passed for every system and no CVE showed as exploited.
- The header KEV count and the severity summary ended early (KEV 0, 25 of 686 advisories) when one local advisory entry had no CVE list; each row is handled on its own now.

## 5.6.294 (2026-10-08)

### Added
- ONTAP release highlights are built from docs.netapp.com What's new pages by ARIA itself (`tools/ontap_release_notes.py`).
- ARIA's scanner data is applied over `data/reference_library.js` at load (release list, EOA dates, IMT versions, switch firmware baselines, release highlights), so a fresh install does not start with empty tables.
- Harvest guard: three attempts at the watchlist lookup; customers and sites lost in a result that dropped 10% or more are kept from the previous harvest; warnings are shown in Settings > Data & Sync.

## 5.6.293 (2026-10-08)

### Fixed
- The reference refresh message states how long each part takes (the knowledge-base crawl can take an hour).

## 5.6.292 (2026-10-08)

### Added
- Settings > Data & Sync: Reference Data & NetApp Library card with the age of every reference source, a stale warning, a refresh-everything-now button, and a keyword search over the NetApp Reference Library folder (auto-detected on Windows and macOS or set by path; read-only; no AI, no network, no sign-in). New `tools/library_manager.py`.

### Fixed
- The browser's release list came from a cache row that never expired (no ONTAP 9.19.1 for weeks); the newer of the cache and the scanner's file is used.
- The enrichment and auto-refresh schedulers were locals of `main()`, so handlers saw none (status "disabled", manual scan failed). They are module-level now, and a manual refresh ignores the fresh-file skips.

## 5.6.291 (2026-10-07)

### Changed
- The Customer Report lifecycle table uses the same-line upgrade target like every other document; the per-row upgrade note is short, with one explanation under the roadmap heading.

## 5.6.290 (2026-10-07)

### Changed
- Fixes for bugs, vulnerabilities and other findings default to a P-release on the release line the system runs; findings with no published fix name the newest known release on that line.

## 5.6.289 (2026-10-07)

### Changed
- Upgrade targets stay on the release line the system runs (newest known release on it), with Active IQ's cross-line recommendation shown as an option. Out-of-support lines still use Active IQ's target.

## 5.6.288 (2026-10-07)

### Changed
- Word tables: MET and MISSED are coloured in the SLA matrix, columns are never narrower than their longest unbreakable word, and the risk-age section has a Longest open heading. Checked by regenerating all documents for one customer and opening them in Word.

## 5.6.287 (2026-10-07)

### Changed
- Swept the other documents for column layouts that Word showed as headings and plain lines. The SLA compliance matrix, the portfolio benchmark and the Handover propensity list are tables, and a column header directly above its rule line is no longer read as a sub-heading.

## 5.6.286 (2026-10-07)

### Changed
- The SVM and LIF section's Per-System Summary is one table (System, SVMs, LIFs, Protocols, Health) with one row per system. It was a line of text per system, which Word turned into a mix of bold headings and shaded blocks. In Word reports the Health column is colour-coded: green for healthy, amber for non-homed LIFs, red for LIFs down or degraded.

## 5.6.285 (2026-10-07)

### Changed
- Recommendation scores in the Word reports are bold and colour-coded with the same bands as the on-screen view: green from 80%, amber from 50%, red below. This covers the '[Score N%]' tags beside each recommendation, the 'Active IQ score N%' line in each finding, and the Score column of the TAM Recommendations summary table.

## 5.6.284 (2026-10-07)

### Fixed
- NetApp advisory data is refreshed only when NetApp changes it. Each stored advisory remembers the date NetApp last updated it; the daily index of NetApp's advisories carries the current dates, and only advisories that are new or whose date differs are fetched again. Before, an advisory was stored once and never refreshed, so a fix or severity NetApp added later would never have appeared.
- The advisory loader retries (up to five times, 30 seconds apart) when the server is still starting or unreachable, instead of giving up until the next page load.

## 5.6.283 (2026-10-07)

### Fixed
- The shelf-module firmware table (IOM, NSM, PSM, ESM) is retired. It disagreed with Active IQ for every module (IOM12 0260 against Active IQ's 0412). A module's recommended release is now Active IQ's own figure for that system, and 'not reported' when Active IQ gives none. Switch firmware baselines are unchanged.
- NetApp's manufacturing test units (systems named MFG_TEST_..., one with a ship date in 1900) that Active IQ lists under a customer are left out of every list and total; they are not the customer's systems.
- A system that does not report ARP or HA status is no longer counted as a pass. It leaves that check's total, so 'ARP 6/6 (applicable)' means six systems confirmed on, and the single-system checklist shows 'not reported' instead of OK.
- The reporting tables mirror a system once even when two Active IQ accounts both report it (38 systems were counted twice), and a recorded age outside 0 to 30 years (one system had -7,973) is stored as unknown.
- Data files nothing reads (the tam_* and firmware probe files and the advisory database backup) were moved to data/archive_unused instead of sitting beside live data.

## 5.6.282 (2026-10-07)

### Fixed
- Data audit against NetApp's own sources. ARIA now downloads NetApp's complete advisory index each day (about 4,500 advisories, mapped CVE to advisory) and every advisory a finding names, so any finding or advisory entry that names a CVE is checked against the real advisory, whatever its source. Hand-entered rows are replaced by the real advisory's title, severity and CVSS score, or dropped when no NetApp advisory backs them: 9 advisory IDs in the local database do not exist, 6 rows paired a CVE with the wrong advisory, 15 rows had invented IDs and a generic link, and the reference library's own advisories included three CVEs NetApp has no advisory for (CVE-2025-27082, CVE-2025-22399 and a Microsoft CVE, CVE-2026-20833) and one (CVE-2024-50379) whose real advisory affects only the HCI compute node, not ONTAP.
- Findings ARIA builds itself from its reference library are kept only when NetApp's advisory names ONTAP (or the system's own software) as affected, so an advisory that names no product yet no longer produces a finding on every system (852 systems for CVE-2026-4747).
- End of availability: the finding named the platform 'ONTAP' instead of the model and fired for dates still in the future. It now names the model (for example 'Platform AFF-A800'), and the checklist's hardware row uses Active IQ's own date for each system first; the hand-compiled table disagreed with Active IQ on most models and omitted several.
- Active IQ Talking Points are a table, one row per system (age, highest-use aggregate, cluster capacity, system capacity, next best action) instead of one long stream of sentences. Active IQ quotes a system's age in two places and the figures can differ (0.93 and 1.13 years for one system): when they differ the age shows as Active IQ's rounded age with both figures, so one system no longer has two ages.
- Knowledge-base links: 277 of 854 were pages NetApp does not serve (205 'gap analysis' links and 9 'feature' links were addresses the scanner guessed). They are removed, gap-analysis entries point at the real Interoperability Matrix Tool, and a feature page is added only when NetApp serves it.
- Remediation Tracker: open, untouched items for findings Active IQ no longer reports (the tracker held 6,653 from one import in August, 220 citing advisories NetApp does not publish) are left out of the list and figures, with a 'No Longer Reported' count.

## 5.6.281 (2026-10-07)

### Fixed
- Findings ARIA made up are no longer listed. ARIA's reference library produced its own 'Security' findings (a version range matched against hand-written advisories) and its own platform end-of-availability finding, and added them to every system in range alongside what Active IQ reported: about 4,100 security findings on 898 systems in the largest fleet. 513 cited advisories NetApp does not publish, 465 were for releases that already have the fix, and the end-of-availability note duplicated Active IQ's own on systems where Active IQ reports it. A finding Active IQ did not raise is now kept only when a real NetApp advisory confirms it for the installed release; the documents say how many were left out.
- Advisory entries built from a finding that is no longer listed go with it (Breede Valley, for example, still cited three advisory IDs NetApp does not publish).
- A finding with no published fix names the system's single upgrade target even when Active IQ reports no recommended release. One report said 'upgrade to a release that contains the fix' for a system whose other documents said 9.15.1P20.
- 'Total Risks' in the Handover Brief and Security Brief now says how many best-practice findings it leaves out, so it no longer reads as a different total from the best-practice count elsewhere.

## 5.6.280 (2026-10-07)

### Fixed
- Findings that Active IQ last reported more than two weeks ago, on a release that already contains the fix, are hidden as resolved by an upgrade (50 findings on 28 systems in the largest fleet). The documents say how many were left out. Findings with a recent date, or no date, stay listed under the 'check in Active IQ' action.
- Security Advisories reports name each advisory by its NetApp ID with the CVEs it covers (for example 'NTAP-20260610-0001 (9 CVEs: ...)') and say '2 advisories covering 10 CVEs' instead of '2 advisories' above a list of 10 CVE numbers. Entries that were labelled 'N/A' or with an Active IQ risk number ('NTAP-3709') now show the real advisory ID or title.
- Knowledge-base and bug notices (for example the PFC and NVMe deallocate notes) are listed as notices, separate from security advisories, in the Security Advisories report and its summary counts.
- An advisory entry with no advisory ID is looked up through its CVE, so it gets the same fixed-release or workaround line as every other finding instead of generic text.

## 5.6.279 (2026-10-07)

### Fixed
- Advisories that do not exist: the local advisory database held hand-entered rows with advisory IDs that NetApp does not publish (they return 'not found'), with placeholder ranges ('9.0 to check advisory') that matched every system. Nine such IDs produced about 3,100 system-advisory entries across the fleet (one, 'Intel Ethernet Controller Info Disclosure', on 832 systems). ARIA now checks every database advisory against NetApp's own advisory service and drops those it cannot find; the documents say how many were left out.
- Impossible capacity figures: used capacity above 100% (for example '809% used', '-709% free') came from physical-used compared with usable capacity, two figures that do not always describe the same thing. Headroom, the used-capacity lines and the runway now use Active IQ's own utilisation figure first, and a computed figure that is not between 0 and 100 is not printed. Systems at 6% used no longer appear in the red capacity zone with no runway.
- 'Up to date' and 'needs an upgrade' no longer contradict each other: a system counts as on a current release for the OS Currency figures and the checklist only when NetApp's advisories also need no newer release (43 systems Active IQ called up to date still had fixes available in a later release). The checklist row names the release needed.
- Findings that Active IQ still reports although the installed release is at or beyond the fixed release (731 findings on 525 systems in the largest fleet) are one 'check in Active IQ' action instead of being counted as upgrade work, and each says Active IQ still reports it.
- ARIA's own stock sentence ('Upgrade to ONTAP x which includes the patch') is no longer quoted as the recommended action.

## 5.6.278 (2026-10-07)

### Fixed
- Advisories matched to a system by software version are no longer listed when the installed release already contains the fix. The local advisory database holds some entries with a placeholder range ('ONTAP 9.0 up to current, check advisory'), which made every ONTAP version look affected, so systems on 9.16.1P13 were listed for fixes released in 9.16.1P4. ARIA now compares the installed release with the fixed releases in NetApp's own advisory (fetched automatically) and drops those advisories. The documents say how many were left out and why. Findings that Active IQ itself raised stay listed and say what to confirm.

## 5.6.277 (2026-10-07)

### Added
- Every failing row of the Operations & Security and Data Protection & Lifecycle checklists (Value & ROI tab) opens when clicked and lists every system that fails the check, with the value that fails it (installed and target release, percent free, days left on the contract, open case counts, and so on). Before, only two examples and a '+N more' count were shown.
- Commit hooks: a commit-msg hook removes, and the pre-push hook refuses, any commit that lists an AI assistant as author or co-author.

## 5.6.276 (2026-10-07)

### Fixed
- One upgrade target per system, used by every document. The highest of the minimum fixed releases of a system's findings, each taken on the branch it runs, is the system's target (for example 9.16.1P9 instead of separate actions for 9.15.1P16, 9.15.1P19, 9.15.1P20 and 9.16.1P9). The Corrective Actions in the Email, Handover, MSP, QBR, Problem Statements, Solution Proposal, Success Plan and Risk & Remediation documents, the Security Fix Floor, each finding's resolution line, the Security Brief CVE matrix and the OS Upgrade Roadmap all state that same figure. Active IQ's recommended release is shown beside it as a separate, labelled figure.
- A finding with no published fix no longer proposes a different upgrade than the system's target: it names the target and says Active IQ's recommended release separately.
- Security Fix Floor is stated per product line (ONTAP, SANtricity OS, StorageGRID) instead of one 'highest requirement' across products, and the cross-site parity figure is labelled as the highest of Active IQ's recommended releases.
- 'Systems' means the systems Active IQ monitors in every document. StorageGRID nodes named only by a grid's node list are stated beside the count, not added to it (the Sales Proposal and Security Brief used to say 11 where other documents said 8).
- Advisories named by a system's own advisory list are fetched too, so no document prints 'None at this time' as the fix for a CVE; database text that is itself an upgrade instruction is no longer labelled a workaround.
- The Prioritized Technical Risks and Security Advisories reports state how many findings were left out as not applicable and show the recommended action per issue. A remediation plan with no steps from Active IQ is built from the resolution and the guidance it links instead of showing an empty list.

## 5.6.275 (2026-10-07)

### Added
- Every risk, CVE and advisory now carries a one-line RESOLUTION for the system it was raised on, worked out by the engine and shown in the Risks view and its remediation dialog, the Security Posture Brief and CVE matrix, the Technical Risks and Security Advisories Word reports, the Top Corrective Actions, change tickets, implementation plans, success plans and the configuration and best-practice findings. Examples: 'Upgrade ONTAP to at least 9.12.1P19 (now 9.12.1P12)', 'Workaround: Disable remote login', 'Update disk firmware', 'Plan a hardware refresh'. It uses the minimum fixed release on the system's own branch, the NetApp advisory's published workaround for the product that system runs, and Active IQ's own fix data, in that order.
- Advisory data is fetched automatically: the server reads each NetApp advisory a finding refers to (affected products, fixed releases per product, workaround) from NetApp's advisory service in the background, caches it (data/advisory_resolutions.json) and serves it at /api/advisory-resolutions, so a new advisory is handled the day Active IQ raises it. How products are matched and worded is in resolution_rules.json (a copy in data/ overrides it); edit it and reload the page, no restart and no code change.
- Findings that do not apply are left out. Active IQ attaches advisories that list only Unified Manager, HCI or other products to ONTAP controllers (28% of the ONTAP findings in the largest fleet checked, and most StorageGRID ones). They move to a not-applicable list, stop counting in scores and documents, and each document that is affected says how many were left out and why.
- Word reports: the Security Brief fix lines are separate labelled rows (Fixed In, Upgrade To, Workaround) instead of one paragraph, and the Word styles know the new Resolution and Workaround labels.

## 5.6.274 (2026-10-07)

### Fixed
- StorageGRID appliance nodes carry the appliance model from the grid node list (SG5860, SG5712, SGF6024, ...) in every deliverable, report, ticket and table. Active IQ's storage controller model (4000, 2806, 5700) is kept as the controller model; nodes Active IQ files as E-Series keep their E-Series analysis.

## 5.6.273 (2026-10-07)

### Fixed
- The model badge beside the rear-panel title showed the storage controller model (4000, 2806, 5700) for StorageGRID appliance nodes; it now shows the appliance model from the grid node list (SG5860, SG5712, SGF6024, ...).

## 5.6.272 (2026-10-07)

### Fixed
- SGF6024 appliances had no rear panel; they are now drawn as an SG6000-CN plus two EF570 storage controllers, with the interconnect diagram.
- Software nodes (VMware, KVM, bare metal) say so instead of "appliance model not identified"; a storage controller whose grid is not in scope says why the model is unknown.
- Every appliance model in the live fleet (SG1000, SG5712, SG5760, SG5812, SG5860, SG6060, SG6160, SGF6024) was checked against its drawing.

## 5.6.271 (2026-10-07)

### Fixed
- A StorageGRID storage node was drawn as a bare E4000 (or E2800) controller canister. Active IQ reports the appliance's storage controller as its own system (model 4000 / 2806); the rear panel and port view now use the appliance model from the grid's node list (SG5712, SG5760, SG5860, SG6060, ...).

## 5.6.270 (2026-10-07)

### Changed
- The sidebar footer is one horizontal line: ARIA, version, signed-in user and Sign out side by side (wrapping only when the sidebar is too narrow).

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
