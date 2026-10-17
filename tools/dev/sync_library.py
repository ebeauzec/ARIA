"""Copy the NetApp Reference Library into the repository (reference/netapp-library/), so ARIA ships with it and works without any external folder.

    python tools/dev/sync_library.py [--source PATH] [--check]

The library is a set of markdown digests and indexes of NetApp's public documentation, each with its source URL and fetch date. It is maintained outside the
repository (by a separate weekly job); this script brings a copy in. It is the only way the shipped copy changes: never edit files under reference/ by hand.

What is copied and what is not:
  * every .md file of the library, with the same folder structure;
  * left out: CHANGELOG.md (the maintenance log of the external library), files that record failed fetches (_FAILED.md), anything that is not markdown;
  * a personal first name in the prose is replaced by "the engineer" (the library was written for one person; the shipped copy is for any reader), and e-mail
    addresses (NetApp's documentation feedback contacts) are omitted.
The copy is checked with the sensitive-data guard before it can be committed (the commit and push hooks run it again).

--check only reports what would change (exit 1 when the shipped copy is out of date). The normal flow, after the weekly harvest or when the check reports changes:
sync, run `python tools/dev/release.py ...` for a release that says "library copy refreshed", test, commit, push.
"""
import argparse
import filecmp
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import library_manager as lm  # noqa: E402

DEST = os.path.join(ROOT, 'reference', 'netapp-library')
SKIP_NAMES = {'CHANGELOG.md'}
SKIP_SUFFIX = ('_FAILED.md',)
# the library was compiled for one person; the shipped copy reads as written for any engineer
_NAME = [(re.compile(r"\bEugene's\b"), "the engineer's"), (re.compile(r'\bEugene\b'), 'the engineer'),
         (re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'), '[e-mail address omitted]'),
         (re.compile(r'\b([A-Za-z0-9_.-]+)@\d{1,3}(?:\.\d{1,3}){3}\b'), r'\1@<host>')]


def clean(text):
    for rx, to in _NAME:
        text = rx.sub(to, text)
    return text


def source_files(src):
    for dp, dn, fn in os.walk(src):
        dn[:] = [d for d in dn if not d.startswith('.')]
        for f in sorted(fn):
            if not f.lower().endswith('.md') or f in SKIP_NAMES or f.endswith(SKIP_SUFFIX):
                continue
            yield os.path.relpath(os.path.join(dp, f), src)


def build(src, out):
    n = 0
    for rel in source_files(src):
        target = os.path.join(out, rel)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(os.path.join(src, rel), encoding='utf-8', errors='replace', newline='') as fh:
            text = clean(fh.read().replace('\r\n', '\n'))
        with open(target, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(text)
        n += 1
    return n


def diff(new_dir, old_dir):
    added, changed, removed = [], [], []
    new = {os.path.relpath(os.path.join(dp, f), new_dir) for dp, _d, fs in os.walk(new_dir) for f in fs}
    old = {os.path.relpath(os.path.join(dp, f), old_dir) for dp, _d, fs in os.walk(old_dir) for f in fs} if os.path.isdir(old_dir) else set()
    for rel in sorted(new):
        if rel not in old:
            added.append(rel)
        elif not filecmp.cmp(os.path.join(new_dir, rel), os.path.join(old_dir, rel), shallow=False):
            changed.append(rel)
    removed = sorted(r for r in old if r not in new and r != 'README.md')
    return added, changed, removed


def behind(src=None):
    """True when the external library differs from the shipped copy, False when they match, None when there is no external library."""
    src = src or lm.find_library({}, include_bundled=False).get('path')
    if not src or not os.path.isfile(os.path.join(src, 'INDEX.md')):
        return None
    with tempfile.TemporaryDirectory() as tmp:
        build(src, tmp)
        return any(diff(tmp, DEST))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--source', help='the library folder; default: the one ARIA finds outside the repository')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args(argv)
    src = a.source
    if not src:
        found = lm.find_library({}, include_bundled=False)
        src = found.get('path')
        if not src:
            print('No external NetApp Reference Library was found: pass --source PATH.')
            return 2
    if not os.path.isfile(os.path.join(src, 'INDEX.md')):
        print(f'{src} has no INDEX.md: not the NetApp Reference Library.')
        return 2
    with tempfile.TemporaryDirectory() as tmp:
        n = build(src, tmp)
        added, changed, removed = diff(tmp, DEST)
        print(f'source: {src}\n{n} files in the library copy: {len(added)} new, {len(changed)} changed, {len(removed)} no longer in the library')
        for tag, lst in (('new', added), ('changed', changed), ('removed', removed)):
            for r in lst[:12]:
                print(f'  {tag:8s} {r}')
            if len(lst) > 12:
                print(f'  ... and {len(lst) - 12} more {tag}')
        if a.check:
            return 1 if (added or changed or removed) else 0
        if not (added or changed or removed):
            print('The shipped copy is current.')
            return 0
        os.makedirs(DEST, exist_ok=True)
        for r in removed:
            os.remove(os.path.join(DEST, r))
        for r in added + changed:
            os.makedirs(os.path.dirname(os.path.join(DEST, r)), exist_ok=True)
            shutil.copyfile(os.path.join(tmp, r), os.path.join(DEST, r))
    print(f'Updated {DEST}. Next: tests, python tools/dev/release.py (a release that says the library copy was refreshed), commit, push.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
