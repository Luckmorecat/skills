import json
import os
import unittest
from unittest import mock

from support import PlanTestCase, git, plan_cli

EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


class LifecycleTestCase(PlanTestCase):
    def setUp(self):
        super().setUp()
        self.init()
        self.plan("slice", "add", "01", "--file", "01-a.md", "--outcome", "first")
        self.plan("slice", "add", "02", "--file", "02-b.md", "--outcome", "second", "--blocked-by", "01:core")
        self.plan("slice", "add", "03", "--file", "03-c.md", "--outcome", "third")

    def slice_(self, sid):
        return self.state()["slices"][sid]

    def checkpoint(self, sid):
        return os.path.join(self.plan_dir, "checkpoints", f"{sid}.md")

    def head(self):
        return git(self.repo, "rev-parse", "HEAD")

    def write_checkpoint(self, sid, text):
        with open(self.checkpoint(sid), "w") as handle:
            handle.write(text)


class StartTest(LifecycleTestCase):
    def test_start_marks_in_progress_with_fixed_point_and_clean_snapshot(self):
        head = self.head()
        self.plan("start", "01")
        s = self.slice_("01")
        self.assertEqual((s["status"], s["fixed_point"], s["snapshot"]), ("in-progress", head, ""))
        self.assertIn("| 01 | 01-a.md | first | None | in-progress |", self.read("plan.md"))

    def test_start_records_porcelain_snapshot_unstripped(self):
        with open(os.path.join(self.repo, "file.txt"), "a") as handle:
            handle.write("more\n")
        with open(os.path.join(self.repo, "new.txt"), "w") as handle:
            handle.write("n\n")
        self.plan("start", "01")
        self.assertEqual(self.slice_("01")["snapshot"], " M file.txt\n?? new.txt\n")

    def test_start_creates_checkpoint_initialized_as_not_started(self):
        self.plan("start", "01")
        with open(self.checkpoint("01")) as handle:
            self.assertIn("Not started", handle.read())

    def test_start_keeps_an_existing_checkpoint(self):
        os.makedirs(os.path.join(self.plan_dir, "checkpoints"))
        self.write_checkpoint("01", "earlier notes\n")
        self.plan("start", "01")
        with open(self.checkpoint("01")) as handle:
            self.assertEqual(handle.read(), "earlier notes\n")

    def test_start_appends_a_dated_log_entry(self):
        head = self.head()
        self.plan("start", "01")
        log = self.read("log.md")
        self.assertRegex(log, r"## \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ — slice 01 started")
        self.assertIn(head, log)

    def test_start_in_unborn_repository_records_empty_tree(self):
        repo = os.path.join(self.tmp, "unborn")
        os.makedirs(repo)
        git(repo, "init", "-q")
        git(repo, "symbolic-ref", "HEAD", "refs/heads/main")
        plan_dir = os.path.join(self.tmp, "plan-unborn")
        self.assertEqual(self.run_plan("init", plan_dir, "--repo", repo, "--target", "main").code, 0)
        self.assertEqual(self.run_plan("slice", "add", "01", "--file", "f", "--outcome", "o",
                                       "--plan", plan_dir).code, 0)
        with open(os.path.join(repo, "a.txt"), "w") as handle:
            handle.write("a\n")
        result = self.run_plan("start", "01", "--plan", plan_dir)
        self.assertEqual(result.code, 0, result.err)
        with open(os.path.join(plan_dir, "state.json")) as handle:
            s = json.load(handle)["slices"]["01"]
        self.assertEqual((s["fixed_point"], s["snapshot"]), (EMPTY_TREE, "?? a.txt\n"))

    def test_start_refuses_a_slice_that_is_not_ready(self):
        self.plan("slice", "edit", "03", "--status", "blocked", "--reason", "waiting")
        result = self.plan_fails("start", "03")
        self.assertIn("slice 03 is blocked, not ready", result.err)
        self.assertIn("--force --reason", result.err)
        self.assertEqual(self.slice_("03")["status"], "blocked")
        self.assertFalse(os.path.exists(self.checkpoint("03")))

    def test_start_refuses_incomplete_dependencies(self):
        result = self.plan_fails("start", "02")
        self.assertIn("slice 02 depends on 01, which is ready, not complete", result.err)
        self.assertEqual(self.slice_("02")["status"], "ready")

    def test_start_refuses_while_another_slice_is_in_progress(self):
        self.plan("start", "01")
        result = self.plan_fails("start", "03")
        self.assertIn("slice 01 is already in progress in the repository checkout", result.err)
        self.assertEqual(self.slice_("03")["status"], "ready")
        self.assertFalse(os.path.exists(self.checkpoint("03")))

    def test_start_refuses_unknown_slice(self):
        self.assertIn("slice 42 does not exist", self.plan_fails("start", "42").err)

    def test_start_refuses_reason_without_force(self):
        result = self.plan_fails("start", "01", "--reason", "why")
        self.assertIn("--reason applies only with --force", result.err)

    def test_force_overrides_each_start_refusal_and_logs_the_reason(self):
        self.plan("start", "01")
        self.plan("slice", "edit", "03", "--status", "blocked", "--reason", "waiting")
        self.plan("start", "02", "--force", "--reason", "deps landed elsewhere")
        self.plan("start", "03", "--force", "--reason", "blocker resolved by hand")
        self.assertEqual(self.slice_("02")["status"], "in-progress")
        s = self.slice_("03")
        self.assertEqual((s["status"], s["reason"]), ("in-progress", None))
        log = self.read("log.md")
        for text in ("deps landed elsewhere", "blocker resolved by hand", "Overrode: slice 02 depends on 01",
                     "Overrode: slice 03 is blocked, not ready", "Overrode: slice 01 is already in progress"):
            self.assertIn(text, log)

    def test_start_failure_leaves_files_unchanged(self):
        before = {name: self.read(name) for name in ("state.json", "log.md", "plan.md")}
        os.mkdir(os.path.join(self.plan_dir, "state.json.tmp"))
        self.plan_fails("start", "01")
        self.assertEqual({name: self.read(name) for name in before}, before)
        self.assertFalse(os.path.exists(os.path.join(self.plan_dir, "checkpoints")))


