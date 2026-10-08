import os
import unittest
from unittest import mock

from support import PlanTestCase, git, plan_cli

START = "<!-- plan:status:start"
END = "<!-- plan:status:end -->"

TABLE = """\
| ID | File | Outcome | Blocked by | Status |
| --- | --- | --- | --- | --- |
| 01 | 01-core.md | Core \\| state works | None | complete |
| 02 | 02-import.md | Import works | 01: state model, writer | in-progress |
| 03 | 03-life.md | Lifecycle | 01 | ready |
| 04 | 04-decide.md | Decisions | 02: import; 03: lifecycle | blocked |
| 05 | 05-migrate.md | Migrate `next-slice` | 02, 03, 04: every consumer | ready |
"""

ABOVE = """\
# Toy plan

## Goal

Ship | things  with  spacing.

## Repository

- Root: {repo}
- Remote: git@example.com:toy.git
- Branch: `main`; commits go directly to `main`.
- Planning revision: {rev}

## Slices

"""

BELOW = """\

## Notes

Trailing prose without newline"""

CHECKPOINT_BODY = """\
Active slice: 02 (Import works), in-progress since 2026-10-09.
- Fixed point: {rev} on `main`; pre-existing dirty snapshot:
  ```
   M file.txt
  ?? notes.txt
  ```
- Owned changes: skills/slice/bin/plan.
- Evidence: focused tests pass.
- Next action: finish the importer."""

HISTORY = """\
## History
- 2026-10-09: Plan created.
- 2026-10-09: Slice 01 complete at abc1234.
"""


def checkpoint_log(body):
    return f"# Log\n\n## Current checkpoint\n{body}\n\n{HISTORY}"


class ImportCase(PlanTestCase):
    def setUp(self):
        super().setUp()
        self.rev = self.commit()

    def write_plan(self, table=TABLE, above=None, below=BELOW, log=None, checkpoint=CHECKPOINT_BODY):
        above = ABOVE.format(repo=self.repo, rev=self.rev) if above is None else above
        self.write("plan.md", above + table + below)
        if log is None:
            log = checkpoint_log(checkpoint.format(rev=self.rev))
        self.write("log.md", log)

    def import_plan(self, *flags):
        result = self.run_plan("import", self.plan_dir, *flags)
        self.assertEqual(result.code, 0, result.err)
        return result

    def import_fails(self, *flags):
        result = self.run_plan("import", self.plan_dir, *flags)
        self.assertNotEqual(result.code, 0, result.out)
        return result

    def snapshot(self):
        files = {}
        for root, dirs, names in os.walk(self.plan_dir):
            for name in dirs + names:
                path = os.path.join(root, name)
                rel = os.path.relpath(path, self.plan_dir)
                if os.path.isdir(path):
                    files[rel + "/"] = None
                else:
                    with open(path, "rb") as handle:
                        files[rel] = handle.read()
        return files

    def table_lines(self, text):
        start = text.index("| ID | File |")
        return [line for line in text[start:].split("\n\n")[0].splitlines() if line.startswith("|")]


