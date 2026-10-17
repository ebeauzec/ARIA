"""Tests for tools/library_updater.py (the reference updater). No network: pages come from a fake fetch."""
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import library_updater as lu  # noqa: E402


def page(body, title='Release notes'):
    return f'<html><head><title>{title}</title></head><body><nav>menu</nav><main>{body}</main><footer>x</footer></body></html>'


FILLER = '<p>' + 'ONTAP release notes list every supported release and what changed in each. ' * 12 + '</p>'


class Fetcher:
    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def __call__(self, url):
        self.calls.append(url)
        v = self.pages.get(url)
        return (v, None) if v is not None else (None, 'HTTP 404')


class TextTests(unittest.TestCase):
    def test_main_block_only(self):
        title, text = lu.html_to_text(page('<h1>Heading</h1><ul><li>one</li><li>two</li></ul>' + FILLER))
        self.assertEqual(title, 'Release notes')
        self.assertIn('# Heading', text)
        self.assertIn('- one', text)
        self.assertNotIn('menu', text)

    def test_atom_feed(self):
        feed = '<?xml version="1.0"?><feed><entry><title>v26.06.2</title><updated>2026-10-08T10:00:00Z</updated></entry></feed>'
        self.assertEqual(lu.html_to_text(feed)[1], '- v26.06.2 (2026-10-08)')

    def test_facts(self):
        f = lu.extract_facts('ONTAP 9.19.1 and 9.18.1P3 fix CVE-2026-1234 (ntap-20261001-0001); see CFBMC-8277 and TR-4569. Trident 26.06.2.')
        self.assertEqual(f['versions']['ONTAP'][-1], '9.19.1')
        self.assertEqual(f['versions']['Trident'], ['26.06.2'])
        self.assertEqual(f['ids']['kb'], ['CFBMC-8277'])
        self.assertEqual(f['ids']['cve'], ['CVE-2026-1234'])

    def test_compare_new_version_and_ids(self):
        old = 'ONTAP 9.18.1 is current. CVE-2026-1111 fixed.'
        new = 'ONTAP 9.19.1 is current. CVE-2026-1111 fixed. CVE-2026-2222 added.'
        ev = lu.compare(old, new, lu.extract_facts(old), lu.extract_facts(new))
        kinds = {e['kind'] for e in ev}
        self.assertIn('new-version', kinds)
        self.assertIn('new-id', kinds)
        self.assertEqual([e for e in ev if e['kind'] == 'new-id'][0]['ids'], ['CVE-2026-2222'])

    def test_date_only_change_is_not_an_event(self):
        a = 'ONTAP release list\nLast updated 2026-10-01\nentry one\nentry two'
        b = 'ONTAP release list\nLast updated 2026-10-08\nentry one\nentry two'
        self.assertEqual(lu.compare(a, b, lu.extract_facts(a), lu.extract_facts(b)), [])

    def test_sign_in_hosts_are_never_requested(self):
        text, err = lu.http_get('https://mysupport.netapp.com/site/x')
        self.assertIsNone(text)
        self.assertIn('not requested', err)
        text, err = lu.http_get('http://docs.netapp.com/x')
        self.assertIsNone(text)


