"""Check a remediation playbook against NetApp's own documentation, with no AI.

A playbook (tools/playbooks.json, data/playbooks_local.json) is only as good as the commands and menu paths in it. This module reads each approved playbook and
checks what it says against the official pages, then records the result (data/playbook_verification.json) for the rest of ARIA to use:

  ONTAP commands   every command in the steps ("storage failover modify -node * -auto-giveback true") is looked up in NetApp's ONTAP command reference
                   (docs.netapp.com/us-en/ontap-cli/<command>.html): the page must exist and every -parameter used must be on it.
  Menu paths       in E-Series and StorageGRID playbooks, each step of a path such as "Support > Upgrade center" must occur in the text of the NetApp pages the playbook
                   cites (the reference updater keeps their text in data/library_refreshed/Playbooks/).

Statuses per item: verified, param-missing (the page has no such parameter: the playbook is wrong or the option changed), not-found (no reference page for that
command, or the path is not on the cited pages: a person looks), unchecked (the page could not be read, or has not been fetched yet). An entry is `ok` when nothing is
param-missing or not-found. What the result is used for:
  * the closing line of a procedure says "checked against NetApp's ONTAP command reference on <date>" instead of "confirm option names for your release";
  * Settings > Data & Sync > Procedure coverage shows how many commands were checked and which need a person;
  * the command pages join the reference updater's page watch, so a change to a command's syntax raises a review item naming the playbook.

    python tools/playbook_verify.py [--refresh] [--offline] [--id ID]      check, write the record, print a report
    python tools/playbook_verify.py --promote [--file PATH]                 approve the drafts that pass every check (new procedures are approved automatically)

Standard library only. It fetches only docs.netapp.com, through library_updater.http_get (an honest user agent; sign-in hosts refused).
"""
import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import library_updater as lu  # noqa: E402
import playbooks as pb  # noqa: E402

CLI_BASE = 'https://docs.netapp.com/us-en/ontap-cli/'
CACHE_SUB = os.path.join('library_refreshed', 'ontap-cli')
RECORD = 'playbook_verification.json'
MAX_AGE_DAYS = 30
# the top-level directories of the ONTAP CLI; a command starts at one of them
ROOTS = ('vserver', 'storage', 'network', 'system', 'security', 'cluster', 'volume', 'snapmirror', 'event', 'snaplock', 'statistics', 'metrocluster', 'job', 'lun', 'qos',
         'dashboard', 'snapshot', 'set', 'autosupport', 'node', 'disk', 'aggr', 'vol', 'options', 'run', 'license', 'timezone', 'date')
_WORD = r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*'
_VAL = r'(?:"[^"]*"|<[^>]*>|\{[^}]*\}|[^\s;,)]+)'
# a command: a root, subcommand words, then -parameters with optional values. It must follow the start of a step, a colon, a semicolon, "then" or a bracket.
_CMD = re.compile(r'(?:(?<=^)|(?<=[:;(])|(?<=\sthen)|(?<=\sor)|(?<=\sand))\s*((?:%s)(?:\s+%s)*)((?:\s+-%s(?:\s+%s)?)*)' % ('|'.join(ROOTS), _WORD, _WORD, _VAL))
_STOP = {'for', 'the', 'to', 'of', 'and', 'or', 'with', 'in', 'on', 'from', 'is', 'a', 'an', 'before', 'after', 'until', 'then', 'when', 'so', 'that', 'which', 'may', 'can', 'will', 'if', 'by', 'as', 'at', 'it', 'on', 'help', 'must', 'should', 'are'}
_STEPNUM = re.compile(r'^\s*\d+\.\s*')
_PATH = re.compile(r'((?:[A-Z][A-Za-z0-9 /()-]*?)(?: > [A-Za-z0-9][A-Za-z0-9 /()-]*?){1,5})(?=[\s.,;:)]|$)')


def _now():
    return datetime.now(timezone.utc).isoformat()


