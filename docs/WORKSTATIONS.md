# Working on ARIA from more than one workstation

The development of ARIA can be carried on from several machines that share one project folder (a folder that is synchronised between the machines, or on a network share). That folder is the whole project: the code, the git history (`.git`), the private working notes (`CLAUDE.md`, `.claude/`), the development tools (`tools/dev/`) and the harvested data (`data/`, `aiq_cache.db`). A second workstation that opens the same folder picks up exactly where the first stopped. This page says what that depends on and what to do so it stays safe. If each machine has its own clone instead, none of this applies: use `git pull` and `git push`.

## What travels with the folder, and what does not

| Travels (it is in the folder) | Stays on each machine |
|---|---|
| Code, tests, docs, `tools/dev/` | The installed Python, Node and Playwright |
| `.git` (history, hooks path, the exclude list) | Claude Code's own memory for the project (it is keyed by the folder's path, which differs between machines) |
| `CLAUDE.md`: the standing rules and the **Session handoff** | Running servers, browser sessions, temporary files |
| `.claude/settings.json`: the session-start hook that runs the upkeep | The state of the synchronisation itself |
| `data/` (reference data, review queue, playbook gap record, `playbooks_local.json`), `aiq_cache.db`, `aiq_config.json` (the Active IQ connection and tokens) | |

`CLAUDE.md` and `.claude/` are private notes and are not committed to git (`.git/info/exclude`); they travel only with the shared folder. Because Claude Code's memory does not travel, **everything a new session needs is in `CLAUDE.md`**: read its Session handoff first.

## First time on a new workstation

1. Install Python 3.9 or newer and Git. Optional: Node (for `node --check app.js` and the playbook tests) and Playwright (`pip install playwright`, then `playwright install chromium`) for `tools/dev/coverage.py` and `docscan.py`.
2. Let the synchronisation of the folder finish, and keep every file available offline, so that no file is only a placeholder.
3. In the folder: `python tools/dev/bootstrap.py --fix`. It reports the tools, sets the git hooks path (`.githooks`: the sensitive-data guard and the commit rules run on every commit and push), and warns about a stale `.git/index.lock`, uncommitted work and unpushed commits.
4. `python tests/run_tests.py` should pass.
5. Open Claude Code in the folder. `CLAUDE.md` and `.claude/settings.json` load by themselves; the session-start hook starts the upkeep (below) and prints what is waiting.

Git needs `user.name` and `user.email` on the machine (the owner's identity only).

## Rules for sharing one folder

* **One workstation at a time.** A synchronisation client copies files, not git operations: two machines committing at once can corrupt `.git`. Before you leave a machine: commit, push, and wait until the synchronisation has finished. When you arrive: wait for it, then run `python tools/dev/bootstrap.py`.
* A push takes about 15 minutes (the pre-push guard scans the history). Run it in the background and check `git status -sb` after it: `## main...origin/main` with nothing after it means it is pushed.
* If the synchronisation reports a conflict copy of a file (a name ending in `(1)` or containing `conflicted copy`), do not guess: compare the two with `git diff --no-index` and keep the right one. A conflict inside `.git` means stop and ask the owner.
* One ARIA server on the data folder at a time. The development tools use port 8091 and record the PID they started in `data/dev/server.pid`; stop only that PID, never `server.py` by name.
* `aiq_config.json` holds tokens and travels with the folder. Do not paste tokens anywhere else; if the Active IQ refresh token expires, renew it in Settings > Connection.
* Line endings: on Windows git writes CRLF into the working files, on a Mac LF. Patch scripts must use `tools/dev/patchlib.py` (it keeps each file's endings).
* Nothing real goes into git: no customer names, hostnames, serials or tokens, in code, tests, docs, scripts or notes. `tools/guard_sensitive.py` refuses the commit if it finds one.

## The upkeep that runs by itself

| What | When | What it does |
|---|---|---|
| Claude Code session-start hook (`.claude/settings.json` runs `tools/dev/maintenance.py session-start`) | Every time a Claude Code session starts or resumes in the folder, on any workstation | Starts, in the background, a sweep of **all** the reference updater's sources, including the NetApp pages every playbook was written from, then records procedure coverage with a headless load of the fleet (if Playwright is installed). Prints the queue, the largest procedure gaps, drafts waiting for approval, and the standing instruction (CLAUDE.md, Session start). |
| ARIA's own scheduler (the server) | 4 minutes after the server starts, then every 24 hours | A sweep of 30 sources, no AI. A change to a release, end-of-availability or advisory page also re-runs the reference scanners. |
| The playbook page watch | In every sweep | A change to a NetApp page that a playbook cites becomes a review item naming the playbook. |
| The scheduled Claude job `aria-library-harvest` | Mondays | The same routine, unattended: library entries, source changes, playbook drafts, release. |

The sweep needs the internet; ARIA itself still works without it, and nothing here needs an AI to run. The AI-written part (reading a NetApp page and drafting or correcting a playbook) is done by the Claude session that the hook briefs, and a draft is approved automatically once it passes the checks.

To run it by hand: `python tools/dev/maintenance.py sweep` (foreground) or `report` (what is waiting).
