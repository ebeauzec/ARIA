"""tools/playbook_verify.py: playbooks checked against NetApp's own pages. No network: pages come from a fake fetch and a temporary data folder."""
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import library_updater as lu  # noqa: E402
import playbook_verify as pv  # noqa: E402


def cli_html(command, params):
    body = '<h1>%s</h1><p>%s</p><h2>Parameters</h2>' % (command, 'Description of the command. ' * 12) + ''.join('<p>[-%s <text>] - A parameter</p>' % p for p in params)
    return '<html><head><title>%s</title></head><body><main>%s</main></body></html>' % (command, body)


class Fetcher:
    def __init__(self, pages):
        self.pages, self.calls = pages, []

    def __call__(self, url):
        self.calls.append(url)
        v = self.pages.get(url)
        return (v, None) if v else (None, 'HTTP 404')


def entry(**kw):
    e = {'id': 'test.example', 'status': 'approved', 'family': 'ontap', 'match': 'x', 'cause': 'c', 'impact': 'i', 'sources': ['https://docs.netapp.com/us-en/ontap/'],
         'steps': ['1. Check: storage failover show -fields auto-giveback', '2. Enable: storage failover modify -node * -auto-giveback true', '3. Confirm: storage failover show']}
    e.update(kw)
    return e


class ParseTests(unittest.TestCase):
    def test_commands_and_their_parameters(self):
        got = pv.all_commands(entry())
        self.assertEqual(got, {'storage failover show': {'fields'}, 'storage failover modify': {'node', 'auto-giveback'}})

    def test_several_commands_in_one_step_and_prose_is_left_alone(self):
        step = '2. Create it: vserver export-policy rule create -vserver <svm> -policyname <p> -clientmatch <subnet> ; vserver export-policy rule modify -vserver {svm} -ruleindex <n>. The volume group and the cluster peer relationship are named in the finding.'
        got = pv.all_commands({'steps': [step]})
        self.assertIn('vserver export-policy rule create', got)
        self.assertEqual(got['vserver export-policy rule modify'], {'vserver', 'ruleindex'})
        self.assertFalse(any(k.startswith(('volume group', 'cluster peer relationship')) for k in got), got)

    def test_set_is_a_command_only_with_privilege(self):
        got = pv.all_commands({'steps': ['1. Do: set -privilege advanced ; storage shelf firmware update -shelf <shelf>', '2. and set volume snapshot autodelete modify -vserver x']})
        self.assertIn('set', got)
        self.assertIn('storage shelf firmware update', got)
        self.assertIn('volume snapshot autodelete modify', got)
        self.assertNotIn('set volume snapshot autodelete modify', got)

    def test_words_after_a_command_that_are_prose_are_cut(self):
        got = pv.all_commands({'steps': ['1. Find them: security certificate show -vserver * ; and security certificate show-truststore for the trusted CAs, then metrocluster check show before and after.']})
        self.assertIn('security certificate show-truststore', got)
        self.assertIn('metrocluster check show', got)

    def test_menu_paths(self):
        e = {'steps': ['1. In System Manager select Support > Upgrade center, then Begin upgrade.', '2. Open Hardware > Drives > Logically replace and click Replace.', '3. Select Maintenance > System > Software update.']}
        self.assertEqual(pv.ui_paths(e), [['Support', 'Upgrade center'], ['Hardware', 'Drives', 'Logically replace'], ['Maintenance', 'System', 'Software update']])


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.base = self.d.name

    def tearDown(self):
        self.d.cleanup()

    def fetcher(self, **extra):
        pages = {pv.CLI_BASE + 'storage-failover-show.html': cli_html('storage failover show', ['fields', 'node']),
                 pv.CLI_BASE + 'storage-failover-modify.html': cli_html('storage failover modify', ['node', 'auto-giveback'])}
        pages.update(extra)
        return Fetcher(pages)

    def test_a_correct_playbook_is_verified_and_pages_are_cached(self):
        f = self.fetcher()
        r = pv.verify_entry(self.base, entry(), f, sleep=lambda s: None)
        self.assertTrue(r['ok'])
        self.assertEqual(r['counts']['verified'], 2)
        self.assertTrue(os.path.exists(os.path.join(self.base, 'data', pv.CACHE_SUB, 'storage-failover-modify.md')))
        n = len(f.calls)
        pv.verify_entry(self.base, entry(), f, sleep=lambda s: None)       # second time: from the cache
        self.assertEqual(len(f.calls), n)

    def test_a_parameter_the_page_does_not_have_is_found(self):
        e = entry(steps=['1. Enable: storage failover modify -node * -auto-giveback-now true', '2. Check: storage failover show', '3. Done: storage failover show'])
        r = pv.verify_entry(self.base, e, self.fetcher(), sleep=lambda s: None)
        bad = [c for c in r['commands'] if c['status'] == 'param-missing']
        self.assertEqual(bad[0]['missing'], ['auto-giveback-now'])
        self.assertFalse(r['ok'])

    def test_a_command_with_no_page_is_not_found_and_an_unreadable_page_is_unchecked(self):
        e = entry(steps=['1. Run: storage failover nosuchcommand -node x', '2. a', '3. b'])
        r = pv.verify_entry(self.base, e, self.fetcher(), sleep=lambda s: None)
        self.assertEqual(r['commands'][0]['status'], 'not-found')

        def boom(url):
            return None, 'URLError: timed out'
        r2 = pv.verify_entry(self.base, entry(), boom, sleep=lambda s: None)
        self.assertTrue(all(c['status'] == 'unchecked' for c in r2['commands']))

    def test_menu_paths_are_checked_against_the_cited_pages(self):
        src = 'https://docs.netapp.com/us-en/e-series-santricity/sm-support/upgrade.html'
        cache = os.path.join(self.base, 'data', lu.CACHE_DIR, 'Playbooks', lu._slug(src) + '.md')
        os.makedirs(os.path.dirname(cache))
        with open(cache, 'w', encoding='utf-8') as fh:
            fh.write('From the left panel, select Support > Upgrade center. Then click Begin upgrade.')
        e = {'id': 'e.test', 'family': 'eseries', 'sources': [src], 'steps': ['1. In System Manager select Support > Upgrade center.', '2. Open Hardware > Drives.']}
        r = pv.verify_entry(self.base, e, None, sleep=lambda s: None)
        by = {p['path']: p for p in r['paths']}
        self.assertEqual(by['Support > Upgrade center']['status'], 'verified')
        self.assertEqual(by['Hardware > Drives']['status'], 'not-found')

    def test_the_record_the_summary_and_the_command_pages(self):
        pv.run(self.base, fetch=self.fetcher(), sleep=lambda s: None, log=lambda *_a: None) if False else None
        os.makedirs(os.path.join(self.base, 'tools'))
        os.makedirs(os.path.join(self.base, 'data'))
        with open(os.path.join(self.base, 'tools', 'playbooks.json'), 'w') as fh:
            json.dump({'playbooks': [entry()]}, fh)
        pv.run(self.base, fetch=self.fetcher(), sleep=lambda s: None)
        s = pv.summary(os.path.join(self.base, 'data'))
        self.assertEqual((s['entries'], s['entriesOk'], s['totals']['verified']), (1, 1, 2))
        self.assertEqual(sorted(pv.command_pages(os.path.join(self.base, 'data'))), sorted([pv.CLI_BASE + 'storage-failover-modify.html', pv.CLI_BASE + 'storage-failover-show.html']))
        # and the page watch of the reference updater now includes them
        self.assertIn(pv.CLI_BASE + 'storage-failover-show.html', lu.playbook_sources(self.base))


