import json
import os
import subprocess
import sys
import unittest
from unittest import mock

from support import PLAN_PATH, PlanTestCase, git, plan_cli


class ParallelTestCase(PlanTestCase):
    """A plan outside the repository: 01, 02, and 04 independent, 03 after 01 and 02."""

    def setUp(self):
        super().setUp()
        self.striker_root = os.path.join(self.tmp, "striker")
        patcher = mock.patch.dict(os.environ, {"STRIKER_ROOT": self.striker_root})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.init()
        self.tip = self.head()
        self.plan("slice", "add", "01", "--file", "01-a.md", "--outcome", "first")
        self.plan("slice", "add", "02", "--file", "02-b.md", "--outcome", "second")
        self.plan("slice", "add", "03", "--file", "03-c.md", "--outcome", "third", "--blocked-by", "01:a", "02:b")
        self.plan("slice", "add", "04", "--file", "04-d.md", "--outcome", "fourth")

    def head(self, rev="HEAD"):
        return git(self.repo, "rev-parse", rev)

    def slice_(self, sid):
        return self.state()["slices"][sid]

    def tree(self, sid):
        return self.slice_(sid)["worktree"]

    def branch_exists(self, branch):
        return git(self.repo, "branch", "--list", branch) != ""

    def work(self, sid, name, content="w\n"):
        """Commits a file on the slice branch in its worktree and returns the commit."""
        path = self.tree(sid)["path"]
        with open(os.path.join(path, name), "w") as handle:
            handle.write(content)
        git(path, "add", name)
        git(path, "-c", "commit.gpgsign=false", "commit", "-q", "-m", f"{sid}: {name}")
        return git(path, "rev-parse", "HEAD")

    def checkpoint(self, sid):
        return os.path.join(self.plan_dir, "checkpoints", f"{sid}.md")

    def write_checkpoint(self, sid, text):
        with open(self.checkpoint(sid), "w") as handle:
            handle.write(text)

    def files(self):
        return {name: self.read(name) for name in ("state.json", "log.md", "plan.md")}

    def failing_git(self, *prefixes):
        """Patches the CLI's git_or_fail to fail Git commands starting with any of prefixes."""
        real = plan_cli.git_or_fail

        def fail(repo, *args):
            if any(args[:len(prefix)] == prefix for prefix in prefixes):
                raise plan_cli.PlanError("killed")
            return real(repo, *args)

        return mock.patch.object(plan_cli, "git_or_fail", side_effect=fail)


