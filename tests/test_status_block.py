import unittest

from support import PlanTestCase

START = "<!-- plan:status:start"
END = "<!-- plan:status:end -->"


class StatusBlockTest(PlanTestCase):
    ABOVE = "# Plan\n\n## Goal\n\nKeep | pipes and  spacing.\n\n## Slices\n\n"
    BELOW = "\n\n## Notes\n\nTrailing prose without newline"

    def outside(self, text):
        start, end = text.index(START), text.index(END) + len(END)
        return text[:start], text[end:]

    def test_prose_around_block_is_byte_identical_across_writes(self):
        self.init()
        before, _ = self.outside(self.read("plan.md"))
        self.write("plan.md", self.ABOVE + self.read("plan.md")[len(before):].rstrip("\n") + self.BELOW)
        self.plan("slice", "add", "01", "--file", "01-a.md", "--outcome", "Core | pipe")
        self.plan("slice", "add", "02", "--file", "02-b.md", "--outcome", "Next", "--blocked-by", "01:core")
        self.plan("slice", "edit", "02", "--status", "blocked", "--reason", "why")
        text = self.read("plan.md")
        self.assertEqual(self.outside(text), (self.ABOVE, self.BELOW))
        self.assertEqual(text.count(START), 1)
        self.assertEqual(text.count(END), 1)

    def test_block_reproduces_plan_format_table(self):
        self.init()
        self.plan("slice", "add", "01", "--file", "01-a.md", "--outcome", "Core | pipe")
        self.plan("slice", "add", "02", "--file", "02-b.md", "--outcome", "Next\nline", "--blocked-by", "01:core")
        text = self.read("plan.md")
        block = text[text.index(START):text.index(END) + len(END)].splitlines()
        self.assertIn("generated", block[0])
        self.assertIn("`plan`", block[0])
        self.assertEqual(block[1:], [
            "| ID | File | Outcome | Blocked by | Status |",
            "| --- | --- | --- | --- | --- |",
            "| 01 | 01-a.md | Core \\| pipe | None | ready |",
            "| 02 | 02-b.md | Next line | 01: core | ready |",
            END,
        ])

    def test_dependencies_render_with_what_they_supply(self):
        self.init()
        self.plan("slice", "add", "01", "--file", "a", "--outcome", "o")
        self.plan("slice", "add", "02", "--file", "b", "--outcome", "o")
        self.plan("slice", "add", "03", "--file", "c", "--outcome", "o", "--blocked-by", "01:model", "02")
        self.assertIn("| 03 | c | o | 01: model; 02 | ready |", self.read("plan.md"))

    def test_write_refuses_damaged_markers_and_changes_nothing(self):
        self.init()
        damaged = self.read("plan.md").replace(END, "")
        self.write("plan.md", damaged)
        state_before = self.read("state.json")
        result = self.plan_fails("slice", "add", "01", "--file", "a", "--outcome", "o")
        self.assertIn("status block", result.err)
        self.assertEqual(self.read("plan.md"), damaged)
        self.assertEqual(self.read("state.json"), state_before)

    def test_init_refuses_plan_with_two_blocks(self):
        self.commit()
        self.write("plan.md", f"{START} -->\n{END}\n{START} -->\n{END}\n")
        result = self.run_plan("init", self.plan_dir, "--repo", self.repo, "--target", "main")
        self.assertNotEqual(result.code, 0)


if __name__ == "__main__":
    unittest.main()
