"""NetApp Reference Library reader and reference-data freshness registry.

No AI and no network access: this module only reads files on disk. It

  * finds the library folder (config `libraryPath`, env ARIA_LIBRARY_PATH, or the usual cloud-drive locations on
    Windows and macOS),
  * reports how fresh the library is (INDEX.md "Last compiled", newest CHANGELOG entry, newest file),
  * builds a searchable index of its markdown files and answers keyword searches with snippets,
  * lists how old every reference data file ARIA keeps is, so a stale source is visible instead of silent.

The library itself is kept up to date by whatever maintains that folder; ARIA only reads it.
"""
import glob
import json
import os
import re
import threading
import time
from datetime import datetime, timezone

STALE_LIBRARY_DAYS = 14
_LIB_MARKER = 'INDEX.md'
_LIB_NAME = 'NetApp Reference Library'
_MAX_FILE_BYTES = 3 * 1024 * 1024
_index_lock = threading.Lock()
_index_cache = {'sig': None, 'docs': [], 'root': None}


# ── locating the folder ──────────────────────────────────────────────────────
def _candidate_paths():
    home = os.path.expanduser('~')
    tail = os.path.join('Cowork', 'NetApp', _LIB_NAME)
    out = []
    # macOS: Google Drive for desktop mounts under ~/Library/CloudStorage/GoogleDrive-<account>/My Drive
    out += glob.glob(os.path.join(home, 'Library', 'CloudStorage', 'GoogleDrive-*', 'My Drive', tail))
    out += glob.glob(os.path.join(home, 'Library', 'CloudStorage', 'GoogleDrive-*', 'My Drive', 'Cowork', _LIB_NAME))
    out += [os.path.join(home, 'Google Drive', 'My Drive', tail), os.path.join(home, 'Google Drive', tail),
            os.path.join(home, 'My Drive', tail), os.path.join(home, 'Documents', tail), os.path.join(home, tail)]
    # Windows: Google Drive is a drive letter (G:\My Drive) or a folder under the profile
    if os.name == 'nt':
        for letter in 'GHDEFIJKLMNOPQRSTUVWXYZ':
            out.append(f'{letter}:\\My Drive\\{tail}')
            out.append(f'{letter}:\\My Drive\\Cowork\\{_LIB_NAME}')
    return out


def find_library(cfg=None):
    """Return {'path', 'source'} for the library folder, or {'path': '', 'source': 'not found'}."""
    cfg = cfg or {}
    tried = []
    for src, p in (('config (libraryPath)', (cfg.get('libraryPath') or '').strip()),
                   ('environment (ARIA_LIBRARY_PATH)', (os.environ.get('ARIA_LIBRARY_PATH') or '').strip())):
        if p:
            p = os.path.expanduser(p)
            tried.append(p)
            if os.path.isfile(os.path.join(p, _LIB_MARKER)):
                return {'path': p, 'source': src}
    for p in _candidate_paths():
        if os.path.isfile(os.path.join(p, _LIB_MARKER)):
            return {'path': p, 'source': 'auto-detected'}
    return {'path': '', 'source': 'not found', 'tried': tried}


# ── freshness ────────────────────────────────────────────────────────────────
def _read(path, limit=None):
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as fh:
            return fh.read(limit) if limit else fh.read()
    except OSError:
        return ''