class BlockResumeTest(LifecycleTestCase):
    def test_block_and_resume_a_started_slice_keep_its_fixed_point_and_snapshot(self):
        with open(os.path.join(self.repo, "dirty.txt"), "w") as handle:
            handle.write("d\n")
        self.plan("start", "01")
        started = self.slice_("01")
        self.commit("later.txt")
        self.plan("block", "01", "--reason", "needs a decision")
        s = self.slice_("01")
        self.assertEqual((s["status"], s["reason"]), ("blocked", "needs a decision"))
        self.assertEqual((s["fixed_point"], s["snapshot"]), (started["fixed_point"], started["snapshot"]))
        self.plan("resume", "01")
        s = self.slice_("01")
        self.assertEqual((s["status"], s["reason"]), ("in-progress", None))
        self.assertEqual((s["fixed_point"], s["snapshot"]), (started["fixed_point"], "?? dirty.txt\n"))

    def test_block_and_resume_an_unstarted_slice_returns_it_to_ready(self):
        self.plan("block", "03", "--reason", "waiting on API")
        self.assertEqual(self.slice_("03")["status"], "blocked")
        self.plan("resume", "03")
        s = self.slice_("03")
        self.assertEqual((s["status"], s["reason"], s["fixed_point"]), ("ready", None, None))

    def test_block_requires_reason(self):
        self.assertIn("--reason", self.plan_fails("block", "01").err)
        self.assertEqual(self.slice_("01")["status"], "ready")

    def test_block_and_resume_log_dated_entries(self):
        self.plan("start", "01")
        self.plan("block", "01", "--reason", "needs a decision")
        self.plan("resume", "01")
        log = self.read("log.md")
        self.assertRegex(log, r"## \S+Z — slice 01 blocked\n\nReason: needs a decision")
        self.assertRegex(log, r"## \S+Z — slice 01 resumed\n\nStatus: in-progress")

    def test_block_refuses_a_complete_or_blocked_slice(self):
        self.plan("slice", "edit", "03", "--status", "blocked", "--reason", "one")
        self.assertIn("slice 03 is blocked; only an in-progress or ready slice",
                      self.plan_fails("block", "03", "--reason", "two").err)
        self.plan("slice", "edit", "01", "--status", "complete", "--force", "--reason", "setup")
        self.assertIn("slice 01 is complete; only an in-progress or ready slice",
                      self.plan_fails("block", "01", "--reason", "x").err)

    def test_resume_refuses_a_slice_that_is_not_blocked(self):
        self.assertIn("slice 01 is ready, not blocked", self.plan_fails("resume", "01").err)

    def test_resume_refuses_while_another_slice_is_in_progress(self):
        self.plan("start", "01")
        self.plan("block", "01", "--reason", "pause")
        self.plan("start", "03")
        result = self.plan_fails("resume", "01")
        self.assertIn("slice 03 is already in progress in the repository checkout", result.err)
        self.plan("resume", "01", "--force", "--reason", "two at once")
        self.assertEqual(self.slice_("01")["status"], "in-progress")
        self.assertIn("two at once", self.read("log.md"))

    def test_force_overrides_block_refusal_and_logs_reason(self):
        self.plan("slice", "edit", "01", "--status", "complete", "--force", "--reason", "setup")
        self.plan("block", "01", "--force", "--reason", "regression found")
        s = self.slice_("01")
        self.assertEqual((s["status"], s["reason"]), ("blocked", "regression found"))
        self.assertIn("Overrode: slice 01 is complete", self.read("log.md"))


