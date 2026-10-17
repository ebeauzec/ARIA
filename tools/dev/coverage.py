"""How much of the fleet has a remediation procedure written for its own system. Needs the harvested data in data/, Playwright, and the test server (started here).

    python tools/dev/coverage.py summary              coverage by platform family and the largest findings with no procedure
    python tools/dev/coverage.py engine               call the remediation engine for every distinct finding: generic fallback / no command syntax / has commands
    python tools/dev/coverage.py example ID [ID...]   print a rendered example of playbook ID (for example eseries.santricity-upgrade)
    python tools/dev/coverage.py record               load the fleet headlessly and record the coverage and the gaps (what maintenance.py does at session start)

The same numbers are shown to the user in Settings > Data & Sync > Procedure coverage; this script is for checking a change to the engine or to a playbook.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import devlib  # noqa: E402

SUMMARY_JS = r"""() => {
  const out = { n: 0, pb: 0, fam: {}, gaps: {} };
  state.systems.forEach(s => { const f = _platformFamily(s); (s.risks || []).forEach(r => {
    const b = out.fam[f] || (out.fam[f] = { n: 0, pb: 0 }); b.n++; out.n++;
    if (r.hasPlaybook) { b.pb++; out.pb++; return; }
    const k = f + ' | ' + (r.category || '') + ' | ' + String(r.description || '').replace(/\d+/g, 'N').slice(0, 95);
    out.gaps[k] = (out.gaps[k] || 0) + 1;
  }); });
  out.gaps = Object.entries(out.gaps).sort((a, b) => b[1] - a[1]).slice(0, 40);
  return out;
}"""

ENGINE_JS = r"""() => {
  const groups = {};
  state.systems.forEach(sys => (sys.risks || []).forEach(r => {
    const k = (r.category || '') + ' | ' + String(r.title || r.name || r.description || '').replace(/\d+/g, 'N').slice(0, 90);
    const g = groups[k] || (groups[k] = { n: 0, sys, risk: r });
    g.n++;
  }));
  return Object.entries(groups).map(([k, g]) => {
    let p = null; try { p = generateDynamicRemediationPlan(g.risk, g.sys); } catch (e) { /* counted as an error */ }
    const steps = ((p && p.steps) || []).join('\n');
    const generic = /standard ONTAP diagnostic commands/.test(steps);
    const cmds = (steps.match(/(?:^|\s)(?:storage|vserver|network|system|volume|snapmirror|security|cluster|event|options|aggr|lun|vol|snapshot|autosupport|node|disk|run|dashboard|set)\s+[a-z-]+(?:\s+[a-z-]+)*/g) || []).length;
    return { k, n: g.n, generic, cmds, err: !p };
  });
}"""

EXAMPLE_JS = r"""(ids) => { const out = {}; state.systems.forEach(s => (s.risks || []).forEach(r => { const id = (r.remediationPlan || {}).playbookId; if (id && ids.includes(id) && !out[id]) out[id] = { finding: r.description, system: s.systemName, plan: r.remediationPlan }; })); return out; }"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=('summary', 'engine', 'example', 'record'))
    ap.add_argument('ids', nargs='*')
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright
    devlib.start_server()
    try:
        with sync_playwright() as p:
            b, pg = devlib.open_fleet(p)
            if a.cmd == 'record':
                # what ARIA does by itself 6 s after a load: put the procedures on late findings, count what is covered and post the gaps to the server
                pg.evaluate("applyPlaybooksToFleet(); reportPlaybookGaps();")
                pg.wait_for_timeout(4000)
                st = pg.evaluate("fetch('/api/library/playbooks/status').then(r => r.json())")
                print(f"recorded: {st.get('pct')}% covered ({st.get('covered')} of {st.get('total')}), {st.get('gapTypes')} kinds of finding without a procedure")
            elif a.cmd == 'summary':
                r = pg.evaluate(SUMMARY_JS)
                print(f"findings {r['n']:,}; with a procedure for their own system {r['pb']:,} ({100.0 * r['pb'] / max(1, r['n']):.1f}%)")
                for f, v in sorted(r['fam'].items()):
                    print(f"  {f:12s} {v['n']:7,d}  covered {v['pb']:7,d}  {100.0 * v['pb'] / max(1, v['n']):5.1f}%")
                print('largest findings with no procedure:')
                for k, n in r['gaps'][:25]:
                    print(f'  {n:6d}  {k}')
            elif a.cmd == 'engine':
                r = pg.evaluate(ENGINE_JS)
                tot = sum(x['n'] for x in r)
                for lab, f in (('generic fallback', lambda x: x['generic']), ('no command syntax', lambda x: not x['generic'] and not x['cmds']), ('has commands', lambda x: not x['generic'] and x['cmds'])):
                    s = [x for x in r if f(x)]
                    print(f'{lab:20s} kinds={len(s):4d} findings={sum(x["n"] for x in s):6d} ({100.0 * sum(x["n"] for x in s) / max(1, tot):.1f}%)')
                print('largest generic fallbacks:')
                for x in sorted((x for x in r if x['generic']), key=lambda x: -x['n'])[:20]:
                    print(f"  {x['n']:6d}  {x['k']}")
            else:
                ex = pg.evaluate(EXAMPLE_JS, a.ids)
                for i in a.ids:
                    x = ex.get(i)
                    if not x:
                        print(f'\nNo finding in this fleet uses {i}')
                        continue
                    print(f"\n### {i}: {x['finding'][:100]} on {x['system']}\ncause: {x['plan']['cause']}")
                    for st in x['plan']['steps']:
                        print('  ', st)
            b.close()
    finally:
        devlib.stop_server()


if __name__ == '__main__':
    main()
