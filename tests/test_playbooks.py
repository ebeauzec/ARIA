"""Remediation playbooks (app.js _remedPlaybook): the commands are written for the system and the object the finding names, are gated by release,
and never leak template text. Runs the real function from app.js under node; skipped when node is not installed."""
import json, os, shutil, subprocess, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE = shutil.which('node')

HARNESS = r"""
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
const a = src.indexOf('function _rvVer'), b = src.indexOf('function generateDynamicRemediationPlan');
const _platformFamily = s => /e-series|^\d{3,4}$/i.test(String(s.platform)) ? 'eseries' : (/storagegrid/i.test(String(s.platform)) ? 'storagegrid' : 'ontap');
eval(src.slice(a, b) + ';globalThis._pb = _remedPlaybook; globalThis._setData = d => { _DATA_PLAYBOOKS = d; };');
_setData(JSON.parse(process.argv[3]));
const cases = JSON.parse(process.argv[2]);
console.log(JSON.stringify(cases.map(c => { const r = _pb(c.risk, c.sys); return r ? { cause: r.cause, steps: r.steps, options: r.options } : null; })));
"""


def run(cases, data=None):
    if data is None:
        sys.path.insert(0, os.path.join(ROOT, 'tools'))
        import playbooks
        data = playbooks.load(os.path.join(ROOT, 'data'))['playbooks']
    p = subprocess.run([NODE, '-e', HARNESS, os.path.join(ROOT, 'app.js'), json.dumps(cases), json.dumps(data)], capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout)


def sysr(ver='9.15.1P17', platform='AFF-A300'):
    return {'clusterName': 'cluster-a', 'systemName': 'cluster-a-01', 'platform': platform, 'ontapVersion': ver}


@unittest.skipUnless(NODE, 'node is not installed')
class PlaybookTests(unittest.TestCase):
    def test_export_rule_uses_named_svm_and_policy(self):
        r = {'description': 'Export Rule is using a client match of 0.0.0.0/0', 'riskDetail': 'This system has SVM svm_demo that has Export Policy pol_demo and default with an export rule client match using 0.0.0.0/0.'}
        out = run([{'risk': r, 'sys': sysr()}])[0]
        text = '\n'.join(out['steps'])
        self.assertIn('-vserver svm_demo -policyname pol_demo', text)
        self.assertNotIn('<svm>', text)

    def test_unknown_names_stay_placeholders(self):
        out = run([{'risk': {'description': 'Vscan is not enabled.'}, 'sys': sysr()}])[0]
        self.assertIn('<svm>', '\n'.join(out['steps']))

    def test_release_gate(self):
        old = run([{'risk': {'description': 'Multi-admin verification not enabled'}, 'sys': sysr('9.8P1')}])[0]
        new = run([{'risk': {'description': 'Multi-admin verification not enabled'}, 'sys': sysr('9.15.1P17')}])[0]
        self.assertNotIn('approval-group create', '\n'.join(old['steps']))
        self.assertIn('approval-group create', '\n'.join(new['steps']))

    def test_security_advisory_gets_an_upgrade_procedure(self):
        r = {'description': 'CVE-2099-0001 Example Vulnerability in NetApp Products', 'riskDetail': 'ONTAP 9 has been determined to have a version or configuration exposed to a vulnerability. Advisory ID: NTAP-20990101-0001.',
             'recommendation': 'Upgrade to ONTAP 9.16.1P16 which includes the patch for this vulnerability.', 'advisoryUrl': 'https://security.netapp.com/advisory/ntap-20990101-0001/'}
        out = run([{'risk': r, 'sys': sysr('9.15.1P17')}])[0]
        text = ' '.join(out['steps'])
        self.assertIn('cluster image update -version 9.16.1P16', text)
        self.assertIn('different release line', text)
        same = run([{'risk': r, 'sys': sysr('9.16.1P4')}])[0]
        self.assertIn('same release line', ' '.join(same['steps']))
        self.assertNotIn('undefined', json.dumps(out))

    def test_not_for_eseries_or_unknown_findings(self):
        self.assertIsNone(run([{'risk': {'description': 'Auto giveback is not enabled'}, 'sys': sysr(platform='2806')}])[0])  # an ONTAP playbook is not used for E-Series
        self.assertIsNone(run([{'risk': {'description': 'Something nobody wrote a procedure for'}, 'sys': sysr()}])[0])

    def test_no_template_text_leaks(self):
        descs = ['Multi-admin verification not enabled', 'Cluster config backups are not being pushed remotely', 'Cluster Log forwarding not configured.', 'Tamperproof snapshot not enabled',
                 'Native FPolicy is not enabled for all vservers configured for NAS protocols.', 'FIPS 140-2 Compliance is disabled', 'Data-at-Rest Encryption is not enabled',
                 'Enable ONTAP anti-ransomware', 'SMB Signing and Encryption not enabled', 'Vserver has multiple default gateways with the same metric', 'Vscan is not enabled.',
                 'Auto giveback is not enabled', 'NTP servers are not redundant', 'Vserver has a single DNS server configured', 'Intercluster peer remote ip address configuration',
                 'Platform AFF-A300 reached End-of-Availability (EOA) on 2021-05-01, with End-of-Support (EOS) on 2026-05-31', 'Detect expired certificates', 'Cluster Peering encryption not enabled',
                 'Enable cluster switch log collection', 'Enable CIFS AES Kerberos Encryption due to MS deprecating RCN support',
                 'Enable cold data monitoring for potential tiering recommendations', 'Enable tiering to reduce on-prem storage needs', 'Enable FlexCache to reduce the need for data replication',
                 'DQP package downrev', 'Maximum limit reached for inflight operations', 'Do not leave the bootarg.login.allowdiag flag set in the environment.',
                 'Snapshots are not enabled on all data volumes to aid in ransomware defense', 'Volume is hitting the default full threshold of 90%', 'Disk firmware is not on the latest revision',
                 'SP/BMC is not running the latest firmware version', 'Shelf Modules with out-of-date firmware']
        outs = run([{'risk': {'description': d}, 'sys': sysr()} for d in descs])
        for d, o in zip(descs, outs):
            self.assertIsNotNone(o, d)
            blob = json.dumps(o)
            for bad in ('${', 'undefined', 'NaN', '[object'):
                self.assertNotIn(bad, blob, d)
            self.assertGreaterEqual(len(o['steps']), 4, d)


if __name__ == '__main__':
    unittest.main()
