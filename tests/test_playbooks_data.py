"""Playbooks as data (tools/playbooks.py) and the data engine in app.js: loading, approval, validation, the gap record and the review queue."""
import json, os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
sys.path.insert(0, HERE)
import playbooks as pb  # noqa: E402


def entry(**kw):
    e = {'id': 'test.example', 'status': 'approved', 'family': 'ontap', 'match': 'example finding', 'cause': 'A cause for {cluster}.', 'impact': 'An impact.',
         'steps': ['1. Check: show {svm}', '2. Change: modify {svm} {thing}', '3. Confirm: show'], 'vars': {'thing': 'thing (\\w+)'}, 'sources': ['https://docs.netapp.com/us-en/ontap/']}
    e.update(kw)
    return e


class LoadTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.dir = self.d.name

    def tearDown(self):
        self.d.cleanup()

    def w(self, name, items):
        with open(os.path.join(self.dir, name), 'w', encoding='utf-8') as fh:
            json.dump({'playbooks': items}, fh)

    def test_shipped_file_is_valid(self):
        ld = pb.load(os.path.join(ROOT, 'data'))   # the shipped set is tools/playbooks.json
        self.assertEqual(ld['problems'], [])
        self.assertGreaterEqual(len(ld['playbooks']), 8)

    def test_only_approved_entries_are_used(self):
        self.w('playbooks_local.json', [entry(id='test.draft', status='draft'), entry(id='test.ok')])
        ld = pb.load(self.dir, os.path.join(self.dir, 'playbooks.json'))
        self.assertEqual([e['id'] for e in ld['playbooks']], ['test.ok'])
        self.assertEqual([e['id'] for e in ld['pending']], ['test.draft'])

    def test_local_replaces_and_rejected_switches_off(self):
        self.w('playbooks.json', [entry(id='test.a', cause='shipped'), entry(id='test.b')])
        self.w('playbooks_local.json', [entry(id='test.a', cause='local'), entry(id='test.b', status='rejected')])
        ld = pb.load(self.dir, os.path.join(self.dir, 'playbooks.json'))
        self.assertEqual({e['id']: e['cause'] for e in ld['playbooks']}, {'test.a': 'local'})

    def test_invalid_entries_are_reported_not_used(self):
        self.w('playbooks_local.json', [entry(id='test.bad', match='(unclosed'), entry(id='test.nosrc', sources=[]), entry(id='test.undeclared', steps=['1. a {nope}', '2. b', '3. c']), entry(id='X')])
        ld = pb.load(self.dir, os.path.join(self.dir, 'playbooks.json'))
        self.assertEqual(ld['playbooks'], [])
        self.assertEqual(ld['counts']['invalid'], 4)
        joined = json.dumps(ld['problems'])
        for needle in ('regular expression', 'sources', '{nope}', 'id must be'):
            self.assertIn(needle, joined)


class ComplianceTests(unittest.TestCase):
    def test_only_netapp_pages_count_as_sources(self):
        self.assertIn('is not a NetApp page', ' '.join(pb.validate(entry(sources=['https://example.com/how-to']))))
        self.assertEqual(pb.validate(entry(sources=['https://docs.netapp.com/us-en/ontap/', 'https://kb.netapp.com/x'])), [])

    def test_no_ontap_commands_in_other_products_and_no_tool_name(self):
        e = entry(family='eseries', steps=['1. Run: cluster image show', '2. b', '3. c'])
        self.assertIn('ONTAP command in an E-Series', ' '.join(pb.validate(e)))
        self.assertEqual(pb.validate(entry(family='eseries', steps=['1. Select Support > Upgrade center.', '2. b', '3. c'])), [])
        self.assertIn('names the tool', ' '.join(pb.validate(entry(cause='ARIA found it'))))


class GapTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.dir = self.d.name

    def tearDown(self):
        self.d.cleanup()

    def gap(self, key, n=3):
        return {'key': key, 'category': 'Best Practices', 'families': ['ontap'], 'count': n, 'systems': 2, 'severity': 'medium', 'detail': 'detail', 'recommendation': 'rec', 'urls': ['https://docs.netapp.com/us-en/ontap/']}

    def queue(self):
        with open(os.path.join(self.dir, 'library_update_queue.json'), encoding='utf-8') as fh:
            return json.load(fh)['items']

    def test_record_status_and_queue(self):
        pb.record_gaps(self.dir, {'total': 100, 'covered': 90, 'gaps': [self.gap('ontap | A | first'), self.gap('ontap | B | second', 9)]}, now='2026-01-01T00:00:00Z')
        st = pb.status(self.dir)
        self.assertEqual(st['pct'], 90.0)
        self.assertEqual([g['key'] for g in st['gaps']], ['ontap | B | second', 'ontap | A | first'])
        q = [v for v in self.queue().values() if v['kind'] == 'playbook-gap']
        self.assertEqual(len(q), 2)
        self.assertTrue(all(v['status'] == 'open' for v in q))
        self.assertIn('playbooks_local.json', q[0]['detail'])

    def test_covered_type_leaves_the_record_and_closes_its_item(self):
        pb.record_gaps(self.dir, {'total': 10, 'covered': 5, 'gaps': [self.gap('ontap | A | first'), self.gap('ontap | B | second')]})
        pb.record_gaps(self.dir, {'total': 10, 'covered': 8, 'gaps': [self.gap('ontap | B | second')]})
        self.assertEqual([g['key'] for g in pb.status(self.dir)['gaps']], ['ontap | B | second'])
        by_title = {v['title']: v for v in self.queue().values()}
        self.assertEqual(by_title['No procedure for: ontap | A | first']['status'], 'closed')
        self.assertEqual(by_title['No procedure for: ontap | B | second']['status'], 'open')

    def test_first_seen_is_kept_and_queue_is_capped(self):
        pb.record_gaps(self.dir, {'total': 1, 'covered': 0, 'gaps': [self.gap('ontap | A | first')]}, now='2026-01-01T00:00:00Z')
        pb.record_gaps(self.dir, {'total': 1, 'covered': 0, 'gaps': [self.gap('ontap | A | first')] + [self.gap(f'ontap | G | {i}', 1) for i in range(60)]}, now='2026-02-01T00:00:00Z')
        g = {x['key']: x for x in pb.status(self.dir)['gaps']}
        self.assertEqual(g['ontap | A | first']['firstSeen'], '2026-01-01T00:00:00Z')
        self.assertLessEqual(len([v for v in self.queue().values() if v['status'] == 'open']), pb.QUEUE_LIMIT)

    def test_acknowledged_item_stays_acknowledged(self):
        pb.record_gaps(self.dir, {'total': 1, 'covered': 0, 'gaps': [self.gap('ontap | A | first')]})
        q = self.queue()
        for v in q.values():
            v['status'] = 'acknowledged'
        with open(os.path.join(self.dir, 'library_update_queue.json'), 'w', encoding='utf-8') as fh:
            json.dump({'items': q}, fh)
        pb.record_gaps(self.dir, {'total': 1, 'covered': 0, 'gaps': [self.gap('ontap | A | first')]})
        self.assertTrue(all(v['status'] == 'acknowledged' for v in self.queue().values()))


