"""ARIA reference updater: the weekly library routine, built into the engine (no AI).

What the maintenance routine used to do by hand, ARIA now does itself:

  1. Sources.   Every page the NetApp Reference Library is built from (the `Source:` line of each library document), plus a short list of key
                pages ARIA always checks (release lists, What's new pages, end-of-availability, TR indexes). With no library folder on the
                machine the list that ships in tools/library_sources.json is used, so a bare install still keeps itself current.
  2. Sweep.     Fetch the key pages every run and the stalest of the others (a budget per run, one request a second), reduce each page to its text,
                and keep a refreshed copy in data/library_refreshed/ (same Source:/Fetched: layout as the library; the library search reads it).
  3. Diff.      Compare each page with the copy from the last run: a newer release number than before, new KB / CVE / advisory / TR ids, or
                lines that were added or removed. Nothing is ever guessed: an event is only what the page text shows.
  4. Check.     Every new id or release number is looked up in ARIA's own data (bulletins, advisories, rules, release catalogue). What ARIA already
                holds is "covered"; the rest goes to the review queue with the page, the lines that changed and, for known-issue ids, a rules stub.
  5. Tables.    The curated reference tables (data/reference_library.js) are classed as kept up to date by a scanner, partly scanner and partly
                by hand, or by hand. For the hand-kept ones the updater lists which official pages changed since the table was last compiled.
  6. Library.   Entries in the library's CHANGELOG that ARIA has not seen are read for ids and versions and cross-checked the same way; an entry
                that says "no material changes" and names nothing ARIA lacks is recorded as handled.

Only public pages are read. The support portal, IMT and library.netapp.com are never requested. A compatibility range, a prose
best-practice change or a new kind of check is never written by this module: those go to the review queue for a person.
"""
import difflib
import gzip
import hashlib
import html as _html
import io
import json
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser

UA = 'Mozilla/5.0 (compatible; ARIA-reference-updater/1.0)'
RATE_SECONDS = 1.0
MAX_BYTES = 2_500_000
TIMEOUT = 20
STATE_NAME = 'library_update_state.json'
REPORT_NAME = 'library_update_report.json'
QUEUE_NAME = 'library_update_queue.json'
SOURCES_NAME = 'library_sources.json'
CACHE_DIR = 'library_refreshed'

ALLOWED_HOSTS = {'docs.netapp.com', 'security.netapp.com', 'www.netapp.com', 'github.com', 'endoflife.date', 'kb.netapp.com', 'www.cisa.gov'}
NEVER_HOSTS = {'mysupport.netapp.com', 'imt.netapp.com', 'library.netapp.com', 'hwu.netapp.com'}

# pages checked on every run (category, title, url)
KEY_PAGES = [
    ('ONTAP-Core', 'ONTAP release support reference', 'https://docs.netapp.com/us-en/ontap/release-notes/release-support-reference.html'),
    ('ONTAP-Core', 'ONTAP 9 what\'s new (highlights)', 'https://docs.netapp.com/us-en/ontap-whatsnew/'),
    ('Kubernetes-Containers', 'Trident release notes', 'https://docs.netapp.com/us-en/trident/trident-rn.html'),
    ('Kubernetes-Containers', 'Trident GitHub releases', 'https://github.com/NetApp/trident/releases.atom'),
    ('Platforms-Hardware', 'ONTAP systems what\'s new', 'https://docs.netapp.com/us-en/ontap-systems/whats-new.html'),
    ('Platforms-Hardware', 'End-of-availability hardware', 'https://docs.netapp.com/us-en/ontap-systems/eoa-hardware.html'),
    ('Platforms-Hardware', 'ONTAP hardware issues (KB index)', 'https://kb.netapp.com/on-prem/ontap/OHW/OHW-Issues'),
    ('Data-Protection', 'SnapCenter release notes', 'https://docs.netapp.com/us-en/snapcenter/release-notes/release-notes.html'),
    ('Data-Protection', 'MetroCluster new features', 'https://docs.netapp.com/us-en/ontap-metrocluster/releasenotes/mcc-new-features.html'),
    ('Cloud-BlueXP', 'Cloud Volumes ONTAP what\'s new', 'https://docs.netapp.com/us-en/storage-management-cloud-volumes-ontap/whats-new.html'),
    ('Cloud-BlueXP', 'StorageGRID what\'s new', 'https://docs.netapp.com/us-en/storagegrid/release-notes/whats-new.html'),
    ('Cloud-BlueXP', 'Disaster recovery what\'s new', 'https://docs.netapp.com/us-en/data-services-disaster-recovery/release-notes/dr-whats-new.html'),
    ('Cloud-BlueXP', 'Backup and recovery what\'s new', 'https://docs.netapp.com/us-en/data-services-backup-recovery/whats-new.html'),
    ('Hypervisors', 'ONTAP tools for VMware vSphere what\'s new', 'https://docs.netapp.com/us-en/ontap-tools-vmware-vsphere-10/release-notes/whats-new.html'),
    ('Networking-Performance', 'ONTAP SAN technical reports', 'https://docs.netapp.com/us-en/ontap-technical-reports/san.html'),
    ('Networking-Performance', 'ONTAP NAS technical reports', 'https://docs.netapp.com/us-en/ontap-technical-reports/nas.html'),
    ('Security-Advisories', 'NetApp security advisories', 'https://security.netapp.com/advisory/'),
]