def commands_in(text):
    """[(command words, [-parameters])] found in one step. Prose such as 'volume group' is filtered out later by the page lookup (not-found, never a failure)."""
    out = []
    t = _STEPNUM.sub('', str(text))
    # commands sit after a label ("Check:", "Enable:") or a separator; make the start of the text count as a separator too
    for m in _CMD.finditer(' ; ' + t):
        words = m.group(1).split()
        params = re.findall(r'(?<!\S)-(%s)' % _WORD, m.group(2) or '')
        # "set volume snapshot ..." is prose ("set the ..."): the set command is `set -privilege ...`
        if words[0] == 'set' and not (len(words) == 1 and params[:1] == ['privilege']):
            words = words[1:]
            if not words or words[0] not in ROOTS:
                continue
        # words after the command that are prose, not subcommands ("security certificate show-truststore for the trusted CAs")
        for i, w in enumerate(words):
            if w in _STOP and i > 0:
                words = words[:i]
                params = []
                break
        if len(words) == 1 and words[0] != 'set':
            continue
        # a lone prose phrase ("volume group", "cluster peer relationship") has no parameters and is not followed by anything command-like: keep only plausible ones
        if not params and len(words) < 3 and not re.search(r'(?:show|create|modify|delete|start|check|get|add|install|enable|disable|run|update|revert|rebalance|relocate|download)\b', ' '.join(words)):
            continue
        out.append((words, params))
    return out


def all_commands(entry):
    """{command text: set(params)} over every step of an entry (including the below-minimum variant)."""
    seen = {}
    texts = [str(s) for s in entry.get('steps') or []] + [str(s) for s in (entry.get('belowMin') or {}).get('steps') or []]
    for t in texts:
        for words, params in commands_in(t):
            seen.setdefault(' '.join(words), set()).update(params)
    return seen


_LEAD = re.compile(r'.*\b(?:select|selecting|open|opens|click|clicking|choose|go to|goes to|under|from|in the|in|on the|on|then|and|or)\s+(?=\S)', re.I | re.S)
_TAIL = re.compile(r'\s*(?:[.;:,)]|\s(?:then|to|for|click|select|under|if|so|until|when|with)\b).*$', re.I | re.S)


def ui_paths(entry):
    """[[segment, ...]] for each menu path "A > B > C" in the steps, reduced to the words of the path itself."""
    out = []
    for s in [str(x) for x in entry.get('steps') or []]:
        t = _STEPNUM.sub('', s)
        for m in re.finditer(r'[^\s>][^>]*?(?: > [^>]+?)+(?=[.;:,)]\s|[.;:,)]$|\s(?:then|and|or|to|for|click|select)\b|$)', t):
            parts = [p for p in m.group(0).split(' > ')]
            if len(parts) < 2:
                continue
            first = re.split(r'[(:]', _LEAD.sub('', parts[0]))[-1].strip(' (')
            words, cap = first.split(), []
            for w in reversed(words):             # the path starts at the capitalised words just before the first ">" ("with Support" -> "Support")
                if w[:1].isupper() or w[:1].isdigit():
                    cap.append(w)
                else:
                    break
            first = ' '.join(reversed(cap[:2])) if cap else ' '.join(w for w in words[-2:] if w.lower() not in ('the', 'a', 'in', 'on', 'of', 'and'))
            mids = [p.strip() for p in parts[1:-1]]
            last = _TAIL.sub('', parts[-1]).strip()
            last = ' '.join(last.split()[:4])
            segs = [x for x in [first] + mids + [last] if x]
            if len(segs) >= 2:
                out.append(segs)
    return out


def _norm(s):
    return re.sub(r'\s+', ' ', re.sub(r'[‘’“”]', "'", str(s)).lower()).strip()


def cli_page(base_dir, words, fetch, refresh=False, offline=False, sleep=time.sleep):
    """(text or None, url, error). The page text is cached under data/library_refreshed/ontap-cli/ and re-read after MAX_AGE_DAYS."""
    name = '-'.join(words)
    url = CLI_BASE + name + '.html'
    cache = os.path.join(base_dir, 'data', CACHE_SUB, name + '.md')
    try:
        age = (time.time() - os.path.getmtime(cache)) / 86400
        if not refresh and age < MAX_AGE_DAYS:
            with open(cache, encoding='utf-8') as fh:
                return fh.read().split('\n\n', 1)[-1], url, None
    except OSError:
        age = None
    if offline:
        try:
            with open(cache, encoding='utf-8') as fh:
                return fh.read().split('\n\n', 1)[-1], url, None
        except OSError:
            return None, url, 'not fetched yet'
    sleep(lu.RATE_SECONDS)
    page, err = fetch(url)
    if err or not page:
        return None, url, err or 'empty'
    title, text = lu.html_to_text(page)
    squash = lambda x: re.sub(r'[\s-]+', '', x)
    if len(text) < 80 or squash(name) not in squash(_norm(title + ' ' + text[:400])):
        return None, url, 'not a command page'
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    with open(cache, 'w', encoding='utf-8') as fh:
        fh.write(f'# {title}\nSource: {url}\nFetched: {datetime.now(timezone.utc).strftime("%Y-%m-%d")}\n\n{text}')
    return text, url, None


