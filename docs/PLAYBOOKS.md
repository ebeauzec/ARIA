# Remediation playbooks as data

A playbook is the procedure for one kind of finding: the cause, the impact, numbered steps with the exact commands (or menu paths), the options, and the NetApp pages it was written from. ARIA fills in the names of the system the finding is on, so the steps read as written for that system.

Procedures live in two places:

* **Data files** (this document): `tools/playbooks.json` (shipped) and `data/playbooks_local.json` (yours, never overwritten by an update). A new entry applies on the next load of the fleet, with no new release.
* **Code**: `_remedPlaybook` in `app.js` (the first ~35 ONTAP procedures, written before this existed). A data entry whose `match` fits a finding is used first, so a data entry replaces a code procedure; new work goes in data.

## How ARIA finds out what is missing

After every load of the fleet the front end counts the findings that got no procedure and reports them (`POST /api/library/playbooks/gaps`). They are kept in `data/playbook_gaps.json` and shown in **Settings > Data & Sync > Procedure coverage** (percentage covered, the kinds of finding with none, drafts waiting for approval, entries that are invalid). The 25 largest are also added to the reference updater's review queue as `playbook-gap` items, which is how the weekly maintenance job (`docs/LIBRARY_HARVEST_ROUTINE.md`) learns what to write. A kind of finding that gets a procedure leaves the record and its queue item closes by itself.

