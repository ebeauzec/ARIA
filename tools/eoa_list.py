"""End-of-availability platform list, read from docs.netapp.com (no AI, no sign-in).

NetApp's page https://docs.netapp.com/us-en/ontap-systems/endofavail/ lists the ONTAP hardware systems that are no longer for sale
(AFF, ASA, FAS, and a few switches). It gives names only, no dates; per-system dates come from Active IQ. ARIA uses the names as the fallback
when a system carries no end-of-availability date of its own. The harvester that tried to read dates from per-model pages found nothing on
today's page, so the list was stuck at an old snapshot.
"""
import html as _html
import json
import os
import re
from datetime import datetime, timezone

URL = 'https://docs.netapp.com/us-en/ontap-systems/endofavail/'
# One docs entry that stands for several models
_ALIASES = {'FAS2700': ['FAS2720', 'FAS2750'], 'FAS8300 AND FAS8700': ['FAS8300', 'FAS8700']}
_NAME = re.compile(r'^(AFF|ASA|FAS)\s*([A-Z]?\d+[A-Za-z]*)(?:\s+and\s+(?:AFF|ASA|FAS)?\s*[A-Z]?\d+[A-Za-z]*)?$', re.I)


def _lines(page):
    body = re.sub(r'<script.*?</script>|<style.*?</style>', '', page, flags=re.S | re.I)
    text = _html.unescape(re.sub(r'<[^>]+>', '\n', body))
    return [re.sub(r'\s+', ' ', l).strip() for l in text.split('\n') if l.strip()]


def parse(page):
    """-> {'platforms': [names as ARIA matches them], 'switches': [model names]}"""
    lines = _lines(page)
    platforms, switches, in_systems, in_more = [], [], False, False
    for l in lines:
        low = l.lower()
        if re.match(r'^(aff|asa|fas) systems\b', low):
            in_systems, in_more = True, False
            continue
        if low.startswith('more resources'):
            in_systems, in_more = False, True
            continue
        if in_more:
            if re.search(r'broadcom|cisco|nvidia', low):
                switches.append(l)
            elif low.startswith('system hardware upgrade') or low.startswith('ontap software upgrade') or low.startswith('terms of use'):
                in_more = False
            continue
        if not in_systems or not _NAME.match(l):
            continue
        key = l.upper()
        if key in _ALIASES:
            names = _ALIASES[key]
        else:
            fam, rest = re.match(r'^(AFF|ASA|FAS)\s*(.+)$', l, re.I).groups()
            fam, rest = fam.upper(), rest.strip()
            if ' and ' in rest.lower():
                names = [(fam + (' ' if fam != 'FAS' else '') + p.strip()).upper() for p in re.split(r'\s+and\s+', rest, flags=re.I)]
            elif fam == 'AFF':
                names = [rest.upper()]                    # Active IQ writes "AFF-A400": "A400" matches it
            elif fam == 'ASA':
                names = ['ASA ' + rest.upper()]
            else:
                names = [(fam + rest).upper()]
        for n in names:
            if n not in platforms:
                platforms.append(n)
    return {'platforms': platforms, 'switches': switches}


def harvest(data_dir, fetch):
    """Merge the page's names into data/eoa_database.json (platforms are only ever added). `fetch(url)` -> (text, error)."""
    text, err = fetch(URL)
    if err or not text:
        return {'error': str(err or 'empty page')}
    got = parse(text)
    if len(got['platforms']) < 5:
        return {'error': 'page layout changed: fewer than 5 platforms found'}
    path = os.path.join(data_dir, 'eoa_database.json')
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            db = json.load(fh)
    except (OSError, ValueError):
        db = {}
    have = {str(p).upper() for p in (db.get('platforms') or [])}
    added = [p for p in got['platforms'] if p.upper() not in have]
    sw = db.get('switches') or []
    sw_have = ' | '.join(str(s.get('model', '')).lower() for s in sw if isinstance(s, dict))
    sw_added = []
    for name in got['switches']:
        toks = re.findall(r'[A-Za-z]*\d[\w-]*', name)          # the model number, so "Broadcom BES-53248" and "Broadcom-supported BES-53248" are one switch
        if not any(t.lower() in sw_have for t in toks):
            sw.append({'model': name, 'type': 'cluster', 'note': 'Listed as end of availability on docs.netapp.com/us-en/ontap-systems/endofavail/'})
            sw_added.append(name)
    db['platforms'] = list(db.get('platforms') or []) + added
    db['switches'] = sw
    db['_lastChecked'] = datetime.now(timezone.utc).isoformat()   # written every run, so "checked today, nothing new" is not mistaken for a stale file
    if added or sw_added:
        db['_lastUpdated'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    db['_source'] = 'docs.netapp.com/us-en/ontap-systems/endofavail/'
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump(db, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, path)
    return {'platformsOnPage': len(got['platforms']), 'added': added, 'switchesAdded': sw_added}
