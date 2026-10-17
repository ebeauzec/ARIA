"""The NetApp Reference Library that ships with ARIA (reference/netapp-library/) and how it is found and kept."""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'dev'))
import library_manager as lm  # noqa: E402
import sync_library  # noqa: E402


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)


class ShippedCopyTests(unittest.TestCase):
    def test_the_copy_is_there_and_is_found_when_nothing_else_is(self):
        self.assertTrue(os.path.isfile(os.path.join(ROOT, 'reference', 'netapp-library', 'INDEX.md')))
        old = lm._candidate_paths
        lm._candidate_paths = lambda: []           # no external library on this machine
        saved = os.environ.pop('ARIA_LIBRARY_PATH', None)
        try:
            found = lm.find_library({})
            self.assertEqual(found['source'], 'bundled with ARIA')
            self.assertTrue(found['path'].replace('\\', '/').endswith('reference/netapp-library'))
            self.assertEqual(lm.find_library({}, include_bundled=False)['source'], 'not found')
        finally:
            lm._candidate_paths = old
            if saved is not None:
                os.environ['ARIA_LIBRARY_PATH'] = saved

    def test_a_library_the_user_points_to_wins_over_the_shipped_copy(self):
        with tempfile.TemporaryDirectory() as d:
            write(os.path.join(d, 'INDEX.md'), '# index')
            self.assertEqual(lm.find_library({'libraryPath': d}), {'path': d, 'source': 'config (libraryPath)'})

    def test_the_copy_can_be_searched(self):
        root = os.path.join(ROOT, 'reference', 'netapp-library')
        res = lm.search(root, 'SnapMirror', limit=3)
        self.assertGreater(res['total'], 0)
        self.assertTrue(res['results'][0].get('path'))

    def test_nothing_personal_or_unwanted_is_in_the_copy(self):
        bad = []
        for dp, _d, fs in os.walk(os.path.join(ROOT, 'reference')):
            for f in fs:
                if f in ('CHANGELOG.md',) or f.endswith('_FAILED.md'):
                    bad.append(f)
                    continue
                text = open(os.path.join(dp, f), encoding='utf-8').read()
                if 'Eugene' in text:
                    bad.append(f + ': a personal name')
                if sync_library._NAME[2][0].search(text):
                    bad.append(f + ': an e-mail address')
        self.assertEqual(bad, [])


class SyncTests(unittest.TestCase):
    def test_what_is_copied_and_what_is_cleaned(self):
        with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as out:
            write(os.path.join(src, 'INDEX.md'), '# Index\r\nFor Eugene: write to ' + 'team' + '@' + 'example.com or ' + 'root' + '@' + '10.1.2.3' + '\r\n')
            write(os.path.join(src, 'CHANGELOG.md'), 'log')
            write(os.path.join(src, 'ONTAP-Core', 'docs', 'a.md'), "Eugene's note")
            write(os.path.join(src, 'ONTAP-Core', 'docs', '_FAILED.md'), 'failed')
            write(os.path.join(src, 'ONTAP-Core', 'docs', 'data.json'), '{}')
            self.assertEqual(sync_library.build(src, out), 2)
            names = sorted(os.path.relpath(os.path.join(dp, f), out).replace('\\', '/') for dp, _d, fs in os.walk(out) for f in fs)
            self.assertEqual(names, ['INDEX.md', 'ONTAP-Core/docs/a.md'])
            idx = open(os.path.join(out, 'INDEX.md'), encoding='utf-8', newline='').read()
            self.assertIn('For the engineer: write to [e-mail address omitted] or root@<host>\n', idx)    # LF endings
            self.assertEqual(open(os.path.join(out, 'ONTAP-Core', 'docs', 'a.md'), encoding='utf-8').read(), "the engineer's note")


if __name__ == '__main__':
    unittest.main()