ARIA never writes a procedure itself and never fetches one at run time; it runs unchanged where no AI and no internet are allowed. Procedures are written by a person or by the maintenance job from NetApp's documentation. They are approved automatically (the owner's standing instruction): a draft becomes approved as soon as it passes every automatic check below (valid, and every command and menu path checked against NetApp's documentation); one that fails stays a draft, with the reasons.

### Only public information

A procedure may cite and quote only pages that anyone can open without an account (docs.netapp.com, kb.netapp.com, security.netapp.com and the like). Nothing from NetApp's customer-only areas goes into a procedure, a document, the library or a commit message: no bulletin, customer-notice or engineering-change ids, no links into the support portal, no wording that points to customer-only content. `tools/guard_compliance.py` holds the rules; `validate()` refuses a procedure that breaks them, the commit and push checks (`tools/guard_sensitive.py`) stop any file or commit message that does, the library sync removes such links, and every generated document drops the ids. Where a finding itself carries such a reference, the procedure says "read the corrective action in the finding".

## Adding one

1. Open the `playbook-gap` item in the review queue (or Settings > Data & Sync > Procedure coverage) for the finding, and the NetApp page it links.
2. Add an entry to `data/playbooks_local.json`:

```json
{
 "playbooks": [
  {
   "id": "ontap.example-setting",
   "status": "draft",
   "family": "ontap",
   "match": "example setting is not enabled",
   "vars": { "volume": "volume\\s+([A-Za-z0-9_.-]+)" },
   "minVersion": "9.11.1",
   "belowMin": { "cause": "This needs ONTAP 9.11.1; {cluster} runs {version}.", "steps": ["1. Plan the upgrade ...", "2. ...", "3. ..."] },
   "cause": "The example setting is off on {cluster}.",
   "impact": "What goes wrong if it stays off.",
   "steps": [
    "1. Check: volume show -vserver {svm} -volume {volume} -fields example",
    "2. Change: volume modify -vserver {svm} -volume {volume} -example true",
    "3. Confirm: volume show -vserver {svm} -volume {volume} -fields example"
   ],
   "options": ["Option A: ... (recommended)."],
   "thirdParty": "Anything outside NetApp that is affected.",
   "security": false,
   "ticket": { "risk": "Low", "window": "Any; no outage", "rollback": "volume modify -vserver {svm} -volume {volume} -example false" },
   "sources": ["https://docs.netapp.com/us-en/ontap/..."]
  }
 ]
}
```

3. Run `python tools/playbook_verify.py --promote`. A draft that is valid and fully verified against NetApp's documentation is approved by itself (`approvedBy` records it) and is used from the next load; one that is not stays a draft and the command prints why. The maintenance run at every session start does this too. You can also set `"status": "approved"` yourself.

### Fields

| Field | Meaning |
|---|---|
| `id` | 3-61 characters: lower-case letters, digits, `.` `-` `_`. A local entry with the id of a shipped one replaces it. |
| `status` | `approved` (used), `draft` (not used yet: it is approved automatically once it passes the checks; the coverage card lists the drafts that have not passed), `rejected` (a local `rejected` entry switches off the shipped one with that id). |
| `family` | `ontap`, `eseries`, `storagegrid` or `any`. A finding whose category names StorageGRID or E-Series/SANtricity counts as that product's even when its system record is classed by a model code. |
| `match` | A regular expression (case-insensitive) tested on the finding's title and detail text. Entries are tried in file order, shipped first. |
| `matchOn` | Optional: `description` tests the title only. |
| `vars` | Names to pull from the finding text: each value is a regular expression whose first group becomes `{name}`. |
| `cause`, `impact`, `steps`, `options`, `thirdParty` | The text. `steps` needs at least three numbered strings. |
| `minVersion`, `belowMin` | ONTAP only: below `minVersion` the `belowMin` text replaces the cause, impact and steps. |
| `security` | `true` lists it in the Security Brief's hardening procedures. |
| `ticket` | `risk`, `window` and `rollback` for the change ticket. Without it the ticket says low risk and "set it back with the same modify command". |
| `approvedBy`, `approvedAt` | Optional record of who approved the entry and when (informational; `status` is what the program reads). |
| `sources` | Required: the NetApp pages the procedure was written from; printed under the steps. |
| `groupKey`, `compact`, `advisoryRef` | For a procedure one upgrade serves for many findings (the advisories an ONTAP, SANtricity or StorageGRID upgrade closes): `groupKey` (for example `SANtricity upgrade to {target} (fixes security advisories)`) names the group the documents print once per system, `compact` is the one-line form shown in each finding's own plan, `advisoryRef` is the id listed for the system. |
| `noVerify`, `note` | Leave out the closing "confirm the finding clears" step; replace the closing note about syntax. |

Placeholders: `{cluster}`, `{node}`, `{svm}`, `{policy}`, `{version}`, `{model}`, `{ref}` (the advisory link), `{detail}` (the finding's own detail text), `{target}` (the release the finding asks for, "Upgrade to SANtricity 11.90R6", otherwise the release Active IQ recommends for the system), `{recommended}`, `{finding}` (the CVE or the NetApp advisory id), `{cve}`, `{advisory}`, and any name declared in `vars` (a regular expression tested on the finding's title, detail and recommendation). A value ARIA cannot find is printed as `<name>`, never guessed; `{name|text}` prints `text` instead when there is no value. A placeholder that is not declared makes the entry invalid (the coverage card names the problem).

## Checked against NetApp's documentation

`tools/playbook_verify.py` (no AI) reads each approved playbook and checks what it says against NetApp's own pages, and the result (`data/playbook_verification.json`) is used everywhere:

* **ONTAP commands** are looked up in the ONTAP command reference (`docs.netapp.com/us-en/ontap-cli/<command>.html`): the page must exist and every `-parameter` in the step must be on it.
* **Menu paths** ("Support > Upgrade center") in E-Series and StorageGRID playbooks must occur in the text of the NetApp pages the playbook cites (the reference updater keeps their text).
* Status per item: `verified`, `param-missing` (the playbook uses an option the page does not have: wrong, or changed), `not-found` (no reference page for that command, or the path is not on the cited pages), `unchecked` (the page could not be read). A playbook is `ok` when nothing is wrong and something was verified.
* A playbook whose items are all verified says so at the end of its steps ("every command ... checked against NetApp's ONTAP command reference on <date>") instead of asking the reader to confirm the options; Settings > Data & Sync > Procedure coverage shows the totals and what needs a person; the command pages join the page watch, so a change to a command's syntax raises a review item naming the playbook.
* It runs after every sweep (session start, the weekly job) or by hand: `python tools/playbook_verify.py` (`--refresh` reads the command pages again, `--offline` uses the cache, `--id ID` one playbook).

Entries are also checked when they are loaded (`tools/playbooks.py`, shown in the same card as "invalid"): the sources must be NetApp pages (docs, kb, security, www, support, interoperability and hardware universe hosts), an E-Series or StorageGRID procedure may not contain ONTAP commands, every placeholder must be declared, and the text may not name the tool.

## Rules for writing one

* Write from NetApp's documentation and put the page in `sources`. Do not write a command from memory: run `python tools/playbook_verify.py --id YOUR-ID` and fix everything it reports (the first run on the ONTAP procedures written before the check existed found thirteen wrong or missing commands and options, all corrected from the command reference). Where a menu path or option name cannot be checked, say "see the linked page" in the step instead.
* Commands are for the platform they run on: no ONTAP commands for E-Series or StorageGRID.
* Gate by release where a feature needs one (`minVersion`).
* Say how to check the state before changing it, how to change it, how to confirm, and how to go back (`ticket.rollback`), and where there is no way back, say that.
* Best practice is the standard: if NetApp's guidance and the finding's own recommendation differ, follow NetApp's published guidance and say so in `thirdParty`.

## Tests

`tests/test_playbooks_data.py` covers loading, approval, validation, the gap record and the data engine; `tests/test_playbooks.py` covers the procedures written in code. Both run under `python tests/run_tests.py` (the engine tests need node).
