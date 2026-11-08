import json
import os
import re
import subprocess
import sys
import textwrap
import unittest
from unittest import mock

from support import PLAN_PATH, PlanTestCase, plan_cli

ENTRY = r"## \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ — "

# Records count pending-review decisions, printing each allocated ID.
DECIDE_LOOP = textwrap.dedent("""
    import contextlib, importlib.machinery, importlib.util, io, sys
    loader = importlib.machinery.SourceFileLoader("plan_cli", {path!r})
    spec = importlib.util.spec_from_loader("plan_cli", loader)
    plan = importlib.util.module_from_spec(spec)
    loader.exec_module(plan)
    import os, time
    prefix, count, plan_dir, go = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
    print("ready", flush=True)
    while not os.path.exists(go):
        time.sleep(0.005)
    for n in range(count):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = plan.main(["decide", "--status", "pending-review", "--undo-cost", "low", "--slices", "01",
                              "--body", f"{{prefix}}{{n}}", "--plan", plan_dir])
        if code:
            sys.exit(code)
        print(out.getvalue().strip(), flush=True)
""").format(path=PLAN_PATH)


class DecisionTestCase(PlanTestCase):
    def setUp(self):
        super().setUp()
        self.init()
        self.plan("slice", "add", "01", "--file", "01-a.md", "--outcome", "first")
        self.plan("slice", "add", "02", "--file", "02-b.md", "--outcome", "second")
        self.plan("slice", "add", "03", "--file", "03-c.md", "--outcome", "third")
        self.plan("slice", "add", "05", "--file", "05-e.md", "--outcome", "fifth")

    def decide(self, *argv, status="pending-review", cost="low", slices="01", body="because"):
        return self.plan("decide", "--status", status, "--undo-cost", cost, "--slices", slices,
                         "--body", body, *argv).out.strip()

    def decisions(self):
        return self.state()["decisions"]