class ImportTableTest(ImportCase):
    def test_every_slice_outcome_dependency_and_status_is_preserved(self):
        self.write_plan()
        self.import_plan()
        slices = self.state()["slices"]
        self.assertEqual(sorted(slices), ["01", "02", "03", "04", "05"])
        self.assertEqual(slices["01"]["outcome"], "Core | state works")
        self.assertEqual(slices["05"]["outcome"], "Migrate `next-slice`")
        self.assertEqual(slices["05"]["file"], "05-migrate.md")
        self.assertEqual(
            {sid: s["status"] for sid, s in slices.items()},
            {"01": "complete", "02": "in-progress", "03": "ready", "04": "blocked", "05": "ready"},
        )
        self.assertEqual(slices["01"]["blocked_by"], [])
        self.assertEqual(slices["02"]["blocked_by"], [{"id": "01", "supplies": "state model, writer"}])
        self.assertEqual(slices["03"]["blocked_by"], [{"id": "01", "supplies": ""}])
        self.assertEqual(
            slices["04"]["blocked_by"],
            [{"id": "02", "supplies": "import"}, {"id": "03", "supplies": "lifecycle"}],
        )
        self.assertEqual(
            slices["05"]["blocked_by"],
            [{"id": d, "supplies": "every consumer"} for d in ("02", "03", "04")],
        )

    def test_status_matches_the_original_table(self):
        self.write_plan()
        self.import_plan()
        self.assertEqual(self.table_lines(self.plan("status").out), TABLE.splitlines())
        self.plan("validate")
        self.assertEqual(self.plan("next").out, "03\t03-life.md\tLifecycle\n")

    def test_table_is_replaced_by_the_status_block_and_prose_is_kept(self):
        self.write_plan()
        self.import_plan()
        text = self.read("plan.md")
        above = ABOVE.format(repo=self.repo, rev=self.rev)
        self.assertTrue(text.startswith(above + START), text)
        self.assertTrue(text.endswith(END + "\n" + BELOW), text)
        self.assertEqual(text.count(START), 1)
        self.assertEqual(text.count("| ID | File | Outcome | Blocked by | Status |"), 1)
        self.assertEqual(self.table_lines(text), TABLE.splitlines())

    def test_blocked_slice_gets_a_reason_pointing_at_its_file(self):
        self.write_plan()
        self.import_plan()
        reason = self.state()["slices"]["04"]["reason"]
        self.assertIn("04-decide.md", reason)
        self.assertIsNone(self.state()["slices"]["03"]["reason"])

    def test_dependency_lists_accept_and_and_file_links(self):
        table = (
            "| ID | File | Outcome | Blocked by | Status |\n"
            "|----|:-----|------|---|---|\n"
            "| 01 | [01-a.md](01-a.md) | A | None | ready |\n"
            "| 02 | `02-b.md` | B | none | ready |\n"
            "| 03 | 03-c.md | C | 01, 02 and 04: shared | ready |\n"
            "| 04 | 04-d.md | D | 01 | ready |\n"
        )
        self.write_plan(table=table)
        self.import_plan()
        slices = self.state()["slices"]
        self.assertEqual(slices["01"]["file"], "01-a.md")
        self.assertEqual(slices["02"]["file"], "02-b.md")
        self.assertEqual([d["id"] for d in slices["03"]["blocked_by"]], ["01", "02", "04"])
        self.assertEqual({d["supplies"] for d in slices["03"]["blocked_by"]}, {"shared"})

    def test_fences_follow_markdown_rules(self):
        decoy = TABLE.replace("| 02 |", "| 09 |")
        above = ABOVE.format(repo=self.repo, rev=self.rev) + (
            "````markdown\n```\n" + decoy + "```\n````\n\n"   # an inner ``` does not close ````
            "~~~\n" + decoy + "~~~ not a closer\n~~~\n\n"      # a closer takes no info string
            "    ```\n\n"                                       # four spaces of indent is not a fence
        )
        self.write_plan(above=above)
        self.import_plan()
        self.assertNotIn("09", self.state()["slices"])
        self.assertEqual(len(self.state()["slices"]), 5)

    def test_table_inside_a_code_fence_is_ignored(self):
        above = ABOVE.format(repo=self.repo, rev=self.rev) + "```markdown\n" + TABLE.replace("| 02 |", "| 09 |") + "```\n\n"
        self.write_plan(above=above)
        self.import_plan()
        self.assertNotIn("09", self.state()["slices"])
        self.assertIn("```markdown\n| ID | File |", self.read("plan.md"))

    def test_import_appends_a_log_entry_and_keeps_history(self):
        self.write_plan()
        self.import_plan()
        log = self.read("log.md")
        self.assertIn(HISTORY, log)
        self.assertIn("— imported by `plan import`", log)
        self.assertIn("Imported 5 slices", log)