class StartWorktreeTest(ParallelTestCase):
    def test_start_creates_branch_and_worktree_at_the_recorded_tip(self):
        result = self.plan("start", "01", "--worktree", "--note", "port 8001", "--note", "db plan_01")
        path = os.path.join(os.path.abspath(self.plan_dir), "worktrees", "01")
        tree = self.tree("01")
        self.assertEqual(tree, {"path": path, "branch": "plan/plan/01", "base": self.tip,
                                "notes": ["port 8001", "db plan_01"]})
        self.assertEqual(git(path, "rev-parse", "HEAD"), self.tip)
        self.assertEqual(git(path, "symbolic-ref", "--short", "HEAD"), "plan/plan/01")
        s = self.slice_("01")
        self.assertEqual((s["status"], s["fixed_point"], s["snapshot"]), ("in-progress", self.tip, ""))
        self.assertTrue(os.path.exists(self.checkpoint("01")))
        self.assertIn(path, result.out)
        entry = self.read("log.md").split("— slice 01 started")[1]
        for text in (f"Worktree: {path}", "Branch: plan/plan/01", f"Base: {self.tip}", "Note: port 8001",
                     "Note: db plan_01", "Dirty snapshot: clean"):
            self.assertIn(text, entry)

    def test_note_requires_worktree(self):
        self.assertIn("--note applies only with --worktree", self.plan_fails("start", "01", "--note", "x").err)

    def test_plan_inside_the_repository_puts_the_worktree_under_striker_root(self):
        plan_dir = os.path.join(self.repo, "plans", "toy")
        self.assertEqual(self.run_plan("init", plan_dir, "--repo", self.repo, "--target", "main").code, 0)
        self.assertEqual(self.run_plan("slice", "add", "01", "--file", "f", "--outcome", "o", "--plan", plan_dir).code, 0)
        # The plan directory is untracked in the repository; it does not count as a dirty root.
        result = self.run_plan("start", "01", "--worktree", "--plan", plan_dir)
        self.assertEqual(result.code, 0, result.err)
        with open(os.path.join(plan_dir, "state.json")) as handle:
            tree = json.load(handle)["slices"]["01"]["worktree"]
        self.assertEqual(tree["path"], os.path.join(self.striker_root, "worktrees", "repo", "toy", "01"))
        self.assertEqual(tree["branch"], "plan/toy/01")
        self.assertEqual(git(tree["path"], "rev-parse", "HEAD"), self.tip)

    def test_path_rule_falls_back_to_xdg_state_home_then_home(self):
        inside = os.path.join(self.repo, "plans", "toy")
        outside = os.path.join(self.tmp, "elsewhere", "toy")
        with mock.patch.dict(os.environ, {"STRIKER_ROOT": "", "XDG_STATE_HOME": os.path.join(self.tmp, "xdg")}):
            self.assertEqual(plan_cli.worktree_path(inside, self.repo, "01"),
                             os.path.join(self.tmp, "xdg", "striker", "worktrees", "repo", "toy", "01"))
            self.assertEqual(plan_cli.worktree_path(outside, self.repo, "01"), os.path.join(outside, "worktrees", "01"))
        with mock.patch.dict(os.environ, {"STRIKER_ROOT": "", "XDG_STATE_HOME": "", "HOME": os.path.join(self.tmp, "h")}):
            self.assertEqual(plan_cli.worktree_path(inside, self.repo, "01"),
                             os.path.join(self.tmp, "h", ".local", "state", "striker", "worktrees", "repo", "toy", "01"))

    def test_failed_worktree_add_removes_what_git_made(self):
        hook = os.path.join(self.repo, ".git", "hooks", "post-checkout")
        with open(hook, "w") as handle:
            handle.write("#!/bin/sh\nexit 1\n")
        os.chmod(hook, 0o755)
        before = self.files()
        result = self.plan_fails("start", "01", "--worktree")
        self.assertIn("`git worktree add", result.err)
        self.assertIn("exit code 1", result.err)
        self.assertEqual(self.files(), before)
        self.assertFalse(os.path.exists(os.path.join(self.plan_dir, "worktrees")))
        self.assertFalse(self.branch_exists("plan/plan/01"))
        self.assertEqual(git(self.repo, "worktree", "list", "--porcelain").count("worktree "), 1)
        os.remove(hook)
        self.plan("start", "01", "--worktree")

    def test_failed_snapshot_after_worktree_add_removes_the_worktree_and_branch(self):
        real = plan_cli.dirty_snapshot

        def fail(path, exclude=None):
            if "worktrees" in path:
                raise plan_cli.PlanError("cannot read `git status`")
            return real(path, exclude)

        with mock.patch.object(plan_cli, "dirty_snapshot", side_effect=fail):
            self.plan_fails("start", "01", "--worktree")
        self.assertEqual(self.slice_("01")["status"], "ready")
        self.assertFalse(os.path.exists(os.path.join(self.plan_dir, "worktrees")))
        self.assertFalse(self.branch_exists("plan/plan/01"))

    def test_constraint_counts_a_slice_in_progress_in_the_checkout(self):
        self.plan("constrain", "01", "04", "--reason", "same database")
        self.plan("start", "04")
        self.assertNotIn("01", [line.split("\t")[0] for line in self.plan("next").out.splitlines()])
        result = self.plan_fails("start", "01", "--worktree")
        self.assertIn("constrained against 04, which is in progress in the repository checkout", result.err)

    def test_git_config_of_the_user_does_not_reach_the_tests(self):
        code, out = plan_cli.run_git(self.repo, "config", "--show-origin", "--list")
        origins = {line.split("\t")[0] for line in out.splitlines()}
        self.assertTrue(origins <= {"file:.git/config"}, origins)

    def test_branch_name_replaces_characters_git_refuses(self):
        self.assertEqual(plan_cli.worktree_branch(self.repo, "/x/my plan..v2~", "01"), "plan/my-plan-v2/01")

    def test_start_refuses_a_target_tip_that_differs_from_the_recorded_one(self):
        outside = self.commit("outside.txt")
        before = self.files()
        result = self.plan_fails("start", "01", "--worktree")
        self.assertIn(f"main is at {outside}, not the recorded tip {self.tip}", result.err)
        self.assertIn("plan target-tip", result.err)
        self.assertEqual(self.files(), before)
        self.assertFalse(os.path.exists(os.path.join(self.plan_dir, "worktrees")))
        self.assertFalse(self.branch_exists("plan/plan/01"))

    def test_start_refuses_a_dirty_root(self):
        with open(os.path.join(self.repo, "file.txt"), "a") as handle:
            handle.write("dirty\n")
        result = self.plan_fails("start", "01", "--worktree")
        self.assertIn("has uncommitted changes outside the plan directory (file.txt)", result.err)
        self.assertIsNone(self.tree("01"))
        self.assertFalse(self.branch_exists("plan/plan/01"))
        os.remove(os.path.join(self.repo, "file.txt"))
        git(self.repo, "checkout", "--", "file.txt")
        with open(os.path.join(self.repo, "untracked.txt"), "w") as handle:
            handle.write("u\n")
        self.assertIn("(untracked.txt)", self.plan_fails("start", "01", "--worktree").err)

    def test_start_refuses_a_root_on_another_branch(self):
        git(self.repo, "checkout", "-q", "-b", "other")
        result = self.plan_fails("start", "01", "--worktree")
        self.assertIn("has other checked out, not main", result.err)

    def test_force_overrides_root_refusals_and_logs_them(self):
        self.commit("outside.txt")
        self.plan("start", "01", "--worktree", "--force", "--reason", "outside commit is harmless")
        self.assertEqual(self.tree("01")["base"], self.tip)
        self.assertIn("Overrode: main is at", self.read("log.md"))

    def test_start_refuses_an_existing_branch_or_path(self):
        git(self.repo, "branch", "plan/plan/01")
        self.assertIn("branch plan/plan/01 already exists", self.plan_fails("start", "01", "--worktree").err)
        os.makedirs(os.path.join(self.plan_dir, "worktrees", "02"))
        self.assertIn("worktrees/02 already exists", self.plan_fails("start", "02", "--worktree").err)
        self.assertEqual(self.slice_("02")["status"], "ready")

    def test_start_refuses_a_slice_that_records_a_worktree(self):
        self.plan("start", "01", "--worktree")
        result = self.plan_fails("start", "01", "--worktree", "--force", "--reason", "again")
        self.assertIn("already has worktree", result.err)

    def test_failed_write_removes_the_worktree_and_branch(self):
        before = self.files()
        with mock.patch.object(plan_cli, "save_state", side_effect=OSError("disk full")):
            result = self.run_plan("start", "01", "--worktree", "--plan", self.plan_dir)
        self.assertNotEqual(result.code, 0)
        self.assertEqual(self.files(), before)
        self.assertFalse(os.path.exists(os.path.join(self.plan_dir, "worktrees")))
        self.assertFalse(os.path.exists(os.path.join(self.plan_dir, "checkpoints")))
        self.assertFalse(self.branch_exists("plan/plan/01"))
        self.assertEqual(git(self.repo, "worktree", "list", "--porcelain").count("worktree "), 1)

    def test_several_worktree_slices_run_at_once_beside_one_in_the_checkout(self):
        self.plan("start", "01", "--worktree")
        self.plan("start", "02", "--worktree")
        self.plan("start", "04")
        self.assertEqual([self.slice_(sid)["status"] for sid in ("01", "02", "04")], ["in-progress"] * 3)
        self.plan("slice", "add", "05", "--file", "05-e.md", "--outcome", "fifth")
        self.assertIn("slice 04 is already in progress in the repository checkout", self.plan_fails("start", "05").err)

    def test_blocked_worktree_slice_resumes_beside_a_slice_in_the_checkout(self):
        self.plan("start", "01", "--worktree")
        self.plan("block", "01", "--reason", "question")
        self.plan("start", "04")
        self.plan("resume", "01")
        self.assertEqual(self.slice_("01")["status"], "in-progress")
        self.assertIn("Worktree: ", self.read("log.md").split("slice 01 resumed")[1])

    def test_complete_refuses_a_worktree_slice(self):
        self.plan("start", "01", "--worktree")
        result = self.plan_fails("complete", "01", "--rev", self.tip, "--evidence", "ok")
        self.assertIn("land it with `plan land 01`", result.err)

    def test_status_shows_worktrees_and_constraints(self):
        self.plan("constrain", "02", "01", "--reason", "same port")
        self.plan("start", "01", "--worktree", "--note", "port 8001")
        tree = self.tree("01")
        out = self.plan("status").out
        self.assertIn(f"worktree {tree['path']} on plan/plan/01 from {self.tip}; notes: port 8001", out)
        self.assertIn("Constraints:\n  01, 02  same port", out)
        view = json.loads(self.plan("status", "--json").out)
        self.assertEqual(view["in_progress"][0]["worktree"], tree)
        self.assertEqual(view["run"]["constraints"], [{"slices": ["01", "02"], "reason": "same port"}])
        self.assertEqual(view["eligible"], ["04"])

    def test_state_written_before_worktrees_loads(self):
        state = self.state()
        del state["run"]["constraints"]
        for s in state["slices"].values():
            del s["worktree"]
        with open(os.path.join(self.plan_dir, "state.json"), "w") as handle:
            json.dump(state, handle)
        self.assertIn("Constraints: none", self.plan("status").out)
        self.plan("start", "01", "--worktree")


