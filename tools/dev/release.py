"""Bump the version everywhere for a release (the first half of the release routine in CLAUDE.md).

    python tools/dev/release.py --title "Short title" --notes "One line for version.json" --kind Added --items items.json [--version 5.6.360] [--date 2026-10-17]

items.json is a list of strings: the entries of the in-app changelog and of CHANGELOG.md. The old version is read from version.json; the new one
defaults to the next patch number. It edits, keeping each file's line endings:
  version.json (version, patch, notes), app.js (APP_VERSION and a new APP_CHANGELOG entry), CHANGELOG.md, index_src.html (the ?v= stamps), README.md (badge).

It does NOT run the tests, the guard, commit or push. The rest of the routine, in order:
  node --check app.js ; python tests/run_tests.py ; python tools/guard_sensitive.py --tree HEAD   (the commit and push hooks run the guard again)
  git add -A ; git commit -m "ARIA <version>: <summary>"       (no Claude/Anthropic trailer, ever; never --no-verify)
  git push origin main   (about 15 minutes with the pre-push guard: run it in the background with stdin from /dev/null, then check git status -sb)
"""
import argparse
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from patchlib import edit, set_root, _path  # noqa: E402


def next_patch(version):
    m = re.fullmatch(r'(\d+)\.(\d+)\.(\d+)', version)
    if not m:
        raise SystemExit(f'cannot read the version {version!r} from version.json')
    return f'{m.group(1)}.{m.group(2)}.{int(m.group(3)) + 1}'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--title', required=True)
    ap.add_argument('--notes', required=True, help='the one line stored in version.json')
    ap.add_argument('--kind', choices=('Added', 'Fixed'), default='Added')
    ap.add_argument('--items', required=True, help='JSON file: a list of strings')
    ap.add_argument('--version', help='default: the next patch')
    ap.add_argument('--date', default=datetime.date.today().isoformat())
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--root', help='another tree (for the tests)')
    a = ap.parse_args(argv)
    if a.root:
        set_root(a.root)

    with open(_path('version.json'), encoding='utf-8') as fh:
        vj = json.load(fh)
    old = vj['version']
    new = a.version or next_patch(old)
    with open(a.items, encoding='utf-8') as fh:
        items = json.load(fh)
    if not isinstance(items, list) or not items or not all(isinstance(i, str) and i.strip() for i in items):
        raise SystemExit('items must be a non-empty JSON list of strings')
    if new == old:
        raise SystemExit(f'the new version equals the current one ({old})')
    print(f'{old} -> {new}: {a.title}')
    if a.dry_run:
        return 0

    icon, color = ('✨', '#3b82f6') if a.kind == 'Added' else ('\U0001F527', '#22c55e')

    def app(t):
        if t.count(f'const APP_VERSION = "{old}"') != 1:
            raise AssertionError(f'app.js: APP_VERSION "{old}" not found exactly once')
        t = t.replace(f'const APP_VERSION = "{old}"', f'const APP_VERSION = "{new}"', 1)
        body = '\n'.join('          %s,' % json.dumps(i, ensure_ascii=False) for i in items)
        entry = ('const APP_CHANGELOG = [\n  {\n    version: "%s",\n    date: "%s",\n    title: %s,\n    sections: [\n      {\n        icon: "%s",\n        label: "%s",\n        color: "%s",\n        items: [\n%s\n        ],\n      },\n    ],\n  },\n'
                 % (new, a.date, json.dumps(a.title, ensure_ascii=False), icon, a.kind, color, body))
        if 'const APP_CHANGELOG = [\n' not in t:
            raise AssertionError('app.js: APP_CHANGELOG not found')
        return t.replace('const APP_CHANGELOG = [\n', entry, 1)

    edit('app.js', app)
    patch = vj.get('patch', 0)

    def ver(t):
        t = re.sub(r'"patch": \d+', '"patch": %d' % (int(patch) + 1), t, count=1)
        t = t.replace(old, new)
        t = re.sub(r'"date": "[^"]*"', '"date": "%s"' % a.date, t, count=1)
        return re.sub(r'"notes": ".*"', lambda m: '"notes": %s' % json.dumps(a.notes, ensure_ascii=False), t, count=1)
    edit('version.json', ver)
    edit('CHANGELOG.md', lambda t: t.replace('# Changelog\n', '# Changelog\n\n## %s (%s)\n\n### %s\n%s\n' % (new, a.date, a.kind, '\n'.join('- ' + i for i in items)), 1))
    edit('index_src.html', lambda t: t.replace('?v=' + old, '?v=' + new))
    edit('README.md', lambda t: t.replace(f'badge/version-{old}-', f'badge/version-{new}-'))
    print('updated: version.json, app.js, CHANGELOG.md, index_src.html, README.md')
    print('next: node --check app.js ; python tests/run_tests.py ; guard ; commit "ARIA %s: ..." (no Claude trailer) ; push in the background' % new)
    return 0


if __name__ == '__main__':
    sys.exit(main())