class ImportRepositoryFactsTest(ImportCase):
    def test_repository_target_and_planning_revision_come_from_plan_md(self):
        self.write_plan()
        self.import_plan()
        state = self.state()
        self.assertEqual(state["repo"], self.repo)
        self.assertEqual(state["run"], {"target": "main", "target_tip": self.rev})
        self.assertEqual(state["planning_revision"], self.rev)

    def test_short_planning_revision_is_expanded(self):
        above = ABOVE.format(repo=self.repo, rev=self.rev[:8])
        self.write_plan(above=above)
        self.import_plan()
        self.assertEqual(self.state()["planning_revision"], self.rev)

    def test_planning_revision_written_as_a_name_is_kept_as_written(self):
        self.write_plan(above=ABOVE.format(repo=self.repo, rev="main"))
        self.import_plan()
        self.assertEqual(self.state()["planning_revision"], "main")

    def test_flags_supply_missing_facts(self):
        self.write_plan(above="# Plan\n\n")
        self.import_plan("--repo", self.repo, "--target", "main")
        state = self.state()
        self.assertEqual((state["repo"], state["run"]["target"]), (self.repo, "main"))
        self.assertIsNone(state["planning_revision"])

    def test_flags_override_plan_md(self):
        git(self.repo, "branch", "feature")
        above = ABOVE.format(repo=os.path.join(self.tmp, "gone"), rev="unborn")
        self.write_plan(above=above)
        self.import_plan("--repo", self.repo, "--target", "feature")
        state = self.state()
        self.assertEqual((state["repo"], state["run"]["target"]), (self.repo, "feature"))
        self.assertIsNone(state["planning_revision"])

    def test_bold_labels_and_target_branch_label_are_read(self):
        git(self.repo, "branch", "release")
        above = (f"# Plan\n\n**Repository root:** `{self.repo}`\n"
                 "- Branch: main\n- **Target branch**: `release` (worktree)\n\n")
        self.write_plan(above=above)
        self.import_plan()
        self.assertEqual((self.state()["repo"], self.state()["run"]["target"]), (self.repo, "release"))

    def test_refuses_when_neither_source_names_the_repository(self):
        self.write_plan(above="# Plan\n\n- Branch: `main`\n\n")
        before = self.snapshot()
        result = self.import_fails()
        self.assertIn("--repo", result.err)
        self.assertEqual(self.snapshot(), before)

    def test_refuses_when_neither_source_names_the_target(self):
        self.write_plan(above=f"# Plan\n\n- Root: {self.repo}\n\n")
        before = self.snapshot()
        result = self.import_fails()
        self.assertIn("--target", result.err)
        self.assertEqual(self.snapshot(), before)

    def test_refuses_a_target_branch_that_does_not_exist(self):
        self.write_plan()
        before = self.snapshot()
        result = self.import_fails("--target", "nope")
        self.assertIn("nope", result.err)
        self.assertEqual(self.snapshot(), before)


