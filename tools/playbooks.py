"""Remediation playbooks as data, and the record of findings that have no procedure yet.

A playbook is a procedure for one kind of finding (see docs/PLAYBOOKS.md for the format). The shipped set is tools/playbooks.json; a person or the weekly
maintenance job adds entries to data/playbooks_local.json, which is never overwritten by an update. Only entries with "status": "approved" are used: a
draft is approved automatically by `playbook_verify.py --promote` once it is valid and every command and menu path in it is verified against NetApp's documentation.

The front end reports which findings in the fleet it could not give a procedure (record_gaps). That record (data/playbook_gaps.json) is what shows in
Settings > Data & Sync > Procedure coverage, and the largest gaps are put into the reference updater's review queue so the maintenance job knows what to write.

Standard library only. No network access: nothing here fetches anything.
"""
import hashlib
import json
import os
import re
import tempfile
import time

PLAYBOOKS_NAME = 'playbooks.json'                 # the shipped set, next to this module (data/ is generated and not in git)
SHIPPED_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), PLAYBOOKS_NAME)
LOCAL_NAME = 'playbooks_local.json'
GAPS_NAME = 'playbook_gaps.json'
QUEUE_NAME = 'library_update_queue.json'
QUEUE_LIMIT = 25            # gap items kept in the review queue at once
FAMILIES = ('ontap', 'eseries', 'storagegrid', 'any')
STATUSES = ('approved', 'draft', 'rejected')
OFFICIAL_HOSTS = {'docs.netapp.com', 'kb.netapp.com', 'security.netapp.com', 'www.netapp.com', 'mysupport.netapp.com', 'imt.netapp.com', 'hwu.netapp.com', 'library.netapp.com'}
_ONTAP_CLI = re.compile(r'\b(?:cluster image|vserver [a-z-]+|storage (?:aggregate|failover|disk|shelf)|network (?:interface|port|route)|volume (?:efficiency|snapshot|modify|show)|system node|snapmirror (?:show|create))\b')
KNOWN_VARS = {'cluster', 'node', 'svm', 'policy', 'version', 'model', 'target', 'ref', 'recommended', 'advisory', 'cve', 'detail', 'finding', 'bug', 'what', 'fixes', 'recommendation', 'scope',
              'metrocluster', 'target2Note', 'sameLineNote', 'lineNote'}
_PLACEHOLDER = re.compile(r'\{\??([a-zA-Z_][a-zA-Z0-9_]*)(?:\|[^}]*)?\}')


def _jload(path):
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def _jsave(path, obj):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as fh:
            json.dump(obj, fh, indent=1, ensure_ascii=False)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


def validate(e):
    """Problems with one playbook entry, as a list of sentences (empty when it is usable)."""
    bad = []
    if not isinstance(e, dict):
        return ['not an object']
    if not re.fullmatch(r'[a-z0-9][a-z0-9._-]{2,60}', str(e.get('id') or '')):
        bad.append('id must be 3-61 lower-case letters, digits, dot, dash or underscore')
    if e.get('family', 'ontap') not in FAMILIES:
        bad.append('family must be one of ' + ', '.join(FAMILIES))
    if e.get('status', 'approved') not in STATUSES:
        bad.append('status must be one of ' + ', '.join(STATUSES))
    try:
        if not str(e.get('match') or '').strip():
            bad.append('match (a regular expression for the finding) is required')
        else:
            re.compile(str(e['match']))
    except re.error as x:
        bad.append('match is not a valid regular expression: ' + str(x))
    for k, v in (e.get('vars') or {}).items():
        try:
            re.compile(str(v))
        except re.error as x:
            bad.append(f'vars.{k} is not a valid regular expression: {x}')
    steps = e.get('steps')
    if not isinstance(steps, list) or len(steps) < 3 or not all(isinstance(s, str) and s.strip() for s in steps):
        bad.append('steps must be a list of at least 3 non-empty strings')
    for k in ('cause', 'impact'):
        if not str(e.get(k) or '').strip():
            bad.append(k + ' is required')
    if not (e.get('sources') or []):
        bad.append('sources (the NetApp pages the procedure was written from) is required')
    for u in e.get('sources') or []:
        host = re.match(r'https://([^/]+)/', str(u))
        if not host or not (host.group(1).lower() in OFFICIAL_HOSTS):
            bad.append(f'source {str(u)[:60]} is not a NetApp page (allowed: ' + ', '.join(sorted(OFFICIAL_HOSTS)) + ')')
    if e.get('family') in ('eseries', 'storagegrid'):
        for s in e.get('steps') or []:
            if _ONTAP_CLI.search(str(s)):
                bad.append('an ONTAP command in an E-Series or StorageGRID procedure: ' + str(s)[:70])
                break
    if re.search(r'\bARIA\b', json.dumps(e, ensure_ascii=False)):
        bad.append('the procedure names the tool (documents are an interpretation of data collected from Active IQ and carry no product name)')
    declared = set((e.get('vars') or {}).keys()) | KNOWN_VARS
    texts = [str(e.get('cause') or ''), str(e.get('impact') or '')] + [str(s) for s in (steps or [])] + [str(s) for s in (e.get('options') or [])]
    texts += [str(e.get('groupKey') or ''), str(e.get('advisoryRef') or '')] + [str(x) for x in (e.get('compact') or [])]
    if e.get('belowMin'):
        texts += [str(e['belowMin'].get('cause') or '')] + [str(s) for s in (e['belowMin'].get('steps') or [])]
    for t in texts:
        for name in _PLACEHOLDER.findall(t):
            if name not in declared:
                bad.append('{' + name + '} is used but not declared in vars')
    if e.get('minVersion') and not re.fullmatch(r'\d+\.\d+(\.\d+)?', str(e['minVersion'])):
        bad.append('minVersion must look like 9.11.1')
    return sorted(set(bad))