class PromoteTests(unittest.TestCase):
    """New procedures are approved automatically when they pass every check; anything else stays a draft."""

    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.base = self.d.name
        os.makedirs(os.path.join(self.base, 'data'))
        self.path = os.path.join(self.base, 'data', 'playbooks_local.json')
        self.fetch = Fetcher({pv.CLI_BASE + 'storage-failover-show.html': cli_html('storage failover show', ['fields', 'node']),
                              pv.CLI_BASE + 'storage-failover-modify.html': cli_html('storage failover modify', ['node', 'auto-giveback'])})

    def tearDown(self):
        self.d.cleanup()

    def write(self, entries):
        with open(self.path, 'w', encoding='utf-8') as fh:
            json.dump({'playbooks': entries}, fh)

    def read(self):
        with open(self.path, encoding='utf-8') as fh:
            return {e['id']: e for e in json.load(fh)['playbooks']}

    def test_a_valid_verified_draft_is_approved_and_the_record_says_how(self):
        self.write([entry(id='test.good', status='draft')])
        ok, kept = pv.promote(self.base, None, self.fetch, sleep=lambda s: None, today='2026-10-17')
        self.assertEqual((ok, kept), (['test.good'], {}))
        e = self.read()['test.good']
        self.assertEqual((e['status'], e['approvedAt']), ('approved', '2026-10-17'))
        self.assertIn('automatic', e['approvedBy'])

    def test_a_wrong_option_an_unofficial_source_or_an_unreadable_page_keeps_a_draft(self):
        wrong = entry(id='test.wrong', status='draft', steps=['1. Run: storage failover modify -node * -not-an-option true', '2. a', '3. b'])
        unofficial = entry(id='test.unofficial', status='draft', sources=['https://example.com/x'])
        self.write([wrong, unofficial, entry(id='test.fine', status='draft')])
        ok, kept = pv.promote(self.base, None, self.fetch, sleep=lambda s: None)
        self.assertEqual(ok, ['test.fine'])
        self.assertIn('param-missing', kept['test.wrong'][0])
        self.assertIn('not a NetApp page', kept['test.unofficial'][0])
        self.assertEqual(self.read()['test.wrong']['status'], 'draft')

        def boom(url):
            return None, 'URLError: offline'
        import shutil
        shutil.rmtree(os.path.join(self.base, 'data', 'library_refreshed'), ignore_errors=True)       # nothing cached: the pages must be read
        self.write([entry(id='test.offline', status='draft')])
        ok, kept = pv.promote(self.base, None, boom, sleep=lambda s: None)
        self.assertEqual(ok, [])
        self.assertIn('unchecked', kept['test.offline'][0])

    def test_menu_paths_are_checked_by_reading_the_cited_page_when_it_is_not_cached(self):
        src = 'https://docs.netapp.com/us-en/e-series-santricity/sm-support/example.html'
        page = '<html><head><title>Example</title></head><body><main><p>' + 'From the left panel, select Support > Diagnostics. ' * 6 + '</p><p>' + 'x' * 300 + '</p></main></body></html>'
        e = {'id': 'test.ui', 'status': 'draft', 'family': 'eseries', 'match': 'x', 'cause': 'c', 'impact': 'i', 'sources': [src], 'steps': ['1. In System Manager select Support > Diagnostics.', '2. b', '3. c']}
        self.write([e])
        ok, kept = pv.promote(self.base, None, Fetcher({src: page}), sleep=lambda s: None)
        self.assertEqual(ok, ['test.ui'], kept)


class ShippedPlaybooksTests(unittest.TestCase):
    def test_every_command_in_the_shipped_playbooks_has_a_known_root(self):
        import playbooks as pb
        ld = pb.load(os.path.join(ROOT, 'data'), os.path.join(ROOT, 'tools', 'playbooks.json'))
        n = 0
        for e in ld['playbooks']:
            if e.get('family') == 'eseries' or e.get('family') == 'storagegrid':
                continue
            for cmd in pv.all_commands(e):
                n += 1
                self.assertIn(cmd.split()[0], pv.ROOTS, (e['id'], cmd))
        self.assertGreater(n, 100)


if __name__ == '__main__':
    unittest.main()
