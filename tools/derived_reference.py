"""Reference tables that used to be kept by hand, derived from data ARIA already collects (no AI, no extra network access).

Inputs, all local files the scanners keep current:
  advisory_resolutions.json   NetApp advisories with their fixed releases per product
  ontap_release_notes.json    per-release feature lists read from the What's new pages
  eoa_database.json           end-of-availability platform names
  platform_hardware.json      models that have documentation pages
  imt_interop.json            integration versions
  fleet_evidence.json         ONTAP releases seen installed or recommended in the monitored fleet (written at harvest)

Output: data/derived_reference.json, applied by server._reference_overlay_js() over the hand-kept file, and the latest release per
ONTAP line merged into data/firmware_baselines.json (ontap.latestByBranch).

What is derived and how (each rule is deliberate and stated here, so the result can be explained):
  latestByBranch      highest release per ONTAP line among every fixed release in the advisories, and every release installed in or
                      recommended for the fleet. Evidence that a release exists, not a claim that nothing newer was published.
  preleaseMinimums    per line, the highest fixed release among advisories rated high or critical (score 7.0 or more) that name ONTAP 9:
                      the first release of that line with no known high or critical advisory open against it.
  currentPlatforms    models with ONTAP hardware documentation that are not on the end-of-availability list, grouped by family.
  upgradeCaveats      per release, the What's new entries that change behaviour (a default flips, something is removed or deprecated, a
                      requirement is added) plus everything in that release's Upgrade section.
  mcFeatureVersions   per MetroCluster feature mentioned in the release notes, the first release that lists it.
Not derived (judgement, not fact): platform replacements, best practices, naming conventions, personalities, Keystone, AFX and ASA r2 notes.
"""
import json
import os
import re
from datetime import datetime, timezone


def _load(path):
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def vkey(v):
    """Sortable key: 9.16.1P9 < 9.16.1P11 < 9.17.1."""
    s = str(v or '')
    nums = tuple(int(x) for x in re.findall(r'\d+', re.split(r'[Pp]', s)[0]))
    p = re.search(r'[Pp](\d+)', s)
    return (nums, int(p.group(1)) if p else 0)


def branch(v):
    m = re.match(r'^\s*(?:ONTAP\s+)?(\d+)\.(\d+)(?:\.(\d+))?', str(v or ''))
    if not m or m.group(1) != '9' or m.group(3) is None:
        return ''
    return f'{m.group(1)}.{m.group(2)}.{m.group(3)}'


def _clean(v):
    m = re.match(r'^\s*(?:ONTAP\s+)?(\d+\.\d+\.\d+(?:[Pp]\d+)?)', str(v or ''))
    return m.group(1).upper() if m else ''


def _ontap_fixes(adv):
    """[(release, advisory record)] for every fixed ONTAP 9 release in one advisory."""
    out = []
    for f in adv.get('fixes') or []:
        if re.match(r'^ONTAP 9\b', str(f.get('product') or '')) and not f.get('wontfix'):
            for v in f.get('versions') or []:
                c = _clean(v)
                if c:
                    out.append(c)
    return out


def latest_by_branch(advisories, evidence):
    best = {}
    def see(v):
        c = _clean(v); b = branch(c)
        if b and (b not in best or vkey(c) > vkey(best[b])):
            best[b] = c
    for adv in advisories.values():
        for v in _ontap_fixes(adv):
            see(v)
    for k in ('installed', 'recommended'):
        for v in (evidence or {}).get(k, []):
            see(v)
    return best


def prerelease_minimums(advisories):
    per = {}
    for aid, adv in advisories.items():
        try:
            score = float(adv.get('score') or 0)
        except (TypeError, ValueError):
            score = 0.0
        if score < 7.0 and str(adv.get('severity') or '').lower() not in ('high', 'critical'):
            continue
        for v in _ontap_fixes(adv):
            b = branch(v)
            if not b:
                continue
            e = per.setdefault(b, {'v': v, 'ids': {}})
            e['ids'][aid.upper()] = (score, (adv.get('cve') or [''])[0])
            if vkey(v) > vkey(e['v']):
                e['v'] = v
    out = {}
    for b, e in per.items():
        top = sorted(e['ids'].items(), key=lambda x: -x[1][0])[:3]
        shown = ', '.join(f"{i} ({c or 'no CVE'}, CVSS {s:g})" for i, (s, c) in top)
        out[b] = {'minSafe': e['v'], 'reason': f"Highest fixed release among {len(e['ids'])} NetApp advisories rated high or critical for ONTAP 9 on this line, from the advisories' own fixed-release lists. Highest scores: {shown}.", 'derived': True}
    return out


_EOA_ALIAS = lambda n: n.upper().replace('AFF ', '').replace('-', ' ').strip()