class ConstraintTest(ParallelTestCase):
    def test_constraint_is_symmetric_and_ordered(self):
        self.plan("constrain", "04", "01", "--reason", "both migrate the schema")
        self.assertEqual(self.state()["run"]["constraints"], [{"slices": ["01", "04"], "reason": "both migrate the schema"}])
        self.assertIn("— constraint 01, 04\n\nReason: both migrate the schema", self.read("log.md"))
        self.assertIn("already constrained", self.plan_fails("constrain", "01", "04", "--reason", "again").err)

    def test_next_and_start_honor_a_constraint_against_a_slice_with_a_worktree(self):
        self.plan("constrain", "01", "04", "--reason", "same port")
        self.assertEqual([line.split("\t")[0] for line in self.plan("next").out.splitlines()], ["01", "02", "04"])
        self.plan("start", "04", "--worktree")
        self.assertEqual(self.plan("next").out.splitlines()[0].split("\t")[0], "02")
        result = self.plan_fails("start", "01", "--worktree")
        self.assertIn("slice 01 is constrained against 04, which is unfinished in worktree", result.err)
        self.assertIn("(same port)", result.err)
        self.assertIn("constrained against 04", self.plan_fails("start", "01").err)
        self.plan("start", "02", "--worktree")
        self.plan("block", "04", "--reason", "paused")
        self.assertNotIn("01", [line.split("\t")[0] for line in self.plan("next").out.splitlines()])
        self.plan("resume", "04")
        self.plan("land", "04", "--evidence", "no code needed")
        self.assertIn("01", [line.split("\t")[0] for line in self.plan("next").out.splitlines()])
        self.plan("start", "01", "--worktree")

    def test_constrain_refusals(self):
        self.assertIn("requires --reason", self.plan_fails("constrain", "01", "02").err)
        self.assertIn("two different slices", self.plan_fails("constrain", "01", "01", "--reason", "x").err)
        self.assertIn("slice 09 does not exist", self.plan_fails("constrain", "01", "09", "--reason", "x").err)
        self.assertEqual(self.state()["run"]["constraints"], [])

    def test_forced_constraint_replaces_the_reason(self):
        self.plan("constrain", "01", "02", "--reason", "old")
        self.plan("constrain", "02", "01", "--force", "--reason", "new")
        self.assertEqual(self.state()["run"]["constraints"], [{"slices": ["01", "02"], "reason": "new"}])
        self.assertIn("Replaces reason: old", self.read("log.md"))

    def test_validate_reports_a_constraint_naming_a_missing_slice(self):
        state = self.state()
        state["run"]["constraints"] = [{"slices": ["01", "99"], "reason": "x"}]
        with open(os.path.join(self.plan_dir, "state.json"), "w") as handle:
            json.dump(state, handle)
        self.assertIn("constraint 01, 99 names slice 99, which does not exist", self.plan_fails("validate").err)


