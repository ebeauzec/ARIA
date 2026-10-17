"""
test_fleet_trend.py - the daily scope trend that backs the 30/60/90 day Better / Unchanged / Worse view.
=========================================================================
Stdlib-only. _get_fleet_trend adds up the dated snapshots of the systems in scope: risks by severity, open severity 1 and 2 cases, how many systems have
ransomware protection on or off, how many have a lapsed contract, the average efficiency ratio, and how many records were captured.

Run via: python tests/run_tests.py  (or directly: python tests/test_fleet_trend.py)
"""

import json
import sqlite3
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import server


def _db(rows):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE system_snapshots (serial_number TEXT, snapshot_date TEXT, customer_name TEXT, system_name TEXT, snapshot_json TEXT, captured_at TEXT, PRIMARY KEY (serial_number, snapshot_date))")
    for serial, day, cust, snap in rows:
        db.execute("INSERT INTO system_snapshots VALUES (?, ?, ?, ?, ?, ?)", (serial, day, cust, serial, json.dumps(snap), day))
    return db


def _d(n):
    return (date.today() - timedelta(days=n)).isoformat()


class FleetTrend(unittest.TestCase):
    def test_daily_totals_for_a_customer(self):
        db = _db([
            ("A", _d(30), "Acme", {"riskCounts": {"critical": 3, "high": 4, "medium": 5, "low": 1}, "openCriticalCases": 1, "isARPEnabled": False, "contractActive": True, "contractEndDate": "2099-01-01", "efficiencyRatio": 3.0}),
            ("B", _d(30), "Acme", {"riskCounts": {"critical": 1, "high": 0, "medium": 2, "low": 0}, "openCriticalCases": 0, "isARPEnabled": True, "contractActive": False, "contractEndDate": "2020-01-01", "efficiencyRatio": 5.0}),
            ("A", _d(0), "Acme", {"riskCounts": {"critical": 1, "high": 2, "medium": 3, "low": 1}, "openCriticalCases": 0, "isARPEnabled": True, "contractActive": True, "contractEndDate": "2099-01-01", "efficiencyRatio": 4.0}),
            ("Z", _d(0), "Other", {"riskCounts": {"critical": 9}}),
        ])
        t = server._get_fleet_trend(db, days=90, customer_name="Acme")
        self.assertEqual([x["date"] for x in t], [_d(30), _d(0)])
        then, now = t
        self.assertEqual((then["critical"], then["high"], then["medium"], then["low"]), (4, 4, 7, 1))
        self.assertEqual((now["critical"], now["high"], now["medium"], now["low"]), (1, 2, 3, 1))
        self.assertEqual((then["arpEnabled"], then["arpDisabled"], now["arpEnabled"], now["arpDisabled"]), (1, 1, 1, 0))
        self.assertEqual((then["contractsLapsed"], now["contractsLapsed"]), (1, 0))
        self.assertEqual((then["avgEfficiency"], now["avgEfficiency"]), (4.0, 4.0))
        self.assertEqual((then["systemCount"], now["systemCount"]), (2, 1))
        self.assertEqual(then["openCriticalCases"], 1)

    def test_a_contract_that_ended_before_the_snapshot_is_lapsed_even_when_marked_active(self):
        db = _db([("A", _d(0), "Acme", {"contractActive": True, "contractEndDate": "2020-05-01"})])
        self.assertEqual(server._get_fleet_trend(db, days=90, customer_name="Acme")[0]["contractsLapsed"], 1)

    def test_missing_measures_do_not_break_the_totals(self):
        db = _db([("A", _d(0), "Acme", {}), ("B", _d(0), "Acme", {"efficiencyRatio": "n/a", "isARPEnabled": None})])
        d = server._get_fleet_trend(db, days=90, customer_name="Acme")[0]
        self.assertEqual((d["critical"], d["arpEnabled"], d["arpDisabled"], d["contractsLapsed"], d["systemCount"]), (0, 0, 0, 0, 2))
        self.assertIsNone(d["avgEfficiency"])

    def test_a_serial_list_scope(self):
        db = _db([("A", _d(0), "Acme", {"riskCounts": {"critical": 2}}), ("B", _d(0), "Acme", {"riskCounts": {"critical": 5}})])
        self.assertEqual(server._get_fleet_trend(db, days=90, serials=["B"])[0]["critical"], 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
