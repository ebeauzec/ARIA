# Where ARIA's data comes from

ARIA's repository contains **no third-party or proprietary data**: it is source code and documentation only, and the demo data is fictional. Everything ARIA shows is retrieved at run time, on the machine that runs it, from one of three places:

1. **Your own Active IQ account**, through NetApp's Active IQ API, with your own credentials.
2. **Public sources** that anyone can read without logging in (listed below).
3. **Files you provide yourself** (an AutoSupport export, a StoragePerf export or instance, an optional local reference file).

What is retrieved is stored only on that machine (the cache database and the `data/` folder) and is never committed to the repository. See [data/README.md](../data/README.md).

The Active IQ API is **not** open source and **not** freely available: it is NetApp's service, it needs a NetApp account and a refresh token, and the data it returns about your systems belongs to NetApp and your organisation. ARIA only reads what your own token is allowed to see. Every other source below is public. The terms of use of each source apply to the use you make of it; check them before you share anything ARIA retrieves.

## 1. Active IQ (your account)

| What | Where it is defined | How |
|---|---|---|
| Fleet inventory, contracts, support dates, firmware, capacity and efficiency, volumes and LUNs, risks and cases, renewals, Success Plans, health scores, OS version catalog, monthly uptime / ARP / risk history, aggregate capacity forecasts, risk metadata, risk first-raised dates and fixing versions, risk counts by severity and impact area, support case counts and trend, forecast power and carbon, used capacity split into NAS / SAN / snapshots, aggregate RAID and storage types, workloads, StorageGRID capacity forecast, ONTAP feature usage, case resolution / bugs / replacement parts | [`api_queries.json`](../api_queries.json) (every query and endpoint) | GraphQL `https://gql.aiq.netapp.com/graphql` |
| Token exchange and the watchlist list | `api_queries.json`, section `rest` | REST `https://api.activeiq.netapp.com` |
| Write-back actions (acknowledge a risk, update a Success Plan, set a qualified version) | `api_queries.json`, entries of type `mutation` | Only after you confirm; administrators only when sign-in is on |

**The API reference.** ARIA's Active IQ queries are developed and maintained using the public Active IQ GraphQL schema reference published on Apollo GraphOS Studio ([ActiveIQ-Graph-Prd-API, variant `current`](https://studio.apollographql.com/public/ActiveIQ-Graph-Prd-API/variant/current/schema/reference)). They are kept in one JSON file, `api_queries.json`, which the engine reads when it starts; the program itself contains no query text. Every query is validated against the reference with `python tools/validate_api_queries.py`, and newer fields (monthly statistics, risk metadata, per-volume settings, aggregate forecasts, contact roles) are chosen from it. The last result is recorded in the file under `schema_reference`. No copy of the schema is stored in the repository.

## 2. Public sources (no login)