class LandTest(ParallelTestCase):
    def start_both(self):
        self.plan("start", "01", "--worktree")
        self.plan("start", "02", "--worktree")
        return self.tree("01"), self.tree("02")

    def test_two_concurrent_slices_land_in_sequence(self):
        first, second = self.start_both()
        a1 = self.work("01", "a1.txt")
        a2 = self.work("01", "a2.txt")
        self.work("02", "b.txt")
        self.write_checkpoint("01", "## Owned changes\na1.txt, a2.txt\n")
        result = self.plan("land", "01", "--evidence", "suite green")
        self.assertIn(f"Landed slice 01 at {a2}", result.out)
        self.assertEqual(self.head("main"), a2)
        self.assertEqual(self.head(), a2)
        s = self.slice_("01")
        self.assertEqual((s["status"], s["landed"], s["worktree"]), ("complete", [a1, a2], None))
        self.assertEqual(self.state()["run"]["target_tip"], a2)
        self.assertFalse(os.path.exists(first["path"]))
        self.assertFalse(self.branch_exists(first["branch"]))
        self.assertFalse(os.path.exists(self.checkpoint("01")))
        log = self.read("log.md")
        entry = log.split("— slice 01 landed")[1].split("\n## ")[0]
        for text in (f"Landed: {a1}, {a2}", f"Fast-forward: main {self.tip} -> {a2}", f"Target tip: {self.tip} -> {a2}",
                     "suite green", "### Owned changes"):
            self.assertIn(text, entry)
        self.assertIn(f"— slice 01 worktree removed\n\nWorktree: {first['path']} (removed)", log)

        result = self.plan_fails("land", "02", "--evidence", "suite green")
        self.assertIn(f"branch {second['branch']} at", result.err)
        self.assertIn(f"is not a fast-forward of main at {a2}", result.err)
        git(second["path"], "-c", "commit.gpgsign=false", "rebase", "-q", "main")
        b = git(second["path"], "rev-parse", "HEAD")
        self.plan("land", "02", "--evidence", "rebased suite green")
        self.assertEqual(self.head("main"), b)
        self.assertEqual(self.slice_("02")["landed"], [b])
        self.assertEqual(self.state()["run"]["target_tip"], b)
        self.assertEqual(self.plan("next").out.splitlines()[0].split("\t")[0], "03")
        self.assertFalse(os.path.exists(os.path.join(self.plan_dir, "worktrees")))
        self.assertEqual(git(self.repo, "branch", "--list", "plan/*"), "")
        self.assertEqual(git(self.repo, "worktree", "list", "--porcelain").count("worktree "), 1)

    def test_land_refusals_change_nothing(self):
        first, _ = self.start_both()
        self.work("01", "a.txt")
        before = self.files()

        with open(os.path.join(self.repo, "file.txt"), "a") as handle:
            handle.write("dirty\n")
        self.assertIn("uncommitted changes outside the plan directory (file.txt)",
                      self.plan_fails("land", "01", "--evidence", "ok").err)
        git(self.repo, "checkout", "--", "file.txt")

        with open(os.path.join(first["path"], "loose.txt"), "w") as handle:
            handle.write("l\n")
        self.assertIn("has uncommitted changes (loose.txt)", self.plan_fails("land", "01", "--evidence", "ok").err)
        os.remove(os.path.join(first["path"], "loose.txt"))

        self.assertIn("evidence is empty", self.plan_fails("land", "01", "--evidence", " ").err)
        self.assertIn("slice 04 has no worktree", self.plan_fails("land", "04", "--evidence", "ok").err)
        self.assertEqual(self.files(), before)
        self.assertEqual(self.head("main"), self.tip)

        outside = self.commit("outside.txt")
        self.assertIn(f"main is at {outside}, not the recorded tip {self.tip}",
                      self.plan_fails("land", "01", "--evidence", "ok").err)
        git(self.repo, "checkout", "-q", "-b", "other")
        self.assertIn("has other checked out, not main", self.plan_fails("land", "01", "--evidence", "ok").err)
        self.assertEqual(self.files(), before)
        self.assertTrue(os.path.isdir(first["path"]))

    def test_rerun_after_a_manual_fast_forward_finishes_without_a_second_one(self):
        first, _ = self.start_both()
        landed = self.work("01", "a.txt")
        self.write_checkpoint("01", "progress notes\n")
        git(self.repo, "merge", "--ff-only", "-q", first["branch"])
        reflog = git(self.repo, "reflog", "show", "main").splitlines()
        self.plan("land", "01", "--evidence", "suite green")
        self.assertEqual(git(self.repo, "reflog", "show", "main").splitlines(), reflog)
        s = self.slice_("01")
        self.assertEqual((s["status"], s["landed"], s["worktree"]), ("complete", [landed], None))
        self.assertEqual(self.state()["run"]["target_tip"], landed)
        entry = self.read("log.md").split("— slice 01 landed")[1]
        self.assertIn(f"Fast-forward: none; main already contains {landed}", entry)
        self.assertIn("progress notes", entry)
        self.assertFalse(self.branch_exists(first["branch"]))

    def test_rerun_after_a_failure_following_the_fast_forward(self):
        first, _ = self.start_both()
        landed = self.work("01", "a.txt")
        real = plan_cli.save_state
        calls = []

        def fail_once(plan_dir, state):
            calls.append(1)
            if len(calls) == 1:
                raise OSError("killed")
            real(plan_dir, state)

        with mock.patch.object(plan_cli, "save_state", side_effect=fail_once):
            self.assertNotEqual(self.run_plan("land", "01", "--evidence", "ok", "--plan", self.plan_dir).code, 0)
        self.assertEqual(self.head("main"), landed)
        self.assertEqual(self.slice_("01")["status"], "in-progress")
        self.assertNotIn("slice 01 landed", self.read("log.md"))
        self.plan("land", "01", "--evidence", "ok")
        s = self.slice_("01")
        self.assertEqual((s["status"], s["landed"], s["worktree"]), ("complete", [landed], None))
        self.assertEqual(self.read("log.md").count("— slice 01 landed"), 1)
        self.assertFalse(os.path.exists(first["path"]))

    def test_rerun_finishes_removing_the_worktree_and_branch(self):
        for failing in ("worktree", "branch"):
            with self.subTest(failing=failing):
                sid = "01" if failing == "worktree" else "02"
                self.plan("start", sid, "--worktree")
                tree = self.tree(sid)
                landed = self.work(sid, f"{sid}.txt")
                prefix = ("worktree", "remove") if failing == "worktree" else ("branch", "-D")
                with self.failing_git(prefix):
                    result = self.run_plan("land", sid, "--evidence", "ok", "--plan", self.plan_dir)
                self.assertNotEqual(result.code, 0)
                s = self.slice_(sid)
                self.assertEqual((s["status"], s["worktree"]), ("complete", tree))
                self.assertEqual(os.path.isdir(tree["path"]), failing == "worktree")
                result = self.plan("land", sid, "--evidence", "ok")
                self.assertIn("already landed", result.out)
                self.assertIsNone(self.tree(sid))
                self.assertFalse(os.path.exists(tree["path"]))
                self.assertFalse(self.branch_exists(tree["branch"]))
                self.assertEqual(self.state()["run"]["target_tip"], landed)
                self.assertEqual(self.read("log.md").count(f"— slice {sid} landed"), 1)

    def test_rerun_deletes_a_checkpoint_left_after_the_state_landed(self):
        self.plan("start", "01", "--worktree")
        self.work("01", "a.txt")
        self.write_checkpoint("01", "notes\n")
        with self.failing_git(("worktree", "remove")):
            self.run_plan("land", "01", "--evidence", "ok", "--plan", self.plan_dir)
        self.write_checkpoint("01", "notes\n")  # as if killed before the checkpoint was deleted
        self.plan("land", "01", "--evidence", "ok")
        self.assertFalse(os.path.exists(self.checkpoint("01")))
        self.assertEqual(self.read("log.md").count("— slice 01 landed"), 1)

    def test_branch_with_commits_the_target_lacks_is_kept(self):
        self.plan("start", "01", "--worktree")
        tree = self.tree("01")
        self.work("01", "a.txt")
        with self.failing_git(("worktree", "remove")):
            self.run_plan("land", "01", "--evidence", "ok", "--plan", self.plan_dir)
        late = self.work("01", "late.txt")
        result = self.plan_fails("land", "01", "--evidence", "ok")
        self.assertIn(f"branch {tree['branch']} at {late} holds commits main lacks", result.err)
        self.assertTrue(self.branch_exists(tree["branch"]))

    def test_no_code_slice_lands_its_base(self):
        self.plan("start", "01", "--worktree")
        tree = self.tree("01")
        self.plan("land", "01", "--evidence", "question answered, nothing to change")
        s = self.slice_("01")
        self.assertEqual((s["status"], s["landed"]), ("complete", [self.tip]))
        self.assertEqual(self.state()["run"]["target_tip"], self.tip)
        self.assertFalse(self.branch_exists(tree["branch"]))

    def test_dirty_worktree_is_not_removed_without_force(self):
        self.plan("start", "01", "--worktree")
        tree = self.tree("01")
        self.work("01", "a.txt")
        with self.failing_git(("worktree", "remove")):
            self.run_plan("land", "01", "--evidence", "ok", "--plan", self.plan_dir)
        with open(os.path.join(tree["path"], "late.txt"), "w") as handle:
            handle.write("unsaved\n")
        result = self.plan_fails("land", "01", "--evidence", "ok")
        self.assertIn(f"worktree {tree['path']} has uncommitted changes (late.txt)", result.err)
        self.assertTrue(os.path.exists(os.path.join(tree["path"], "late.txt")))
        self.assertEqual(self.tree("01"), tree)
        self.plan("land", "01", "--evidence", "ok", "--force", "--reason", "late.txt is scratch")
        self.assertIsNone(self.tree("01"))
        self.assertFalse(os.path.exists(tree["path"]))
        self.assertIn("Reason: late.txt is scratch\nOverrode: worktree", self.read("log.md"))

    def test_no_code_land_still_checks_the_root(self):
        self.plan("start", "01", "--worktree")
        outside = self.commit("outside.txt")
        before = self.files()
        result = self.plan_fails("land", "01", "--evidence", "nothing to change")
        self.assertIn(f"main is at {outside}, not the recorded tip {self.tip}", result.err)
        git(self.repo, "reset", "-q", "--hard", self.tip)
        with open(os.path.join(self.repo, "file.txt"), "a") as handle:
            handle.write("dirty\n")
        self.assertIn("uncommitted changes outside the plan directory",
                      self.plan_fails("land", "01", "--evidence", "nothing to change").err)
        self.assertEqual(self.files(), before)

    def test_no_code_land_behind_the_target_keeps_the_recorded_tip(self):
        self.start_both()
        landed = self.work("02", "b.txt")
        self.plan("land", "02", "--evidence", "ok")
        self.plan("land", "01", "--evidence", "nothing to change")
        s = self.slice_("01")
        self.assertEqual((s["status"], s["landed"]), ("complete", [self.tip]))
        self.assertEqual(self.state()["run"]["target_tip"], landed)

    def test_rerun_after_a_kill_between_the_log_entry_and_state(self):
        first, _ = self.start_both()
        landed = self.work("01", "a.txt")
        killer = (
            "import importlib.machinery, importlib.util, os, sys\n"
            "loader = importlib.machinery.SourceFileLoader('plan_cli', sys.argv[1])\n"
            "spec = importlib.util.spec_from_loader('plan_cli', loader)\n"
            "plan = importlib.util.module_from_spec(spec)\n"
            "loader.exec_module(plan)\n"
            "plan.save_state = lambda plan_dir, state: os._exit(9)\n"
            "plan.main(sys.argv[2:])\n"
        )
        result = subprocess.run([sys.executable, "-c", killer, PLAN_PATH, "land", "01", "--evidence", "ok",
                                 "--plan", self.plan_dir], capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 9, result.stderr)
        self.assertEqual(self.head("main"), landed)
        self.assertEqual(self.slice_("01")["status"], "in-progress")
        reflog = git(self.repo, "reflog", "show", "main").splitlines()
        self.plan("land", "01", "--evidence", "ok")
        self.assertEqual(git(self.repo, "reflog", "show", "main").splitlines(), reflog)
        s = self.slice_("01")
        self.assertEqual((s["status"], s["landed"], s["worktree"]), ("complete", [landed], None))
        # the killed run's entry stays in the history; the rerun appends the complete one (see `land --help`)
        self.assertEqual(self.read("log.md").count("— slice 01 landed"), 2)
        self.assertFalse(self.branch_exists(first["branch"]))
        self.assertEqual(self.plan("validate").out, "Plan is valid\n")

    def test_untracked_files_count_as_dirt_when_status_hides_them(self):
        # Set in the repository, so the tests' isolation from the user's Git config does not hide it.
        git(self.repo, "config", "status.showUntrackedFiles", "no")
        with open(os.path.join(self.repo, "loose.txt"), "w") as handle:
            handle.write("l\n")
        self.assertIn("(loose.txt)", self.plan_fails("start", "01", "--worktree").err)
        self.plan("start", "04")
        self.assertEqual(self.slice_("04")["snapshot"], "?? loose.txt\n")
        os.remove(os.path.join(self.repo, "loose.txt"))
        self.plan("start", "01", "--worktree")
        tree = self.tree("01")
        self.work("01", "a.txt")
        with self.failing_git(("worktree", "remove")):
            self.run_plan("land", "01", "--evidence", "ok", "--plan", self.plan_dir)
        with open(os.path.join(tree["path"], "precious"), "w") as handle:
            handle.write("p\n")
        self.assertIn("has uncommitted changes (precious)", self.plan_fails("land", "01", "--evidence", "ok").err)
        self.assertTrue(os.path.exists(os.path.join(tree["path"], "precious")))

    def test_rerun_refuses_outside_commits_brought_in_by_a_manual_fast_forward(self):
        self.plan("start", "01", "--worktree")
        tree = self.tree("01")
        outside = self.commit("outside.txt")
        git(tree["path"], "-c", "commit.gpgsign=false", "rebase", "-q", "main")
        landed = self.work("01", "a.txt")
        git(self.repo, "merge", "--ff-only", "-q", tree["branch"])
        before = self.files()
        result = self.plan_fails("land", "01", "--evidence", "ok")
        self.assertIn(f"main reached {landed} from {outside}, which holds commits after the recorded tip {self.tip}",
                      result.err)
        self.assertEqual(self.files(), before)
        self.plan("target-tip", outside, "--reason", "hotfix made outside the plan")
        self.plan("land", "01", "--evidence", "ok")
        s = self.slice_("01")
        self.assertEqual((s["status"], s["landed"]), ("complete", [landed]))
        self.assertEqual(self.state()["run"]["target_tip"], landed)

    def drop_target_reflog(self):
        """Leaves the target branch without a reflog, as core.logAllRefUpdates=false or an expired reflog does."""
        git(self.repo, "config", "core.logAllRefUpdates", "false")
        os.remove(os.path.join(self.repo, ".git", "logs", "refs", "heads", "main"))

    def test_rerun_without_a_reflog_refuses_to_guess_where_the_target_came_from(self):
        self.plan("start", "01", "--worktree")
        tree = self.tree("01")
        self.drop_target_reflog()
        outside = self.commit("outside.txt")
        git(tree["path"], "-c", "commit.gpgsign=false", "rebase", "-q", "main")
        self.work("01", "a.txt")
        git(self.repo, "merge", "--ff-only", "-q", tree["branch"])
        before = self.files()
        result = self.plan_fails("land", "01", "--evidence", "ok")
        self.assertIn("reflog does not show where it reached", result.err)
        self.assertEqual(self.files(), before)
        self.assertNotIn(outside, self.state()["run"]["target_tip"])

    def test_lands_own_fast_forward_records_a_reflog_entry_for_recovery(self):
        self.plan("start", "01", "--worktree")
        self.drop_target_reflog()
        landed = self.work("01", "a.txt")
        real = plan_cli.save_state
        calls = []

        def fail_once(plan_dir, state):
            calls.append(1)
            if len(calls) == 1:
                raise OSError("killed")
            real(plan_dir, state)

        with mock.patch.object(plan_cli, "save_state", side_effect=fail_once):
            self.assertNotEqual(self.run_plan("land", "01", "--evidence", "ok", "--plan", self.plan_dir).code, 0)
        self.assertEqual(self.head("main"), landed)
        self.plan("land", "01", "--evidence", "ok")
        self.assertEqual(self.slice_("01")["landed"], [landed])

    def test_rerun_skips_reflog_entries_beyond_the_branch_tip(self):
        self.plan("start", "01", "--worktree")
        tree = self.tree("01")
        landed = self.work("01", "a.txt")
        git(self.repo, "merge", "--ff-only", "-q", tree["branch"])
        self.commit("mistake.txt")
        git(self.repo, "reset", "-q", "--hard", landed)
        self.plan("land", "01", "--evidence", "ok")
        s = self.slice_("01")
        self.assertEqual((s["status"], s["landed"]), ("complete", [landed]))

    def test_forced_recovery_over_outside_commits_lands_only_what_the_fast_forward_added(self):
        self.plan("start", "01", "--worktree")
        tree = self.tree("01")
        self.commit("outside.txt")
        git(tree["path"], "-c", "commit.gpgsign=false", "rebase", "-q", "main")
        landed = self.work("01", "a.txt")
        git(self.repo, "merge", "--ff-only", "-q", tree["branch"])
        self.plan("land", "01", "--evidence", "ok", "--force", "--reason", "outside commit reviewed")
        self.assertEqual(self.slice_("01")["landed"], [landed])
        self.assertEqual(self.state()["run"]["target_tip"], landed)
        self.assertIn("Overrode: main reached", self.read("log.md"))

    def test_forced_land_over_a_tip_mismatch_logs_the_override(self):
        self.plan("start", "01", "--worktree")
        tree = self.tree("01")
        outside = self.commit("outside.txt")
        git(tree["path"], "-c", "commit.gpgsign=false", "rebase", "-q", "main")
        landed = self.work("01", "a.txt")
        self.plan("land", "01", "--evidence", "ok", "--force", "--reason", "outside commit reviewed")
        self.assertEqual(self.slice_("01")["landed"], [landed])
        self.assertEqual(self.state()["run"]["target_tip"], landed)
        self.assertNotIn(outside, self.slice_("01")["landed"])
        self.assertIn("Reason: outside commit reviewed\nOverrode: main is at", self.read("log.md"))


