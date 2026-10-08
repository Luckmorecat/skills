import unittest

from support import PlanTestCase


class SliceAddTest(PlanTestCase):
    def setUp(self):
        super().setUp()
        self.init()

    def test_add_records_slice(self):
        self.plan("slice", "add", "01", "--file", "01-x.md", "--outcome", "It works", "--status", "ready")
        self.assertEqual(
            self.state()["slices"]["01"],
            {"file": "01-x.md", "outcome": "It works", "status": "ready", "reason": None, "blocked_by": [],
             "fixed_point": None, "snapshot": None},
        )

    def test_add_defaults_to_ready(self):
        self.plan("slice", "add", "01", "--file", "01-x.md", "--outcome", "o")
        self.assertEqual(self.state()["slices"]["01"]["status"], "ready")

    def test_add_records_dependencies_with_what_they_supply(self):
        self.plan("slice", "add", "01", "--file", "01-x.md", "--outcome", "o")
        self.plan("slice", "add", "02", "--file", "02-y.md", "--outcome", "o")
        self.plan(
            "slice", "add", "03", "--file", "03-z.md", "--outcome", "o",
            "--blocked-by", "01:state model, writer", "02",
        )
        self.assertEqual(
            self.state()["slices"]["03"]["blocked_by"],
            [{"id": "01", "supplies": "state model, writer"}, {"id": "02", "supplies": ""}],
        )

    def test_blocked_by_flag_is_repeatable(self):
        self.plan("slice", "add", "01", "--file", "a", "--outcome", "o")
        self.plan("slice", "add", "02", "--file", "b", "--outcome", "o")
        self.plan("slice", "add", "03", "--file", "c", "--outcome", "o",
                  "--blocked-by", "01:x", "--blocked-by", "02:y")
        self.assertEqual([d["id"] for d in self.state()["slices"]["03"]["blocked_by"]], ["01", "02"])

    def test_add_refuses_duplicate_id(self):
        self.plan("slice", "add", "01", "--file", "01-x.md", "--outcome", "first")
        result = self.plan_fails("slice", "add", "01", "--file", "01-y.md", "--outcome", "second")
        self.assertIn("01", result.err)
        self.assertEqual(self.state()["slices"]["01"]["outcome"], "first")

    def test_add_refuses_missing_dependency(self):
        result = self.plan_fails("slice", "add", "02", "--file", "b", "--outcome", "o", "--blocked-by", "07:thing")
        self.assertIn("07", result.err)
        self.assertEqual(self.state()["slices"], {})

    def test_add_refuses_self_dependency(self):
        result = self.plan_fails("slice", "add", "01", "--file", "a", "--outcome", "o", "--blocked-by", "01")
        self.assertIn("dependency cycle: 01 -> 01", result.err)

    def test_add_blocked_requires_reason(self):
        result = self.plan_fails("slice", "add", "01", "--file", "a", "--outcome", "o", "--status", "blocked")
        self.assertIn("--status blocked requires --reason", result.err)
        self.plan("slice", "add", "01", "--file", "a", "--outcome", "o", "--status", "blocked",
                  "--reason", "needs a decision")
        slice_ = self.state()["slices"]["01"]
        self.assertEqual((slice_["status"], slice_["reason"]), ("blocked", "needs a decision"))

    def test_add_refuses_lifecycle_status_without_force(self):
        result = self.plan_fails("slice", "add", "01", "--file", "a", "--outcome", "o", "--status", "complete")
        self.assertIn("--force", result.err)

    def test_add_refuses_malformed_id(self):
        for bad in ("0 1", "01:x"):
            result = self.plan_fails("slice", "add", bad, "--file", "a", "--outcome", "o")
            self.assertIn(f"slice ID {bad!r} must match", result.err)

    def test_add_requires_file_and_outcome(self):
        self.assertIn("--file", self.plan_fails("slice", "add", "01", "--outcome", "o").err)
        self.assertIn("--outcome", self.plan_fails("slice", "add", "01", "--file", "a").err)


