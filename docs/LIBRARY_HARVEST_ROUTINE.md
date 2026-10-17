# Library harvest routine

A weekly routine that brings what the NetApp Reference Library (and a few direct searches) learned into ARIA. ARIA itself never uses AI: this routine
is a maintenance job, run by Claude Code on the development machine, whose only output is ordinary, reviewable changes to ARIA's data files, rules
files and code. What ships contains no AI.

Run it from the repository root. Follow `CLAUDE.md` for the release workflow; its rules
win over anything here.

## What ARIA now does by itself (reference updater, `tools/library_updater.py`)

Sections 1 and 3 below used to be done by hand. ARIA now runs them in its own engine, with no AI: the scheduler starts a sweep four minutes after
start-up and then every 24 hours (`libraryUpdateEnabled`, `libraryUpdateIntervalHours`, `libraryUpdateBudget` in `aiq_config.json`); Settings > Data &
Sync > Reference updater has "Sweep now"; `python tools/library_updater.py [--budget N]` runs one from the command line.

| Step of this routine | Done by ARIA |
|---|---|
| 3. Check each topic against the official source | Reads the key pages every run (release lists, What's new pages, end-of-availability, TR indexes, advisories) and the stalest of the other pages the library's documents name in their `Source:` line (the list ships in `tools/library_sources.json`, so a machine without the library folder sweeps too). One request a second, public pages only. |
| Compare with what ARIA holds | A newer release number than the last read, new KB / CVE / advisory ids, or added and removed lines. Each id and release is looked up in ARIA's own data: held ones are "covered", the rest go to the review queue. |
| Apply what a scanner can apply | A change to a release, end-of-availability, advisory or What's new page runs the existing scanners at once (version catalogue, EOA, advisories, release notes). |
| 1. Read the library's new CHANGELOG entries | Ids and releases in each unseen entry are checked the same way; an entry that says "no material changes" and names nothing ARIA lacks is recorded as harvested by itself. |
| Say what is out of date | Settings shows each curated reference table (`data/reference_library.js`) as kept up to date by a scanner, partly by a scanner, or by hand; for the by-hand ones it lists the official pages that changed since the file was compiled. A copy of every page read is kept in `data/library_refreshed/` and is searchable next to the library. |

What stays for a person (or for this routine, run by Claude Code): the **review queue** (`data/library_update_queue.json`, shown in Settings, or
`python -c "import sys;sys.path.insert(0,'tools');import library_updater as u,json;print(json.dumps(u.status('.')['queue'],indent=1))"`). Items are a release ARIA
does not hold, ids ARIA has no rule for (with a rules stub), a key page whose text changed, a source that stopped answering, or a library entry that names something ARIA lacks.
Sections 2 and 4 below still apply to those items: the updater never writes a compatibility range, a prose best-practice fact or a new kind of check.
Close an item in Settings ("done, close it") once it is dealt with.

## 0. Ground rules

- **Nothing invented.** Add only what a source states. Where the library says a fix version is behind the support login, ARIA says so too.
- **Every added entry carries `source`**: where it came from and the date (for example "NetApp KB CFBMC-8277, recorded in the NetApp Reference Library on 2026-10-08").
- **A search summary is not evidence.** Several WebSearch summaries have been wrong (a Nutanix GA date, a Trident Protect version, a stale DR page date). Confirm a
  fact on the vendor page itself (direct fetch) before it goes into ARIA. If it cannot be confirmed, record it as rejected in the report.
- **No customer data, ever.** No customer names, system names, serial numbers or addresses in any file, commit message or report that is committed.
- **Do not guess compatibility ranges.** The minimum and maximum ONTAP release of an integration version come from NetApp's interoperability matrix (sign-in
  needed). Without it, ARIA lists the newer version as "ahead of the table" and a person fills in the range.
- Never use `--no-verify`; never add a Claude or Anthropic credit to a commit or pull request; stop and report if the sensitive-data guard objects.

## 1. What is new in the library

```
python tools/library_manager.py --unharvested
```

prints every `CHANGELOG.md` entry of the library that is not yet recorded in `data/library_harvest_state.json`. Read each one in full. If the command says
the library folder was not found, set `libraryPath` in `aiq_config.json` (or `ARIA_LIBRARY_PATH`) and stop if it still fails.

## 2. Where each kind of fact goes

| What the library (or a source) states | Where it goes in ARIA |
|---|---|
| A known issue of a firmware version (BMC, SP, shelf module, drive) for a model family | `resolution_rules.json` > `firmwareKnownIssues` (`id`, `component`, `families`, `versions` or `minVersion`, `summary`, `note`, `url`, `source`) |
| A known issue of a network or I/O card's firmware (part number, model families, firmware version) | `resolution_rules.json` > `firmwareKnownIssues` with `component: "CARD"`, `cardPartNumbers`, `cardLabel`, `families` (exact family names), `versions`; the adapter inventory check (`_cardFwKnownIssues`, `_dfCardFwSummary`) reads it, in the installed-cards table and the Firmware Currency deliverable |
| A known issue of one upgrade path (from release, to line) | `resolution_rules.json` > `upgradePathKnownIssues` |
| A newer current SP/BMC firmware version for a model family | `data/firmware_baselines.json` > `spBmc` (`byModel` and `families[].latestKnown`); only ever upward |
| A newer release of a NetApp-owned integration (Host Utilities, ONTAP tools, SnapCenter, Trident, Harvest) | Nothing by hand: `tools/netapp_docs_versions.py` and the GitHub scan read it. If the product has no source yet, add one to `SOURCES` in `tools/netapp_docs_versions.py` |
| A newer release of a third-party product (Veeam, vSphere, Proxmox, ...) | `tools/netapp_docs_versions.py` `JSON_SOURCES` if endoflife.date lists it; compatibility ranges only if the library quotes NetApp's own statement, then `data/imt_interop.json` `versions` with a `source` |
| A new end-of-availability platform or switch | Nothing by hand: `tools/eoa_list.py` reads NetApp's page. Check that it picked it up |
| A new security advisory | Nothing by hand: the advisory scan reads both lists. Check by id that ARIA has every advisory the library names (`data/security_bulletins.json`) |
| A release-note fact (default changes, removed features, new requirements) | Nothing by hand: `tools/ontap_release_notes.py` and `tools/derived_reference.py` read the What's new pages. Only a fact that is not on those pages goes in the local `data/reference_library.js` (not in the repository) |
| A change in a best-practice document (a Technical Report revision, ARP or MAV behaviour) | A line in `docs/` or the local reference file; record the revision number and date |
| A change that needs new logic (a new kind of check) | Build it in the same run, without asking (owner, 2026-10-11): rule in the rules file, check in app.js, shown in the report that already carries that kind of finding, tested on the real fleet and with a simulated hit, then released. Only a change that needs a decision (a design choice, a compatibility range) goes to the report as a proposal |