class EngineTests(unittest.TestCase):
    """The data engine in app.js, run under node."""

    @classmethod
    def setUpClass(cls):
        import test_playbooks as tp
        cls.tp = tp
        if not tp.NODE:
            raise unittest.SkipTest('node is not installed')

    def run_one(self, e, risk, sys_, extra=None):
        return self.tp.run([{'risk': risk, 'sys': sys_}], data=[e] + (extra or []))[0]

    def test_placeholders_are_filled_from_the_system_and_the_finding(self):
        out = self.run_one(entry(), {'description': 'Example finding', 'riskDetail': 'SVM svm_demo has thing blue.'}, self.tp.sysr())
        text = '\n'.join(out['steps'])
        self.assertIn('show svm_demo', text)
        self.assertIn('modify svm_demo blue', text)
        self.assertIn('cluster-a', out['cause'])

    def test_unknown_values_stay_visible_placeholders(self):
        out = self.run_one(entry(), {'description': 'Example finding'}, self.tp.sysr())
        text = '\n'.join(out['steps'])
        self.assertIn('<svm>', text)
        self.assertIn('<thing>', text)
        self.assertNotIn('{', text)

    def test_family_and_status_are_respected(self):
        self.assertIsNone(self.run_one(entry(family='eseries'), {'description': 'Example finding'}, self.tp.sysr()))
        out = self.run_one(entry(family='eseries', steps=['1. a', '2. b', '3. c']), {'description': 'Example finding'}, self.tp.sysr(platform='2806'))
        self.assertIn('SANtricity', '\n'.join(out['steps']))
        self.assertNotIn('ONTAP 9 command reference', '\n'.join(out['steps']))

    def test_release_gate_uses_below_min(self):
        e = entry(minVersion='9.11.1', belowMin={'cause': 'Too old.', 'steps': ['1. Upgrade', '2. Then enable', '3. Done']})
        old = self.run_one(e, {'description': 'Example finding'}, self.tp.sysr('9.8P1'))
        new = self.run_one(e, {'description': 'Example finding'}, self.tp.sysr('9.15.1P17'))
        self.assertEqual(old['cause'], 'Too old.')
        self.assertIn('cluster-a', new['cause'])

    def test_sources_ticket_and_security_flag_are_carried(self):
        out = self.run_one(entry(security=True, ticket={'risk': 'Low', 'window': 'Any', 'rollback': 'undo'}), {'description': 'Example finding'}, self.tp.sysr())
        self.assertIn('Source: https://docs.netapp.com/us-en/ontap/', out['steps'])

    def test_eseries_remote_login_playbook_ships_and_applies(self):
        risk = {'description': 'Remote Login is Enabled', 'riskDetail': 'Disable Remote Login when not being instructed to use it.'}
        out = self.tp.run([{'risk': risk, 'sys': self.tp.sysr(platform='2806')}])[0]
        self.assertIsNotNone(out)
        text = '\n'.join(out['steps'])
        self.assertIn('Configure remote login (SSH)', text)
        self.assertNotIn('ONTAP 9 command reference', text)

    def test_santricity_advisory_gets_a_grouped_upgrade_procedure(self):
        risk = {'description': 'CVE-2099-0002 Example Vulnerability in NetApp Products',
                'riskDetail': 'E-Series/EF-Series SANtricity OS (controller firmware) has been determined to have a version or configuration exposed to a vulnerability. NTAP-20990101-0002.',
                'recommendation': 'Upgrade to SANtricity 11.90R6 which includes the patch for this vulnerability.', 'advisoryUrl': 'https://security.netapp.com/advisory/ntap-20990101-0002/'}
        sys_ = dict(self.tp.sysr(platform='2806'), santricityVersion='11.80.1R2', ontapVersion='11.80.1R2')
        out = self.tp.run([{'risk': risk, 'sys': sys_}])[0]
        self.assertIsNotNone(out)
        text = ' '.join(out['steps'])
        self.assertIn('SANtricity OS 11.90R6', text)
        self.assertIn('Support > Upgrade center', text)
        self.assertNotIn('undefined', json.dumps(out))
        self.assertNotIn('ONTAP 9 command reference', text)

    def test_storagegrid_advisory_uses_the_recommended_release(self):
        risk = {'description': 'CVE-2099-0003 Example Vulnerability in StorageGRID', 'riskDetail': 'StorageGRID Webscale has been determined to have a version or configuration exposed to a vulnerability. Advisory ID: NTAP-20990101-0003.',
                'recommendation': 'Upgrade to the latest recommended OS version that resolves this vulnerability.'}
        sys_ = dict(self.tp.sysr(platform='SG6060'), recommendedOSVersion='11.9.0.8')
        out = self.tp.run([{'risk': risk, 'sys': sys_}])[0]
        self.assertIsNotNone(out)
        self.assertIn('11.9.0.8', ' '.join(out['steps']))


if __name__ == '__main__':
    unittest.main()