# The curated reference tables (data/reference_library.js): how each is kept, what backs it, and which official pages it is compiled from.
# mode: 'scanner' = rebuilt by a scanner, 'partial' = scanner for the facts a page states, by hand for the rest, 'manual' = by hand.
TABLES = [
    ('SOFTWARE_VERSION_DATABASES', 'Release lists (ONTAP, StorageGRID, SANtricity)', 'scanner', 'version_catalog.json', r'release-support-reference|storagegrid/release-notes|santricity'),
    ('REFERENCE_LIBRARY_EOA_PLATFORMS', 'End-of-availability platforms', 'scanner', 'eoa_database.json', r'ontap-systems/eoa|eoa-hardware'),
    ('REFERENCE_LIBRARY_EOA_DATES', 'End-of-availability dates', 'scanner', 'eoa_database.json', r'ontap-systems/eoa|eoa-hardware'),
    ('REFERENCE_LIBRARY_EOA_SWITCHES', 'End-of-availability switches', 'scanner', 'eoa_database.json', r'ontap-systems/eoa|eoa-hardware|switches'),
    ('REFERENCE_LIBRARY_CURRENT_PLATFORMS', 'Current platforms', 'scanner', 'derived_reference.json', r'ontap-systems/whats-new'),
    ('REFERENCE_LIBRARY_FIRMWARE_BASELINES', 'Firmware baselines', 'scanner', 'firmware_baselines.json', r'OHW|firmware|switches'),
    ('REFERENCE_LIBRARY_ONTAP_HIGHLIGHTS', 'ONTAP release highlights', 'scanner', 'ontap_release_notes.json', r'ontap-whatsnew|release-notes'),
    ('REFERENCE_LIBRARY_PRELEASE_MINIMUMS', 'Minimum releases per platform', 'scanner', 'derived_reference.json', r'ontap-whatsnew|ontap-systems/whats-new'),
    ('REFERENCE_LIBRARY_MC_REQUIREMENTS', 'MetroCluster requirements', 'partial', 'derived_reference.json', r'ontap-metrocluster'),
    ('REFERENCE_LIBRARY_UPGRADE_CAVEATS', 'Upgrade caveats', 'partial', 'derived_reference.json', r'ontap-whatsnew|upgrade|release-notes'),
    ('IMT_INTEROP_MATRIX', 'Interoperability matrix (versions by scanner, ranges by hand)', 'partial', 'imt_interop.json', r'ontap-sanhost|ontap-tools|snapcenter|trident|veeam|vmware|proxmox'),
    ('REFERENCE_LIBRARY_ADVISORIES', 'Advisories worth knowing', 'partial', 'advisory_resolutions.json', r'security\.netapp\.com'),
    ('REFERENCE_LIBRARY_INTEGRATION_NOTES', 'Integration notes', 'partial', 'imt_interop.json', r'trident|snapcenter|ontap-tools|ontap-sanhost'),
    ('REFERENCE_LIBRARY_INTEGRATIONS', 'Integrations', 'manual', None, r'trident|snapcenter|ontap-tools|ontap-sanhost|veeam|vmware|proxmox|openstack|nutanix'),
    ('REFERENCE_LIBRARY_BEST_PRACTICES', 'Best practices', 'manual', None, r'ontap-technical-reports|TR-4569|ransomware|multi-admin|security-hardening'),
    ('REFERENCE_LIBRARY_PLATFORM_REPLACEMENTS', 'Platform replacements', 'manual', None, r'ontap-systems'),
    ('REFERENCE_LIBRARY_ASA_R2', 'ASA r2', 'manual', None, r'asa-r2|ontap-systems'),
    ('REFERENCE_LIBRARY_AFX_NOTES', 'AFX', 'manual', None, r'afx|ontap-systems'),
    ('REFERENCE_LIBRARY_KEYSTONE', 'Keystone', 'manual', None, r'keystone'),
    ('REFERENCE_LIBRARY_NAMING_CONVENTIONS', 'Naming conventions', 'manual', None, r'ontap-systems|naming'),
    ('REFERENCE_LIBRARY_ONTAP_PERSONALITIES', 'ONTAP personalities', 'manual', None, r'ontap-systems|personalit'),
]