## 3. Searches beyond the library

Check each topic against the official source directly (docs.netapp.com, kb.netapp.com, security.netapp.com, the vendor's own release pages), compare with what
ARIA holds, and apply section 2 for any difference:

1. **ONTAP** releases and P-releases: `docs.netapp.com/us-en/ontap/release-notes/release-support-reference.html`; compare with `data/version_catalog.json` and `data/derived_reference.json`.
2. **Security**: new NetApp advisories and CISA KEV additions that name NetApp products; compare ids with `data/security_bulletins.json` and `data/cisa_kev.json`.
3. **Firmware**: the ONTAP Hardware Issues KB index (`kb.netapp.com/on-prem/ontap/OHW/OHW-Issues`): new BMC, SP, BIOS, shelf-module and disk firmware articles and their known-issue articles.
4. **Platforms**: `docs.netapp.com/us-en/ontap-systems/whats-new.html` and the end-of-availability page.
5. **Other NetApp software**: StorageGRID, SANtricity, SnapCenter, Trident, ONTAP tools, Host Utilities, Active IQ Unified Manager, Cloud Volumes ONTAP: what's-new pages.
6. **Best practices**: the Technical Report indexes (security hardening TR-4569, NFS, SAN, SnapMirror, MetroCluster), ransomware protection and multi-admin verification pages.
7. **Interoperability**: switch firmware pages (`ontap-systems-switches`), Host Utilities, VMware, Veeam, Commvault, Proxmox, OpenStack release notes.

Keep this list current: add a topic when the library gains a category.

### Procedures that are missing (`playbook-gap` items)

Reading NetApp's pages: `docs.netapp.com` answers HTTP 403 to requests that identify themselves as an AI fetch tool (a plain `curl` and ARIA's own updater get the page), so read pages with the updater's reader, which says honestly what it is: `python -c "import sys; sys.path.insert(0,'tools'); import library_updater as lu; t,e=lu.http_get(URL); print(lu.html_to_text(t)[1])"`. Search engines give the page addresses.

The review queue (`data/library_update_queue.json`) holds `playbook-gap` items: kinds of finding in the fleet that have no remediation procedure, largest first (the same list is in Settings > Data & Sync > Procedure coverage). For each one, as far as the time allows:

1. Open the NetApp page the item links and the pages it cites. Write the procedure **only from the documentation**: every command, option and menu path must be on the page. If a step cannot be confirmed, write "see the linked page" instead of a guess.
2. Add an entry to `data/playbooks_local.json` with `"status": "draft"`, in the format of `docs/PLAYBOOKS.md` (family, match, vars, cause, impact, steps, options, ticket with rollback, sources). Keep ONTAP commands out of E-Series and StorageGRID entries.
3. Run `python tests/run_tests.py`: an invalid entry is reported by `tests/test_playbooks_data.py`. Then run `python tools/playbook_verify.py --promote`: a draft that is valid and whose every command and menu path is verified against NetApp's documentation is approved automatically (the owner's standing instruction); one that fails stays a draft and the command says why: fix it from the page.
4. Say in the report which gap items now have a draft, which could not be written, and why.

## 3b. Refresh the copy that ships with ARIA

The NetApp Reference Library ships with ARIA in `reference/netapp-library/`. When the external library (the folder this routine reads) has changed, run `python tools/dev/sync_library.py --check`; if it reports changes, run it without `--check`, then include "library copy refreshed" in the release. The script leaves out the maintenance log and failed-fetch lists, removes a personal first name and e-mail addresses, and the sensitive-data guard checks the result. Never edit `reference/` by hand.

## 4. Check, release, record

1. `node --check app.js`, `python -m pyflakes server.py tools/*.py`, `python tests/run_tests.py`; if any code changed, a smoke run generating the deliverables.
2. If anything in the repository changed: bump the version, run the guard (`--tree HEAD`, `--history`), commit and push exactly as `CLAUDE.md` says. If nothing changed, do not release.
3. `python tools/library_manager.py --mark-harvested --note "<one line>"`.
4. Write `data/library_harvest_report.md` (local, not committed): date, entries read, what was added and where, what was rejected and why, what needs a person.
5. If anything in the report needs a person (a compatibility range, a new kind of check, a failed guard), say so first in the final message.

## 5. If it cannot run unattended

A permission prompt, a missing library folder or a failing check ends the run: leave the repository unchanged and write the reason into the report. The
Settings > Data & Sync card in ARIA shows how many library entries are not yet harvested, so a stalled routine is visible.
