import json
import os
import unittest

from support import PlanTestCase


class ValidateTest(PlanTestCase):
    def setUp(self):
        super().setUp()
        self.init()

    def corrupt(self, slices):
        """Simulates a damaged state.json that bypassed the CLI's own refusals."""
        state = self.state()
        state["slices"] = slices
        with open(os.path.join(self.plan_dir, "state.json"), "w") as handle:
            json.dump(state, handle)

    @staticmethod
    def slice_(*deps, status="ready"):
        return {"file": "f", "outcome": "o", "status": status, "reason": None,
                "blocked_by": [{"id": d, "supplies": ""} for d in deps],
                "fixed_point": None, "snapshot": None}

    def test_state_written_before_later_fields_reads_them_as_null(self):
        state = self.state()
        del state["planning_revision"]
        state["slices"] = {"01": {"file": "f", "outcome": "o", "status": "ready", "reason": None, "blocked_by": []}}
        with open(os.path.join(self.plan_dir, "state.json"), "w") as handle:
            json.dump(state, handle)
        self.plan("validate")
        view = json.loads(self.plan("status", "--json").out)
        self.assertIsNone(view["slices"][0]["fixed_point"])
        self.plan("slice", "add", "02", "--file", "g", "--outcome", "o", "--blocked-by", "01")
        saved = self.state()
        self.assertIsNone(saved["planning_revision"])
        self.assertEqual(
            (saved["slices"]["01"]["fixed_point"], saved["slices"]["01"]["snapshot"], saved["slices"]["01"]["landed"]),
            (None, None, None),
        )

    def test_valid_graph_exits_zero(self):
        self.plan("slice", "add", "01", "--file", "a", "--outcome", "o")
        self.plan("slice", "add", "02", "--file", "b", "--outcome", "o", "--blocked-by", "01")
        self.plan("validate")

    def test_names_each_missing_dependency(self):
        self.corrupt({"01": self.slice_("07"), "02": self.slice_("08", "01")})
        result = self.plan_fails("validate")
        self.assertIn("slice 01 is blocked by 07, which does not exist", result.err)
        self.assertIn("slice 02 is blocked by 08, which does not exist", result.err)

    def test_names_each_cycle(self):
        self.corrupt({
            "01": self.slice_("02"), "02": self.slice_("01"),
            "03": self.slice_("05"), "04": self.slice_("03"), "05": self.slice_("04"),
            "06": self.slice_("06"), "07": self.slice_("01"),
        })
        result = self.plan_fails("validate")
        self.assertIn("dependency cycle: 01 -> 02 -> 01", result.err)
        self.assertIn("dependency cycle: 03 -> 05 -> 04 -> 03", result.err)
        self.assertIn("dependency cycle: 06 -> 06", result.err)
        self.assertNotIn("-> 07", result.err)  # the temp path in the message may contain "07"
        self.assertNotIn("cycle: 07", result.err)

    def test_names_each_cycle_through_a_shared_slice(self):
        self.corrupt({"A": self.slice_("B"), "B": self.slice_("A", "C"), "C": self.slice_("B")})
        result = self.plan_fails("validate")
        self.assertIn("dependency cycle: A -> B -> A", result.err)
        self.assertIn("dependency cycle: B -> C -> B", result.err)
        self.assertIn("2 problem(s)", result.err)

    def test_long_dependency_chain_is_checked_without_recursion_limits(self):
        count = 3000
        slices = {f"s{n}": self.slice_(f"s{n + 1}") for n in range(count)}
        slices[f"s{count}"] = self.slice_("s0")
        self.corrupt(slices)
        result = self.plan_fails("validate")
        self.assertIn("dependency cycle: s0 -> s1 -> s2", result.err)
        self.assertIn("1 problem(s)", result.err)

    def test_every_elementary_cycle_is_named(self):
        ids = ["01", "02", "03", "04"]
        self.corrupt({i: self.slice_(*[j for j in ids if j != i]) for i in ids})
        result = self.plan_fails("validate")
        self.assertIn("20 problem(s)", result.err)
        self.assertIn("dependency cycle: 01 -> 04 -> 03 -> 02 -> 01", result.err)

    def test_cycle_report_is_capped(self):
        ids = [f"0{n}" for n in range(1, 7)]
        self.corrupt({i: self.slice_(*[j for j in ids if j != i]) for i in ids})
        result = self.plan_fails("validate")
        self.assertIn("more than 50 dependency cycles; only the first are listed", result.err)
        self.assertIn("51 problem(s)", result.err)

    def test_cycle_search_stays_fast_beside_many_acyclic_paths(self):
        # 01 <-> 02, with 40 dependency diamonds under 02: 2**40 paths, one cycle.
        slices = {"01": self.slice_("02"), "02": self.slice_("01", "a0")}
        for n in range(40):
            slices[f"a{n}"] = self.slice_(f"b{n}", f"c{n}")
            below = [f"a{n + 1}"] if n < 39 else []
            slices[f"b{n}"], slices[f"c{n}"] = self.slice_(*below), self.slice_(*below)
        self.corrupt(slices)
        result = self.run_executable("validate", "--plan", self.plan_dir, timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("1 problem(s)", result.stderr)
        self.assertIn("dependency cycle: 01 -> 02 -> 01", result.stderr)

    def test_damaged_state_shape_is_reported_without_traceback(self):
        broken = self.slice_()
        del broken["blocked_by"]
        self.corrupt({"01": broken})
        for command in (("validate",), ("status",), ("next",)):
            result = self.plan_fails(*command)
            self.assertIn("plan: error:", result.err)
            self.assertIn("blocked_by", result.err)
            self.assertNotIn("Traceback", result.err)

    def test_state_without_slices_is_reported(self):
        with open(os.path.join(self.plan_dir, "state.json"), "w") as handle:
            json.dump({"schema": 1}, handle)
        result = self.plan_fails("status")
        self.assertIn("plan: error:", result.err)

    def test_ids_that_sort_equal_are_reported(self):
        self.corrupt({"1": self.slice_(), "01": self.slice_()})
        result = self.plan_fails("validate")
        self.assertIn("slice IDs 01 and 1 collide", result.err)

    def test_reports_unknown_status_and_blocked_without_reason(self):
        self.corrupt({"01": self.slice_(status="done"), "02": self.slice_(status="blocked")})
        result = self.plan_fails("validate")
        self.assertIn("unknown status 'done'", result.err)
        self.assertIn("slice 02 is blocked without a reason", result.err)


class StatusAndNextTest(PlanTestCase):
    def setUp(self):
        super().setUp()
        self.init()
        self.tip = self.state()["run"]["target_tip"]
        self.plan("slice", "add", "01", "--file", "01-a.md", "--outcome", "Core")
        self.plan("slice", "add", "02", "--file", "02-b.md", "--outcome", "Import", "--blocked-by", "01:state model")
        self.plan("slice", "add", "03", "--file", "03-c.md", "--outcome", "Other")
        self.plan("slice", "add", "10", "--file", "10-d.md", "--outcome", "Last")
        self.plan("slice", "add", "04", "--file", "04-e.md", "--outcome", "Wait",
                  "--status", "blocked", "--reason", "needs a decision")
        self.plan("slice", "edit", "01", "--status", "complete", "--force", "--reason", "test setup")
        self.plan("slice", "edit", "03", "--status", "in-progress", "--force", "--reason", "test setup")

    def test_next_lists_ready_slices_with_complete_dependencies_in_id_order(self):
        result = self.plan("next")
        self.assertEqual([line.split("\t")[0] for line in result.out.splitlines()], ["02", "10"])

    def test_next_limit_caps_the_list(self):
        result = self.plan("next", "--limit", "1")
        self.assertEqual([line.split("\t")[0] for line in result.out.splitlines()], ["02"])

    def test_next_rejects_non_positive_limit(self):
        self.plan_fails("next", "--limit", "0")

    def test_next_skips_slice_with_unfinished_dependency(self):
        self.plan("slice", "add", "11", "--file", "f", "--outcome", "o", "--blocked-by", "03")
        self.assertNotIn("11", [line.split("\t")[0] for line in self.plan("next").out.splitlines()])

    def test_status_text_shows_table_eligible_progress_blocked_and_run(self):
        out = self.plan("status").out
        self.assertIn("| 02 | 02-b.md | Import | 01: state model | ready |", out)
        self.assertIn("Eligible: 02, 10", out)
        self.assertIn("03  " + os.path.join(os.path.abspath(self.plan_dir), "checkpoints", "03.md")
                      + "  (fixed point not recorded)", out)
        self.assertIn("04  needs a decision", out)
        self.assertIn("Target: main at " + self.tip, out)
        self.assertIn("Repository: " + self.repo, out)

    def test_status_json_carries_the_same_view(self):
        view = json.loads(self.plan("status", "--json").out)
        self.assertEqual(view["eligible"], ["02", "10"])
        self.assertEqual(
            view["in_progress"],
            [{"id": "03", "checkpoint": os.path.join(os.path.abspath(self.plan_dir), "checkpoints", "03.md"),
              "fixed_point": None}],
        )
        self.assertEqual(view["blocked"], [{"id": "04", "reason": "needs a decision", "fixed_point": None,
                                            "checkpoint": None}])
        self.assertEqual(view["run"], {"target": "main", "target_tip": self.tip})
        self.assertEqual(view["repo"], self.repo)
        self.assertEqual([s["id"] for s in view["slices"]], ["01", "02", "03", "04", "10"])
        self.assertEqual(view["slices"][1]["blocked_by"], [{"id": "01", "supplies": "state model"}])

    def test_reports_without_state_fail_on_stderr(self):
        os.remove(os.path.join(self.plan_dir, "state.json"))
        result = self.plan_fails("status")
        self.assertIn("state.json", result.err)
        self.assertEqual(result.out, "")


if __name__ == "__main__":
    unittest.main()
