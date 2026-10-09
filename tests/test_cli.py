import os
import unittest

from support import PlanTestCase


class CommandLineTest(PlanTestCase):
    def test_plan_directory_defaults_to_current_directory(self):
        self.init()
        result = self.run_executable("slice", "add", "01", "--file", "f", "--outcome", "o", cwd=self.plan_dir)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_executable("next", cwd=self.plan_dir)
        self.assertEqual(result.stdout, "01\tf\to\n")

    def test_plan_option_is_accepted_before_the_command(self):
        self.init()
        result = self.run_executable("--plan", self.plan_dir, "status")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Eligible: none", result.stdout)

    def test_errors_go_to_stderr_with_non_zero_exit(self):
        self.init()
        result = self.run_executable("slice", "edit", "42", "--outcome", "x", "--plan", self.plan_dir)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("42", result.stderr)

    def test_usage_errors_exit_non_zero(self):
        result = self.run_executable("frobnicate")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("frobnicate", result.stderr)

    def test_help_documents_commands_and_state_fields(self):
        result = self.run_executable("--help")
        self.assertEqual(result.returncode, 0)
        lines = [line.strip() for line in result.stdout.splitlines()]
        for command in ("init", "import", "slice", "validate", "status", "next", "start", "block", "resume",
                        "complete", "land", "constrain", "target-tip", "decide", "decisions", "grant", "revoke"):
            # Python 3.9 puts a long command name on a line of its own, its summary below
            self.assertTrue(any(line == command or line.startswith(command + " ") for line in lines), command)
        for field in ("schema", "repo", "run.target", "run.target_tip", "slices.<ID>.file",
                      "slices.<ID>.outcome", "slices.<ID>.status", "slices.<ID>.reason", "slices.<ID>.blocked_by",
                      "planning_revision", "slices.<ID>.fixed_point", "slices.<ID>.snapshot", "slices.<ID>.landed",
                      "run.grant", "run.constraints", "slices.<ID>.worktree", "worktrees/<ID>", "decisions.<R>.status", "decisions.<R>.undo_cost", "decisions.<R>.slices",
                      "decisions.<R>.recorded", "decisions.<R>.updated", "checkpoints/<ID>.md"):
            self.assertTrue(any(line.startswith(field) for line in lines), field)
        self.assertIn("--force --reason", result.stdout)
        self.assertTrue(any(line.startswith("--plan DIR") for line in lines))

    def test_each_subcommand_documents_its_flags(self):
        expectations = {
            ("init",): ("--repo", "--target", "state.json"),
            ("import",): ("--repo", "--target", "state.json"),
            ("slice", "add"): ("--file", "--outcome", "--blocked-by", "--status", "--note", "--force", "--reason",
                                "--plan", "@FILE", "log.md"),
            ("slice", "edit"): ("--file", "--outcome", "--blocked-by", "--status", "--note", "--force", "--reason",
                                "--plan", "@FILE", "log.md"),
            ("validate",): ("--plan", "state.json"),
            ("status",): ("--json", "--plan", "checkpoint"),
            ("next",): ("--limit", "--plan"),
            ("start",): ("--worktree", "--note", "--force", "--reason", "--plan", "fixed point", "checkpoints/<ID>.md",
                         "STRIKER_ROOT", "plan/<plan directory name>/<ID>"),
            ("land",): ("--evidence", "--force", "--reason", "--plan", "@FILE", "fast-forward", "Resuming"),
            ("constrain",): ("--reason", "--force", "--plan", "run.constraints", "plan next"),
            ("target-tip",): ("--reason", "--force", "--plan", "run.target_tip", "descend"),
            ("block",): ("--force", "--reason", "--plan", "blocked"),
            ("resume",): ("--force", "--reason", "--plan", "in-progress"),
            ("complete",): ("--rev", "--evidence", "--force", "--reason", "--plan", "@FILE", "log.md"),
            ("decide",): ("--status", "--undo-cost", "--slices", "--body", "--force", "--reason", "--plan", "@FILE",
                          "R<n>", "irreversible", "log.md"),
            ("decisions",): ("--pending", "--json", "--plan", "unfinished"),
            ("grant",): ("--note", "--force", "--reason", "--plan", "run.grant"),
            ("revoke",): ("--note", "--force", "--reason", "--plan", "run.grant"),
        }
        for command, flags in expectations.items():
            result = self.run_executable(*command, "--help")
            self.assertEqual(result.returncode, 0, command)
            lines = [line.strip() for line in result.stdout.splitlines()]
            for flag in flags:
                if flag.startswith("--"):
                    self.assertTrue(any(line.startswith(flag) for line in lines), (command, flag))
                else:
                    self.assertIn(flag, result.stdout, (command, flag))

    def test_missing_plan_directory_is_reported_without_creating_files(self):
        missing = os.path.join(self.tmp, "missing")
        result = self.run_executable("slice", "add", "01", "--file", "f", "--outcome", "o", "--plan", missing)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("plan: error: no state.json", result.stderr)
        self.assertFalse(os.path.exists(missing))

    def test_plan_without_state_gets_no_lock_file(self):
        os.makedirs(self.plan_dir)
        result = self.run_executable("slice", "add", "01", "--file", "f", "--outcome", "o", "--plan", self.plan_dir)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(os.listdir(self.plan_dir), [])

    def test_undecodable_plan_file_is_reported_without_traceback(self):
        self.init()
        with open(os.path.join(self.plan_dir, "plan.md"), "wb") as handle:
            handle.write(b"\xff\xfe broken")
        result = self.run_executable("slice", "add", "01", "--file", "f", "--outcome", "o", "--plan", self.plan_dir)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("plan: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_runs_without_executable_bit_through_python(self):
        self.commit()
        result = self.run_executable("init", os.path.join(self.tmp, "p2"), "--repo", self.repo, "--target", "main")
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
