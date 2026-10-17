"""Check a workstation before working on ARIA from the shared folder, and say what is left to do. Run it first on every machine and every time you sit down:

    python tools/dev/bootstrap.py            report
    python tools/dev/bootstrap.py --fix      also set the things that are safe to set (the git hooks path)

It reads, never writes, except for --fix. It does not touch tokens, the data folder or any Active IQ account.
"""
import argparse
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OK, WARN, BAD = 'ok  ', 'warn', 'FAIL'
problems = 0


def say(level, text):
    global problems
    problems += level == BAD
    print(f'[{level}] {text}')


def run(*cmd, cwd=ROOT):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=60)
        return r.returncode, (r.stdout or '').strip(), (r.stderr or '').strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, '', str(e)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--fix', action='store_true')
    a = ap.parse_args()
    print(f'ARIA folder: {ROOT}\n')

    # tools
    py = sys.version_info
    say(OK if py >= (3, 9) else BAD, f'Python {py.major}.{py.minor}.{py.micro} ({sys.executable}); 3.9 or newer is needed')
    node = shutil.which('node')
    say(OK if node else WARN, 'node ' + (run('node', '--version')[1] if node else 'not found: needed for tests/test_playbooks*.py and `node --check app.js` (those tests skip without it)'))
    git = shutil.which('git')
    say(OK if git else BAD, 'git ' + (run('git', '--version')[1] if git else 'not found'))
    import importlib.util
    if importlib.util.find_spec('playwright'):
        say(OK, 'playwright is installed (the tools in tools/dev/ that open the fleet in a browser need it and `playwright install chromium`)')
    else:
        say(WARN, 'playwright is not installed: only tools/dev/coverage.py and docscan.py need it (pip install playwright ; playwright install chromium)')

    # the folder is a git clone
    if git:
        code, top, _ = run('git', 'rev-parse', '--show-toplevel')
        if code != 0:
            say(BAD, 'this folder is not a git repository (the .git folder did not sync from Google Drive yet?)')
        else:
            hp = run('git', 'config', '--get', 'core.hooksPath')[1]
            if hp == '.githooks':
                say(OK, 'git hooks path is .githooks (the guard, the no-Claude-credit and no-sensitive-data hooks run)')
            elif a.fix:
                run('git', 'config', 'core.hooksPath', '.githooks')
                say(OK, 'set core.hooksPath to .githooks')
            else:
                say(BAD, f'git hooks path is {hp!r}, not .githooks: run this with --fix. Without it commits skip the guard.')
            for key in ('user.name', 'user.email'):
                say(OK if run('git', 'config', '--get', key)[1] else WARN, f'git {key}: ' + (run('git', 'config', '--get', key)[1] or 'not set (git config --global ' + key + ' ...)'))
            say(OK, 'git autocrlf = ' + (run('git', 'config', '--get', 'core.autocrlf')[1] or 'unset') + ' (Windows keeps CRLF in the working files; tools/dev/patchlib.py edits either)')
            lock = os.path.join(ROOT, '.git', 'index.lock')
            if os.path.exists(lock):
                say(BAD, '.git/index.lock exists: another git command is running, or one was cut off (or Google Drive synced a lock from the other machine). If none is running, delete it.')
            br = run('git', 'status', '-sb')[1].split('\n')
            say(OK, 'branch: ' + br[0].replace('## ', ''))
            dirty = [l for l in br[1:] if l.strip()]
            if dirty:
                say(WARN, f'{len(dirty)} changed file(s) not committed (work in progress from another session, or Google Drive still syncing): `git status` then decide; do not start a second change on top without looking')
            else:
                say(OK, 'working tree is clean')
            sy = run('git', 'log', '-1', '--format=%h %s')[1]
            say(OK, 'last commit: ' + sy[:100])
            if 'ahead' in br[0]:
                say(WARN, 'commits not pushed yet: ' + br[0] + ' (push, in the background: the pre-push guard takes about 15 minutes)')
            if 'behind' in br[0]:
                say(WARN, 'origin has newer commits: `git fetch origin` and look before changing anything')

    # the files that make the folder self-describing
    for f, why in (('CLAUDE.md', 'standing rules and the session handoff (git-ignored on purpose; it travels with this folder)'), ('docs/WORKSTATIONS.md', 'how to work from the shared folder'),
                   ('tools/guard_sensitive.py', 'the sensitive-data guard'), ('.githooks/pre-push', 'the push hook')):
        say(OK if os.path.exists(os.path.join(ROOT, f)) else (BAD if f != 'CLAUDE.md' else WARN), f'{f}: ' + ('present' if os.path.exists(os.path.join(ROOT, f)) else 'MISSING') + f' ({why})')
    say(OK if os.path.exists(os.path.join(ROOT, 'aiq_config.json')) else WARN, 'aiq_config.json (Active IQ connection and tokens): ' + ('present' if os.path.exists(os.path.join(ROOT, 'aiq_config.json')) else 'missing: enter the connection in Settings > Connection; never put tokens in a command or a note'))
    say(OK if os.path.isdir(os.path.join(ROOT, 'data')) else WARN, 'data/ (harvest cache, reference data, playbook gap record): ' + ('present' if os.path.isdir(os.path.join(ROOT, 'data')) else 'missing'))

    # a test server left running by the dev tools
    pidf = os.path.join(ROOT, 'data', 'dev', 'server.pid')
    if os.path.exists(pidf):
        say(WARN, f'data/dev/server.pid says a test server was started (PID {open(pidf).read().strip()}): if it is not running on this machine, delete the file; it may belong to the other workstation')

    print('\nNext: python tests/run_tests.py   |   read the "Session handoff" section of CLAUDE.md   |   docs/WORKSTATIONS.md')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