class DecideTest(DecisionTestCase):
    def test_decide_prints_sequential_ids_and_records_the_index(self):
        self.assertEqual(self.decide(cost="high", slices="03,05"), "R1")
        self.assertEqual(self.decide(), "R2")
        d = self.decisions()["R1"]
        self.assertEqual((d["status"], d["undo_cost"], d["slices"]), ("pending-review", "high", ["03", "05"]))
        self.assertRegex(d["recorded"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        self.assertIsNone(d["updated"])
        self.assertEqual(sorted(self.decisions()), ["R1", "R2"])

    def test_decide_appends_the_body_under_an_r_heading(self):
        self.decide(cost="high", slices="03,05", body="Use a lock file.\n\n# Alternatives\n\nNone.")
        log = self.read("log.md")
        self.assertRegex(log, ENTRY + r"R1 pending-review\n\nStatus: pending-review\nUndo cost: high\n"
                              r"Slices: 03, 05 \(unfinished: 03, 05\)\n\nUse a lock file\.\n\n### Alternatives")

    def test_decide_reads_the_body_from_a_file(self):
        path = os.path.join(self.tmp, "body.md")
        with open(path, "w") as handle:
            handle.write("From a file.\n")
        self.decide(body="@" + path)
        self.assertIn("From a file.", self.read("log.md"))

    def test_decide_accepts_repeated_and_space_separated_slices(self):
        self.plan("decide", "--status", "pending-review", "--undo-cost", "low", "--slices", "01, 02",
                  "--slices", "05", "--body", "b")
        self.assertEqual(self.decisions()["R1"]["slices"], ["01", "02", "05"])

    def test_decide_accepts_none_for_no_dependent_slices(self):
        self.decide(slices="none")
        self.assertEqual(self.decisions()["R1"]["slices"], [])
        self.assertIn("Slices: none", self.read("log.md"))

    def test_decide_refuses_unknown_slices_even_with_force(self):
        result = self.plan_fails("decide", "--status", "pending-review", "--undo-cost", "low", "--slices", "01,99",
                                 "--body", "b")
        self.assertIn("decision R1 names slice 99, which does not exist", result.err)
        self.plan_fails("decide", "--status", "pending-review", "--undo-cost", "low", "--slices", "99",
                        "--body", "b", "--force", "--reason", "try")
        self.assertEqual(self.decisions(), {})
        self.assertNotIn("R1", self.read("log.md"))

    def test_decide_refuses_a_slice_listed_twice(self):
        result = self.plan_fails("decide", "--status", "pending-review", "--undo-cost", "low", "--slices", "01,01",
                                 "--body", "b")
        self.assertIn("slice 01 is listed twice", result.err)

    def test_decide_refuses_undo_costs_outside_the_four_levels(self):
        result = self.plan_fails("decide", "--status", "pending-review", "--undo-cost", "huge", "--slices", "01",
                                 "--body", "b")
        self.assertIn("huge", result.err)
        self.assertEqual(self.decisions(), {})

    def test_decide_refuses_unknown_status(self):
        result = self.plan_fails("decide", "--status", "rejected", "--undo-cost", "low", "--slices", "01",
                                 "--body", "b")
        self.assertIn("invalid choice: 'rejected'", result.err)
        self.assertEqual(self.decisions(), {})

    def test_new_decision_requires_undo_cost_slices_and_body(self):
        for missing in ("--undo-cost", "--slices", "--body"):
            argv = {"--undo-cost": "low", "--slices": "01", "--body": "b"}
            del argv[missing]
            flat = [x for pair in argv.items() for x in pair]
            result = self.plan_fails("decide", "--status", "pending-review", *flat)
            self.assertIn(missing, result.err)
        self.assertEqual(self.decisions(), {})

    def test_empty_body_is_refused_unless_forced(self):
        result = self.plan_fails("decide", "--status", "pending-review", "--undo-cost", "low", "--slices", "01",
                                 "--body", "  \n")
        self.assertIn("body is empty", result.err)
        self.plan("decide", "--status", "pending-review", "--undo-cost", "low", "--slices", "01", "--body", "",
                  "--force", "--reason", "prose is in the slice file")
        self.assertIn("Reason: prose is in the slice file", self.read("log.md"))
        self.assertIn("R1", self.decisions())

    def test_decide_can_record_an_approved_decision(self):
        self.assertEqual(self.decide(status="approved"), "R1")
        self.assertEqual(self.decisions()["R1"]["status"], "approved")
        self.assertRegex(self.read("log.md"), ENTRY + "R1 approved\n")

    def test_numbering_continues_after_r_entries_already_in_log_md(self):
        self.write("log.md", "# Log\n\n- R1 (undo cost: low): x\n  - R15 (undo cost: low): y; see also R7.\n"
                             "Not a decision: R2D2, FOR3, R0, and a mention of R99.\n")
        self.assertEqual(self.decide(), "R16")
        self.assertEqual(self.decide(), "R17")

    def test_numbering_reads_each_decision_line_shape(self):
        for line, expected in (("### R4 Lock files", "R5"), ("## 2026-10-09T00:00:00Z — R6 approved", "R7"),
                               ("R8: kept", "R9"), ("R20 (undo cost: low)", "R21"),
                               ("R40 regression fixed.\n- R3", "R4"), ("1. **R10** (undo cost: low)", "R11"),
                               ("- __R12__ x", "R13"), ("    - R14 (undo cost: low): nested", "R15"),
                               ("```\nR50 inside a fence\n```\n- R2", "R3")):
            with self.subTest(line=line):
                self.write("log.md", line + "\n")
                self.assertEqual(plan_cli.next_decision_id(self.plan_dir, {}), expected)

    def test_later_decisions_follow_the_index_whatever_the_log_mentions(self):
        self.decide(body="See the R40 alternative.\n- R90 as a list item.")
        self.plan("start", "01", "--force", "--reason", "per R70")
        self.assertEqual(self.decide(), "R2")
        self.assertEqual(self.decide(), "R3")

    def test_reason_without_force_is_refused(self):
        result = self.plan_fails("decide", "--status", "pending-review", "--undo-cost", "low", "--slices", "01",
                                 "--body", "b", "--reason", "why")
        self.assertIn("--reason applies only with --force", result.err)

    def test_failed_state_write_leaves_no_decision_entry(self):
        with mock.patch.object(plan_cli, "save_state", side_effect=OSError("disk full")):
            result = self.plan_fails("decide", "--status", "pending-review", "--undo-cost", "low",
                                     "--slices", "01", "--body", "b")
        self.assertIn("disk full", result.err)
        self.assertNotIn("R1", self.read("log.md"))
        self.assertEqual(self.decide(), "R1")


class UpdateDecisionTest(DecisionTestCase):
    def setUp(self):
        super().setUp()
        self.decide(cost="medium", slices="03")
        self.decide(cost="high", slices="03,05")

    def test_pending_decision_moves_to_approved_and_logs_the_update(self):
        self.assertEqual(self.plan("decide", "R2", "--status", "approved", "--body", "User agreed.").out.strip(), "R2")
        d = self.decisions()["R2"]
        self.assertEqual((d["status"], d["undo_cost"], d["slices"]), ("approved", "high", ["03", "05"]))
        self.assertRegex(d["updated"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        self.assertRegex(self.read("log.md"), ENTRY + r"R2 approved\n\nStatus: pending-review -> approved\n\n"
                                                      r"User agreed\.\n")
        self.assertEqual(self.decisions()["R1"]["status"], "pending-review")

    def test_update_without_body_logs_only_the_change(self):
        self.plan("decide", "R1", "--status", "approved")
        self.assertRegex(self.read("log.md"), ENTRY + r"R1 approved\n\nStatus: pending-review -> approved\n$")

    def test_update_can_revise_undo_cost_and_slices(self):
        self.plan("decide", "R1", "--status", "approved", "--undo-cost", "low", "--slices", "02")
        d = self.decisions()["R1"]
        self.assertEqual((d["undo_cost"], d["slices"]), ("low", ["02"]))
        log = self.read("log.md")
        self.assertIn("Undo cost: medium -> low", log)
        self.assertIn("Slices: 03 -> 02", log)

    def test_approving_an_approved_decision_is_refused(self):
        self.plan("decide", "R2", "--status", "approved")
        before = self.read("log.md")
        result = self.plan_fails("decide", "R2", "--status", "approved")
        self.assertIn("decision R2 is already approved", result.err)
        self.assertIn("--force --reason", result.err)
        self.assertEqual(self.read("log.md"), before)

    def test_approved_decision_does_not_return_to_pending_without_force(self):
        self.plan("decide", "R2", "--status", "approved")
        result = self.plan_fails("decide", "R2", "--status", "pending-review")
        self.assertIn("decision R2 is approved; it cannot return to pending-review", result.err)
        self.plan("decide", "R2", "--status", "pending-review", "--force", "--reason", "user reopened it")
        self.assertEqual(self.decisions()["R2"]["status"], "pending-review")
        self.assertIn("Reason: user reopened it", self.read("log.md"))

    def test_pending_decision_restated_without_amendment_is_refused(self):
        before = self.read("log.md")
        result = self.plan_fails("decide", "R1", "--status", "pending-review", "--undo-cost", "medium",
                                 "--slices", "03")
        self.assertIn("decision R1 is already pending-review; pass --undo-cost, --slices, or --body", result.err)
        self.assertEqual(self.read("log.md"), before)

    def test_reordered_slices_amend_nothing(self):
        self.plan("decide", "R2", "--status", "approved", "--slices", "05,03")
        self.assertEqual(self.decisions()["R2"]["slices"], ["03", "05"])
        self.assertRegex(self.read("log.md"), ENTRY + r"R2 approved\n\nStatus: pending-review -> approved\n$")
        result = self.plan_fails("decide", "R1", "--status", "pending-review", "--slices", "03")
        self.assertIn("already pending-review", result.err)

    def test_forced_restatement_is_not_logged_as_amended(self):
        self.plan("decide", "R2", "--status", "approved")
        self.plan("decide", "R2", "--status", "approved", "--force", "--reason", "re-record")
        self.assertRegex(self.read("log.md"), ENTRY + r"R2 approved\n\nStatus: approved\n$")

    def test_pending_decision_is_amended_without_force(self):
        self.plan("decide", "R1", "--status", "pending-review", "--undo-cost", "high", "--body", "Wider than thought.")
        d = self.decisions()["R1"]
        self.assertEqual((d["status"], d["undo_cost"]), ("pending-review", "high"))
        log = self.read("log.md")
        self.assertRegex(log, ENTRY + r"R1 pending-review\n\nStatus: pending-review \(amended\)\n"
                              r"Undo cost: medium -> high\n\nWider than thought\.\n$")
        self.assertNotIn("forced", log)

    def test_unknown_decision_is_refused_even_with_force(self):
        result = self.plan_fails("decide", "R9", "--status", "approved")
        self.assertIn("decision R9 does not exist", result.err)
        self.plan_fails("decide", "R9", "--status", "approved", "--force", "--reason", "x")
        self.assertNotIn("R9", self.decisions())

    def test_malformed_decision_id_is_refused(self):
        for bad in ("2", "r2", "R02", "R0", "Rx", "R1\n"):
            result = self.plan_fails("decide", bad, "--status", "approved")
            self.assertIn("decision ID", result.err)

    def test_update_refuses_unknown_slices(self):
        result = self.plan_fails("decide", "R1", "--status", "approved", "--slices", "42")
        self.assertIn("decision R1 names slice 42, which does not exist", result.err)
        self.assertEqual(self.decisions()["R1"]["status"], "pending-review")


class ListDecisionsTest(DecisionTestCase):
    def setUp(self):
        super().setUp()
        self.decide(cost="low", slices="01")           # R1
        self.decide(cost="irreversible", slices="02")  # R2
        self.decide(cost="high", slices="03,05")       # R3
        self.decide(cost="high", slices="01,03")       # R4
        self.decide(cost="medium", slices="none")      # R5
        self.decide(cost="irreversible", slices="05")  # R6
        self.plan("decide", "R6", "--status", "approved")
        self.plan("slice", "edit", "03", "--status", "complete", "--force", "--reason", "test setup")

    def ids(self, *argv):
        return [line.split("\t")[0] for line in self.plan("decisions", *argv).out.splitlines()]

    def test_pending_lists_costliest_first_then_by_id(self):
        self.assertEqual(self.ids("--pending"), ["R2", "R3", "R4", "R5", "R1"])

    def test_numeric_id_order_breaks_ties(self):
        for _ in range(5):
            self.decide(cost="low", slices="01")
        self.assertEqual(self.ids("--pending")[-6:], ["R1", "R7", "R8", "R9", "R10", "R11"])

    def test_without_pending_lists_every_decision_in_id_order(self):
        self.assertEqual(self.ids(), ["R1", "R2", "R3", "R4", "R5", "R6"])

    def test_rows_show_dependent_and_unfinished_slices(self):
        rows = {line.split("\t")[0]: line for line in self.plan("decisions").out.splitlines()}
        self.assertEqual(rows["R3"], "R3\tpending-review\thigh\tslices: 03, 05\tunfinished: 05")
        self.assertEqual(rows["R5"], "R5\tpending-review\tmedium\tslices: none\tunfinished: none")
        self.assertEqual(rows["R6"], "R6\tapproved\tirreversible\tslices: 05\tunfinished: 05")

    def test_json_carries_the_same_rows(self):
        rows = json.loads(self.plan("decisions", "--pending", "--json").out)
        self.assertEqual([r["id"] for r in rows], ["R2", "R3", "R4", "R5", "R1"])
        r3 = rows[1]
        self.assertEqual((r3["status"], r3["undo_cost"], r3["slices"], r3["unfinished"]),
                         ("pending-review", "high", ["03", "05"], ["05"]))
        self.assertIn("recorded", r3)
        self.assertIn("updated", r3)

    def test_empty_index_prints_nothing(self):
        plan_dir = os.path.join(self.tmp, "p2")
        self.assertEqual(self.run_plan("init", plan_dir, "--repo", self.repo, "--target", "main").code, 0)
        result = self.run_plan("decisions", "--plan", plan_dir)
        self.assertEqual((result.code, result.out), (0, ""))
        self.assertEqual(json.loads(self.run_plan("decisions", "--json", "--plan", plan_dir).out), [])


class ConcurrentDecideTest(DecisionTestCase):
    def test_concurrent_decide_calls_allocate_distinct_sequential_ids(self):
        count = 15
        go = os.path.join(self.tmp, "go")
        writers = [
            subprocess.Popen([sys.executable, "-c", DECIDE_LOOP, prefix, str(count), self.plan_dir, go],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for prefix in ("a", "b")
        ]
        for writer in writers:
            self.assertEqual(writer.stdout.readline().strip(), "ready")
        open(go, "w").close()
        printed = []
        for writer in writers:
            out, err = writer.communicate(timeout=120)
            self.assertEqual(writer.returncode, 0, err)
            printed += out.split()
        expected = [f"R{n}" for n in range(1, 2 * count + 1)]
        self.assertEqual(sorted(printed, key=lambda i: int(i[1:])), expected)
        self.assertEqual(sorted(self.decisions(), key=lambda i: int(i[1:])), expected)
        log = self.read("log.md")
        self.assertEqual(sorted(re.findall(r"— (R\d+) pending-review\n", log), key=lambda i: int(i[1:])), expected)
        for prefix in ("a", "b"):
            for n in range(count):
                self.assertEqual(log.count(f"\n{prefix}{n}\n"), 1)
        self.plan("validate")


class GrantTest(PlanTestCase):
    def setUp(self):
        super().setUp()
        self.init()

    def grant(self):
        return self.state()["run"]["grant"]

    def test_new_plan_has_no_grant(self):
        self.assertIsNone(self.grant())
        self.assertIn("Autonomy: not granted", self.plan("status").out)
        self.assertIsNone(json.loads(self.plan("status", "--json").out)["run"]["grant"])

    def test_grant_records_a_timestamp_and_log_entry_and_status_shows_it(self):
        self.plan("grant", "--note", "user granted autonomy in chat")
        grant = self.grant()
        self.assertRegex(grant["granted"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        self.assertEqual(grant["note"], "user granted autonomy in chat")
        self.assertRegex(self.read("log.md"), ENTRY + r"autonomy granted\n\nGranted: " + grant["granted"]
                         + r"\nNote: user granted autonomy in chat\n")
        self.assertIn(f"Autonomy: granted {grant['granted']} (user granted autonomy in chat)", self.plan("status").out)
        self.assertEqual(json.loads(self.plan("status", "--json").out)["run"]["grant"], grant)

    def test_grant_without_note(self):
        self.plan("grant")
        self.assertIsNone(self.grant()["note"])
        self.assertIn("Autonomy: granted " + self.grant()["granted"] + "\n", self.plan("status").out + "\n")

    def test_revoke_clears_the_grant_with_a_log_entry(self):
        self.plan("grant")
        granted = self.grant()["granted"]
        self.plan("revoke", "--note", "run finished")
        self.assertIsNone(self.grant())
        self.assertRegex(self.read("log.md"), ENTRY + r"autonomy revoked\n\nRevoked grant from: " + granted
                         + r"\nNote: run finished\n")
        self.assertIn("Autonomy: not granted", self.plan("status").out)

    def test_round_trip_survives_reload(self):
        self.plan("grant")
        self.plan("revoke")
        self.plan("grant", "--note", "again")
        self.assertEqual(self.grant()["note"], "again")
        self.assertEqual(self.read("log.md").count("autonomy granted"), 2)

    def test_grant_while_granted_is_refused_unless_forced(self):
        self.plan("grant", "--note", "first")
        first = self.grant()
        result = self.plan_fails("grant", "--note", "second")
        self.assertIn(f"autonomy is already granted ({first['granted']})", result.err)
        self.assertEqual(self.grant(), first)
        self.plan("grant", "--note", "second", "--force", "--reason", "user restated the grant")
        self.assertEqual(self.grant()["note"], "second")
        log = self.read("log.md")
        self.assertIn("Reason: user restated the grant", log)
        self.assertIn("Replaces grant from: " + first["granted"], log)

    def test_revoke_without_grant_is_refused_unless_forced(self):
        result = self.plan_fails("revoke")
        self.assertIn("autonomy is not granted", result.err)
        self.plan("revoke", "--force", "--reason", "make sure")
        self.assertIsNone(self.grant())
        self.assertIn("No grant was recorded.", self.read("log.md"))

    def test_grant_reason_without_force_is_refused(self):
        self.assertIn("--reason applies only with --force", self.plan_fails("grant", "--reason", "x").err)


class LaterFieldsTest(PlanTestCase):
    def setUp(self):
        super().setUp()
        self.init()

    def rewrite(self, change):
        state = self.state()
        change(state)
        with open(os.path.join(self.plan_dir, "state.json"), "w") as handle:
            json.dump(state, handle)

    def test_state_without_decisions_or_grant_reads_them_as_empty(self):
        def drop(state):
            del state["decisions"]
            del state["run"]["grant"]
        self.rewrite(drop)
        self.plan("validate")
        self.assertEqual(self.plan("decisions").out, "")
        self.assertIn("Autonomy: not granted", self.plan("status").out)
        self.plan("slice", "add", "01", "--file", "f", "--outcome", "o")
        self.assertEqual((self.state()["decisions"], self.state()["run"]["grant"]), ({}, None))

    def test_malformed_decision_index_is_refused_on_load(self):
        cases = (
            lambda s: s.update(decisions=[]),
            lambda s: s.update(decisions={"R1": "x"}),
            lambda s: s.update(decisions={"R1": {"status": "approved", "undo_cost": "low", "slices": "01",
                                                 "recorded": "t", "updated": None}}),
            lambda s: s.update(decisions={"X1": {"status": "approved", "undo_cost": "low", "slices": [],
                                                 "recorded": "t", "updated": None}}),
            lambda s: s.update(decisions={"R1\n": {"status": "approved", "undo_cost": "low", "slices": [],
                                                   "recorded": "t", "updated": None}}),
            lambda s: s["run"].update(grant="yes"),
            lambda s: s["run"].update(grant={"note": None}),
            lambda s: s["run"].update(grant={"granted": "t"}),
        )
        for case in cases:
            self.init_fresh()
            self.rewrite(case)
            result = self.plan_fails("status")
            self.assertIn("malformed", result.err)

    def init_fresh(self):
        import shutil
        shutil.rmtree(self.plan_dir)
        self.assertEqual(self.run_plan("init", self.plan_dir, "--repo", self.repo, "--target", "main").code, 0)

    def test_extra_decision_keys_do_not_break_listing(self):
        self.rewrite(lambda s: s.update(decisions={"R1": {"status": "approved", "undo_cost": "low", "slices": [],
                                                          "recorded": "t", "updated": None, "id": "x",
                                                          "unfinished": 1}}))
        rows = json.loads(self.plan("decisions", "--json").out)
        self.assertEqual((rows[0]["id"], rows[0]["unfinished"]), ("R1", []))

    def test_validate_names_unknown_decision_values_and_missing_slices(self):
        self.rewrite(lambda s: s.update(decisions={"R1": {"status": "maybe", "undo_cost": "huge", "slices": ["07"],
                                                          "recorded": "t", "updated": None}}))
        result = self.plan_fails("validate")
        self.assertIn("decision R1 has unknown status 'maybe'", result.err)
        self.assertIn("decision R1 has unknown undo cost 'huge'", result.err)
        self.assertIn("decision R1 names slice 07, which does not exist", result.err)


if __name__ == "__main__":
    unittest.main()
