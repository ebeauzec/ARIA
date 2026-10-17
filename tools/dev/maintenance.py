"""Keep ARIA's reference data and remediation playbooks up to date from NetApp's documentation, every time someone works on the project.

    python tools/dev/maintenance.py session-start   the Claude Code SessionStart hook (.claude/settings.json): start the sweep in the background, print the report
    python tools/dev/maintenance.py report          print the report only
    python tools/dev/maintenance.py sweep           run the whole sweep now, in the foreground
    python tools/dev/maintenance.py check           exit 1 when review items are still open (use before a release)

What a session start does (nothing here needs an AI; the AI-written part is what the printed instructions ask Claude to do):
  1. Starts, detached, `_background`: the reference updater over ALL its sources (release lists, advisories, end-of-availability, what's-new pages, and the NetApp
     pages every playbook was written from), then, when Playwright is installed, a headless load of the fleet that records which findings have no procedure.
     A sweep that started less than 45 minutes ago is not started twice.
  2. Prints what is waiting: the open review items by kind, the procedure coverage and the largest gaps, drafts that did not pass the checks, library entries not yet absorbed.
  3. Prints the standing instruction for the session (CLAUDE.md, "Session start"): work the queue before other work.

The state lives in data/ (shared with another workstation when the project folder is synchronised between machines); the run log is data/dev/maintenance.log.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'tools'))

LOCK_MINUTES = 45


def _paths(root):
    d = os.path.join(root, 'data')
    return {'data': d, 'dev': os.path.join(d, 'dev'), 'lock': os.path.join(d, 'dev', 'maintenance.lock'), 'status': os.path.join(d, 'dev', 'maintenance_status.json'),
            'log': os.path.join(d, 'dev', 'maintenance.log'), 'queue': os.path.join(d, 'library_update_queue.json'), 'state': os.path.join(d, 'library_update_state.json'),
            'gaps': os.path.join(d, 'playbook_gaps.json')}


def _jload(path):
    try:
        with open(path, encoding='utf-8') as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def _age(iso):
    try:
        t = datetime.fromisoformat(str(iso).replace('Z', '+00:00'))
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        s = (datetime.now(timezone.utc) - t).total_seconds()
    except (ValueError, TypeError):
        return 'never'
    return 'just now' if s < 90 else f'{int(s // 60)} min ago' if s < 5400 else f'{int(s // 3600)} h ago' if s < 172800 else f'{int(s // 86400)} days ago'


def start_background(root=ROOT):
    """Start the sweep detached. Returns a sentence saying what happened."""
    p = _paths(root)
    os.makedirs(p['dev'], exist_ok=True)
    st = _jload(p['status'])
    try:
        age = time.time() - os.path.getmtime(p['lock'])
        if age < LOCK_MINUTES * 60:
            return f'a sweep started {int(age / 60)} min ago is still running'
    except OSError:
        pass                      # no lock: none is running
    if st.get('finishedAt'):
        try:
            done = datetime.fromisoformat(st['finishedAt'])
            if (datetime.now(timezone.utc) - done).total_seconds() < 10 * 60:
                return f'a sweep finished {_age(st["finishedAt"])}; not repeated so soon'
        except ValueError:
            pass
    with open(p['lock'], 'w') as fh:
        fh.write(str(os.getpid()))
    with open(p['status'], 'w', encoding='utf-8') as fh:
        json.dump({'startedAt': datetime.now(timezone.utc).isoformat(), 'steps': []}, fh)
    log = open(p['log'], 'a', encoding='utf-8')
    cmd = [sys.executable, os.path.join(HERE, 'maintenance.py'), '_background']
    kw = {'cwd': root, 'stdout': log, 'stderr': log, 'stdin': subprocess.DEVNULL}
    if os.name == 'nt':
        kw['creationflags'] = 0x00000008 | 0x00000200      # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    else:
        kw['start_new_session'] = True
    subprocess.Popen(cmd, **kw)
    return 'started in the background (about 4-6 minutes); run `python tools/dev/maintenance.py report` for the result'


def background(root=ROOT):
    """The detached job: the sweep, then (when Playwright is installed) the coverage record."""
    p = _paths(root)
    st = _jload(p['status']) or {'startedAt': datetime.now(timezone.utc).isoformat(), 'steps': []}

    def save():
        with open(p['status'], 'w', encoding='utf-8') as fh:
            json.dump(st, fh, indent=1)

    def step(name, fn):
        t0 = time.time()
        try:
            res = fn()
            st['steps'].append({'step': name, 'ok': True, 'seconds': int(time.time() - t0), 'note': res})
        except Exception as e:      # a step that fails is reported, the next one still runs
            st['steps'].append({'step': name, 'ok': False, 'seconds': int(time.time() - t0), 'note': f'{type(e).__name__}: {str(e)[:200]}'})
        save()

    def sweep():
        import library_manager as lm
        import library_updater as lu
        cfg = _jload(os.path.join(root, 'aiq_config.json'))
        rep = lu.run_update(root, cfg, budget=1000, library_manager=lm, log=lambda *_a, **_k: None)
        return f"{rep['checked']} page(s) read of {rep['sources']}, {rep['changedPages']} changed, {rep['openItems']} open item(s), {len(rep.get('unreachable') or [])} unreachable"

    def record():
        import importlib.util
        if not importlib.util.find_spec('playwright'):
            return 'skipped: Playwright is not installed (pip install playwright ; playwright install chromium)'
        if not os.path.exists(os.path.join(root, 'aiq_cache.db')):
            return 'skipped: no harvested fleet (aiq_cache.db) on this machine'
        r = subprocess.run([sys.executable, os.path.join(HERE, 'coverage.py'), 'record'], cwd=root, capture_output=True, text=True, timeout=900)
        return (r.stdout or r.stderr or '').strip()[-300:]

    def verify():
        import playbook_verify as pv
        pv.run(root)
        s = pv.summary(p['data'])
        t = s['totals']
        return f"{s['entriesOk']} of {s['entries']} playbooks fully verified; commands and menu paths: {t['verified']} verified, {t['param-missing']} wrong parameter, {t['not-found']} not found, {t['unchecked']} unchecked"

    def promote():
        import playbook_verify as pv
        ok, kept = pv.promote(root)
        return ('approved: ' + ', '.join(ok) if ok else 'no draft to approve') + ('; still drafts: ' + '; '.join(f'{k} ({v[0][:60]})' for k, v in kept.items()) if kept else '')

    step('reference updater sweep (all sources)', sweep)
    step('approve the drafts that pass the checks', promote)
    step('verify playbook commands against the NetApp command reference', verify)
    step('procedure coverage record (headless)', record)
    st['finishedAt'] = datetime.now(timezone.utc).isoformat()
    save()
    try:
        os.remove(p['lock'])
    except OSError:
        pass


def report(root=ROOT, started_note=None):
    p = _paths(root)
    q = (_jload(p['queue']).get('items') or {})
    openq = [i for i in q.values() if i.get('status') == 'open']
    by = {}
    for i in openq:
        by.setdefault(i.get('kind', '?'), []).append(i)
    state = _jload(p['state'])
    st = _jload(p['status'])
    gaps = _jload(p['gaps'])
    out = [f"== ARIA maintenance, {datetime.now().strftime('%Y-%m-%d %H:%M')} (automatic at session start) =="]
    if started_note:
        out.append('Sweep: ' + started_note + '.')
    if st.get('finishedAt'):
        out.append(f"Last background run finished {_age(st['finishedAt'])}: " + '; '.join(f"{s['step']} -> {'ok' if s['ok'] else 'FAILED'} ({s['note']})" for s in st.get('steps', [])))
    else:
        out.append(f"Reference updater last ran {_age(state.get('lastRun'))}.")
    if by:
        out.append(f'Open review items: {len(openq)} (' + ', '.join(f'{k} {len(v)}' for k, v in sorted(by.items())) + ').')
    else:
        out.append('Open review items: none.')
    try:
        import playbooks as pb
        ld = pb.load(p['data'], os.path.join(root, 'tools', 'playbooks.json'))
        w = pb.source_watch(p['data'], ld)
        out.append(f"Procedures: {ld['counts']['approved']} playbooks in use, {ld['counts']['pending']} draft(s) not approved yet, {ld['counts']['invalid']} invalid; "
                   + (f"coverage {gaps.get('pct')}% ({gaps.get('covered'):,} of {gaps.get('total'):,} findings), recorded {_age(gaps.get('updated'))}" if gaps.get('pct') is not None else 'coverage not recorded on this machine yet')
                   + f"; {w['read']} of {w['pages']} source pages read, {w['changedOpen']} changed since.")
        for g in sorted((gaps.get('gaps') or {}).values(), key=lambda x: -x.get('count', 0))[:6]:
            out.append(f"  gap: {g['count']:>5} x {g['key'][:100]}")
        try:
            import playbook_verify as pv
            vs = pv.summary(p['data'])
            t = vs['totals']
            out.append(f"  verification against NetApp's documentation ({_age(vs['at'])}): {t['verified']} commands and menu paths verified, {t['param-missing']} with a parameter the page does not have, {t['not-found']} not found, {t['unchecked']} unchecked")
            for r in vs['review'][:6]:
                out.append(f"  NEEDS REVIEW {r['id']}: {r['item']} ({r['status']})")
        except Exception:
            pass
        for d in ld['pending'][:5]:
            out.append(f"  draft that has not passed the checks: {d['id']} (python tools/playbook_verify.py --promote says why)")
        for x in ld['problems'][:3]:
            out.append(f"  INVALID playbook {x['id']}: {x['problems'][0]}")
    except Exception as e:
        out.append(f'Procedures: could not read ({e}).')
    try:
        import sync_library as _sl
        if _sl.behind():
            out.append('The library copy that ships with ARIA (reference/netapp-library/) is behind the external library: python tools/dev/sync_library.py, then release.')
    except Exception:
        pass
    try:
        import library_manager as lm
        lib = (lm.find_library(_jload(os.path.join(root, 'aiq_config.json'))) or {}).get('path')
        n = len(lm.unharvested(lib, p['data'])) if lib else None
        if n:
            out.append(f'Library entries not yet absorbed: {n} (python tools/library_manager.py --unharvested).')
    except Exception:
        pass
    work = bool(by) or (not gaps.get('pct') is None and bool(gaps.get('gaps')))
    out.append('')
    if work:
        out.append("INSTRUCTION (CLAUDE.md, 'Session start'): before other work, unless the user's first message is urgent, work this queue: (1) library items and new releases/advisories: "
                   "docs/LIBRARY_HARVEST_ROUTINE.md section 2; (2) each `playbook-source-changed` item: read the page (tools/library_updater.http_get + html_to_text; WebFetch gets 403 from docs.netapp.com) "
                   "and correct the playbook; (3) the largest `playbook-gap` items, up to five this session: write the playbook as a draft from the NetApp pages only (docs/PLAYBOOKS.md), never from memory, then run `python tools/playbook_verify.py --promote` (new procedures are approved automatically when they pass the checks); "
                   "(4) tests, guard, release and push per CLAUDE.md; then say in one short paragraph what was done. If the user wants something else first, do that and come back to this.")
    else:
        out.append('Nothing in the queue needs doing now.')
    return '\n'.join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=('session-start', 'report', 'sweep', 'check', '_background'))
    ap.add_argument('--root', default=ROOT)
    a = ap.parse_args(argv)
    if a.cmd == 'session-start':
        note = start_background(a.root)
        print(report(a.root, note))
    elif a.cmd == 'report':
        print(report(a.root))
    elif a.cmd == 'sweep':
        background(a.root)
        print(report(a.root))
    elif a.cmd == '_background':
        background(a.root)
    elif a.cmd == 'check':
        q = (_jload(_paths(a.root)['queue']).get('items') or {})
        n = len([i for i in q.values() if i.get('status') == 'open'])
        print(f'{n} open review item(s)')
        return 1 if n else 0
    return 0


if __name__ == '__main__':
    sys.exit(main())