class RunTests(unittest.TestCase):
    def setUp(self):
        self.base = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.base, 'data'))
        with open(os.path.join(self.base, 'data', 'version_catalog.json'), 'w') as fh:
            json.dump({'ontap': ['9.18.1', '9.17.1'], 'storagegrid': ['12.0'], 'santricity': ['12.0']}, fh)
        with open(os.path.join(self.base, 'resolution_rules.json'), 'w') as fh:
            fh.write('{"firmwareKnownIssues": [{"id": "CFBMC-8277"}]}')
        self.url = lu.KEY_PAGES[0][2]
        self.quiet = lambda *_a, **_k: None

    def tearDown(self):
        shutil.rmtree(self.base, ignore_errors=True)

    def sweep(self, body):
        pages = {k[2]: page('<p>Unrelated key page.</p>' + FILLER) for k in lu.KEY_PAGES}   # every other key page reads fine and never changes
        pages[self.url] = page(body)
        return lu.run_update(self.base, {}, fetch=Fetcher(pages), budget=0, log=self.quiet, sleep=lambda s: None)

    def test_first_read_is_a_baseline_then_a_new_release_is_queued(self):
        r1 = self.sweep('<h1>Releases</h1><p>ONTAP 9.18.1 is the newest release.</p>' + FILLER)
        self.assertEqual(r1['events'], [])
        self.assertEqual(r1['baselined'], len(lu.KEY_PAGES))
        r2 = self.sweep('<h1>Releases</h1><p>ONTAP 9.19.1 is the newest release.</p><p>ONTAP 9.18.1 before it.</p>' + FILLER)
        ev = [e for e in r2['events'] if e['kind'] == 'new-version']
        self.assertEqual((ev[0]['was'], ev[0]['now']), ('9.18.1', '9.19.1'))
        self.assertFalse(ev[0]['covered'])   # ARIA's catalogue does not hold 9.19 yet
        self.assertTrue(r2['scannersNeeded'])
        st = lu.status(self.base)
        self.assertEqual(st['queue'][0]['kind'], 'new-version')
        self.assertTrue(os.path.isdir(os.path.join(self.base, 'data', lu.CACHE_DIR)))

    def test_a_release_ARIA_already_holds_is_covered_and_not_queued(self):
        self.sweep('<p>ONTAP 9.17.1 is the newest release.</p>' + FILLER)
        r = self.sweep('<p>ONTAP 9.18.1 is the newest release.</p><p>ONTAP 9.17.1 before it.</p>' + FILLER)
        ev = [e for e in r['events'] if e['kind'] == 'new-version'][0]
        self.assertTrue(ev['covered'])
        self.assertEqual(lu.status(self.base)['openItems'], 0)

    def test_known_issue_id_stub_and_ack(self):
        self.sweep('<p>Known issues: CFBMC-8277.</p>' + FILLER)
        self.sweep('<p>Known issues: CFBMC-8277, CFBMC-9999.</p>' + FILLER)
        q = lu.status(self.base)['queue']
        self.assertEqual(len(q), 1)   # CFBMC-8277 is in the rules, so only the new id is queued
        self.assertEqual(q[0]['stubs'][0]['id'], 'CFBMC-9999')
        self.assertEqual(q[0]['stubs'][0]['component'], 'BMC')
        self.assertEqual(lu.ack(os.path.join(self.base, 'data'), [q[0]['id']]), 1)
        self.assertEqual(lu.status(self.base)['openItems'], 0)
        self.sweep('<p>Known issues: CFBMC-8277, CFBMC-9999.</p>' + FILLER)   # the same id again does not reopen it
        self.assertEqual(lu.status(self.base)['openItems'], 0)

    def test_a_changed_playbook_source_page_queues_a_review_of_that_playbook(self):
        os.makedirs(os.path.join(self.base, 'tools'))
        src = 'https://docs.netapp.com/us-en/ontap/example/procedure.html'
        pb = {'playbooks': [{'id': 'ontap.example', 'status': 'approved', 'family': 'ontap', 'match': 'example', 'cause': 'c', 'impact': 'i', 'steps': ['1. a', '2. b', '3. c'], 'sources': [src]},
                            {'id': 'ontap.other', 'status': 'approved', 'family': 'ontap', 'match': 'other', 'cause': 'c', 'impact': 'i', 'steps': ['1. a', '2. b', '3. c'], 'sources': [src, 'https://mysupport.netapp.com/x']}]}
        with open(os.path.join(self.base, 'tools', 'playbooks.json'), 'w') as fh:
            json.dump(pb, fh)
        self.assertEqual(lu.playbook_sources(self.base), {src: ['ontap.example', 'ontap.other']})   # a sign-in host is never watched
        self.assertIn(src, [x['url'] for x in lu.load_sources(self.base)])

        def run(body):
            pages = {k[2]: page('<p>Unrelated key page.</p>' + FILLER) for k in lu.KEY_PAGES}
            pages[src] = page(body)
            return lu.run_update(self.base, {}, fetch=Fetcher(pages), budget=5, log=self.quiet, sleep=lambda s: None)
        run('<h1>Procedure</h1><p>Run the first command.</p><p>Then run the second command.</p>' + FILLER)       # baseline: nothing queued
        self.assertEqual([i for i in lu.status(self.base)['queue'] if i['kind'] == 'playbook-source-changed'], [])
        r = run('<h1>Procedure</h1><p>Run the NEW first command with a new option.</p><p>Then run the second command after a check.</p>' + FILLER)
        self.assertEqual(r['playbookPages'], 1)
        items = [i for i in lu.status(self.base)['queue'] if i['kind'] == 'playbook-source-changed']
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['playbooks'], ['ontap.example', 'ontap.other'])
        self.assertIn('ontap.example', items[0]['title'])
        run('<h1>Procedure</h1><p>Run the NEW first command with a new option.</p><p>Then run the second command after a check.</p>' + FILLER)       # unchanged again: no second item
        self.assertEqual(len([i for i in lu.status(self.base)['queue'] if i['kind'] == 'playbook-source-changed']), 1)

    def test_unreadable_page_is_reported_and_queued_after_three_runs(self):
        f = Fetcher({})
        for _ in range(3):
            r = lu.run_update(self.base, {}, fetch=f, budget=0, log=self.quiet, sleep=lambda s: None)
        self.assertTrue(r['unreachable'])
        self.assertTrue(any(i['kind'] == 'source-unreachable' for i in lu.status(self.base)['queue']))

    def test_tables_say_which_hand_kept_table_has_a_changed_source(self):
        ref = os.path.join(self.base, 'data', 'reference_library.js')
        with open(ref, 'w') as fh:
            fh.write('window.ARIA_REF = {};')
        os.utime(ref, (1, 1))   # compiled long ago
        self.sweep('<p>ONTAP systems what\'s new: AFF A90.</p>' + FILLER)
        url = 'https://docs.netapp.com/us-en/ontap-systems/whats-new.html'
        f = Fetcher({u: page('<p>x</p>' + FILLER) for u in [s[2] for s in lu.KEY_PAGES]})
        f.pages[url] = page('<p>ONTAP systems what\'s new: AFX 2K added.</p>' + FILLER)
        lu.run_update(self.base, {}, fetch=Fetcher({url: page('<p>ONTAP systems what\'s new: AFF A90.</p>' + FILLER)}), budget=0, log=self.quiet, sleep=lambda s: None)
        lu.run_update(self.base, {}, fetch=f, budget=0, log=self.quiet, sleep=lambda s: None)
        tables = {t['key']: t for t in lu.status(self.base)['tables']}
        self.assertEqual(tables['REFERENCE_LIBRARY_PLATFORM_REPLACEMENTS']['status'], 'review')
        self.assertEqual(tables['REFERENCE_LIBRARY_PLATFORM_REPLACEMENTS']['mode'], 'manual')


if __name__ == '__main__':
    unittest.main()