class ImportCheckpointTest(ImportCase):
    def test_checkpoint_naming_the_active_slice_moves_to_its_file(self):
        self.write_plan()
        self.import_plan()
        body = CHECKPOINT_BODY.format(rev=self.rev)
        self.assertEqual(self.read(os.path.join("checkpoints", "02.md")), body + "\n")
        log = self.read("log.md")
        self.assertNotIn("Current checkpoint", log)
        self.assertNotIn("Next action: finish the importer", log)
        self.assertTrue(log.startswith("# Log\n\n" + HISTORY), log)
        self.assertIn("checkpoints/02.md", log)

    def test_state_records_fixed_point_and_snapshot(self):
        self.write_plan()
        self.import_plan()
        slice_ = self.state()["slices"]["02"]
        self.assertEqual(slice_["fixed_point"], self.rev)
        self.assertEqual(slice_["snapshot"], " M file.txt\n?? notes.txt\n")
        self.assertIsNone(self.state()["slices"]["03"]["fixed_point"])
        self.assertIsNone(self.state()["slices"]["03"]["snapshot"])

    def test_short_fixed_point_is_expanded_and_clean_snapshot_is_empty(self):
        body = "Active slice: 02.\n- Fixed point: {short}; pre-existing dirty snapshot clean.\n- Next action: go."
        self.write_plan(log=checkpoint_log(body.format(short=self.rev[:7])))
        self.import_plan()
        slice_ = self.state()["slices"]["02"]
        self.assertEqual((slice_["fixed_point"], slice_["snapshot"]), (self.rev, ""))

    def test_inline_snapshot_in_backticks(self):
        body = "Slice 02 in progress.\n- Starting revision: `{rev}`\n- Dirty snapshot: `M a.txt`, `?? b.txt`"
        self.write_plan(log=checkpoint_log(body.format(rev=self.rev)))
        self.import_plan()
        self.assertEqual(self.state()["slices"]["02"]["snapshot"], "M a.txt\n?? b.txt\n")

    def test_checkpoint_naming_no_active_slice_stays_in_history(self):
        body = "No active slice. Slice 01 complete. Eligible next: 03."
        table = TABLE.replace("| in-progress |", "| ready |")
        self.write_plan(table=table, log=checkpoint_log(body))
        self.import_plan()
        self.assertFalse(os.path.exists(os.path.join(self.plan_dir, "checkpoints")))
        log = self.read("log.md")
        self.assertNotIn("## Current checkpoint", log)
        self.assertIn(body, log)
        self.assertIn(HISTORY, log)

    def test_in_progress_slice_without_a_checkpoint_is_noted(self):
        self.write_plan(log="# Log\n\n" + HISTORY)
        result = self.import_plan()
        self.assertIsNone(self.state()["slices"]["02"]["fixed_point"])
        self.assertIn("02", result.err)
        self.assertIn("fixed point", self.read("log.md"))

    def test_existing_checkpoint_file_is_kept_and_read(self):
        existing = "Worker checkpoint for 02.\n- Fixed point: {rev}\n- Dirty snapshot: clean\n".format(rev=self.rev)
        os.makedirs(os.path.join(self.plan_dir, "checkpoints"))
        self.write(os.path.join("checkpoints", "02.md"), existing)
        self.write_plan()
        self.import_plan()
        self.assertEqual(self.read(os.path.join("checkpoints", "02.md")), existing)
        self.assertEqual(self.state()["slices"]["02"]["fixed_point"], self.rev)
        self.assertIn("Next action: finish the importer", self.read("log.md"))

    def test_checkpoint_naming_two_started_slices_is_not_moved(self):
        table = TABLE.replace("| 03 | 03-life.md | Lifecycle | 01 | ready |",
                              "| 03 | 03-life.md | Lifecycle | 01 | in-progress |")
        body = "Run state: 02 in worktree a, 03 in worktree b."
        self.write_plan(table=table, log=checkpoint_log(body))
        result = self.import_plan()
        self.assertFalse(os.path.exists(os.path.join(self.plan_dir, "checkpoints")))
        self.assertIn(body, self.read("log.md"))
        self.assertIn("03", result.err)

    def test_slice_id_inside_dates_times_and_hashes_does_not_name_it(self):
        body = "Updated 2026-10-02 at 00:02 from a02b, see v1.02 and x-02."
        self.write_plan(log=checkpoint_log(body))
        self.import_plan()
        self.assertFalse(os.path.exists(os.path.join(self.plan_dir, "checkpoints")))
        self.assertIn(body, self.read("log.md"))

    def test_in_progress_slice_owns_a_checkpoint_that_mentions_a_blocked_one(self):
        body = "Active slice: 02.\n- Fixed point: {rev}\n- Snapshot: clean\n- 04 stays blocked on a decision."
        self.write_plan(log=checkpoint_log(body.format(rev=self.rev)))
        self.import_plan()
        self.assertIn("04 stays blocked", self.read(os.path.join("checkpoints", "02.md")))
        self.assertIsNone(self.state()["slices"]["04"]["fixed_point"])

    def test_words_that_look_like_hex_are_not_fixed_points(self):
        body = "Active slice: 02.\n- Fixed point: effaced, then {rev}\n- Owned changes: tests/snapshot_test.py\n"
        self.write_plan(log=checkpoint_log(body.format(rev=self.rev)))
        self.import_plan()
        slice_ = self.state()["slices"]["02"]
        self.assertEqual((slice_["fixed_point"], slice_["snapshot"]), (self.rev, None))

    def test_relative_repo_flag_resolves_against_the_current_directory(self):
        self.write_plan(above="# Plan\n\n")
        cwd = os.getcwd()
        self.addCleanup(os.chdir, cwd)
        os.chdir(self.tmp)
        self.import_plan("--repo", "repo", "--target", "main")
        self.assertEqual(self.state()["repo"], self.repo)

    def test_checkpoint_mentioning_a_blocked_unstarted_slice_stays_in_history(self):
        body = "No active slice. Slice 04 is blocked until the user answers R1."
        table = TABLE.replace("| in-progress |", "| ready |")
        self.write_plan(table=table, log=checkpoint_log(body))
        self.import_plan()
        self.assertFalse(os.path.exists(os.path.join(self.plan_dir, "checkpoints")))
        self.assertIn(body, self.read("log.md"))
        self.assertIsNone(self.state()["slices"]["04"]["fixed_point"])

    def test_slice_id_followed_by_a_colon_names_it(self):
        body = "Slice 02: halfway.\n- Fixed point: {rev}"
        self.write_plan(log=checkpoint_log(body.format(rev=self.rev)))
        self.import_plan()
        self.assertTrue(os.path.exists(os.path.join(self.plan_dir, "checkpoints", "02.md")))

    def test_existing_checkpoint_file_for_the_named_slice_is_noted(self):
        os.makedirs(os.path.join(self.plan_dir, "checkpoints"))
        self.write(os.path.join("checkpoints", "02.md"), "Worker notes.\n")
        self.write_plan()
        result = self.import_plan()
        self.assertIn("checkpoints/02.md already exists", result.err)

    def test_blocked_started_slice_gets_its_checkpoint(self):
        table = TABLE.replace("| in-progress |", "| ready |")
        body = "Slice 04 blocked after start.\n- Fixed point: {rev}\n- Snapshot: clean\n- Next action: ask."
        self.write_plan(table=table, log=checkpoint_log(body.format(rev=self.rev)))
        self.import_plan()
        self.assertIn("Next action: ask.", self.read(os.path.join("checkpoints", "04.md")))
        self.assertEqual(self.state()["slices"]["04"]["fixed_point"], self.rev)


