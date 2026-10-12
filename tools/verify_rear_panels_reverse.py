"""
Reverse rear-panel check: ports the drawing shows that NetApp's own pages for the platform never mention.

verify_rear_panels.py asks "does every port NetApp documents have a place on the drawing". This asks the other way round: with nothing reported for the system,
which fixed ports does the drawing show, and does NetApp's install / cabling / setup text for that platform name them. A drawn port that the documentation never
mentions is not necessarily wrong (the text may only describe the ports it tells you to cable), but it is the list to check against the Hardware Universe.

Usage:  ARIA_URL=http://127.0.0.1:8080/ python tools/verify_rear_panels_reverse.py   (needs playwright + curl; reads only public NetApp documentation)
"""
import json, os, re, subprocess
from playwright.sync_api import sync_playwright
from verify_rear_panels import curl, tokens, URL

PAIRS = {  # platform string used by the app -> documentation directory
    'aff-a150': 'a150', 'aff-a220': 'a220', 'aff-a250': 'a250', 'aff-c250': 'c250', 'aff-a300': 'a300', 'aff-a320': 'a320', 'aff-a400': 'a400', 'aff-c400': 'c400',
    'aff-a700': 'a700', 'aff-a800': 'a800', 'aff-c800': 'c800', 'aff-a900': 'a900', 'aff-c190': 'c190', 'aff-a20': 'a20-30-50', 'aff-a30': 'a20-30-50', 'aff-a50': 'a20-30-50',
    'aff-c30': 'c30-60', 'aff-c60': 'c30-60', 'aff-a70': 'a70-90', 'aff-a90': 'a70-90', 'aff-a1k': 'a1k', 'asa-a250': 'asa250', 'asa-a800': 'asa800', 'asa-a70': 'a70-90',
    'fas8200': 'fas8200', 'fas8300': 'fas8300', 'fas8700': 'fas8300', 'fas9000': 'fas9000', 'fas9500': 'fas9500', 'fas2650': 'fas2600', 'fas2720': 'fas2700',
    'fas2750': 'fas2700', 'fas2820': 'fas2800', 'fas500f': 'fas500f', 'fas50': 'fas50', 'fas70': 'fas-70-90', 'fas90': 'fas-70-90',
}
JS = r"""(plats)=>plats.map(p=>{const s={platform:p,systemName:'x-01',serialNumber:'x'};let h='';try{h=_buildControllerBackplate(s,[{name:'e0M',type:'mgmt',status:'online',details:{speed:'1 Gbps'}}],p,false,false,false)}catch(e){return {plat:p,err:e.message}}
  return {plat:p,drawn:[...new Set([...h.matchAll(/id="port-slot-([^"]+)"/g)].map(x=>x[1]))]}})"""

if __name__ == '__main__':
    tree = json.loads(curl('https://api.github.com/repos/NetAppDocs/ontap-systems/git/trees/main?recursive=1'))['tree']
    docs = {}
    for d in sorted(set(PAIRS.values())):
        eth, fc = tokens(d, tree)
        docs[d] = set(eth) | set(fc)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(); pg.goto(URL)
        pg.wait_for_function('typeof _buildControllerBackplate === "function"', timeout=120000)
        for r in pg.evaluate(JS, list(PAIRS)):
            if r.get('err'):
                print(r['plat'], 'ERROR', r['err']); continue
            d = docs[PAIRS[r['plat']]]
            extra = [x for x in r['drawn'] if x != 'e0M' and x not in d]
            print(f"{r['plat']:10s} docs {PAIRS[r['plat']]:10s} drawn {len(r['drawn']):2d}  not mentioned in the docs: {', '.join(extra) if extra else 'none'}")
        b.close()