class CompleteTest(LifecycleTestCase):
    def setUp(self):
        super().setUp()
        self.fixed_point = self.head()
        self.plan("start", "01")

    def test_complete_records_landed_revision_folds_checkpoint_and_marks_complete(self):
        landed = self.commit("work.txt")
        self.write_checkpoint("01", "Owned changes: work.txt\nNext action: commit.\n")
        self.plan("complete", "01", "--rev", landed, "--evidence", "tests green under both interpreters")
        s = self.slice_("01")
        self.assertEqual((s["status"], s["landed"]), ("complete", [landed]))
        self.assertFalse(os.path.exists(self.checkpoint("01")))
        log = self.read("log.md")
        entry = log[log.index("— slice 01 complete"):]
        self.assertIn(landed, entry)
        self.assertIn("tests green under both interpreters", entry)
        self.assertIn("Owned changes: work.txt\nNext action: commit.", entry)
        self.assertIn("| 01 | 01-a.md | first | None | complete |", self.read("plan.md"))
        self.assertEqual([line.split("\t")[0] for line in self.plan("next").out.splitlines()], ["02", "03"])

    def test_complete_accepts_an_ancestor_of_the_target_tip_and_several_revisions(self):
        first = self.commit("a.txt")
        second = self.commit("b.txt")
        self.commit("c.txt")
        self.plan("complete", "01", "--rev", first[:10], "--rev", second, "--evidence", "ok")
        self.assertEqual(self.slice_("01")["landed"], [first, second])

    def test_complete_reads_evidence_from_a_file(self):
        landed = self.commit("work.txt")
        path = os.path.join(self.tmp, "evidence.md")
        with open(path, "w") as handle:
            handle.write("Ran 10 tests, OK\n")
        self.plan("complete", "01", "--rev", landed, "--evidence", "@" + path)
        self.assertIn("Ran 10 tests, OK", self.read("log.md"))

    def test_no_code_completion_uses_the_fixed_point(self):
        self.plan("complete", "01", "--rev", self.fixed_point, "--evidence", "experiment answered: no change needed")
        self.assertEqual(self.slice_("01")["landed"], [self.fixed_point])

    def test_no_code_completion_in_an_unborn_repository(self):
        repo = os.path.join(self.tmp, "unborn")
        os.makedirs(repo)
        git(repo, "init", "-q")
        git(repo, "symbolic-ref", "HEAD", "refs/heads/main")
        plan_dir = os.path.join(self.tmp, "plan-unborn")
        for argv in (("init", plan_dir, "--repo", repo, "--target", "main"),
                     ("slice", "add", "01", "--file", "f", "--outcome", "o", "--plan", plan_dir),
                     ("start", "01", "--plan", plan_dir),
                     ("complete", "01", "--rev", EMPTY_TREE, "--evidence", "nothing to build", "--plan", plan_dir)):
            result = self.run_plan(*argv)
            self.assertEqual(result.code, 0, (argv, result.err))
        with open(os.path.join(plan_dir, "state.json")) as handle:
            s = json.load(handle)["slices"]["01"]
        self.assertEqual((s["status"], s["landed"]), ("complete", [EMPTY_TREE]))

    def test_complete_refuses_a_revision_not_on_the_target_branch(self):
        git(self.repo, "checkout", "-q", "-b", "side")
        side = self.commit("side.txt")
        git(self.repo, "checkout", "-q", "main")
        result = self.plan_fails("complete", "01", "--rev", side, "--evidence", "ok")
        self.assertIn(f"revision {side} is not the tip of main or its ancestor", result.err)
        self.assertEqual(self.slice_("01")["status"], "in-progress")
        self.assertTrue(os.path.exists(self.checkpoint("01")))

    def test_complete_refuses_a_revision_git_cannot_resolve(self):
        result = self.plan_fails("complete", "01", "--rev", "no-such-rev", "--evidence", "ok")
        self.assertIn("revision no-such-rev is not a commit in", result.err)

    def test_complete_treats_an_option_like_revision_as_no_commit(self):
        result = self.plan_fails("complete", "01", "--rev=--all", "--evidence", "ok")
        self.assertIn("revision --all is not a commit in", result.err)

    def test_complete_refuses_empty_evidence(self):
        landed = self.commit("work.txt")
        self.assertIn("evidence is empty", self.plan_fails("complete", "01", "--rev", landed, "--evidence", " \n").err)
        path = os.path.join(self.tmp, "empty.md")
        open(path, "w").close()
        self.assertIn("evidence is empty", self.plan_fails("complete", "01", "--rev", landed,
                                                           "--evidence", "@" + path).err)
        self.assertEqual(self.slice_("01")["status"], "in-progress")

    def test_complete_reports_a_missing_evidence_file(self):
        landed = self.commit("work.txt")
        missing = os.path.join(self.tmp, "nope")
        result = self.plan_fails("complete", "01", "--rev", landed, "--evidence", "@" + missing)
        self.assertIn(f"cannot read evidence file {missing}", result.err)

    def test_complete_refuses_a_slice_that_is_not_in_progress(self):
        landed = self.commit("work.txt")
        result = self.plan_fails("complete", "03", "--rev", landed, "--evidence", "ok")
        self.assertIn("slice 03 is ready, not in-progress", result.err)
        self.assertEqual(self.slice_("03")["status"], "ready")

    def test_complete_requires_rev_and_evidence(self):
        self.assertIn("--rev", self.plan_fails("complete", "01", "--evidence", "ok").err)
        self.assertIn("--evidence", self.plan_fails("complete", "01", "--rev", self.fixed_point).err)

    def test_force_overrides_each_complete_refusal_and_logs_the_reason(self):
        git(self.repo, "checkout", "-q", "-b", "side")
        side = self.commit("side.txt")
        git(self.repo, "checkout", "-q", "main")
        self.plan("complete", "01", "--rev", side, "--evidence", "", "--force", "--reason", "landed via squash")
        self.plan("complete", "03", "--rev", "gone", "--evidence", "ok", "--force", "--reason", "rewritten")
        self.assertEqual(self.slice_("01")["landed"], [side])
        self.assertEqual((self.slice_("03")["status"], self.slice_("03")["landed"]), ("complete", ["gone"]))
        log = self.read("log.md")
        for text in ("landed via squash", "rewritten", "Overrode: evidence is empty",
                     f"Overrode: revision {side} is not the tip of main", "Overrode: slice 03 is ready",
                     "Overrode: revision gone is not a commit"):
            self.assertIn(text, log)

    def test_folded_checkpoint_headings_nest_under_the_slice_entry(self):
        landed = self.commit("work.txt")
        self.write_checkpoint("01", "# Checkpoint\n\n## Owned changes\n\n```\n# not a heading\n```\n")
        self.plan("complete", "01", "--rev", landed, "--evidence", "## Tests\nok")
        log = self.read("log.md")
        self.assertIn("\n### Checkpoint\n", log)
        self.assertIn("\n#### Owned changes\n", log)
        self.assertIn("\n# not a heading\n", log)
        self.assertIn("\n### Tests\n", log)
        self.assertNotIn("\n## Owned changes", log)

    def test_complete_without_a_checkpoint_file_notes_it(self):
        landed = self.commit("work.txt")
        os.remove(self.checkpoint("01"))
        self.plan("complete", "01", "--rev", landed, "--evidence", "ok")
        self.assertIn("No checkpoint file", self.read("log.md"))
        self.assertEqual(self.slice_("01")["status"], "complete")

    def test_complete_failure_keeps_checkpoint_and_log(self):
        landed = self.commit("work.txt")
        before = {name: self.read(name) for name in ("state.json", "log.md", "plan.md")}
        os.mkdir(os.path.join(self.plan_dir, "state.json.tmp"))
        self.plan_fails("complete", "01", "--rev", landed, "--evidence", "ok")
        self.assertEqual({name: self.read(name) for name in before}, before)
        self.assertTrue(os.path.exists(self.checkpoint("01")))

    def test_forced_failure_keeps_only_the_override_record(self):
        before = self.read("log.md")
        os.mkdir(os.path.join(self.plan_dir, "state.json.tmp"))
        self.plan_fails("complete", "01", "--rev", "gone", "--evidence", "ok", "--force", "--reason", "logged first")
        log = self.read("log.md")
        self.assertTrue(log.startswith(before))
        self.assertIn("logged first", log)
        self.assertNotIn("slice 01 complete", log)


