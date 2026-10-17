"""tools/guard_compliance.py: nothing from NetApp's customer-only areas may be shipped. No network, no repository needed."""
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import guard_compliance as gc  # noqa: E402


def kinds(text):
    return {k for _l, _n, k, _h in gc.scan_text('x.md', text)}


class RuleTests(unittest.TestCase):
    def test_bulletin_notice_and_change_ids(self):
        self.assertIn('NetApp support-bulletin id', kinds('see ' + 'SU' + '570 for details'))
        self.assertIn('NetApp customer-notice id', kinds('notice ' + 'CPC' + '-00602'))
        self.assertIn('NetApp engineering-change id', kinds('change ' + 'ECD' + '-18064'))

    def test_links_and_wording_of_customer_only_areas(self):
        self.assertIn('NetApp customer-bulletin link', kinds('https://kb.netapp.com/' + 'Support_' + 'Bulletins/x'))
        self.assertIn('NetApp support-portal article link', kinds('https://mysupport.netapp.com/site/article?id=1'))
        self.assertIn('NetApp customer-only wording', kinds('Read the ' + 'support ' + 'bulletin first'))
        self.assertIn('content behind a sign-in', kinds('It needs a ' + 'NetApp Support sign-in'))
        self.assertIn('content behind a sign-in', kinds('a support article that needs a sign-in'))
        self.assertIn('content behind a sign-in', kinds('dates are not ' + 'published openly'))
        self.assertIn('marked confidential or internal', kinds('NetApp ' + 'Confidential'))

    def test_ordinary_text_passes(self):
        for t in ('Security bulletins are matched by CVE and NTAP advisory id.',
                  'ARIA sign-in uses local accounts or single sign-on.',
                  'Download the firmware from https://mysupport.netapp.com/site/downloads',
                  'See https://kb.netapp.com/on-prem/ontap/Ontap_OS/OS-KBs/Some_article and NTAP-20240101-0001.',
                  'Node SU1 and the SUN platform'):
            self.assertEqual(kinds(t), set(), t)

    def test_a_marked_line_and_the_rule_files_are_skipped(self):
        self.assertEqual(gc.scan_text('a.md', 'SU' + '570 compliance-ok: reviewed'), [])
        self.assertEqual(gc.scan_text('tools/guard_compliance.py', 'SU' + '570'), [])
        self.assertEqual(gc.scan_text('tests/test_guard_compliance.py@abcdef1', 'SU' + '570'), [])

    def test_procedure_sources_and_scrubbing(self):
        self.assertTrue(gc.gated_source('https://kb.netapp.com/' + 'Support_' + 'Bulletins/Customer_Bulletins/x'))
        self.assertTrue(gc.gated_source('https://mysupport.netapp.com/site/x'))
        self.assertEqual(gc.gated_source('https://docs.netapp.com/us-en/ontap/x.html'), '')
        self.assertNotIn('570', gc.scrub_text('failures due to ' + 'SU' + '570 and KB ID: ' + 'SU' + '588 end'))


class PlaybookTests(unittest.TestCase):
    def test_a_procedure_cannot_cite_or_quote_customer_only_information(self):
        import playbooks as pb
        base = {'id': 'ontap.x', 'status': 'approved', 'family': 'ontap', 'match': 'x', 'cause': 'c', 'impact': 'i',
                'steps': ['1. a', '2. b', '3. c'], 'sources': ['https://docs.netapp.com/us-en/ontap/x.html']}
        self.assertEqual(pb.validate(dict(base)), [])
        gated = dict(base, sources=['https://mysupport.netapp.com/site/x'])
        self.assertTrue(pb.validate(gated))
        text = dict(base, steps=['1. Read the ' + 'support ' + 'bulletin', '2. b', '3. c'])
        self.assertTrue(any('customer-only' in m for m in pb.validate(text)))


class RepositoryTests(unittest.TestCase):
    def test_the_repository_as_committed_is_clean(self):
        try:
            names = subprocess.run(['git', 'ls-files'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
        except Exception:
            self.skipTest('no git')
        bad = []
        for n in names:
            if n.lower().endswith(('.png', '.jpg', '.ico', '.zip', '.exe', '.pdf', '.docx', '.xlsx', '.pptx')):
                continue
            try:
                with open(os.path.join(ROOT, n), encoding='utf-8', errors='replace') as fh:
                    bad.extend(gc.scan_text(n, fh.read()))
            except OSError:
                pass
        self.assertEqual(bad[:5], [], 'customer-only NetApp information in the repository')


if __name__ == '__main__':
    unittest.main()
