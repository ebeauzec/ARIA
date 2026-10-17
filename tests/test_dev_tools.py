"""tools/dev: the line-ending-safe patch helpers, the release bump and the maintenance report."""
import json
import os
import sys
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'tools', 'dev'))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'tools'))
import patchlib  # noqa: E402
import release  # noqa: E402
import maintenance  # noqa: E402


def write(path, text, crlf=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text.replace('\n', '\r\n') if crlf else text)


def read(path):
    with open(path, encoding='utf-8', newline='') as fh:
        return fh.read()


class PatchTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        patchlib.set_root(self.d.name)

    def tearDown(self):
        patchlib.set_root(None)
        self.d.cleanup()

    def test_crlf_and_lf_are_kept(self):
        write(os.path.join(self.d.name, 'a.txt'), 'one\ntwo\n', crlf=True)
        write(os.path.join(self.d.name, 'b.txt'), 'one\ntwo\n')
        for f in ('a.txt', 'b.txt'):
            patchlib.replace_once(f, 'one\ntwo', 'one\nTWO')
        self.assertEqual(read(os.path.join(self.d.name, 'a.txt')), 'one\r\nTWO\r\n')
        self.assertEqual(read(os.path.join(self.d.name, 'b.txt')), 'one\nTWO\n')

    def test_the_anchor_must_occur_exactly_once(self):
        write(os.path.join(self.d.name, 'a.txt'), 'x\nx\n')
        with self.assertRaises(AssertionError):
            patchlib.replace_once('a.txt', 'x', 'y')
        with self.assertRaises(AssertionError):
            patchlib.replace_once('a.txt', 'missing', 'y')
        self.assertEqual(read(os.path.join(self.d.name, 'a.txt')), 'x\nx\n')    # nothing was written


class ReleaseTests(unittest.TestCase):
    def test_every_place_is_bumped_and_line_endings_survive(self):
        with tempfile.TemporaryDirectory() as d:
            write(os.path.join(d, 'version.json'), '{\n  "version": "1.2.3",\n  "patch": 3,\n  "date": "2026-01-01",\n  "notes": "old"\n}', crlf=True)
            write(os.path.join(d, 'app.js'), 'const APP_VERSION = "1.2.3";\nconst APP_CHANGELOG = [\n  {\n    version: "1.2.3",\n  },\n];\n', crlf=True)
            write(os.path.join(d, 'CHANGELOG.md'), '# Changelog\n\n## 1.2.3 (2026-01-01)\n')
            write(os.path.join(d, 'index_src.html'), '<script src="app.js?v=1.2.3"></script><link href="styles.css?v=1.2.3">')
            write(os.path.join(d, 'README.md'), '![v](https://img.shields.io/badge/version-1.2.3-blue)')
            items = os.path.join(d, 'items.json')
            write(items, json.dumps(['First item.', 'Second "quoted" item.']))
            try:
                release.main(['--root', d, '--title', 'A title', '--notes', 'A note', '--kind', 'Fixed', '--items', items, '--date', '2026-02-02'])
            finally:
                patchlib.set_root(None)
            vj = json.loads(read(os.path.join(d, 'version.json')))
            self.assertEqual((vj['version'], vj['patch'], vj['date'], vj['notes']), ('1.2.4', 4, '2026-02-02', 'A note'))
            app = read(os.path.join(d, 'app.js'))
            self.assertIn('const APP_VERSION = "1.2.4";', app)
            self.assertIn('version: "1.2.4"', app)
            self.assertIn('version: "1.2.3"', app)          # the previous entry stays
            self.assertIn('"Second \\"quoted\\" item."', app)
            self.assertEqual(app.count('\r\n'), app.count('\n'))      # still CRLF throughout
            self.assertIn('## 1.2.4 (2026-02-02)\n\n### Fixed\n- First item.', read(os.path.join(d, 'CHANGELOG.md')))
            self.assertEqual(read(os.path.join(d, 'index_src.html')).count('?v=1.2.4'), 2)
            self.assertIn('badge/version-1.2.4-', read(os.path.join(d, 'README.md')))


class MaintenanceTests(unittest.TestCase):
    def test_report_lists_the_queue_and_the_instruction(self):
        with tempfile.TemporaryDirectory() as d:
            data = os.path.join(d, 'data')
            write(os.path.join(data, 'library_update_queue.json'), json.dumps({'items': {
                'a': {'id': 'a', 'kind': 'playbook-gap', 'status': 'open'}, 'b': {'id': 'b', 'kind': 'playbook-source-changed', 'status': 'open'}, 'c': {'id': 'c', 'kind': 'new-id', 'status': 'closed'}}}))
            write(os.path.join(data, 'playbook_gaps.json'), json.dumps({'pct': 90.0, 'covered': 9, 'total': 10, 'updated': '2026-01-01T00:00:00Z', 'gaps': {'k': {'key': 'ontap | X | an uncovered finding', 'count': 4}}}))
            txt = maintenance.report(d, 'started in the background')
            self.assertIn('Open review items: 2 (playbook-gap 1, playbook-source-changed 1)', txt)
            self.assertIn('an uncovered finding', txt)
            self.assertIn('INSTRUCTION', txt)
            self.assertIn('Sweep: started in the background.', txt)

    def test_an_empty_queue_says_there_is_nothing_to_do(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, 'data'))
            txt = maintenance.report(d)
            self.assertIn('Open review items: none.', txt)
            self.assertIn('Nothing in the queue needs doing now.', txt)

    def test_a_running_sweep_is_not_started_twice(self):
        with tempfile.TemporaryDirectory() as d:
            p = maintenance._paths(d)
            os.makedirs(p['dev'])
            write(p['lock'], '1')
            write(p['status'], json.dumps({'startedAt': '2026-01-01T00:00:00Z', 'steps': []}))
            self.assertIn('still running', maintenance.start_background(d))
            old = time.time() - 3 * 3600
            os.utime(p['lock'], (old, old))
            self.assertGreater(time.time() - os.path.getmtime(p['lock']), maintenance.LOCK_MINUTES * 60)


if __name__ == '__main__':
    unittest.main()