def load(data_dir, shipped_path=None):
    """{'playbooks': approved entries (local ones replace shipped ones with the same id), 'pending': drafts, 'problems': [...], 'counts': {...}}"""
    # the shipped set sits next to this module; in the packaged app the module is inside an archive, so tools/ beside data/ is tried too
    cands = [shipped_path] if shipped_path else [SHIPPED_PATH, os.path.join(os.path.dirname(os.path.abspath(data_dir)), 'tools', PLAYBOOKS_NAME)]
    shipped = (_jload(next((c for c in cands if os.path.isfile(c)), cands[0])).get('playbooks') or [])
    local = (_jload(os.path.join(data_dir, LOCAL_NAME)).get('playbooks') or [])
    by_id, order, problems, pending = {}, [], [], []
    for src, items in (('shipped', shipped), ('local', local)):
        for e in items:
            if not isinstance(e, dict):
                continue
            errs = validate(e)
            if errs:
                problems.append({'id': str(e.get('id') or '?'), 'source': src, 'problems': errs})
                continue
            if e.get('status', 'approved') != 'approved':
                if e.get('status') == 'draft':
                    pending.append({'id': e['id'], 'source': src, 'match': e.get('match'), 'status': 'draft'})
                elif src == 'local' and e['id'] in by_id:
                    by_id.pop(e['id'])          # a rejected local entry switches off the shipped one with the same id
                    order.remove(e['id'])
                continue
            if e['id'] not in by_id:
                order.append(e['id'])
            by_id[e['id']] = dict(e, _source=src)
    return {'playbooks': [by_id[i] for i in order if i in by_id], 'pending': pending, 'problems': problems,
            'counts': {'shipped': len([e for e in shipped if isinstance(e, dict)]), 'local': len([e for e in local if isinstance(e, dict)]), 'approved': len(by_id), 'pending': len(pending), 'invalid': len(problems)}}


def _gap_id(key):
    return 'pbgap-' + hashlib.sha1(key.encode('utf-8')).hexdigest()[:10]