| Source | Used for | Code |
|---|---|---|
| **CISA Known Exploited Vulnerabilities catalog** (cisa.gov JSON feed) | Flags vulnerabilities that are being exploited | `server.py` `_scan_cisa_kev` |
| **NIST National Vulnerability Database** (NVD API 2.0, services.nvd.nist.gov; a free API key is optional and raises the rate limit) | CVE scores and descriptions | `fetch_cve_nvd`, `_scan_nvd_netapp` |
| **FIRST EPSS** (api.first.org) | Exploit-probability scores | `_scan_epss` |
| **NetApp security advisories** (security.netapp.com, public advisory index) | Which advisories affect which ONTAP versions | `_scan_netapp_psirt`, `tools/reference_harvester.py` |
| **NetApp Knowledge Base** public articles (kb.netapp.com, the structured data the pages publish) | Operational bug articles and links | `_scan_knowledge_base` |
| **NetApp product documentation** (docs.netapp.com, discovered through its published sitemap) | Release notes and the version catalog, platform hardware (slots, ports), end-of-availability notices, upgrade information, switch software versions | `_scan_version_catalog`, `_scan_hardware_docs`, `harvest_eoa_announcements`, `_scan_sitemap_discovery`, `hw_docs_harvester.py` |
| **GitHub** public repositories and releases (the NetApp organisation's open-source projects such as Trident and Harvest, and the documentation repository); an optional personal token with no permissions raises the rate limit | Latest versions of integrations and documentation structure | `tools/firmware_harvester.py`, `hw_docs_harvester.py` |
| **PyPI** (the public netapp-ontap package page) | Latest ONTAP library version | `harvest_ontap_pypi` |
| **endoflife.date** (open data) | ONTAP release lifecycle; the newest released Veeam, Proxmox VE and vSphere versions | `harvest_ontap_endoflife`, `tools/netapp_docs_versions.py` |
| **Derived reference tables** (computed locally from the advisory, release-note, end-of-availability, hardware and fleet data above) | Latest release per ONTAP line, minimum safe release per line, current platforms, upgrade caveats and MetroCluster feature versions | `tools/derived_reference.py` (rules stated in its header) |
| **NetApp documentation pages read by ARIA's own scrapers** (docs.netapp.com) | ONTAP release highlights (What's new pages), the end-of-availability platform list, the newest Host Utilities and SnapCenter versions | `tools/ontap_release_notes.py`, `tools/eoa_list.py`, `tools/netapp_docs_versions.py` |
| **Public integration pages** (for example the Ansible Galaxy and Terraform registry pages of NetApp's own collections, and the Harvest site) | Latest versions of NetApp integrations | `server.py` reference scanner |

Notes:
- The advisory, knowledge-base and documentation pages are NetApp's published content. ARIA reads facts from them (versions, dates, identifiers) and keeps them in your local cache; it does not republish the pages.
- ARIA does **not** query the NetApp Support site (mysupport.netapp.com) or any page that needs a sign-in. The Bugs Online lookup that once pointed there is switched off.
- The scanners run on a schedule you control in Settings > Data & Sync. The documentation sitemap discovery only reads the sitemap that the site publishes and skips the language sections its robots.txt asks crawlers to avoid.

## 3. Files you provide

| Input | Used for |
|---|---|
| **AutoSupport exports** you import (Action Planner, offline import) | Per-system detail for systems that are not reachable through Active IQ |
| **A StoragePerf instance or export** you connect (Settings > StoragePerf) | Measured performance next to the Active IQ view |
| **A disk-qualification package file** you place in `data/` (optional) | Drive firmware baselines. ARIA does not download it |
| **A NetApp Reference Library folder** (optional, read-only) | Searchable from Settings > Data & Sync, with its freshness shown. ARIA finds the folder itself (config `libraryPath`, environment `ARIA_LIBRARY_PATH`, or the usual Google Drive locations on Windows and macOS) and only reads it; whatever maintains the folder keeps it current. No sign-in, no network, no AI |
| **`data/reference_library.js`** (optional, local) | Hand-kept reference tables (platform replacements, upgrade caveats, best practices). ARIA's own scanner data is applied over it, so a machine without the file still gets the release list, end-of-availability dates, interoperability versions, switch firmware baselines and ONTAP release highlights |
| **Settings** | Your Active IQ tokens, SLA policy, notification webhook, subgroups |

## What ARIA does not use

- No data from a paid or licensed third-party data provider.
- No data from NetApp internal or partner-only tools.
- No AI or machine-learning service: all analysis is deterministic code that runs locally.
- No telemetry: ARIA does not send your data anywhere except the Active IQ API calls you configure and the optional webhook you set.

## Where it is stored

On the machine that runs ARIA: `aiq_config.json` (tokens and settings), `aiq_cache.db` (the cache and history), and `data/` (reference data). In a container this is the one volume (`/var/lib/aria`); see [DEPLOY.md](DEPLOY.md). The `.gitignore` and the pre-commit and pre-push checks (`tools/guard_sensitive.py`) keep all of it out of the repository.
