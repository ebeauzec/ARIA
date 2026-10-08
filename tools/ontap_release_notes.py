"""ONTAP "What's new" harvester: ARIA builds its own per-release highlights from docs.netapp.com.

No AI and no sign-in: it reads NetApp's public release-notes pages (docs.netapp.com/us-en/ontap/release-notes/whats-new-<release>.html),
splits each into its sections and feature titles with plain HTML parsing, and writes data/ontap_release_notes.json. The app overlays
that file on the curated highlights so a new release appears without anyone editing a table.
"""
import html as _html
import json
import os
import re
import time
from datetime import datetime, timezone

BASE = 'https://docs.netapp.com/us-en/ontap/release-notes/whats-new-{slug}.html'
# sections that matter most to a TAM, in the order they are summarised
_SECTION_PRIORITY = ['Security', 'Data protection', 'SAN', 'NAS', 'Upgrade', 'Networking', 'S3 object storage', 'Storage resource management enhancements', 'System Manager']
_MIN_RELEASE = (9, 9)


def _text(fragment):
    t = re.sub(r'<[^>]+>', ' ', fragment or '')
    return re.sub(r'\s+', ' ', _html.unescape(t)).strip()


def parse_whats_new(page):
    """{section title: [{'title', 'detail'}]} from one What's new page."""
    page = re.sub(r'<script.*?</script>|<style.*?</style>|<nav.*?</nav>', '', page, flags=re.S | re.I)
    parts = re.split(r'<h2[^>]*>', page)
    out = {}
    for part in parts[1:]:
        head, _, body = part.partition('</h2>')
        title = _text(head)
        if not title or title.lower() in ('related information', 'what\'s next'):
            continue
        items = []
        for row in re.findall(r'<tr[^>]*>(.*?)</tr>', body, flags=re.S | re.I):
            cells = [_text(c) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, flags=re.S | re.I)]
            if cells and cells[0] and cells[0].lower() not in ('feature', 'description', 'new feature', 'update', 'enhancement'):
                items.append({'title': cells[0][:160], 'detail': (cells[1] if len(cells) > 1 else '')[:300]})
        if not items:
            for li in re.findall(r'<li[^>]*>(.*?)</li>', body, flags=re.S | re.I):
                t = _text(li)
                if 8 < len(t) < 300:
                    items.append({'title': t[:160], 'detail': ''})
        if items:
            out[title] = items
    return out


def summarise(sections, limit=700):
    """One readable line: the first features of the sections that matter most."""
    order = [s for s in _SECTION_PRIORITY if s in sections] + [s for s in sections if s not in _SECTION_PRIORITY]
    chunks = []
    for s in order:
        titles = [i['title'] for i in sections[s][:2]]
        chunks.append(f"{s}: " + '; '.join(titles))
    text = ' | '.join(chunks)
    return text if len(text) <= limit else text[:limit].rsplit(' ', 1)[0] + ' …'


def _release_tuple(v):
    m = re.match(r'^(\d+)\.(\d+)', v or '')
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def harvest(data_dir, releases, fetch, force=False, max_age_hours=72):
    """Refresh data/ontap_release_notes.json. `fetch(url)` returns (text, error). Returns a short result dict.
    A release that already has notes is not fetched again (release notes of a shipped version do not change much), except the newest
    two releases, which NetApp keeps editing."""
    path = os.path.join(data_dir, 'ontap_release_notes.json')
    cur = {}
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            cur = json.load(fh)
    except (OSError, ValueError):
        cur = {}
    if not force and cur.get('fetchedAt'):
        try:
            age = (datetime.now(timezone.utc) - datetime.fromisoformat(cur['fetchedAt'])).total_seconds() / 3600
            if age < max_age_hours:
                return {'skipped': 'fresh'}
        except ValueError:
            pass
    rels = sorted({r for r in releases if _release_tuple(r) >= _MIN_RELEASE and re.match(r'^\d+\.\d+\.\d+$', r)}, key=_release_tuple)
    known = cur.get('releases') or {}
    newest = set(rels[-2:])
    added, updated, failed = [], [], []
    for rel in rels:
        if rel in known and rel not in newest and not force:
            continue
        url = BASE.format(slug=rel.replace('.', ''))
        text, err = fetch(url)
        if err or not text:
            if rel not in known:
                failed.append(rel)
            continue
        sections = parse_whats_new(text)
        if not sections:
            failed.append(rel)
            continue
        entry = {'url': url, 'sections': sections, 'summary': summarise(sections)}
        (updated if rel in known else added).append(rel)
        known[rel] = entry
        time.sleep(1.5)   # be polite to docs.netapp.com
    doc = {'fetchedAt': datetime.now(timezone.utc).isoformat(), 'source': 'docs.netapp.com/us-en/ontap/release-notes/', 'releases': known}
    _write(path, doc)
    return {'added': added, 'updated': updated, 'failed': failed}


def _write(path, doc):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, path)