class TargetTipTest(LifecycleTestCase):
    def setUp(self):
        super().setUp()
        self.recorded = self.state()["run"]["target_tip"]
        self.plan("start", "01")

    def test_complete_advances_the_recorded_tip_to_a_landed_live_tip(self):
        landed = self.commit("work.txt")
        self.plan("complete", "01", "--rev", landed, "--evidence", "ok")
        self.assertEqual(self.state()["run"]["target_tip"], landed)
        self.assertIn(f"Target tip: {self.recorded} -> {landed}", self.read("log.md"))

    def test_complete_keeps_the_recorded_tip_when_outside_commits_follow(self):
        landed = self.commit("work.txt")
        outside = self.commit("outside.txt")
        self.plan("complete", "01", "--rev", landed, "--evidence", "ok")
        self.assertEqual(self.state()["run"]["target_tip"], self.recorded)
        self.assertIn(f"Target tip: kept at {self.recorded}; the live tip {outside} holds commits", self.read("log.md"))

    def test_complete_keeps_the_recorded_tip_when_an_outside_commit_lands_mid_slice(self):
        self.commit("outside.txt")
        landed = self.commit("work.txt")
        self.plan("complete", "01", "--rev", landed, "--evidence", "ok")
        self.assertEqual(self.state()["run"]["target_tip"], self.recorded)

    def test_complete_advances_over_several_landed_commits_only_when_all_are_given(self):
        first = self.commit("a.txt")
        second = self.commit("b.txt")
        self.plan("complete", "01", "--rev", first, "--rev", second, "--evidence", "ok")
        self.assertEqual(self.state()["run"]["target_tip"], second)

    def test_complete_keeps_the_tip_when_a_slice_commit_is_not_given(self):
        self.commit("a.txt")
        second = self.commit("b.txt")
        self.plan("complete", "01", "--rev", second, "--evidence", "ok")
        self.assertEqual(self.state()["run"]["target_tip"], self.recorded)

    def test_back_to_back_slices_keep_the_tip_current(self):
        first = self.commit("a.txt")
        self.plan("complete", "01", "--rev", first, "--evidence", "ok")
        self.plan("start", "03")
        second = self.commit("b.txt")
        self.plan("complete", "03", "--rev", second, "--evidence", "ok")
        self.assertEqual(self.state()["run"]["target_tip"], second)

    def test_complete_keeps_the_recorded_tip_when_outside_commits_precede_the_start(self):
        self.plan("block", "01", "--reason", "pause")
        self.plan("slice", "edit", "01", "--status", "ready", "--force", "--reason", "restart later")
        self.commit("outside.txt")
        self.plan("start", "01")
        landed = self.commit("work.txt")
        self.plan("complete", "01", "--rev", landed, "--evidence", "ok")
        self.assertEqual(self.state()["run"]["target_tip"], self.recorded)

    def test_complete_keeps_the_recorded_tip_when_the_target_was_rewritten(self):
        git(self.repo, "checkout", "-q", "--orphan", "fresh")
        git(self.repo, "rm", "-q", "-rf", ".")
        rewritten = self.commit("new-root.txt")
        git(self.repo, "branch", "-f", "main", rewritten)
        git(self.repo, "checkout", "-q", "main")
        self.plan("complete", "01", "--rev", rewritten, "--evidence", "ok")
        self.assertEqual(self.state()["run"]["target_tip"], self.recorded)

    def test_complete_records_the_first_tip_of_an_unborn_target(self):
        repo = os.path.join(self.tmp, "unborn")
        os.makedirs(repo)
        git(repo, "init", "-q")
        git(repo, "symbolic-ref", "HEAD", "refs/heads/main")
        plan_dir = os.path.join(self.tmp, "plan-unborn")
        for argv in (("init", plan_dir, "--repo", repo, "--target", "main"),
                     ("slice", "add", "01", "--file", "f", "--outcome", "o", "--plan", plan_dir),
                     ("start", "01", "--plan", plan_dir)):
            self.assertEqual(self.run_plan(*argv).code, 0, argv)
        with open(os.path.join(repo, "a.txt"), "w") as handle:
            handle.write("a\n")
        git(repo, "add", "a.txt")
        git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "first")
        first = git(repo, "rev-parse", "HEAD")
        result = self.run_plan("complete", "01", "--rev", first, "--evidence", "ok", "--plan", plan_dir)
        self.assertEqual(result.code, 0, result.err)
        with open(os.path.join(plan_dir, "state.json")) as handle:
            self.assertEqual(json.load(handle)["run"]["target_tip"], first)

    def test_no_code_completion_leaves_the_tip_unchanged(self):
        self.plan("complete", "01", "--rev", self.head(), "--evidence", "no change")
        self.assertEqual(self.state()["run"]["target_tip"], self.recorded)
        self.assertIn(f"Target tip: {self.recorded} (unchanged)", self.read("log.md"))