def source_text(base_dir, entry, fetch=None, sleep=time.sleep):
    """The cached text of the pages an entry cites (kept by the reference updater), joined. A page that is not cached yet is read now when `fetch` is given
    (docs.netapp.com and the other hosts the updater may read) and cached the way the updater does, so a new playbook can be checked at once."""
    parts = []
    for u in entry.get('sources') or []:
        cache = os.path.join(base_dir, 'data', lu.CACHE_DIR, 'Playbooks', lu._slug(u) + '.md')
        try:
            with open(cache, encoding='utf-8') as fh:
                parts.append(fh.read())
                continue
        except OSError:
            pass
        host = u.split('/')[2] if u.startswith('https://') and u.count('/') >= 3 else ''
        if fetch and host in lu.ALLOWED_HOSTS and host != 'kb.netapp.com':
            sleep(lu.RATE_SECONDS)
            page, err = fetch(u)
            if page and not err:
                title, text = lu.html_to_text(page)
                if len(text) >= 200:
                    os.makedirs(os.path.dirname(cache), exist_ok=True)
                    body = f'# {title}\nSource: {u}\nFetched: {datetime.now(timezone.utc).strftime("%Y-%m-%d")}\nRead to check a playbook (no AI).\n\n{text}'
                    with open(cache, 'w', encoding='utf-8') as fh:
                        fh.write(body)
                    parts.append(body)
    return _norm('\n'.join(parts))


def verify_entry(base_dir, entry, fetch=None, refresh=False, offline=False, sleep=time.sleep, pages=None):
    """The record for one entry. `pages` is a per-run cache {command: (text, url, err)}."""
    fetch = fetch or lu.http_get
    pages = pages if pages is not None else {}
    rec = {'id': entry['id'], 'family': entry.get('family', 'ontap'), 'commands': [], 'paths': [], 'at': _now()}
    fam = entry.get('family', 'ontap')
    if fam in ('ontap', 'any'):
        for cmd, params in sorted(all_commands(entry).items()):
            words = cmd.split()
            if cmd not in pages:
                pages[cmd] = cli_page(base_dir, words, fetch, refresh, offline, sleep)
            text, url, err = pages[cmd]
            item = {'command': cmd, 'url': url, 'params': sorted(params)}
            if text is None:
                item['status'] = 'unchecked' if err and err != 'HTTP 404' and err != 'not a command page' else 'not-found'
                item['note'] = err
            else:
                missing = [p for p in sorted(params) if not re.search(r'(?<![\w-])-%s(?![\w-])' % re.escape(p), text)]
                item['status'] = 'param-missing' if missing else 'verified'
                if missing:
                    item['missing'] = missing
            rec['commands'].append(item)
    if fam in ('eseries', 'storagegrid', 'any'):
        hay = source_text(base_dir, entry, None if offline else fetch, sleep)
        seen = set()
        for segs in ui_paths(entry):
            key = ' > '.join(segs)
            if key in seen:
                continue
            seen.add(key)
            if not hay:
                rec['paths'].append({'path': key, 'status': 'unchecked', 'note': 'the cited pages have not been fetched yet'})
                continue
            missing = [s for s in segs if _norm(s) not in hay]
            rec['paths'].append({'path': key, 'status': 'not-found' if missing else 'verified', **({'missing': missing} if missing else {})})
    items = rec['commands'] + rec['paths']
    rec['counts'] = {k: sum(1 for i in items if i['status'] == k) for k in ('verified', 'param-missing', 'not-found', 'unchecked')}
    rec['ok'] = rec['counts']['param-missing'] == 0 and rec['counts']['not-found'] == 0 and rec['counts']['verified'] > 0
    return rec


def run(base_dir, fetch=None, refresh=False, offline=False, only=None, sleep=time.sleep, log=print):
    ld = pb.load(os.path.join(base_dir, 'data'), os.path.join(base_dir, 'tools', 'playbooks.json'))
    pages, entries = {}, {}
    for e in ld['playbooks']:
        if only and e['id'] != only:
            continue
        entries[e['id']] = verify_entry(base_dir, e, fetch, refresh, offline, sleep, pages)
    old = {}
    try:
        with open(os.path.join(base_dir, 'data', RECORD), encoding='utf-8') as fh:
            old = json.load(fh).get('entries') or {}
    except (OSError, ValueError):
        pass
    if only:
        old.update(entries)
        entries = old
    out = {'at': _now(), 'entries': entries}
    os.makedirs(os.path.join(base_dir, 'data'), exist_ok=True)
    tmp = os.path.join(base_dir, 'data', RECORD + '.tmp')
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, os.path.join(base_dir, 'data', RECORD))
    return out


