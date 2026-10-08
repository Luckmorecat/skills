import os
import unittest

from support import PlanTestCase, git


class InitTest(PlanTestCase):
    def test_init_records_repository_target_and_tip(self):
        tip = self.commit()
        self.run_plan("init", self.plan_dir, "--repo", self.repo, "--target", "main")
        state = self.state()
        self.assertEqual(state["schema"], 1)
        self.assertEqual(state["repo"], self.repo)
        self.assertEqual(state["run"]["target"], "main")
        self.assertEqual(state["run"]["target_tip"], tip)
        self.assertEqual(state["planning_revision"], tip)
        self.assertEqual(state["slices"], {})

    def test_init_creates_empty_log_and_plan_with_status_block(self):
        self.init()
        self.assertEqual(self.read("log.md"), "")
        plan = self.read("plan.md")
        self.assertEqual(plan.count("<!-- plan:status:start"), 1)
        self.assertEqual(plan.count("<!-- plan:status:end -->"), 1)
        self.assertIn("| ID | File | Outcome | Blocked by | Status |", plan)

    def test_init_preserves_existing_plan_prose(self):
        prose = "# My plan\n\n## Goal\n\nShip it.\n"
        self.write("plan.md", prose)
        self.init()
        plan = self.read("plan.md")
        self.assertTrue(plan.startswith(prose))
        self.assertEqual(plan.count("<!-- plan:status:start"), 1)

    def test_init_preserves_existing_log(self):
        self.write("log.md", "# Log\n\nold history\n")
        self.init()
        self.assertEqual(self.read("log.md"), "# Log\n\nold history\n")

    def test_init_refuses_directory_with_state(self):
        self.init()
        before = self.read("state.json")
        result = self.run_plan("init", self.plan_dir, "--repo", self.repo, "--target", "main")
        self.assertNotEqual(result.code, 0)
        self.assertIn("state.json", result.err)
        self.assertEqual(self.read("state.json"), before)

    def test_init_refuses_non_git_directory(self):
        not_repo = os.path.join(self.tmp, "nope")
        os.makedirs(not_repo)
        result = self.run_plan("init", self.plan_dir, "--repo", not_repo, "--target", "main")
        self.assertNotEqual(result.code, 0)
        self.assertFalse(os.path.exists(os.path.join(self.plan_dir, "state.json")))

    def test_init_refuses_unknown_target_branch(self):
        self.commit()
        result = self.run_plan("init", self.plan_dir, "--repo", self.repo, "--target", "nope")
        self.assertNotEqual(result.code, 0)
        self.assertIn("nope", result.err)

    def test_init_in_unborn_repository_records_no_tip(self):
        result = self.run_plan("init", self.plan_dir, "--repo", self.repo, "--target", "main")
        self.assertEqual(result.code, 0, result.err)
        self.assertIsNone(self.state()["run"]["target_tip"])

    def test_repo_given_as_subdirectory_records_the_root(self):
        self.commit()
        sub = os.path.join(self.repo, "sub")
        os.makedirs(sub)
        self.run_plan("init", self.plan_dir, "--repo", sub, "--target", "main")
        self.assertEqual(self.state()["repo"], self.repo)


if __name__ == "__main__":
    unittest.main()