class WriteFailureTest(LifecycleTestCase):
    def test_checkpoint_is_removed_even_when_the_status_block_write_fails(self):
        self.plan("start", "01")
        landed = self.commit("work.txt")
        with mock.patch.object(plan_cli, "write_plan_file", side_effect=OSError("disk full")):
            self.plan_fails("complete", "01", "--rev", landed, "--evidence", "ok")
        self.assertEqual(self.slice_("01")["status"], "complete")
        self.assertFalse(os.path.exists(self.checkpoint("01")))

    def test_a_partial_checkpoint_creation_leaves_nothing_behind(self):
        before = {name: self.read(name) for name in ("state.json", "log.md", "plan.md")}
        real = plan_cli.atomic_write

        def failing(path, text):
            if os.path.basename(path) == "01.md":
                raise OSError("disk full")
            real(path, text)

        with mock.patch.object(plan_cli, "atomic_write", side_effect=failing):
            self.plan_fails("start", "01")
        self.assertEqual({name: self.read(name) for name in before}, before)
        self.assertFalse(os.path.exists(os.path.join(self.plan_dir, "checkpoints")))

    def test_an_undeletable_checkpoint_is_noted_on_stderr(self):
        self.plan("start", "01")
        os.remove(self.checkpoint("01"))
        os.mkdir(self.checkpoint("01"))
        with open(os.path.join(self.checkpoint("01"), "keep"), "w"):
            pass
        result = self.plan("complete", "01", "--rev", self.head(), "--evidence", "ok")
        self.assertIn(f"plan: note: could not delete {self.checkpoint('01')}", result.err)
        self.assertEqual(self.slice_("01")["status"], "complete")

    def test_a_malformed_landed_field_is_refused_on_load(self):
        state = self.state()
        for bad in ("abc", [1], {}):
            state["slices"]["01"]["landed"] = bad
            with open(os.path.join(self.plan_dir, "state.json"), "w") as handle:
                json.dump(state, handle)
            self.assertIn("slices.01.landed must be a list of strings or null", self.plan_fails("status").err)