def _parse_date(s):
    try:
        return datetime.strptime(s, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def library_status(root):
    """Freshness and size of the library at `root`."""
    if not root or not os.path.isdir(root):
        return {'found': False}
    idx = _read(os.path.join(root, 'INDEX.md'), 20000)
    m = re.search(r'Last compiled:\s*(\d{4}-\d{2}-\d{2})', idx)
    compiled = m.group(1) if m else ''
    chlog = _read(os.path.join(root, 'CHANGELOG.md'), 60000)
    entries = re.findall(r'^##\s+(\d{4}-\d{2}-\d{2})\s*[—-]\s*(.+)$', chlog, flags=re.M)
    last_entry = {'date': entries[0][0], 'title': entries[0][1].strip()} if entries else {}
    cats, newest_file, n_docs = [], 0, 0
    for name in sorted(os.listdir(root)):
        d = os.path.join(root, name)
        if not os.path.isdir(d):
            continue
        files = [os.path.join(dp, f) for dp, _dn, fs in os.walk(d) for f in fs if f.lower().endswith('.md')]
        if not files:
            continue
        mt = max(os.path.getmtime(f) for f in files)
        newest_file = max(newest_file, mt)
        n_docs += len(files)
        cats.append({'name': name, 'docs': len(files), 'newest': datetime.fromtimestamp(mt, timezone.utc).strftime('%Y-%m-%d')})
    now = datetime.now(timezone.utc)
    ref = _parse_date(compiled) or _parse_date(last_entry.get('date'))
    age = (now - ref).days if ref else None
    return {
        'found': True, 'path': root, 'compiled': compiled, 'lastEntry': last_entry, 'docs': n_docs, 'categories': cats,
        'newestFile': datetime.fromtimestamp(newest_file, timezone.utc).strftime('%Y-%m-%d') if newest_file else '',
        'ageDays': age, 'stale': age is None or age > STALE_LIBRARY_DAYS, 'staleAfterDays': STALE_LIBRARY_DAYS,
    }


# ── index and search ─────────────────────────────────────────────────────────
def _signature(root):
    n, newest = 0, 0.0
    for dp, _dn, fs in os.walk(root):
        for f in fs:
            if f.lower().endswith('.md'):
                n += 1
                try:
                    newest = max(newest, os.path.getmtime(os.path.join(dp, f)))
                except OSError:
                    pass
    return (root, n, newest)


def _build_index(root):
    docs = []
    for dp, _dn, fs in os.walk(root):
        for f in sorted(fs):
            if not f.lower().endswith('.md'):
                continue
            full = os.path.join(dp, f)
            try:
                if os.path.getsize(full) > _MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            text = _read(full)
            rel = os.path.relpath(full, root).replace('\\', '/')
            title = (re.search(r'^#\s+(.+)$', text, flags=re.M) or [None, os.path.splitext(f)[0]])[1].strip()
            src = (re.search(r'^Source:\s*(\S+)', text, flags=re.M) or [None, ''])[1]
            fetched = (re.search(r'^Fetched:\s*(\d{4}-\d{2}-\d{2})', text, flags=re.M) or [None, ''])[1]
            docs.append({'path': rel, 'title': title, 'category': rel.split('/')[0] if '/' in rel else 'General', 'source': src, 'fetched': fetched,
                         'modified': datetime.fromtimestamp(os.path.getmtime(full), timezone.utc).strftime('%Y-%m-%d'),
                         'text': text, 'lower': text.lower(), 'tlower': title.lower()})
    return docs


def _get_index(root):
    sig = _signature(root)
    with _index_lock:
        if _index_cache['sig'] != sig:
            _index_cache.update({'sig': sig, 'docs': _build_index(root), 'root': root})
        return _index_cache['docs']


def _snippet(text, lower, terms, width=240):
    pos = -1
    for t in terms:
        pos = lower.find(t)
        if pos >= 0:
            break
    if pos < 0:
        return ''
    start = max(0, pos - width // 3)
    end = min(len(text), start + width)
    s = re.sub(r'\s+', ' ', text[start:end]).strip()
    return ('… ' if start > 0 else '') + s + (' …' if end < len(text) else '')


def search(root, query, limit=25):
    """Keyword search: every term must appear in the document; title hits and repeated hits rank higher."""
    terms = [t for t in re.findall(r'[A-Za-z0-9][A-Za-z0-9._\-/]*', (query or '').lower()) if len(t) > 1]
    if not root or not terms:
        return {'query': query, 'results': [], 'total': 0}
    results = []
    for d in _get_index(root):
        low = d['lower']
        if not all(t in low for t in terms):
            continue
        score = sum(min(low.count(t), 20) for t in terms) + 25 * sum(1 for t in terms if t in d['tlower']) + (10 if d['path'].lower().endswith('readme.md') else 0)
        results.append((score, d))
    results.sort(key=lambda x: -x[0])
    out = [{'path': d['path'], 'title': d['title'], 'category': d['category'], 'source': d['source'], 'fetched': d['fetched'], 'modified': d['modified'],
            'snippet': _snippet(d['text'], d['lower'], terms), 'score': s} for s, d in results[:limit]]
    return {'query': query, 'results': out, 'total': len(results)}


def read_doc(root, rel):
    """Return a library markdown file's text; refuses anything outside the library folder or that is not markdown."""
    if not root or not rel or not rel.lower().endswith('.md'):
        return None
    full = os.path.realpath(os.path.join(root, rel))
    base = os.path.realpath(root)
    if os.path.commonpath([full, base]) != base or not os.path.isfile(full):
        return None
    return _read(full)


# ── reference data freshness (everything ARIA refreshes on its own) ──────────
# (label, file, refreshed by, stale after hours, note)
_SOURCES = [
    ('ONTAP / StorageGRID / SANtricity release list', 'version_catalog.json', 'built-in scanner (docs.netapp.com)', 48, ''),
    ('ONTAP release highlights (What\'s new pages)', 'ontap_release_notes.json', 'built-in scanner (docs.netapp.com)', 24 * 10, ''),
    ('Derived reference tables (release lines, minimum releases, platforms, caveats)', 'derived_reference.json', 'built-in scanner, derived from the sources above', 24 * 10, ''),
    ('End-of-availability dates', 'eoa_database.json', 'built-in scanner', 24 * 10, ''),
    ('Interoperability (IMT) versions', 'imt_interop.json', 'built-in scanner', 24 * 10, ''),
    ('Firmware baselines', 'firmware_baselines.json', 'built-in scanner', 24 * 10, ''),
    ('Platform hardware', 'platform_hardware.json', 'built-in scanner (docs.netapp.com)', 24 * 10, ''),
    ('NetApp security advisories (index)', 'advisory_index.json', 'built-in scanner (security.netapp.com)', 72, ''),
    ('Advisory fixes and workarounds', 'advisory_resolutions.json', 'built-in scanner (security.netapp.com)', 72, ''),
    ('Security bulletins', 'security_bulletins.json', 'built-in scanner (PSIRT, NVD, EPSS)', 48, ''),
    ('CISA known-exploited list', 'cisa_kev.json', 'built-in scanner (CISA)', 48, ''),
    ('Knowledge base', 'knowledge_base.json', 'built-in scanner (KB crawl)', 24 * 14, ''),
    ('Curated reference tables', 'reference_library.js', 'compiled by hand on this machine', None, 'Hand-kept: platform replacements, upgrade caveats, best practices. Everything above is applied over it'),
]


def data_freshness(data_dir):
    now = time.time()
    out = []
    for label, fname, by, stale_h, note in _SOURCES:
        p = os.path.join(data_dir, fname)
        if not os.path.isfile(p):
            out.append({'label': label, 'file': fname, 'refreshedBy': by, 'present': False, 'note': note or 'Not present on this machine yet', 'stale': stale_h is not None})
            continue
        mt = os.path.getmtime(p)
        age_h = (now - mt) / 3600.0
        out.append({'label': label, 'file': fname, 'refreshedBy': by, 'present': True, 'updated': datetime.fromtimestamp(mt, timezone.utc).strftime('%Y-%m-%d %H:%M'),
                    'ageHours': round(age_h, 1), 'staleAfterHours': stale_h, 'stale': bool(stale_h and age_h > stale_h), 'static': stale_h is None, 'note': note})
    return out