class SliceEditTest(PlanTestCase):
    def setUp(self):
        super().setUp()
        self.init()
        self.plan("slice", "add", "01", "--file", "01-a.md", "--outcome", "first")
        self.plan("slice", "add", "02", "--file", "02-b.md", "--outcome", "second", "--blocked-by", "01:core")

    def test_edit_changes_outcome_and_file(self):
        self.plan("slice", "edit", "01", "--outcome", "new outcome", "--file", "01-new.md")
        slice_ = self.state()["slices"]["01"]
        self.assertEqual((slice_["outcome"], slice_["file"]), ("new outcome", "01-new.md"))

    def test_edit_replaces_dependencies(self):
        self.plan("slice", "add", "03", "--file", "c", "--outcome", "o")
        self.plan("slice", "edit", "02", "--blocked-by", "03:other")
        self.assertEqual(self.state()["slices"]["02"]["blocked_by"], [{"id": "03", "supplies": "other"}])

    def test_edit_clears_dependencies_with_none(self):
        self.plan("slice", "edit", "02", "--blocked-by", "None")
        self.assertEqual(self.state()["slices"]["02"]["blocked_by"], [])

    def test_edit_moves_between_ready_and_blocked(self):
        self.plan("slice", "edit", "02", "--status", "blocked", "--reason", "waiting on API")
        slice_ = self.state()["slices"]["02"]
        self.assertEqual((slice_["status"], slice_["reason"]), ("blocked", "waiting on API"))
        self.plan("slice", "edit", "02", "--status", "ready")
        slice_ = self.state()["slices"]["02"]
        self.assertEqual((slice_["status"], slice_["reason"]), ("ready", None))

    def test_edit_to_blocked_requires_reason(self):
        result = self.plan_fails("slice", "edit", "02", "--status", "blocked")
        self.assertIn("--reason", result.err)
        self.assertEqual(self.state()["slices"]["02"]["status"], "ready")

    def test_edit_updates_reason_of_blocked_slice(self):
        self.plan("slice", "edit", "02", "--status", "blocked", "--reason", "one")
        self.plan("slice", "edit", "02", "--reason", "two")
        self.assertEqual(self.state()["slices"]["02"]["reason"], "two")

    def test_edit_refuses_cycle(self):
        result = self.plan_fails("slice", "edit", "01", "--blocked-by", "02")
        self.assertIn("cycle", result.err)
        self.assertEqual(self.state()["slices"]["01"]["blocked_by"], [])

    def test_edit_refuses_missing_dependency(self):
        result = self.plan_fails("slice", "edit", "02", "--blocked-by", "09")
        self.assertIn("09", result.err)

    def test_edit_refuses_unknown_slice(self):
        result = self.plan_fails("slice", "edit", "42", "--outcome", "x")
        self.assertIn("42", result.err)

    def test_edit_refuses_no_change(self):
        self.assertIn("nothing to change", self.plan_fails("slice", "edit", "01").err)

    def test_edit_refuses_lifecycle_status_without_force(self):
        result = self.plan_fails("slice", "edit", "01", "--status", "complete")
        self.assertIn("--force", result.err)
        self.assertEqual(self.state()["slices"]["01"]["status"], "ready")

    def test_force_overrides_guard_and_logs_reason(self):
        self.plan("slice", "edit", "01", "--status", "complete", "--force", "--reason", "landed before the CLI")
        self.assertEqual(self.state()["slices"]["01"]["status"], "complete")
        log = self.read("log.md")
        self.assertIn("landed before the CLI", log)
        self.assertIn("01", log)
        self.assertIn("complete", log)

    def test_editing_status_of_finished_slice_is_guarded(self):
        self.plan("slice", "edit", "01", "--status", "complete", "--force", "--reason", "r1")
        result = self.plan_fails("slice", "edit", "01", "--status", "ready")
        self.assertIn("slice 01 status complete -> ready is outside ready/blocked", result.err)
        self.plan("slice", "edit", "01", "--status", "ready", "--force", "--reason", "r2: reopened")
        self.assertEqual(self.state()["slices"]["01"]["status"], "ready")
        self.assertIn("r2: reopened", self.read("log.md"))

    def test_force_requires_reason(self):
        result = self.plan_fails("slice", "edit", "01", "--status", "complete", "--force")
        self.assertIn("--force requires --reason", result.err)

    def test_reason_without_purpose_is_refused(self):
        result = self.plan_fails("slice", "edit", "01", "--outcome", "x", "--reason", "why")
        self.assertIn("--reason applies only to a blocked slice or with --force", result.err)

    def test_unforced_writes_leave_log_untouched(self):
        self.plan("slice", "edit", "01", "--outcome", "changed")
        self.assertEqual(self.read("log.md"), "")

    def test_force_never_overrides_integrity_errors(self):
        result = self.plan_fails("slice", "edit", "01", "--blocked-by", "02", "--force", "--reason", "please")
        self.assertIn("dependency cycle: 01 -> 02 -> 01", result.err)
        result = self.plan_fails("slice", "add", "01", "--file", "a", "--outcome", "o", "--force", "--reason", "please")
        self.assertIn("slice 01 already exists", result.err)
        self.assertEqual(self.read("log.md"), "")

    def test_force_alone_is_not_a_change(self):
        result = self.plan_fails("slice", "edit", "01", "--force", "--reason", "why")
        self.assertIn("nothing to change", result.err)
        self.assertEqual(self.read("log.md"), "")

    def test_forced_override_is_logged_even_when_state_write_fails(self):
        import os
        before = self.read("state.json")
        os.mkdir(os.path.join(self.plan_dir, "state.json.tmp"))
        self.plan_fails("slice", "edit", "01", "--status", "complete", "--force", "--reason", "logged first")
        self.assertIn("logged first", self.read("log.md"))
        self.assertEqual(self.read("state.json"), before)

    def test_add_refuses_id_that_sorts_like_an_existing_one(self):
        result = self.plan_fails("slice", "add", "1", "--file", "a", "--outcome", "o")
        self.assertIn("slice IDs 01 and 1 collide", result.err)
        self.assertNotIn("1", self.state()["slices"])


if __name__ == "__main__":
    unittest.main()