class ReopenTest(LifecycleTestCase):
    def test_reopening_a_complete_slice_clears_landed_and_recreates_its_checkpoint(self):
        self.plan("start", "01")
        self.plan("complete", "01", "--rev", self.head(), "--evidence", "ok")
        self.plan("block", "01", "--force", "--reason", "regression found")
        self.assertIsNone(self.slice_("01")["landed"])
        self.plan("resume", "01")
        s = self.slice_("01")
        self.assertEqual((s["status"], s["landed"]), ("in-progress", None))
        with open(self.checkpoint("01")) as handle:
            self.assertIn("Resumed with no checkpoint recorded", handle.read())
        self.assertIn("(created; none was recorded)", self.read("log.md"))

    def test_resume_keeps_an_existing_checkpoint(self):
        self.plan("start", "01")
        self.write_checkpoint("01", "progress\n")
        self.plan("block", "01", "--reason", "pause")
        self.plan("resume", "01")
        with open(self.checkpoint("01")) as handle:
            self.assertEqual(handle.read(), "progress\n")


class SliceEditReopenTest(LifecycleTestCase):
    def test_forced_edit_back_to_ready_clears_the_lifecycle_record(self):
        self.plan("start", "01")
        self.plan("complete", "01", "--rev", self.head(), "--evidence", "ok")
        self.plan("slice", "edit", "01", "--status", "ready", "--force", "--reason", "redo")
        s = self.slice_("01")
        self.assertEqual((s["status"], s["fixed_point"], s["snapshot"], s["landed"]), ("ready", None, None, None))
        self.plan("block", "01", "--reason", "pause")
        self.plan("resume", "01")
        self.assertEqual(self.slice_("01")["status"], "ready")

    def test_editing_a_blocked_started_slice_keeps_its_fixed_point_until_it_is_made_ready(self):
        self.plan("start", "01")
        self.plan("block", "01", "--reason", "pause")
        fixed = self.slice_("01")["fixed_point"]
        self.plan("slice", "edit", "01", "--reason", "new reason")
        self.assertEqual(self.slice_("01")["fixed_point"], fixed)
        self.plan("slice", "edit", "01", "--status", "ready")
        s = self.slice_("01")
        self.assertEqual((s["status"], s["fixed_point"], s["snapshot"]), ("ready", None, None))
        self.plan("block", "01", "--reason", "again")
        self.plan("resume", "01")
        self.assertEqual(self.slice_("01")["status"], "ready")