class ImportRefusalTest(ImportCase):
    def assert_refused(self, *needles, flags=()):
        before = self.snapshot()
        result = self.import_fails(*flags)
        for needle in needles:
            self.assertIn(needle, result.err)
        self.assertEqual(self.snapshot(), before)
        if ".plan.lock" not in before:
            self.assertFalse(os.path.exists(os.path.join(self.plan_dir, ".plan.lock")))
        return result

    def test_refuses_when_state_json_exists(self):
        self.write_plan()
        self.assertEqual(self.run_plan("init", self.plan_dir, "--repo", self.repo, "--target", "main").code, 0)
        self.assert_refused("state.json")

    def test_refuses_without_a_slice_table(self):
        self.write_plan(table="No table here.\n")
        self.assert_refused("| ID | File | Outcome | Blocked by | Status |")

    def test_refuses_a_spine_plan_naming_it_unsupported(self):
        self.write("spine.md", "# Spine\n")
        self.write("map.md", "# Map\n")
        self.write("log.md", "# Log\n")
        self.assert_refused("spine.md", "not supported")

    def test_refuses_a_spine_plan_with_a_plan_md_but_no_table(self):
        self.write("spine.md", "# Spine\n")
        self.write_plan(table="")
        self.assert_refused("spine.md", "not supported")

    def test_refuses_unknown_status(self):
        self.write_plan(table=TABLE.replace("| ready |", "| done |", 1))
        self.assert_refused("unknown status 'done'")

    def test_refuses_missing_dependency(self):
        self.write_plan(table=TABLE.replace("| 01 | ready |", "| 07: thing | ready |"))
        self.assert_refused("03 is blocked by 07, which does not exist")

    def test_refuses_cycles(self):
        self.write_plan(table=TABLE.replace("| 01 | 01-core.md | Core \\| state works | None |",
                                            "| 01 | 01-core.md | Core \\| state works | 05 |"))
        self.assert_refused("dependency cycle: 01 -> 05 -> 02 -> 01")

    def test_refuses_colliding_and_duplicate_ids(self):
        self.write_plan(table=TABLE + "| 1 | x.md | X | None | ready |\n")
        self.assert_refused("slice IDs 01 and 1 collide")
        self.write_plan(table=TABLE + "| 03 | x.md | X | None | ready |\n")
        self.assert_refused("slice 03 is listed twice")

    def test_refuses_a_row_with_the_wrong_number_of_cells(self):
        self.write_plan(table=TABLE + "| 06 | x.md | X | ready |\n")
        self.assert_refused("4 cells")

    def test_refuses_an_unreadable_dependency(self):
        self.write_plan(table=TABLE.replace("| 01 | ready |", "| 01 (state model) | ready |"))
        self.assert_refused("01 (state model)", "ID: what it supplies")

    def test_refuses_a_dependency_listed_twice(self):
        self.write_plan(table=TABLE.replace("| 01 | ready |", "| 01: a; 01: b | ready |"))
        self.assert_refused("dependency 01 is listed twice")

    def test_refuses_two_slice_tables(self):
        self.write_plan(table=TABLE + "\n" + TABLE)
        self.assert_refused("2 slice tables")

    def test_refuses_a_plan_md_that_already_has_a_status_block(self):
        self.write_plan(table=TABLE + "\n" + START + " -->\n" + END + "\n")
        self.assert_refused("status block")

    def test_refuses_two_current_checkpoints(self):
        log = checkpoint_log(CHECKPOINT_BODY.format(rev=self.rev)) + "\n## Current checkpoint\nAgain 02.\n"
        self.write_plan(log=log)
        self.assert_refused("Current checkpoint")

    def test_refuses_missing_plan_directory_without_creating_it(self):
        missing = os.path.join(self.tmp, "missing")
        result = self.run_plan("import", missing)
        self.assertNotEqual(result.code, 0)
        self.assertFalse(os.path.exists(missing))

    def test_write_failure_restores_every_file(self):
        self.write_plan()
        before = self.snapshot()
        real = plan_cli.atomic_write
        calls = []

        def failing(path, text):
            calls.append(path)
            if path.endswith("state.json"):
                raise OSError("disk full")
            real(path, text)

        with mock.patch.object(plan_cli, "atomic_write", failing):
            result = self.import_fails()
        self.assertIn("disk full", result.err)
        self.assertGreaterEqual(len(calls), 4)
        self.assertEqual(self.snapshot(), before)
        self.assertNotIn(".plan.lock", self.snapshot())

    def test_refuses_a_checkpoints_path_that_is_a_file(self):
        self.write_plan()
        self.write("checkpoints", "not a directory\n")
        self.assert_refused("checkpoints", "not a directory")

    def test_failure_after_the_lock_keeps_a_lock_file_that_existed(self):
        self.write_plan()
        self.write(".plan.lock", "")
        before = self.snapshot()
        with mock.patch.object(plan_cli, "atomic_write", side_effect=OSError("disk full")):
            self.import_fails()
        self.assertEqual(self.snapshot(), before)


