"""
test_harvest_paging.py - the systems list of a harvest must never be saved as complete when a page failed.
=========================================================================
Stdlib-only. A timeout, a dropped connection, a proxy error page or a 429/5xx answer on page 2 or later of the systems query used to end the list
quietly, and the partial fleet (255 systems of 1,697 in one real case) was saved over the good cache. _gql_page retries such a page, and
_keep_unseen_systems carries over the previous harvest's systems that an incomplete harvest lacks.

Run via: python tests/run_tests.py  (or directly: python tests/test_harvest_paging.py)
"""

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent.parent))
import server


def _ok(n):
    return 200, {"data": {"systems": {"cursor": "c", "systems": [{"serialNumber": f"S{i}"} for i in range(n)]}}}


class GqlPageRetry(unittest.TestCase):
    def test_a_good_page_is_returned_at_once(self):
        with mock.patch.object(server, "_gql", return_value=_ok(3)) as g:
            st, resp, failed = server._gql_page("tok", "q", sleep=lambda s: None)
        self.assertFalse(failed)
        self.assertEqual(g.call_count, 1)
        self.assertEqual(len(resp["data"]["systems"]["systems"]), 3)

    def test_a_timeout_is_retried_and_then_succeeds(self):
        timeout = (0, {"errors": [{"message": "Non-JSON response (HTTP 0): timed out"}]})
        waits = []
        with mock.patch.object(server, "_gql", side_effect=[timeout, timeout, _ok(2)]) as g:
            st, resp, failed = server._gql_page("tok", "q", sleep=waits.append)
        self.assertFalse(failed)
        self.assertEqual(g.call_count, 3)
        self.assertEqual(waits, [3.0, 6.0])   # the pause doubles

    def test_a_page_that_keeps_failing_is_reported_failed(self):
        bad = (503, {"errors": [{"message": "Service Unavailable"}]})
        with mock.patch.object(server, "_gql", return_value=bad) as g:
            st, resp, failed = server._gql_page("tok", "q", tries=3, sleep=lambda s: None)
        self.assertTrue(failed)
        self.assertEqual(st, 503)
        self.assertEqual(g.call_count, 3)

    def test_a_non_dict_answer_is_a_failure(self):
        with mock.patch.object(server, "_gql", return_value=(0, None)):
            _, _, failed = server._gql_page("tok", "q", tries=2, sleep=lambda s: None)
        self.assertTrue(failed)

    def test_an_error_about_one_field_is_not_retried_when_systems_came_back(self):
        # Active IQ answers HTTP 200 with data AND an errors array when one system has a null field: the page is good
        resp = {"data": {"systems": {"cursor": "c", "systems": [{"serialNumber": "S1"}]}}, "errors": [{"message": "Float cannot represent non numeric value"}]}
        with mock.patch.object(server, "_gql", return_value=(200, resp)) as g:
            _, _, failed = server._gql_page("tok", "q", sleep=lambda s: None)
        self.assertFalse(failed)
        self.assertEqual(g.call_count, 1)

    def test_a_privilege_error_is_not_retried(self):
        resp = {"errors": [{"message": "Not authorized: unfiltered_system_access required"}]}
        with mock.patch.object(server, "_gql", return_value=(200, resp)) as g:
            _, _, failed = server._gql_page("tok", "q", sleep=lambda s: None)
        self.assertFalse(failed)   # not a transient fault: the caller decides what a privilege block means
        self.assertEqual(g.call_count, 1)


class KeepUnseenSystems(unittest.TestCase):
    def test_systems_the_new_harvest_lacks_are_kept_and_marked(self):
        new = [{"serialNumber": "A"}, {"serialNumber": "B"}]
        old = [{"serialNumber": "A", "systemName": "old a"}, {"serialNumber": "C"}, {"serialNumber": "D"}]
        merged, kept = server._keep_unseen_systems(new, old)
        self.assertEqual(kept, 2)
        self.assertEqual([x["serialNumber"] for x in merged], ["A", "B", "C", "D"])
        self.assertTrue(all(x.get("_keptFromPreviousHarvest") for x in merged[2:]))
        self.assertNotIn("_keptFromPreviousHarvest", merged[0])
        self.assertNotIn("_keptFromPreviousHarvest", old[1])   # the previous harvest's own records are not changed

    def test_a_new_record_wins_over_the_old_one_for_the_same_serial(self):
        merged, kept = server._keep_unseen_systems([{"serialNumber": "A", "systemName": "new"}], [{"serialNumber": "A", "systemName": "old"}])
        self.assertEqual(kept, 0)
        self.assertEqual(merged[0]["systemName"], "new")

    def test_nothing_to_keep_without_a_previous_harvest(self):
        merged, kept = server._keep_unseen_systems([{"serialNumber": "A"}], None)
        self.assertEqual((len(merged), kept), (1, 0))

    def test_records_without_a_serial_are_not_carried_over(self):
        merged, kept = server._keep_unseen_systems([], [{"systemName": "no serial"}, {"serialNumber": ""}])
        self.assertEqual((merged, kept), ([], 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
