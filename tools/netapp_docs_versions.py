"""Newest released versions of NetApp-owned integrations, read from docs.netapp.com release-notes pages (no AI, no sign-in).

ARIA's interoperability table (data/imt_interop.json) holds, per integration, a recommended version and a compatibility range per version
(minimum and maximum ONTAP). The ranges are not on a release-notes page, so ARIA never writes them. What it can read is which version is the
newest released: that goes into `latestReleased` next to `currentRecommended`, and the Settings card lists every integration whose newest
release is ahead of the table, so the gap is visible instead of silent.
"""
import html as _html
import json
import os
import re
from datetime import datetime, timezone

SOURCES = [
    {'key': 'host_utilities_linux', 'url': 'https://docs.netapp.com/us-en/ontap-sanhost/hu-luhu-release-notes.html', 'pat': r'Host Utilities\s+(\d+\.\d+(?:\.\d+)?)'},
    {'key': 'host_utilities_windows', 'url': 'https://docs.netapp.com/us-en/ontap-sanhost/hu-wuhu-release-notes.html', 'pat': r'Host Utilities\s+(\d+\.\d+(?:\.\d+)?)'},
    {'key': 'snapcenter', 'url': 'https://docs.netapp.com/us-en/snapcenter/release-notes/release-notes.html', 'pat': r'SnapCenter\s+(?:Software\s+)?(\d+\.\d+(?:\.\d+)?)'},
]


# Structured, public JSON (endoflife.date) for integrations whose vendor pages are not machine-readable. Version numbers only: the first
# release cycle's `latest`. Earlier attempts at scraping vendor marketing pages got these wrong, which is why this reads a JSON API instead.
JSON_SOURCES = [
    {'key': 'veeam', 'url': 'https://endoflife.date/api/veeam-backup-and-replication.json'},
    {'key': 'proxmox_ve', 'url': 'https://endoflife.date/api/proxmox-ve.json'},
    {'key': 'vmware_vsphere', 'url': 'https://endoflife.date/api/vmware-esxi.json'},
]


def _vt(v):
    return tuple(int(p) for p in re.findall(r'\d+', str(v or ''))[:4])


def newest(page, pattern):
    """Highest version number the pattern finds on the page (release-notes pages list older releases too)."""
    body = re.sub(r'<script.*?</script>|<style.*?</style>', '', page, flags=re.S | re.I)
    text = _html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', body)))
    found = re.findall(pattern, text)
    return max(found, key=_vt) if found else ''


def harvest(data_dir, fetch):
    path = os.path.join(data_dir, 'imt_interop.json')
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            db = json.load(fh)
    except (OSError, ValueError):
        return {'error': 'imt_interop.json not found'}
    changed, failed = {}, []
    for src in SOURCES:
        text, err = fetch(src['url'])
        latest = newest(text, src['pat']) if text and not err else ''
        if not latest:
            failed.append(src['key'])
            continue
        entry = db.setdefault(src['key'], {})
        if entry.get('latestReleased') != latest:
            changed[src['key']] = {'was': entry.get('latestReleased', ''), 'now': latest}
        entry['latestReleased'] = latest
        entry['latestSource'] = src['url']
        entry['latestChecked'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    for src in JSON_SOURCES:
        text, err = fetch(src['url'])
        latest = ''
        try:
            rows = json.loads(text) if text and not err else []
            latest = str((rows[0] or {}).get('latest') or '') if rows else ''
        except (ValueError, AttributeError, IndexError):
            latest = ''
        if not re.match(r'^\d+\.\d+', latest):
            failed.append(src['key'])
            continue
        entry = db.setdefault(src['key'], {})
        if entry.get('latestReleased') != latest:
            changed[src['key']] = {'was': entry.get('latestReleased', ''), 'now': latest}
        entry['latestReleased'] = latest
        entry['latestSource'] = src['url']
        entry['latestChecked'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    db['_lastChecked'] = datetime.now(timezone.utc).isoformat()
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump(db, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, path)
    return {'changed': changed, 'failed': failed}


def newer_than_table(data_dir):
    """Integrations whose newest released version is ahead of the version ARIA's compatibility table recommends."""
    try:
        with open(os.path.join(data_dir, 'imt_interop.json'), 'r', encoding='utf-8') as fh:
            db = json.load(fh)
    except (OSError, ValueError):
        return []
    out = []
    for key, e in db.items():
        if key.startswith('_') or not isinstance(e, dict) or not e.get('latestReleased'):
            continue
        ours = e.get('currentRecommended') or ''
        if _vt(e['latestReleased'])[:2] > _vt(ours)[:2]:   # a patch release inside the recommended minor version is not a gap
            out.append({'key': key, 'name': e.get('name') or key, 'ours': ours, 'latest': e['latestReleased'], 'source': e.get('latestSource', '')})
    return out