def promote(base_dir, path=None, fetch=None, offline=False, sleep=time.sleep, today=None):
    """Approve the drafts in a playbook file that pass every automatic check (the owner's standing instruction, 2026-10-17: new procedures are approved
    automatically). A draft is approved when the entry is valid (official NetApp sources only, placeholders declared, no ONTAP commands in another product's
    procedure, no tool name) and every command and menu path in it is verified against NetApp's documentation: nothing wrong, nothing unchecked. Any other
    draft stays a draft, with the reasons. Returns (approved ids, {id: reasons})."""
    path = path or os.path.join(base_dir, 'data', pb.LOCAL_NAME)
    try:
        with open(path, encoding='utf-8') as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return [], {}
    approved, kept, pages = [], {}, {}
    for e in doc.get('playbooks') or []:
        if not isinstance(e, dict) or e.get('status') != 'draft':
            continue
        probs = pb.validate(dict(e, status='approved'))
        if probs:
            kept[e.get('id', '?')] = probs
            continue
        rec = verify_entry(base_dir, e, fetch, False, offline, sleep, pages)
        c = rec['counts']
        why = [f'{c[k]} {k}' for k in ('param-missing', 'not-found', 'unchecked') if c[k]]
        if why:
            kept[e['id']] = ['verification: ' + ', '.join(why)]
            continue
        e['status'] = 'approved'
        e['approvedBy'] = 'automatic (valid, and every command and menu path checked against NetApp documentation)'
        e['approvedAt'] = today or datetime.now(timezone.utc).strftime('%Y-%m-%d')
        approved.append(e['id'])
    if approved:
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as fh:
            json.dump(doc, fh, indent=1, ensure_ascii=False)
        os.replace(tmp, path)
    return approved, kept


def load_record(data_dir):
    try:
        with open(os.path.join(data_dir, RECORD), encoding='utf-8') as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {'at': '', 'entries': {}}


def summary(data_dir):
    rec = load_record(data_dir)
    tot = {'verified': 0, 'param-missing': 0, 'not-found': 0, 'unchecked': 0}
    review = []
    for e in rec['entries'].values():
        for k, v in (e.get('counts') or {}).items():
            tot[k] = tot.get(k, 0) + v
        for i in e.get('commands', []) + e.get('paths', []):
            if i['status'] in ('param-missing', 'not-found'):
                review.append({'id': e['id'], 'item': i.get('command') or i.get('path'), 'status': i['status'], 'missing': i.get('missing') or []})
    return {'at': rec.get('at') or '', 'entries': len(rec['entries']), 'entriesOk': sum(1 for e in rec['entries'].values() if e.get('ok')), 'totals': tot, 'review': review[:40]}


def command_pages(data_dir):
    """{url: [playbook ids]} of the ONTAP command pages the verified playbooks rely on: the reference updater watches them."""
    out = {}
    for e in load_record(data_dir)['entries'].values():
        for c in e.get('commands', []):
            if c['status'] in ('verified', 'param-missing'):
                out.setdefault(c['url'], [])
                if e['id'] not in out[c['url']]:
                    out[c['url']].append(e['id'])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--refresh', action='store_true', help='read the command pages again even when cached')
    ap.add_argument('--offline', action='store_true', help='use the cached pages only')
    ap.add_argument('--id')
    ap.add_argument('--promote', action='store_true', help='approve the drafts that pass every check (default file: data/playbooks_local.json)')
    ap.add_argument('--file', help='with --promote: another playbook file, for example tools/playbooks.json')
    ap.add_argument('--root', default=os.path.dirname(HERE))
    a = ap.parse_args(argv)
    if a.promote:
        ok, kept = promote(a.root, a.file, offline=a.offline)
        print('approved: ' + (', '.join(ok) or 'none'))
        for k, why in kept.items():
            print(f'  stays a draft: {k}: ' + '; '.join(why)[:300])
        return 0
    run(a.root, refresh=a.refresh, offline=a.offline, only=a.id)
    s = summary(os.path.join(a.root, 'data'))
    print(f"{s['entries']} playbook(s) checked, {s['entriesOk']} fully verified; items: " + ', '.join(f'{k} {v}' for k, v in s['totals'].items()))
    for r in s['review']:
        print(f"  {r['status']:13s} {r['id']}: {r['item']}" + (f"  (not on the page: {', '.join('-' + m if not m.startswith('-') else m for m in r['missing'])})" if r['missing'] else ''))
    return 1 if any(r['status'] == 'param-missing' for r in s['review']) else 0


if __name__ == '__main__':
    sys.exit(main())