def record_gaps(data_dir, report, now=None):
    """Merge what the front end found uncovered. report = {'total': n findings, 'covered': n, 'gaps': [{key, category, families, count, systems, severity, detail, recommendation, urls}]}.
    A type that now has a procedure leaves the record; the review queue gets the largest open gaps (kind 'playbook-gap') and drops the ones that are covered."""
    now = now or time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    path = os.path.join(data_dir, GAPS_NAME)
    old = _jload(path)
    old_items = old.get('gaps') or {}
    items = {}
    for g in (report.get('gaps') or [])[:400]:
        key = str(g.get('key') or '').strip()[:200]
        if not key:
            continue
        prev = old_items.get(key) or {}
        items[key] = {
            'key': key, 'category': str(g.get('category') or '')[:80], 'families': sorted(set(str(f) for f in (g.get('families') or []))), 'count': int(g.get('count') or 0),
            'systems': int(g.get('systems') or 0), 'severity': str(g.get('severity') or '')[:20], 'detail': str(g.get('detail') or '')[:400], 'recommendation': str(g.get('recommendation') or '')[:400],
            'urls': [str(u)[:300] for u in (g.get('urls') or [])[:3]], 'firstSeen': prev.get('firstSeen') or now, 'lastSeen': now}
    total, covered = int(report.get('total') or 0), int(report.get('covered') or 0)
    out = {'updated': now, 'total': total, 'covered': covered, 'pct': round(100.0 * covered / total, 1) if total else None, 'gaps': items,
           'history': ((old.get('history') or []) + [{'at': now, 'total': total, 'covered': covered}])[-60:]}
    _jsave(path, out)
    # the review queue: the largest open gaps, so the maintenance job knows what to write
    qpath = os.path.join(data_dir, QUEUE_NAME)
    q = _jload(qpath).get('items') or {}
    live = {_gap_id(k) for k in items}
    for qid in [i for i, v in q.items() if v.get('kind') == 'playbook-gap' and (i not in live)]:
        if q[qid].get('status') == 'open':
            q[qid]['status'] = 'closed'
            q[qid]['closedNote'] = 'a procedure now covers it'
    top = sorted(items.values(), key=lambda g: (-g['count'], g['key']))[:QUEUE_LIMIT]
    for g in top:
        qid = _gap_id(g['key'])
        cur = q.get(qid)
        if cur and cur.get('status') == 'acknowledged':
            continue
        q[qid] = {'id': qid, 'kind': 'playbook-gap', 'title': 'No procedure for: ' + g['key'], 'category': 'Procedures',
                  'detail': f"{g['count']} finding{'s' if g['count'] != 1 else ''} on {g['systems']} system{'s' if g['systems'] != 1 else ''} ({', '.join(g['families']) or 'unknown family'}). "
                            f"Write a playbook entry in data/playbooks_local.json (status draft) from NetApp's documentation; see docs/PLAYBOOKS.md. Example: {g['detail']}",
                  'url': (g['urls'] or [''])[0], 'status': (cur or {}).get('status', 'open'), 'firstSeen': (cur or {}).get('firstSeen') or now, 'lastSeen': now}
    _jsave(qpath, {'items': q})
    return {'gaps': len(items), 'queued': len(top)}


def source_watch(data_dir, ld=None):
    """How many of the NetApp pages the playbooks were written from the reference updater has read, and how many have changed since (open review items)."""
    ld = ld or load(data_dir)
    urls = set()
    for e in ld['playbooks']:
        for u in e.get('sources') or []:
            if str(u).startswith('https://docs.netapp.com/') or str(u).startswith('https://security.netapp.com/') or str(u).startswith('https://www.netapp.com/'):
                urls.add(str(u))
    pages = (_jload(os.path.join(data_dir, 'library_update_state.json')).get('pages') or {})
    read = sum(1 for u in urls if (pages.get(u) or {}).get('hash'))
    changed = [i for i in (_jload(os.path.join(data_dir, QUEUE_NAME)).get('items') or {}).values() if i.get('kind') == 'playbook-source-changed' and i.get('status') == 'open']
    return {'pages': len(urls), 'read': read, 'changedOpen': len(changed), 'changed': [{'title': i.get('title'), 'url': i.get('url')} for i in changed[:10]]}


def status(data_dir):
    g = _jload(os.path.join(data_dir, GAPS_NAME))
    ld = load(data_dir)
    gaps = sorted((g.get('gaps') or {}).values(), key=lambda x: (-x.get('count', 0), x.get('key', '')))
    try:
        import playbook_verify as _pv
        verification = _pv.summary(data_dir)
    except Exception:
        verification = None
    return {'verification': verification, 'updated': g.get('updated') or '', 'total': g.get('total'), 'covered': g.get('covered'), 'pct': g.get('pct'), 'history': g.get('history') or [],
            'gaps': gaps[:60], 'gapTypes': len(gaps), 'playbooks': ld['counts'], 'sourceWatch': source_watch(data_dir, ld), 'pending': ld['pending'], 'problems': ld['problems']}
