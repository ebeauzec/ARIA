"""Generate the Action Planner documents and deliverables for one customer and scan them for the problems found in earlier reviews.

    python tools/dev/docscan.py --customer "<part of the customer name>" [--out data/dev/docs]

It generates every deliverable (text and Word) and a set of Action Planner tabs through the same download code the browser uses, then reports, per file:
  * product-name mentions (documents must not name the tool: they are an interpretation of data collected from Active IQ), and whether the basis line is present
  * product codes Active IQ reports that should read as sold names (AFF-A800, FDvM300, a bare E-Series number)
  * unreplaced template text (${...}, undefined, NaN, [object)
and writes the files to --out so they can be opened. The customer is an argument because real customer names must not appear in this repository.
"""
import argparse
import base64
import io
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import devlib  # noqa: E402

SETUP = r"""(cust) => {
  window.__files = []; window._dlBlob = (name, blob) => { window.__files.push({ name, blob }); }; window.alert = () => {};
  const names = Object.keys(state.systems.reduce((a, s) => (a[s.customerName] = 1, a), {}));
  const name = names.find(c => new RegExp(cust, 'i').test(c));
  if (!name) return { error: 'no customer matches', names: names.length };
  const sel = document.getElementById('planTargetSelect'); const v = 'CUST:' + name;
  if (![...sel.options].some(o => o.value === v)) { const o = document.createElement('option'); o.value = v; o.textContent = name; sel.appendChild(o); } sel.value = v;
  try { generateActionPlan(); } catch (e) {}
  return { name, systems: state.systems.filter(s => s.customerName === name).length };
}"""

STEP = r"""async ([code, fmt]) => {
  window.__files.length = 0; window.__dlFmtOverride = fmt;
  try { const r = eval(code); if (r && r.then) await r; } catch (e) { return { err: String(e.message) }; }
  window.__dlFmtOverride = null;
  const out = [];
  for (const f of window.__files) { const buf = new Uint8Array(await f.blob.arrayBuffer()); let bin = ''; for (let i = 0; i < buf.length; i += 8192) bin += String.fromCharCode.apply(null, buf.subarray(i, i + 8192)); out.push({ name: f.name, b64: btoa(bin) }); }
  return { out };
}"""

DELIVERABLES = ['PROBLEM_STATEMENTS', 'TICKET', 'IMPLEMENTATION', 'CONFIGURATION_REVIEW', 'EMAIL', 'SOLUTION_PROPOSAL', 'SALES_PROPOSAL', 'RISK_REMEDIATION_BRIEF', 'SECURITY_BRIEF',
                'SUSTAINABILITY_REPORT', 'SUCCESS_PLAN', 'QBR_PACK', 'MSP_REPORT', 'HANDOVER_BRIEF', 'VALUE_REPORT', 'CUSTOMER_REPORT']
STEPS = [(f"downloadDeliverable('{t}')", 'md', t) for t in DELIVERABLES] + [(f"downloadDeliverable('{t}')", 'docx', t + ' (word)') for t in ('EMAIL', 'SECURITY_BRIEF', 'IMPLEMENTATION')] \
    + [(f'downloadPlanSection({i})', 'md', f'tab {i}') for i in (1, 2, 3, 5, 6, 7, 8, 12, 29)] + [(f'downloadPlanSectionWord({i})', 'docx', f'tab {i} (word)') for i in (1, 6, 7, 29)]

BRAND = re.compile(r'ARIA|AIQ Advisor|\bthis tool\b|\bthe tool\b')
CODES = re.compile(r'(?<![\w(-])((?:AFF|ASA)-[A-Z]?\d+\w*|FDvM\d+|CDvM\d+)(?![\w-])')
LEAK = re.compile(r'\$\{|\bundefined\b|\bNaN\b|\[object')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--customer', required=True)
    ap.add_argument('--out', default=os.path.join(devlib.OUT, 'docs'))
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright
    os.makedirs(a.out, exist_ok=True)
    devlib.start_server()
    try:
        with sync_playwright() as p:
            b, pg = devlib.open_fleet(p)
            r = pg.evaluate(SETUP, a.customer)
            if r.get('error'):
                sys.exit('no customer name matches ' + repr(a.customer))
            print('scope:', r['systems'], 'systems')
            pg.wait_for_timeout(4000)
            bad = 0
            for code, fmt, label in STEPS:
                res = pg.evaluate(STEP, [code, fmt])
                if 'err' in res:
                    print(f'{label:34s} ERROR {res["err"][:80]}')
                    continue
                for f in res['out']:
                    raw = base64.b64decode(f['b64'])
                    with open(os.path.join(a.out, re.sub(r'[^A-Za-z0-9._-]+', '_', f['name'])), 'wb') as fh:
                        fh.write(raw)
                    if f['name'].lower().endswith('.docx'):
                        z = zipfile.ZipFile(io.BytesIO(raw))
                        text = ''.join(z.read(x).decode('utf-8', 'ignore') for x in z.namelist() if x.endswith('.xml'))
                    else:
                        text = raw.decode('utf-8', 'ignore')
                    basis = 'interpretation of the data collected from NetApp Active IQ' in text
                    brand, codes, leak = len(BRAND.findall(text)), sorted(set(CODES.findall(text)))[:4], len(LEAK.findall(text))
                    flag = 'ok' if basis and not brand and not codes and not leak else 'CHECK'
                    bad += flag != 'ok'
                    print(f'{label:34s} {len(raw) // 1024:>7} kB  basis={"yes" if basis else "NO "} product-name={brand} codes={codes or "-"} leaks={leak}  {flag}')
            print(f'{bad} file(s) to check; files are in {a.out}')
            b.close()
    finally:
        devlib.stop_server()


if __name__ == '__main__':
    main()
