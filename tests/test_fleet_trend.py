"""
test_fleet_trend.py - the daily scope trend behind the risk trend chart and the 30/60/90 day Better / Unchanged / Worse view.
=========================================================================
Stdlib-only. _get_fleet_trend adds up the dated snapshots of the systems in scope: risks by severity, open severity 1 and 2 cases, how many systems have
ransomware protection on or off, how many have a lapsed contract, the average efficiency ratio, and how many records were counted.

The days must be comparable. Only the systems of the latest snapshot are counted on every day, and a day is `valid: false` when too few of them were captured
or when a harvest stored no risks for most of them (the chart used to fall to zero on such days, and jump on the day capture widened).

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


def _rec(crit=0, high=0, med=0, low=0, **kw):
    r = {"riskCounts": {"critical": crit, "high": high, "medium": med, "low": low}}
    r.update(kw)
    return r


class FleetTrend(unittest.TestCase):
    def test_daily_totals_for_the_systems_of_the_latest_snapshot(self):
        db = _db([
            ("A", _d(30), "Acme", _rec(3, 4, 5, 1, openCriticalCases=1, isARPEnabled=False, contractActive=True, contractEndDate="2099-01-01", efficiencyRatio=3.0)),
            ("B", _d(30), "Acme", _rec(1, 0, 2, 0, isARPEnabled=True, contractActive=False, contractEndDate="2020-01-01", efficiencyRatio=5.0)),
            ("A", _d(0), "Acme", _rec(1, 2, 3, 1, isARPEnabled=True, contractActive=True, contractEndDate="2099-01-01", efficiencyRatio=4.0)),
            ("B", _d(0), "Acme", _rec(0, 1, 1, 0, isARPEnabled=True, contractActive=False, contractEndDate="2020-01-01", efficiencyRatio=5.0)),
            ("Z", _d(0), "Other", _rec(9)),
        ])
        t = server._get_fleet_trend(db, days=90, customer_name="Acme")
        self.assertEqual([x["date"] for x in t], [_d(30), _d(0)])
        then, now = t
        self.assertEqual((then["critical"], then["high"], then["medium"], then["low"]), (4, 4, 7, 1))
        self.assertEqual((now["critical"], now["high"], now["medium"], now["low"]), (1, 3, 4, 1))
        self.assertEqual((then["arpEnabled"], then["arpDisabled"], now["arpEnabled"], now["arpDisabled"]), (1, 1, 2, 0))
        self.assertEqual((then["contractsLapsed"], now["contractsLapsed"]), (1, 1))
        self.assertEqual((then["avgEfficiency"], now["avgEfficiency"]), (4.0, 4.5))
        self.assertEqual((then["systemCount"], now["systemCount"]), (2, 2))
        self.assertEqual(then["openCriticalCases"], 1)
        self.assertTrue(then["valid"] and now["valid"])

    def test_a_system_not_in_the_latest_snapshot_is_not_counted_on_earlier_days(self):
        db = _db([("A", _d(30), "Acme", _rec(2)), ("GONE", _d(30), "Acme", _rec(50)), ("A", _d(0), "Acme", _rec(2))])
        t = server._get_fleet_trend(db, days=90, customer_name="Acme")
        self.assertEqual([x["critical"] for x in t], [2, 2])   # the line is flat: nothing changed on the systems that are still there

    def test_a_day_that_captured_too_few_of_the_systems_is_not_valid(self):
        rows = [(f"S{i}", _d(0), "Acme", _rec(1)) for i in range(10)] + [(f"S{i}", _d(5), "Acme", _rec(1)) for i in range(3)] + [(f"S{i}", _d(10), "Acme", _rec(1)) for i in range(9)]
        t = {x["date"]: x for x in server._get_fleet_trend(db=_db(rows), days=90, customer_name="Acme")}
        self.assertFalse(t[_d(5)]["valid"])
        self.assertAlmostEqual(t[_d(5)]["coverage"], 0.3)
        self.assertTrue(t[_d(10)]["valid"] and t[_d(0)]["valid"])

    def test_a_harvest_that_stored_no_risks_is_not_a_day_with_no_risks(self):
        rows = [(f"S{i}", _d(0), "Acme", _rec(2, 3)) for i in range(10)] + [(f"S{i}", _d(7), "Acme", _rec()) for i in range(10)] + [(f"S{i}", _d(14), "Acme", _rec(2, 3)) for i in range(10)]
        t = {x["date"]: x for x in server._get_fleet_trend(db=_db(rows), days=90, customer_name="Acme")}
        self.assertFalse(t[_d(7)]["valid"])   # every system suddenly has no risks: the data is missing, not the risks
        self.assertEqual(t[_d(7)]["critical"], 0)
        self.assertTrue(t[_d(14)]["valid"])

    def test_systems_that_really_have_no_risks_do_not_make_a_day_invalid(self):
        rows = [(f"S{i}", d, "Acme", _rec() if i < 4 else _rec(1)) for d in (_d(0), _d(7)) for i in range(10)]
        t = server._get_fleet_trend(db=_db(rows), days=90, customer_name="Acme")
        self.assertTrue(all(x["valid"] for x in t))

    def test_a_contract_that_ended_before_the_snapshot_is_lapsed_even_when_marked_active(self):
        db = _db([("A", _d(0), "Acme", {"contractActive": True, "contractEndDate": "2020-05-01"})])
        self.assertEqual(server._get_fleet_trend(db, days=90, customer_name="Acme")[0]["contractsLapsed"], 1)

    def test_missing_measures_do_not_break_the_totals(self):
        db = _db([("A", _d(0), "Acme", {}), ("B", _d(0), "Acme", {"efficiencyRatio": "n/a", "isARPEnabled": None})])
        d = server._get_fleet_trend(db, days=90, customer_name="Acme")[0]
        self.assertEqual((d["critical"], d["arpEnabled"], d["arpDisabled"], d["contractsLapsed"], d["systemCount"]), (0, 0, 0, 0, 2))
        self.assertIsNone(d["avgEfficiency"])

    def test_a_serial_list_scope(self):
        db = _db([("A", _d(0), "Acme", _rec(2)), ("B", _d(0), "Acme", _rec(5))])
        self.assertEqual(server._get_fleet_trend(db, days=90, serials=["B"])[0]["critical"], 5)

    def test_no_snapshots(self):
        self.assertEqual(server._get_fleet_trend(_db([]), days=90), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