class ImportThenLifecycleTest(ImportCase):
    """An imported plan carries on through start, block, resume, and complete."""

    def test_imported_in_progress_slice_completes_with_its_checkpoint_folded(self):
        self.write_plan()
        self.import_plan()
        landed = self.commit("work.txt")
        self.plan("complete", "02", "--rev", landed, "--evidence", "suite green")
        self.assertEqual(self.state()["slices"]["02"]["status"], "complete")
        self.assertFalse(os.path.exists(os.path.join(self.plan_dir, "checkpoints", "02.md")))
        entry = self.read("log.md").split("— slice 02 complete", 1)[1]
        self.assertIn("Next action: finish the importer.", entry)
        self.assertIn(f"Fixed point: {self.rev}", entry)
        self.plan("start", "03")
        self.assertEqual(self.state()["slices"]["03"]["fixed_point"], landed)

    def test_imported_blocked_started_slice_resumes_in_progress(self):
        table = TABLE.replace("| in-progress |", "| ready |")
        body = "Slice 04 blocked after start.\n- Fixed point: {rev}\n- Snapshot: clean\n- Next action: ask."
        self.write_plan(table=table, log=checkpoint_log(body.format(rev=self.rev)))
        self.import_plan()
        self.commit("later.txt")
        self.plan("resume", "04")
        slice_ = self.state()["slices"]["04"]
        self.assertEqual((slice_["status"], slice_["fixed_point"], slice_["snapshot"]), ("in-progress", self.rev, ""))


class ImportCommandLineTest(ImportCase):
    def test_import_help_documents_flags_and_formats(self):
        result = self.run_executable("import", "--help")
        self.assertEqual(result.returncode, 0)
        for text in ("--repo", "--target", "| ID | File | Outcome | Blocked by | Status |",
                     "Current checkpoint", "checkpoints/<ID>.md", "spine.md", "Planning revision"):
            self.assertIn(text, result.stdout)

    def test_import_runs_as_an_executable(self):
        self.write_plan()
        result = self.run_executable("import", self.plan_dir)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Imported 5 slices", result.stdout)


if __name__ == "__main__":
    unittest.main()