class TargetTipTest(ParallelTestCase):
    def test_records_a_descendant_with_its_reason(self):
        self.commit("one.txt")
        outside = self.commit("two.txt")
        self.plan("target-tip", outside[:10], "--reason", "hotfix pushed by hand")
        self.assertEqual(self.state()["run"]["target_tip"], outside)
        entry = self.read("log.md").split("— target tip recorded")[1]
        for text in (f"Target tip: {self.tip} -> {outside}", "Commits accepted: 2", "Reason: hotfix pushed by hand"):
            self.assertIn(text, entry)
        self.plan("start", "01", "--worktree")
        self.assertEqual(self.tree("01")["base"], outside)

    def test_refuses_a_revision_that_does_not_descend_from_the_recorded_tip(self):
        git(self.repo, "checkout", "-q", "--orphan", "other")
        orphan = self.commit("orphan.txt")
        git(self.repo, "checkout", "-q", "main")
        before = self.files()
        result = self.plan_fails("target-tip", orphan, "--reason", "x")
        self.assertIn(f"does not descend from the recorded tip {self.tip}", result.err)
        self.assertEqual(self.files(), before)

    def test_refusals(self):
        git(self.repo, "checkout", "-q", "-b", "side")
        side = self.commit("side.txt")
        git(self.repo, "checkout", "-q", "main")
        self.assertIn("is not the tip of main or its ancestor", self.plan_fails("target-tip", side, "--reason", "x").err)
        self.assertIn("requires --reason", self.plan_fails("target-tip", side).err)
        self.assertIn("is not a commit", self.plan_fails("target-tip", "nope", "--reason", "x").err)
        self.assertIn("already the recorded tip", self.plan_fails("target-tip", self.tip, "--reason", "x").err)

    def test_force_accepts_a_rewritten_target(self):
        git(self.repo, "checkout", "-q", "--orphan", "fresh")
        rewritten = self.commit("fresh.txt")
        git(self.repo, "branch", "-f", "main", rewritten)
        git(self.repo, "checkout", "-q", "main")
        self.plan("target-tip", rewritten, "--force", "--reason", "history rewritten on purpose")
        self.assertEqual(self.state()["run"]["target_tip"], rewritten)
        self.assertIn("Overrode: revision", self.read("log.md"))


if __name__ == "__main__":
    unittest.main()