class StatusTest(LifecycleTestCase):
    def test_status_reports_fixed_point_and_checkpoint_of_blocked_started_slices(self):
        head = self.head()
        self.plan("start", "01")
        self.plan("block", "01", "--reason", "pause")
        self.plan("block", "03", "--reason", "waiting")
        checkpoint = os.path.join(os.path.abspath(self.plan_dir), "checkpoints", "01.md")
        view = json.loads(self.plan("status", "--json").out)
        self.assertEqual(view["blocked"], [
            {"id": "01", "reason": "pause", "fixed_point": head, "checkpoint": checkpoint, "worktree": None},
            {"id": "03", "reason": "waiting", "fixed_point": None, "checkpoint": None, "worktree": None},
        ])
        out = self.plan("status").out
        self.assertIn(f"01  pause  (fixed point {head}; checkpoint {checkpoint})", out)
        self.assertIn("03  waiting\n", out)

    def test_status_reports_fixed_point_and_checkpoint_of_in_progress_slices(self):
        head = self.head()
        self.plan("start", "01")
        checkpoint = os.path.join(os.path.abspath(self.plan_dir), "checkpoints", "01.md")
        view = json.loads(self.plan("status", "--json").out)
        self.assertEqual(view["in_progress"], [{"id": "01", "checkpoint": checkpoint, "fixed_point": head,
                                                "worktree": None}])
        self.assertIn(f"01  {checkpoint}  (fixed point {head})", self.plan("status").out)


if __name__ == "__main__":
    unittest.main()
