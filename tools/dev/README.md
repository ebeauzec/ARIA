# tools/dev: the development helpers

Scripts for working on ARIA, not part of ARIA. They live in the repository so a second workstation (or a new session) has the same tools as the first. They
contain no customer names, tokens or machine paths: customers are command-line arguments, paths come from the repository root, and everything they write goes to
`data/dev/` (git-ignored).

| Script | What for |
|---|---|
| `bootstrap.py` | Run first on a workstation: tools present, git hooks path, stale lock, uncommitted work, unpushed commits. `--fix` sets the hooks path. |
| `maintenance.py` | The automatic upkeep: starts the full reference sweep at every Claude Code session start (hook in `.claude/settings.json`), prints the queue and the standing instruction. `report`, `sweep`, `check`. |
| `release.py` | Version bump in all five places (`version.json`, `app.js` APP_VERSION + APP_CHANGELOG, `CHANGELOG.md`, `index_src.html` stamps, README badge). Does not commit or push. |
| `patchlib.py` | `edit()` / `replace_once()` for patch scripts: keeps each file's line endings, fails if an anchor is not found exactly once. |
| `coverage.py` | `summary`, `engine`, `example ID`, `record`: how much of the fleet has a procedure for its own system (needs Playwright and the harvested fleet). |
| `docscan.py` | Generate the deliverables for one customer and scan them for product-name mentions, unrenamed model codes and template leaks (needs Playwright). |
| `devlib.py` | Shared: start/stop the test server on port 8091 by PID, open the fleet in a browser. |

Conventions that are easy to get wrong:

* Write patch scripts to a file with the Write tool, not a shell heredoc (backslashes and quotes get mangled), and use `patchlib`.
* The test server is port 8091, one at a time, stopped by PID. Never stop `server.py` by name: that has stopped the owner's own server and harvest before.
* Do not put real customer names, hostnames or serials in a script, a test or a note; the guard will refuse the commit.
* `python tests/run_tests.py` is the suite; the tests that need node skip without it.