def current_platforms(hardware, eoa_platforms):
    eoa = {_EOA_ALIAS(p) for p in (eoa_platforms or [])}
    groups = {'aff_a_series': [], 'aff_c_series': [], 'fas': [], 'afx': []}
    for entry in (hardware or {}).values():
        for m in entry.get('models') or []:
            name = str(m).strip()
            token = _EOA_ALIAS(name)
            if any(token == e or token.replace('ASA ', '') == e for e in eoa):
                continue
            up = name.upper()
            if up.startswith('AFF A'):
                g = 'aff_a_series'
            elif up.startswith('AFF C'):
                g = 'aff_c_series'
            elif up.startswith('AFX'):
                g = 'afx'
            elif up.startswith('FAS'):
                g = 'fas'
            else:
                continue
            if name not in groups[g]:
                groups[g].append(name)
    return {k: sorted(v, key=lambda x: [int(t) if t.isdigit() else t for t in re.findall(r'\d+|\D+', x)]) for k, v in groups.items() if v}


_CHANGE = re.compile(r'\b(enabled by default|disabled by default|by default|no longer|removed|deprecat|replaces|replaced by|now requires?|requires?\b|must\b|not supported|end of)\b', re.I)


def upgrade_caveats(notes):
    out = {}
    for rel, entry in ((notes or {}).get('releases') or {}).items():
        items = []
        for sec, rows in (entry.get('sections') or {}).items():
            for r in rows:
                text = (r.get('title') or '') + ' ' + (r.get('detail') or '')
                if sec.lower() == 'upgrade' or _CHANGE.search(text):
                    line = f"{r['title']}" + (f": {r['detail']}" if r.get('detail') else '')
                    items.append(f"{sec}: {line}"[:320])
        if items:
            out[rel] = items[:10]
    return out


def mc_feature_versions(notes):
    first = {}
    for rel, entry in sorted(((notes or {}).get('releases') or {}).items(), key=lambda x: vkey(x[0])):
        for sec, rows in (entry.get('sections') or {}).items():
            for r in rows:
                if re.search(r'metrocluster', (r.get('title') or '') + ' ' + (r.get('detail') or ''), re.I):
                    t = (r['title'] or '')[:90]
                    if t and t not in first:
                        first[t] = rel
    return first


def build(data_dir):
    d = lambda n: os.path.join(data_dir, n)
    adv = _load(d('advisory_resolutions.json')) or {}
    adv = adv.get('resolutions', adv) if isinstance(adv, dict) else {}
    adv = {k: v for k, v in adv.items() if isinstance(v, dict)}
    notes = _load(d('ontap_release_notes.json')) or {}
    eoa = _load(d('eoa_database.json')) or {}
    hw = (_load(d('platform_hardware.json')) or {}).get('platforms') or {}
    imt = _load(d('imt_interop.json')) or {}
    ev = _load(d('fleet_evidence.json')) or {}
    out = {
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'latestByBranch': latest_by_branch(adv, ev),
        'prereleaseMinimums': prerelease_minimums(adv),
        'currentPlatforms': current_platforms(hw, eoa.get('platforms')),
        'upgradeCaveats': upgrade_caveats(notes),
        'mcFeatureVersions': mc_feature_versions(notes),
        'tridentGA': (imt.get('trident') or {}).get('currentRecommended') or '',
        'basis': {'advisories': len(adv), 'releaseNotes': len((notes or {}).get('releases') or {}), 'fleetReleases': len(ev.get('installed', [])) + len(ev.get('recommended', []))},
    }
    tmp = d('derived_reference.json') + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, d('derived_reference.json'))
    # keep the latest-release-per-line baseline the harvest and the app already read current
    fw = _load(d('firmware_baselines.json'))
    if isinstance(fw, dict) and out['latestByBranch']:
        cur = ((fw.get('ontap') or {}).get('latestByBranch')) or {}
        changed = False
        for b, v in out['latestByBranch'].items():
            if b not in cur or vkey(v) > vkey(cur[b]):
                cur[b] = v
                changed = True
        if changed:
            fw.setdefault('ontap', {})['latestByBranch'] = cur
            tmp = d('firmware_baselines.json') + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as fh:
                json.dump(fw, fh, indent=2, ensure_ascii=False)
            os.replace(tmp, d('firmware_baselines.json'))
    return out['basis'] | {'branches': len(out['latestByBranch']), 'minimums': len(out['prereleaseMinimums'])}


def write_fleet_evidence(data_dir, systems):
    """Union of the ONTAP releases seen installed and recommended; called at the end of every harvest."""
    path = os.path.join(data_dir, 'fleet_evidence.json')
    cur = _load(path) or {}
    inst, rec = set(cur.get('installed') or []), set(cur.get('recommended') or [])
    for s in systems or []:
        a = _clean(s.get('ontapVersion') or s.get('osVersion'))
        b = _clean(s.get('recommendedOSVersion'))
        if a:
            inst.add(a)
        if b:
            rec.add(b)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump({'installed': sorted(inst, key=vkey), 'recommended': sorted(rec, key=vkey), 'updated': datetime.now(timezone.utc).isoformat()}, fh)
    os.replace(tmp, path)