# ── fetch ───────────────────────────────────────────────────────────────────────────────────
def http_get(url, timeout=TIMEOUT, ctx=None):
    """(text, error). Never raises; refuses sign-in hosts and anything but https. ctx: the ssl context to use (the server passes its own, which trusts a corporate proxy)."""
    p = urllib.parse.urlsplit(url)
    if p.scheme != 'https' or p.netloc.lower() in NEVER_HOSTS:
        return None, 'not requested (sign-in or non-https host)'
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,application/atom+xml,application/json;q=0.9,*/*;q=0.5', 'Accept-Encoding': 'gzip'})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            raw = r.read(MAX_BYTES + 1)
            if r.headers.get('Content-Encoding') == 'gzip':
                raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                return None, 'page larger than 2.5 MB'
            enc = (r.headers.get_content_charset() or 'utf-8')
            return raw.decode(enc, errors='replace'), None
    except urllib.error.HTTPError as e:
        return None, f'HTTP {e.code}'
    except Exception as e:   # offline, DNS, TLS, timeout: all the same to the caller
        return None, f'{type(e).__name__}: {str(e)[:80]}'


# ── page -> text ───────────────────────────────────────────────────────────────────────────────
class _Extract(HTMLParser):
    SKIP = {'script', 'style', 'noscript', 'svg', 'nav', 'footer', 'header', 'aside', 'form', 'button', 'iframe'}
    BLOCK = {'p', 'div', 'section', 'article', 'main', 'tr', 'table', 'ul', 'ol', 'br', 'pre', 'blockquote', 'dl', 'dt', 'dd'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip, self.title, self._in_title, self.main_depth, self.found_main = [], 0, '', False, 0, False
        self.all = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        if tag == 'title':
            self._in_title = True
        if tag in ('main', 'article') and not self.found_main:
            self.found_main = True
        if tag in self.BLOCK or tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'):
            self._both('\n')
            if tag == 'li':
                self._both('- ')
            if tag[0] == 'h' and len(tag) == 2:
                self._both('#' * int(tag[1]) + ' ')

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        if tag == 'title':
            self._in_title = False
        if tag in self.BLOCK or tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th'):
            self._both('\n' if tag not in ('td', 'th') else ' | ')

    def _both(self, s):
        if not self.skip:
            self.all.append(s)
            if self.found_main:
                self.out.append(s)

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self.skip:
            return
        self.all.append(data)
        if self.found_main:
            self.out.append(data)


def _clean(text):
    lines = [re.sub(r'[ \t ]+', ' ', l).strip() for l in text.split('\n')]
    out, blank = [], 0
    for l in lines:
        if not l or l in ('-', '|'):
            blank += 1
            if blank == 1 and out:
                out.append('')
            continue
        blank = 0
        out.append(l)
    return '\n'.join(out).strip()


def html_to_text(page):
    """(title, text) of a page: the main/article block when the page has one, otherwise the whole body; feeds (Atom) become one line per entry."""
    if not page:
        return '', ''
    if page.lstrip().startswith('<?xml') or '<feed' in page[:400]:
        entries = re.findall(r'<entry>.*?</entry>', page, flags=re.S)
        lines = []
        for e in entries[:60]:
            t = _html.unescape(re.sub(r'<[^>]+>', '', (re.search(r'<title[^>]*>(.*?)</title>', e, flags=re.S) or [0, ''])[1])).strip()
            u = (re.search(r'<updated>(.*?)</updated>', e) or [0, ''])[1][:10]
            lines.append(f'- {t} ({u})')
        return 'feed', '\n'.join(lines)
    p = _Extract()
    try:
        p.feed(page)
    except Exception:
        pass
    main = _clean(''.join(p.out))
    text = main if len(main) > 400 else _clean(''.join(p.all))
    return _clean(p.title), text


# ── facts a page states ─────────────────────────────────────────────────────────────────────────
_VERSION_RX = {
    'ONTAP': r'\b(9\.\d{1,2}\.\d{1,2}(?:P\d{1,3})?)\b',
    'StorageGRID': r'StorageGRID\s+(1[1-9]\.\d{1,2}(?:\.\d{1,2})?)',
    'Trident': r'\b(2\d\.(?:0[1-9]|1[0-2])(?:\.\d)?)\b',
    'SnapCenter': r'SnapCenter\s+(?:Software\s+)?(\d\.\d{1,2}(?:\.\d{1,2})?)',
    'SANtricity': r'SANtricity\s+(?:OS\s+)?(1[0-2]\.\d{1,2}(?:\.\d{1,2})?)',
    'ONTAP tools': r'ONTAP tools(?: for VMware vSphere)?\s+(\d{1,2}\.\d{1,2}(?:\.\d)?)',
    'Host Utilities': r'Host Utilities\s+(\d\.\d{1,2}(?:\.\d)?)',
}
_ID_RX = {
    'cve': r'\bCVE-\d{4}-\d{4,7}\b',
    'advisory': r'\bntap-\d{8}-\d{4}\b',
    'kb': r'\b(?:CONTAP|CFBMC|CFDIAGS|CFHWD|CFFSI|CFOHW|CFNET|CFSP|CFIOM|CFNSM)-\d{2,7}\b',
    'tr': r'\bTR-\d{4}(?:-\d+)?\b',
}


def _vt(v):
    return tuple(int(x) for x in re.findall(r'\d+', str(v))[:4]) + ((0,) if 'P' not in str(v) else (int(re.search(r'P(\d+)', str(v)).group(1)),))


def extract_facts(text):
    """{'versions': {product: [..]}, 'ids': {kind: [..]}} found in the page text (sorted, capped)."""
    versions, ids = {}, {}
    for prod, rx in _VERSION_RX.items():
        found = sorted(set(re.findall(rx, text)), key=_vt)
        if found:
            versions[prod] = found[-40:]
    for kind, rx in _ID_RX.items():
        found = sorted(set(re.findall(rx, text)))
        if found:
            ids[kind] = found[:300]
    return {'versions': versions, 'ids': ids}


# ── what ARIA already holds ────────────────────────────────────────────────────────────────────
def _jload(path):
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def aria_holdings(base_dir):
    """The ids and release numbers ARIA's own data already carries."""
    data = os.path.join(base_dir, 'data')
    ids, versions = set(), {}
    text_blobs = []
    for fname in ('security_bulletins.json', 'advisory_index.json', 'advisory_resolutions.json', 'knowledge_base.json', 'firmware_baselines.json', 'imt_interop.json', 'derived_reference.json', 'ontap_release_notes.json', 'eoa_database.json'):
        try:
            with open(os.path.join(data, fname), 'r', encoding='utf-8', errors='replace') as fh:
                text_blobs.append(fh.read())
        except OSError:
            pass
    try:
        with open(os.path.join(base_dir, 'resolution_rules.json'), 'r', encoding='utf-8', errors='replace') as fh:
            text_blobs.append(fh.read())
    except OSError:
        pass
    blob = '\n'.join(text_blobs)
    for rx in _ID_RX.values():
        ids.update(re.findall(rx, blob))
    vc = _jload(os.path.join(data, 'version_catalog.json'))
    for prod, key in (('ONTAP', 'ontap'), ('StorageGRID', 'storagegrid'), ('SANtricity', 'santricity')):
        versions[prod] = set(str(v) for v in (vc.get(key) or []))
    return {'ids': ids, 'versions': versions, 'blob': blob}


def _version_known(prod, v, hold):
    if v in hold['blob']:
        return True
    known = hold['versions'].get(prod)
    if known:
        return any(k == v or k.startswith('.'.join(v.split('.')[:2])) for k in known)
    return False


# ── sources ───────────────────────────────────────────────────────────────────────────────────
def _slug(url):
    p = urllib.parse.urlsplit(url)
    s = re.sub(r'[^A-Za-z0-9]+', '-', (p.netloc + p.path)).strip('-')[:90]
    return f'{s}-{hashlib.sha1(url.encode()).hexdigest()[:6]}'


def library_sources(library_root):
    """(category, title, url) of every library document that names a public source page."""
    out = []
    if not library_root or not os.path.isdir(library_root):
        return out
    for dp, _dn, fs in os.walk(library_root):
        for f in fs:
            if not f.lower().endswith('.md'):
                continue
            try:
                with open(os.path.join(dp, f), 'r', encoding='utf-8', errors='replace') as fh:
                    head = fh.read(1500)
            except OSError:
                continue
            m = re.search(r'^Source:\s*(https?://\S+)', head, flags=re.M)
            if not m:
                continue
            t = (re.search(r'^#\s+(.+)$', head, flags=re.M) or [0, os.path.splitext(f)[0]])[1].strip()
            rel = os.path.relpath(dp, library_root).replace('\\', '/')
            out.append((rel.split('/')[0] if rel != '.' else 'General', t, m.group(1).strip().rstrip(').,')))
    return out


def playbook_sources(base_dir):
    """{url: [playbook ids]} for every approved playbook (tools/playbooks.json and data/playbooks_local.json) and the NetApp pages it lists as sources. Sign-in hosts are left out."""
    out = {}
    try:
        import playbooks as _pb
        ld = _pb.load(os.path.join(base_dir, 'data'), os.path.join(base_dir, 'tools', 'playbooks.json'))
    except Exception:
        return out
    for e in ld['playbooks']:
        for u in e.get('sources') or []:
            h = urllib.parse.urlsplit(str(u)).netloc.lower()
            if str(u).startswith('https://') and h in ALLOWED_HOSTS and h not in NEVER_HOSTS:
                out.setdefault(str(u), [])
                if e['id'] not in out[str(u)]:
                    out[str(u)].append(e['id'])
    try:
        import playbook_verify as _pv
        for url, ids in _pv.command_pages(os.path.join(base_dir, 'data')).items():
            lst = out.setdefault(url, [])
            lst.extend(i for i in ids if i not in lst)
    except Exception:
        pass
    return out


def load_sources(base_dir, library_root=None):
    """Key pages first, then the library's own sources (or the shipped list when there is no library folder); one entry per URL, allowed hosts only."""
    seen, out = set(), []

    def add(cat, title, url, key):
        h = urllib.parse.urlsplit(url).netloc.lower()
        if url in seen or h in NEVER_HOSTS or h not in ALLOWED_HOSTS:
            return
        if h == 'kb.netapp.com' and not key:   # individual KB articles are not read; only the index is
            return
        seen.add(url)
        out.append({'url': url, 'category': cat, 'title': title, 'key': key})

    for cat, title, url in KEY_PAGES:
        add(cat, title, url, True)
    lib = library_sources(library_root)
    if not lib:
        shipped = _jload(os.path.join(base_dir, 'tools', SOURCES_NAME)).get('sources') or []
        lib = [(s.get('category', 'General'), s.get('title', ''), s.get('url', '')) for s in shipped]
    for cat, title, url in lib:
        if url:
            add(cat, title, url, False)
    # the pages the remediation playbooks were written from: a change to one is a reason to re-read the procedure
    for url, ids in sorted(playbook_sources(base_dir).items()):
        add('Playbooks', 'Playbook source (' + ', '.join(ids[:3]) + (', ...' if len(ids) > 3 else '') + ')', url, False)
    return out


def write_shipped_sources(base_dir, library_root):
    """Save the library's source list (urls only) so a machine without the library folder can still sweep."""
    items = [{'category': c, 'title': t, 'url': u} for c, t, u in library_sources(library_root)
             if urllib.parse.urlsplit(u).netloc.lower() in ALLOWED_HOSTS and urllib.parse.urlsplit(u).netloc.lower() != 'kb.netapp.com']
    items.sort(key=lambda x: (x['category'], x['url']))
    p = os.path.join(base_dir, 'tools', SOURCES_NAME)
    with open(p, 'w', encoding='utf-8') as fh:
        json.dump({'note': 'Public pages the NetApp Reference Library is built from (addresses only), used by the reference updater when the library folder is not on this machine.', 'sources': items}, fh, indent=1, ensure_ascii=False)
    return len(items)


# ── compare ───────────────────────────────────────────────────────────────────────────────────
_NOISE = re.compile(r'^(?:last (?:updated|modified)|published|updated|fetched)\b|^\d{1,2}/\d{1,2}/\d{2,4}$|^\d{4}-\d{2}-\d{2}', re.I)


def _real_lines(text):
    return [l for l in text.split('\n') if l.strip() and not _NOISE.match(l.strip())]


def compare(prev_text, new_text, prev_facts, new_facts):
    """Events between two reads of one page."""
    ev = []
    for prod, now in (new_facts.get('versions') or {}).items():
        was = (prev_facts.get('versions') or {}).get(prod) or []
        if was and _vt(now[-1]) > _vt(was[-1]):
            ev.append({'kind': 'new-version', 'product': prod, 'was': was[-1], 'now': now[-1]})
    for kind, now in (new_facts.get('ids') or {}).items():
        was = set((prev_facts.get('ids') or {}).get(kind) or [])
        fresh = [i for i in now if i not in was]
        if fresh and was:
            ev.append({'kind': 'new-id', 'idKind': kind, 'ids': fresh[:25]})
    a, b = _real_lines(prev_text or ''), _real_lines(new_text or '')
    if a != b:
        d = list(difflib.unified_diff(a, b, lineterm='', n=0))
        add = [l[1:].strip() for l in d if l.startswith('+') and not l.startswith('+++')]
        rem = [l[1:].strip() for l in d if l.startswith('-') and not l.startswith('---')]
        if len(add) + len(rem) >= 2:
            ev.append({'kind': 'changed', 'added': [x[:170] for x in add[:6]], 'removed': [x[:170] for x in rem[:3]], 'addedCount': len(add), 'removedCount': len(rem)})
    return ev


# ── review queue ─────────────────────────────────────────────────────────────────────────────
def _item_id(*parts):
    return hashlib.sha1('|'.join(str(p) for p in parts).encode()).hexdigest()[:12]


def make_fetch(ctx_getter):
    """A fetch function that uses the caller's ssl context."""
    return lambda url: http_get(url, ctx=ctx_getter() if ctx_getter else None)


def kb_stub(kb_id, page_title, page_url, today):
    """A rules-file stub for a known-issue article id. Nothing is invented: the summary is left for the reader to fill from the article."""
    comp = {'CFBMC': 'BMC', 'CFSP': 'SP', 'CFDIAGS': 'CARD', 'CFNSM': 'SHELF', 'CFIOM': 'SHELF', 'CFHWD': 'DISK'}.get(kb_id.split('-')[0], '')
    return {'id': kb_id, 'component': comp or '(set from the article)', 'families': [], 'versions': [], 'summary': '(read the article: what the issue is)',
            'url': f'https://kb.netapp.com/on-prem/ontap/OHW/OHW-Kbs/{kb_id}', 'source': f'Named on {page_title}' + (f' ({page_url})' if page_url else '') + f'; recorded by the ARIA reference updater on {today}; article body not read'}


def load_queue(data_dir):
    return _jload(os.path.join(data_dir, QUEUE_NAME)).get('items') or {}


def save_queue(data_dir, items):
    tmp = os.path.join(data_dir, QUEUE_NAME + '.tmp')
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump({'items': items}, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, os.path.join(data_dir, QUEUE_NAME))


def ack(data_dir, ids, note=''):
    q = load_queue(data_dir)
    n = 0
    for i in ids:
        if i in q and q[i].get('status') != 'acknowledged':
            q[i]['status'] = 'acknowledged'
            q[i]['ackedAt'] = datetime.now(timezone.utc).isoformat()
            q[i]['note'] = note
            n += 1
    save_queue(data_dir, q)
    return n


# ── tables ───────────────────────────────────────────────────────────────────────────────────
def tables_status(base_dir, pages):
    """Status of each curated reference table. A scanner-kept table is current when its backing file is fresh; a hand-kept one lists the official
    pages that changed after the table file was last written (so 'static (manual)' says what to look at)."""
    data = os.path.join(base_dir, 'data')
    ref = os.path.join(data, 'reference_library.js')
    ref_mtime = os.path.getmtime(ref) if os.path.isfile(ref) else 0
    out = []
    now = time.time()
    for key, label, mode, backing, rx in TABLES:
        rxc = re.compile(rx, re.I)
        changed = [{'title': p.get('title', ''), 'url': u, 'changedAt': p['changedAt']} for u, p in pages.items()
                   if p.get('changedAt') and rxc.search(u) and _iso_ts(p['changedAt']) > ref_mtime]
        updated, age_h = '', None
        if backing and os.path.isfile(os.path.join(data, backing)):
            mt = os.path.getmtime(os.path.join(data, backing))
            updated, age_h = datetime.fromtimestamp(mt, timezone.utc).strftime('%Y-%m-%d'), round((now - mt) / 3600, 1)
        elif ref_mtime:
            updated, age_h = datetime.fromtimestamp(ref_mtime, timezone.utc).strftime('%Y-%m-%d'), round((now - ref_mtime) / 3600, 1)
        if mode == 'scanner':
            status = 'kept up to date' if age_h is not None and age_h < 24 * 10 else 'stale'
        elif mode == 'partial':
            status = 'review' if changed else 'kept up to date (ranges by hand)'
        else:
            status = 'review' if changed else 'no source change seen'
        out.append({'key': key, 'label': label, 'mode': mode, 'updated': updated, 'status': status, 'changedSources': changed[:6], 'changedCount': len(changed)})
    return out


def _iso_ts(s):
    try:
        return datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
    except (ValueError, AttributeError):
        return 0


# ── library changelog cross-check ───────────────────────────────────────────────────────────
def crosscheck_library(base_dir, library_root, lm):
    """Read the library's unseen CHANGELOG entries for ids and release numbers and look each up in ARIA's data."""
    if not library_root or lm is None:
        return {'entries': [], 'items': []}
    data_dir = os.path.join(base_dir, 'data')
    todo = lm.unharvested(library_root, data_dir)
    if todo is None:
        todo = lm.changelog_headings(library_root)[:3]
    hold = aria_holdings(base_dir)
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    entries, items = [], []
    for h in todo[:12]:
        text = lm.changelog_entry(library_root, h)
        facts = extract_facts(text)
        gaps = []
        for kind, ids in facts['ids'].items():
            if kind == 'tr':   # a Technical Report number is a document reference, not data ARIA keeps
                continue
            for i in ids:
                if i not in hold['ids']:
                    gaps.append({'kind': kind, 'id': i})
        for prod, vs in facts['versions'].items():
            if vs and not _version_known(prod, vs[-1], hold) and prod in ('ONTAP', 'StorageGRID', 'SANtricity'):
                gaps.append({'kind': 'version', 'id': f'{prod} {vs[-1]}'})
        quiet = bool(re.search(r'no material changes', text, re.I))
        entries.append({'heading': h, 'quiet': quiet, 'gaps': len(gaps)})
        if gaps:
            items.append({'id': _item_id('library', h, len(gaps)), 'kind': 'library-entry', 'title': f'Library entry {h}', 'detail': f'{len(gaps)} id or release number named that ARIA does not hold: ' + ', '.join(g['id'] for g in gaps[:12]),
                          'url': '', 'category': 'Library', 'stubs': [kb_stub(g['id'], f'library entry {h}', '', today) for g in gaps if g['kind'] == 'kb'][:8]})
    return {'entries': entries, 'items': items, 'todo': todo}


# ── the run ──────────────────────────────────────────────────────────────────────────────────
def load_state(data_dir):
    s = _jload(os.path.join(data_dir, STATE_NAME))
    s.setdefault('pages', {})
    return s


def save_json(path, obj):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


def run_update(base_dir, cfg=None, fetch=http_get, budget=30, log=print, sleep=time.sleep, library_manager=None):
    """One sweep. Returns the report (also written to data/library_update_report.json)."""
    cfg = cfg or {}
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(os.path.join(data_dir, CACHE_DIR), exist_ok=True)
    started = datetime.now(timezone.utc)
    today = started.strftime('%Y-%m-%d')
    lm = library_manager
    lib_root = ''
    if lm is not None:
        try:
            lib_root = lm.find_library(cfg).get('path') or ''
        except Exception:
            lib_root = ''
    sources = load_sources(base_dir, lib_root)
    state = load_state(data_dir)
    pages = state['pages']
    keyp = [s for s in sources if s['key']]
    rest = sorted((s for s in sources if not s['key']), key=lambda s: pages.get(s['url'], {}).get('fetchedAt') or '')
    batch = keyp + rest[:max(0, budget)]
    hold = aria_holdings(base_dir)
    queue = load_queue(data_dir)
    pbmap = playbook_sources(base_dir)
    events, checked, failed, changed_n, baselined = [], 0, [], 0, 0
    for n, src in enumerate(batch):
        url = src['url']
        if n:
            sleep(RATE_SECONDS)
        page, err = fetch(url)
        rec = pages.setdefault(url, {'title': src['title'], 'category': src['category']})
        rec['title'], rec['category'] = src['title'], src['category']
        checked += 1
        if err or not page:
            rec['failures'] = rec.get('failures', 0) + 1
            rec['lastError'] = err or 'empty'
            failed.append({'url': url, 'title': src['title'], 'error': rec['lastError']})
            if rec['failures'] == 3:
                iid = _item_id('unreachable', url)
                queue.setdefault(iid, {'id': iid, 'kind': 'source-unreachable', 'title': src['title'], 'detail': f'Not readable on {rec["failures"]} runs in a row ({rec["lastError"]}). The page may have moved or is no longer public.', 'url': url, 'category': src['category'], 'firstSeen': today, 'status': 'open'})
            continue
        rec['failures'] = 0
        rec.pop('lastError', None)
        title, text = html_to_text(page)
        if len(text) < 200:
            rec['gated'] = True
            rec['fetchedAt'] = started.isoformat()
            continue
        rec.pop('gated', None)
        facts = extract_facts(text)
        cache = os.path.join(data_dir, CACHE_DIR, src['category'], _slug(url) + '.md')
        prev_text = ''
        try:
            with open(cache, 'r', encoding='utf-8') as fh:
                prev_text = fh.read().split('\n\n', 1)[-1]
        except OSError:
            pass
        ev = compare(prev_text, text, rec.get('facts') or {}, facts) if prev_text and rec.get('facts') else []
        if not prev_text:
            baselined += 1
        digest = hashlib.sha1(text.encode('utf-8')).hexdigest()
        if rec.get('hash') and rec['hash'] != digest:
            rec['changedAt'] = started.isoformat()
            changed_n += 1
        elif not rec.get('hash'):
            rec['firstSeenAt'] = started.isoformat()
        rec.update({'hash': digest, 'fetchedAt': started.isoformat(), 'bytes': len(text), 'facts': {'versions': {k: v[-6:] for k, v in facts['versions'].items()}, 'ids': {k: v[:300] for k, v in facts['ids'].items()}}})
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        with open(cache, 'w', encoding='utf-8') as fh:
            fh.write(f'# {title or src["title"]}\nSource: {url}\nFetched: {today}\nAuto-refreshed by the ARIA reference updater (text of the page; no AI). The curated library copy, if any, is separate.\n\n{text}')
        for e in ev:
            if e['kind'] == 'changed' and url in pbmap:
                ids = pbmap[url]
                iid = _item_id('pbsrc', url, digest[:8])
                queue.setdefault(iid, {'id': iid, 'kind': 'playbook-source-changed', 'category': 'Procedures',
                                       'title': 'Re-read playbook' + ('s ' if len(ids) != 1 else ' ') + ', '.join(ids[:4]) + (', ...' if len(ids) > 4 else '') + ': its NetApp source page changed',
                                       'detail': f'{e["addedCount"]} line(s) added, {e["removedCount"]} removed on the page the procedure was written from. Added: ' + ' | '.join(e['added'][:4]) + ('. Removed: ' + ' | '.join(e['removed'][:2]) if e['removed'] else '') +
                                                 '. Compare the page with the steps of the playbook (docs/PLAYBOOKS.md); if a command, menu path or prerequisite changed, correct the entry (a copy with the same id in data/playbooks_local.json overrides the shipped one), then close this item.',
                                       'url': url, 'status': 'open', 'firstSeen': today, 'playbooks': ids})
            e.update({'url': url, 'title': src['title'], 'category': src['category']})
            events.append(e)
            if e['kind'] == 'new-version':
                covered = _version_known(e['product'], e['now'], hold)
                e['covered'] = covered
                if not covered:
                    iid = _item_id('version', e['product'], e['now'])
                    queue.setdefault(iid, {'id': iid, 'kind': 'new-version', 'title': f'{e["product"]} {e["now"]}', 'detail': f'{e["product"]} {e["now"]} appears on "{src["title"]}" (the page showed {e["was"]} last time). ARIA\'s release data does not hold it yet; the release scanner is run, and if it still does not, the page needs reading.', 'url': url, 'category': src['category'], 'firstSeen': today, 'status': 'open'})
            elif e['kind'] == 'new-id':
                miss = [i for i in e['ids'] if i not in hold['ids']]
                e['covered'] = not miss
                if miss:
                    iid = _item_id('ids', url, ','.join(miss))
                    queue.setdefault(iid, {'id': iid, 'kind': 'new-id', 'title': f'{len(miss)} new {e["idKind"].upper()} id{"s" if len(miss) != 1 else ""}: ' + ', '.join(miss[:6]), 'detail': f'Named on "{src["title"]}" and not in ARIA\'s data.', 'url': url, 'category': src['category'], 'firstSeen': today, 'status': 'open',
                                           'stubs': [kb_stub(i, src['title'], url, today) for i in miss if e['idKind'] == 'kb'][:8]})
            elif e['kind'] == 'changed' and src['key'] and not any(x['kind'] in ('new-version', 'new-id') for x in ev):   # a change a new release or id already explains is not queued twice
                iid = _item_id('changed', url, digest[:8])
                queue.setdefault(iid, {'id': iid, 'kind': 'page-changed', 'title': f'{src["title"]} changed', 'detail': f'{e["addedCount"]} line(s) added, {e["removedCount"]} removed. Added: ' + ' | '.join(e['added'][:4]), 'url': url, 'category': src['category'], 'firstSeen': today, 'status': 'open'})
    state['pages'] = pages
    state['lastRun'] = started.isoformat()
    lib = crosscheck_library(base_dir, lib_root, lm) if lib_root else {'entries': [], 'items': []}
    for it in lib['items']:
        it.setdefault('firstSeen', today)
        it.setdefault('status', 'open')
        queue.setdefault(it['id'], it)
    quiet_done = [e['heading'] for e in lib['entries'] if e['quiet'] and not e['gaps']]
    auto_marked = False
    if lib['entries'] and len(quiet_done) == len(lib['entries']) and lm is not None:
        try:
            lm.mark_harvested(lib_root, data_dir, 'auto: every unseen entry says no material changes and names nothing ARIA lacks (ARIA reference updater)')
            auto_marked = True
        except Exception:
            pass
    save_json(os.path.join(data_dir, STATE_NAME), state)
    save_queue(data_dir, queue)
    relevant = any(e['kind'] in ('new-version', 'new-id') for e in events) or any(
        (p.get('changedAt') and _iso_ts(p['changedAt']) >= started.timestamp() - 1) and re.search(r'release-support|eoa|ontap-systems|security\.netapp|ontap-whatsnew', u) for u, p in pages.items())
    open_items = [i for i in queue.values() if i.get('status') == 'open']
    report = {
        'startedAt': started.isoformat(), 'finishedAt': datetime.now(timezone.utc).isoformat(), 'sources': len(sources), 'checked': checked, 'baselined': baselined, 'changedPages': changed_n,
        'unreachable': failed[:20], 'gated': [u for u, p in pages.items() if p.get('gated')][:20], 'events': events[:60], 'scannersNeeded': bool(relevant),
        'library': {'found': bool(lib_root), 'entriesRead': [e['heading'] for e in lib['entries']], 'autoMarkedHarvested': auto_marked},
        'playbookPages': len(pbmap), 'openItems': len(open_items), 'neverChecked': sum(1 for s in sources if s['url'] not in pages or not pages[s['url']].get('hash')),
        'tables': tables_status(base_dir, pages),
    }
    save_json(os.path.join(data_dir, REPORT_NAME), report)
    log(f'  [LIBRARY] Reference updater: {checked} page(s) read, {changed_n} changed, {len(events)} event(s), {len(open_items)} open review item(s)')
    return report


def status(base_dir):
    data_dir = os.path.join(base_dir, 'data')
    rep = _jload(os.path.join(data_dir, REPORT_NAME))
    state = load_state(data_dir)
    q = [i for i in load_queue(data_dir).values() if i.get('status') == 'open']
    q.sort(key=lambda i: (i.get('kind') != 'new-version', i.get('firstSeen', '')), reverse=False)
    out = dict(rep) if rep else {}
    out['queue'] = q[:60]
    out['openItems'] = len(q)
    out['pagesKnown'] = len(state.get('pages') or {})
    out['lastRun'] = state.get('lastRun') or ''
    if not rep:
        out['tables'] = tables_status(base_dir, state.get('pages') or {})
    return out


class Scheduler:
    """Runs one sweep soon after start-up and then every interval; a run is a batch, so the whole source list is covered over a few runs."""

    def __init__(self, base_dir, cfg_loader, interval_hours=24, budget=30, on_relevant=None, library_manager=None, log=print, fetch=None):
        self.base_dir, self.cfg_loader, self.interval, self.budget = base_dir, cfg_loader, max(1, interval_hours) * 3600, budget
        self.on_relevant, self.lm, self.log, self.fetch = on_relevant, library_manager, log, fetch or http_get
        self._lock = threading.Lock()
        self._running = False
        self._timer = None

    def running(self):
        return self._running

    def start(self, delay=300):
        self._timer = threading.Timer(delay, self._tick)
        self._timer.daemon = True
        self._timer.start()

    def stop(self):
        if self._timer:
            self._timer.cancel()

    def _tick(self):
        try:
            cfg = self.cfg_loader() or {}
            if cfg.get('libraryUpdateEnabled', True):
                self.run_now(sync=True)
        finally:
            self._timer = threading.Timer(self.interval, self._tick)
            self._timer.daemon = True
            self._timer.start()

    def run_now(self, sync=False):
        with self._lock:
            if self._running:
                return {'started': False, 'reason': 'already running'}
            self._running = True

        def work():
            try:
                cfg = self.cfg_loader() or {}
                rep = run_update(self.base_dir, cfg, fetch=self.fetch, budget=int(cfg.get('libraryUpdateBudget') or self.budget), log=self.log, library_manager=self.lm)
                if rep.get('scannersNeeded') and self.on_relevant:
                    try:
                        self.on_relevant()
                    except Exception as e:
                        self.log(f'  [LIBRARY] Scanner run after a change failed: {e}')
            except Exception as e:
                self.log(f'  [LIBRARY] Reference updater failed: {type(e).__name__}: {e}')
            finally:
                self._running = False
        if sync:
            work()
        else:
            threading.Thread(target=work, daemon=True).start()
        return {'started': True}


if __name__ == '__main__':
    # python tools/library_updater.py [--budget N] [--seed]   one sweep now / write tools/library_sources.json from the library folder
    import argparse
    import sys
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(here, 'tools'))
    import library_manager as _lm
    ap = argparse.ArgumentParser()
    ap.add_argument('--budget', type=int, default=30)
    ap.add_argument('--seed', action='store_true')
    a = ap.parse_args()
    cfg = _jload(os.path.join(here, 'aiq_config.json'))
    if a.seed:
        root = _lm.find_library(cfg).get('path')
        print('wrote', write_shipped_sources(here, root), 'sources' if root else '(no library folder found)')
    else:
        rep = run_update(here, cfg, budget=a.budget, library_manager=_lm)
        print(json.dumps({k: v for k, v in rep.items() if k not in ('tables', 'events')}, indent=1, ensure_ascii=False))
