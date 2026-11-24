from __future__ import annotations

import ast
import fcntl
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SOL_LOOP_DIR = os.path.join(REPO_ROOT, "skills", "sol-loop")
REVIEW_CLI = os.path.join(SOL_LOOP_DIR, "bin", "review")

FAKE_CODEX_SCRIPT = """#!/usr/bin/env python3
import json
import os
import sys
import time

state_file = os.environ["FAKE_CODEX_STATE"]
with open(state_file, "r", encoding="utf-8") as fh:
    data = json.load(fh)

idx = len(data["calls"])
argv = sys.argv[1:]
output_path = None
for i, tok in enumerate(argv):
    if tok == "-o" and i + 1 < len(argv):
        output_path = argv[i + 1]
        break

data["calls"].append({
    "argv": argv,
    "cwd": os.getcwd(),
    "stdin_eof": sys.stdin.read() == "",
})

responses = data["responses"]
spec = responses[idx] if idx < len(responses) else responses[-1]

with open(state_file, "w", encoding="utf-8") as fh:
    json.dump(data, fh)

if spec.get("sleep"):
    time.sleep(spec["sleep"])

for event in spec.get("jsonl", []):
    sys.stdout.write(json.dumps(event) + "\\n")
if spec.get("raw_stdout"):
    sys.stdout.write(spec["raw_stdout"])
sys.stdout.flush()

if spec.get("stderr"):
    sys.stderr.write(spec["stderr"])
    sys.stderr.flush()

if output_path and "output" in spec and spec["output"] is not None:
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(spec["output"])

if spec.get("sleep_after"):
    time.sleep(spec["sleep_after"])

raise SystemExit(spec.get("returncode", 0))
"""


class SolLoopReviewTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = self.tmp.name
        self.repo = os.path.join(self.root, "repo")
        os.makedirs(self.repo)

        self.fake_codex = os.path.join(self.root, "fake-codex")
        with open(self.fake_codex, "w", encoding="utf-8") as fh:
            fh.write(FAKE_CODEX_SCRIPT)
        os.chmod(self.fake_codex, os.stat(self.fake_codex).st_mode | stat.S_IXUSR)

        self.fake_state = os.path.join(self.root, "fake-codex-state.json")
        self.base = self.init_git_repo()

    def init_git_repo(self) -> str:
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.repo, check=True)
        with open(os.path.join(self.repo, "app.py"), "w", encoding="utf-8") as fh:
            fh.write("def run():\n    return 1\n")
        subprocess.run(["git", "add", "app.py"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=self.repo, check=True)
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo, text=True).strip()

    def set_fake_responses(self, responses: list[dict]) -> None:
        with open(self.fake_state, "w", encoding="utf-8") as fh:
            json.dump({"calls": [], "responses": responses}, fh)

    def get_fake_calls(self) -> list[dict]:
        with open(self.fake_state, "r", encoding="utf-8") as fh:
            return json.load(fh)["calls"]

    def make_env(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        env = {k: v for k, v in os.environ.items() if not k.startswith("SOL_LOOP_")}
        env["FAKE_CODEX_STATE"] = self.fake_state
        if extra:
            env.update(extra)
        return env

    def run_cli(
        self,
        *args: str,
        env_extra: dict[str, str] | None = None,
        stdin_text: str | None = None,
        cwd: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, REVIEW_CLI, *args],
            cwd=cwd or self.root,
            env=self.make_env(env_extra),
            input=stdin_text,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

    def test_defaults_full_lifecycle_pinned_base_and_cumulative_usage(self) -> None:
        with open(os.path.join(self.repo, "app.py"), "w", encoding="utf-8") as fh:
            fh.write("def run():\n    return 2\n")
        with open(os.path.join(self.repo, "extra.py"), "w", encoding="utf-8") as fh:
            fh.write("x = 1\ny = 2\n")

        self.set_fake_responses([
            {
                "jsonl": [
                    {"type": "thread.started", "thread_id": "thr-sol-1"},
                    {"type": "turn.completed", "usage": {"input_tokens": 412666, "cached_input_tokens": 364672, "output_tokens": 2898}},
                ],
                "output": "VERDICT: CHANGES\nS1 [should] app.py:2 Check return value. Fix: return 3.\n",
            },
            {
                "jsonl": [
                    {"type": "thread.started", "thread_id": "thr-sol-1"},
                    {"type": "turn.completed", "usage": {"input_tokens": 710159, "cached_input_tokens": 646656, "output_tokens": 4049}},
                ],
                "output": "S1 still open: add regression test\nVERDICT: CHANGES\n",
            },
            {
                "jsonl": [
                    {"type": "thread.started", "thread_id": "thr-sol-1"},
                    {"type": "turn.completed", "usage": {"input_tokens": 956271, "cached_input_tokens": 887680, "output_tokens": 4420}},
                ],
                "output": "S1 resolved\nVERDICT: APPROVE\n",
            },
        ])

        # Pass mutable ref HEAD; CLI must pin it to the immutable SHA even if commits land before reply
        r1_proc = self.run_cli(
            "start",
            "--repo", self.repo,
            "--base", "HEAD",
            "--intent", "Fix `$HOME` and `backticks` edge case $(echo nope)",
            "--out-of-scope", "UI formatting",
            "--checks", "pytest: 3 passed",
            "--codex-bin", self.fake_codex,
        )
        self.assertEqual(r1_proc.returncode, 0, r1_proc.stderr)
        r1 = json.loads(r1_proc.stdout)
        self.assertEqual(r1["status"], "ok")
        self.assertEqual(r1["model"], "gpt-6.2-sol")
        self.assertEqual(r1["effort"], "xhigh")
        self.assertEqual(r1["verdict"], "CHANGES")
        self.assertEqual(r1["findings_summary"], {"blocker": 0, "should": 1, "nit": 0, "still_open": 0})
        self.assertEqual(r1["usage"], {"input_tokens": 412666, "cached_input_tokens": 364672, "output_tokens": 2898})
        self.assertEqual(r1["diff_stat"]["untracked_files"], 1)
        self.assertEqual(r1["diff_stat"]["untracked_lines"], 2)

        # Commit fix before Round 2 to verify pinned base SHA does not drift
        with open(os.path.join(self.repo, "app.py"), "w", encoding="utf-8") as fh:
            fh.write("def run():\n    return 3\n")
        subprocess.run(["git", "add", "app.py"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "fix return"], cwd=self.repo, check=True)

        r2 = json.loads(
            self.run_cli(
                "reply",
                "--session", r1["session"],
                "--ledger", "S1 fixed: return 3 in app.py:2",
                "--changed-path", "app.py",
                "--checks", "pytest: 3 passed",
            ).stdout
        )
        self.assertEqual(r2["status"], "ok")
        self.assertEqual(r2["mode"], "resume")
        self.assertEqual(r2["usage"], {"input_tokens": 297493, "cached_input_tokens": 281984, "output_tokens": 1151})

        with open(os.path.join(self.repo, "test_app.py"), "w", encoding="utf-8") as fh:
            fh.write("assert True\n")

        r3 = json.loads(
            self.run_cli(
                "reply",
                "--session", r1["session"],
                "--ledger", "S1 fixed: added test_app.py",
                "--changed-path", "test_app.py",
                "--checks", "pytest: 4 passed",
            ).stdout
        )
        self.assertEqual(r3["status"], "ok")
        self.assertEqual(r3["verdict"], "APPROVE")
        self.assertEqual(r3["usage"], {"input_tokens": 246112, "cached_input_tokens": 241024, "output_tokens": 371})

        calls = self.get_fake_calls()
        self.assertEqual(len(calls), 3)
        # Round 1: codex exec with -C, gpt-6.2-sol, xhigh, -s read-only, verbatim shell metacharacters
        argv1 = calls[0]["argv"]
        self.assertEqual(argv1[0], "exec")
        self.assertEqual(argv1[argv1.index("-C") + 1], os.path.abspath(self.repo))
        self.assertEqual(argv1[argv1.index("-m") + 1], "gpt-6.2-sol")
        self.assertIn("model_reasoning_effort=xhigh", argv1)
        self.assertEqual(argv1[argv1.index("-s") + 1], "read-only")
        self.assertTrue(calls[0]["stdin_eof"])
        self.assertEqual(os.path.realpath(calls[0]["cwd"]), os.path.realpath(self.repo))
        self.assertIn("Fix `$HOME` and `backticks` edge case $(echo nope)", argv1[-1])
        self.assertIn(f"- git diff {self.base}", argv1[-1])
        self.assertIn("- read untracked files directly: extra.py", argv1[-1])

        # Round 2 & 3: codex exec resume runs with cwd=repo and read-only sandbox_mode, keeping pinned base SHA
        argv2 = calls[1]["argv"]
        self.assertEqual(argv2[:3], ["exec", "resume", "thr-sol-1"])
        self.assertIn('sandbox_mode="read-only"', argv2)
        self.assertEqual(os.path.realpath(calls[1]["cwd"]), os.path.realpath(self.repo))
        self.assertIn(f"- git diff {self.base}", argv2[-1])
        self.assertIn("test_app.py", calls[2]["argv"][-1])

        rcpt = json.loads(self.run_cli("receipt", "--session", r1["session"]).stdout)
        self.assertEqual(rcpt["base"], self.base)
        self.assertEqual(rcpt["model"], "gpt-6.2-sol")
        self.assertEqual(rcpt["effort"], "xhigh")
        self.assertEqual(rcpt["rounds_completed"], 3)
        self.assertEqual(rcpt["final_verdict"], "APPROVE")
        self.assertEqual(
            rcpt["usage_total"],
            {"input_tokens": 956271, "cached_input_tokens": 887680, "output_tokens": 4420},
        )
        self.assertTrue(rcpt["usage_complete"])
        self.assertEqual(rcpt["initial_diff_stat"]["untracked_files"], 1)
        self.assertEqual(rcpt["final_diff_stat"]["untracked_files"], 2)

    def test_scoped_paths_isolate_unrelated_untracked_and_expand_on_reply(self) -> None:
        with open(os.path.join(self.repo, "app.py"), "w", encoding="utf-8") as fh:
            fh.write("def run():\n    return 9\n")
        with open(os.path.join(self.repo, "unrelated-dirty.txt"), "w", encoding="utf-8") as fh:
            fh.write("secret unrelated work\n")
        os.makedirs(os.path.join(self.repo, "src"), exist_ok=True)
        with open(os.path.join(self.repo, "src", "[id].py"), "w", encoding="utf-8") as fh:
            fh.write("id_val = 1\n")
        subprocess.run(["git", "add", "src/[id].py"], cwd=self.repo, check=True)
        with open(os.path.join(self.repo, "src", "AGENTS.md"), "w", encoding="utf-8") as fh:
            fh.write("Strict src rules\n")
        with open(os.path.join(self.repo, "CLAUDE.md"), "w", encoding="utf-8") as fh:
            fh.write("Root Claude rules\n")

        self.set_fake_responses([
            {
                "jsonl": [{"type": "thread.started", "thread_id": "t-scope"}],
                "output": "VERDICT: CHANGES\nS1 [blocker] app.py:2 Add test. Fix: add test_fix.py.\n",
            },
            {
                "jsonl": [{"type": "thread.started", "thread_id": "t-scope"}],
                "output": "S1 resolved\nVERDICT: APPROVE\n",
            },
        ])

        r1 = json.loads(
            self.run_cli(
                "start",
                "--repo", self.repo,
                "--base", self.base,
                "--intent", "Update app return",
                "--checks", "ok",
                "--path", "app.py", "src/[id].py",
                "--rule", "docs/CUSTOM.md",
                "--codex-bin", self.fake_codex,
            ).stdout
        )
        self.assertEqual(r1["status"], "ok")
        p1 = self.get_fake_calls()[0]["argv"][-1]
        self.assertNotIn("unrelated-dirty.txt", p1)
        self.assertIn(":(literal)src/[id].py", p1)
        self.assertIn("Repo rules: CLAUDE.md, src/AGENTS.md, docs/CUSTOM.md", p1)

        with open(os.path.join(self.repo, "test_fix.py"), "w", encoding="utf-8") as fh:
            fh.write("def test_run():\n    assert True\n")

        r2 = json.loads(
            self.run_cli(
                "reply",
                "--session", r1["session"],
                "--ledger", "S1 fixed: added test_fix.py",
                "--changed-path", "test_fix.py",
            ).stdout
        )
        self.assertEqual(r2["status"], "ok")
        p2 = self.get_fake_calls()[1]["argv"][-1]
        self.assertIn("read untracked scoped files directly: test_fix.py", p2)
        self.assertNotIn("unrelated-dirty.txt", p2)

        rcpt = json.loads(self.run_cli("receipt", "--session", r1["session"]).stdout)
        self.assertEqual(rcpt["scoped_paths"], ["app.py", "src/[id].py", "test_fix.py"])
        self.assertEqual(rcpt["initial_diff_stat"]["untracked_files"], 0)
        self.assertEqual(rcpt["final_diff_stat"]["untracked_files"], 1)

    def test_env_and_cli_override_precedence_and_validation(self) -> None:
        self.set_fake_responses([{"jsonl": [], "output": "VERDICT: APPROVE\n"}])
        r = json.loads(
            self.run_cli(
                "start",
                "--repo", self.repo,
                "--base", self.base,
                "--intent", "Check env",
                "--checks", "ok",
                "--effort", "high",
                env_extra={
                    "SOL_LOOP_MODEL": "gpt-6.3-sol",
                    "SOL_LOOP_EFFORT": "medium",
                    "SOL_LOOP_CODEX_BIN": self.fake_codex,
                },
            ).stdout
        )
        self.assertEqual(r["model"], "gpt-6.3-sol")
        self.assertEqual(r["effort"], "high")  # CLI beats env

        bad = self.run_cli(
            "start",
            "--repo", self.repo,
            "--base", self.base,
            "--intent", "Too many rounds",
            "--checks", "ok",
            "--max-rounds", "6",
        )
        self.assertEqual(bad.returncode, 2)
        self.assertIn("extended_max_rounds", bad.stderr)

    def test_verdict_parsing_nit_only_and_contradictions(self) -> None:
        # Nit-only CHANGES with clean formatting -> nit_only=True
        self.set_fake_responses([
            {
                "jsonl": [],
                "output": "VERDICT: CHANGES\nS1 [nit] app.py:1 Rename local var. Fix: rename.\n",
            },
        ])
        r_nit = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base,
                "--intent", "Nit test", "--checks", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        self.assertEqual(r_nit["status"], "ok")
        self.assertTrue(r_nit["nit_only"])

        # Contradictory APPROVE with numbered still-open finding -> retried once and recovers
        self.set_fake_responses([
            {"jsonl": [], "output": "1. S1, S2 still open: unresolved\nVERDICT: APPROVE\n"},
            {"jsonl": [], "output": "1. S1, S2 still open: unresolved\nVERDICT: CHANGES\n"},
        ])
        r_contra = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base,
                "--intent", "Contradiction", "--checks", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        self.assertEqual(r_contra["status"], "ok")
        self.assertTrue(r_contra["retried"])
        self.assertEqual(r_contra["verdict"], "CHANGES")
        self.assertEqual(r_contra["findings_summary"]["still_open"], 2)
        self.assertTrue(os.path.isfile(os.path.join(r_contra["session"], "r1-attempt1.md")))

        # Fenced VERDICT is ignored; real VERDICT outside fence succeeds
        self.set_fake_responses([
            {
                "jsonl": [],
                "output": "```text\nVERDICT: CHANGES\n```\nVERDICT: APPROVE\n",
            },
        ])
        r_fence = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base,
                "--intent", "Fence", "--checks", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        self.assertEqual(r_fence["status"], "ok")
        self.assertEqual(r_fence["verdict"], "APPROVE")

    def test_unavailable_errors_fail_fast_without_retry(self) -> None:
        # Missing binary
        r_missing = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base,
                "--intent", "Missing", "--checks", "ok",
                "--codex-bin", "/nonexistent/codex-bin",
            ).stdout
        )
        self.assertEqual(r_missing["status"], "blocked")
        self.assertTrue(r_missing["unavailable"])
        self.assertFalse(r_missing["retried"])

        # Structured 401 in turn.failed skips retry
        self.set_fake_responses([
            {
                "returncode": 1,
                "jsonl": [
                    {
                        "type": "turn.failed",
                        "status": 401,
                        "error": {"message": "Request failed (req_401a)"},
                    }
                ],
            }
        ])
        r_401 = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base,
                "--intent", "Auth fail", "--checks", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        self.assertEqual(r_401["status"], "blocked")
        self.assertTrue(r_401["unavailable"])
        self.assertFalse(r_401["retried"])
        self.assertIn("authentication error", r_401["blocker_reason"])
        self.assertEqual(len(self.get_fake_calls()), 1)

        # Unsupported model skips retry
        self.set_fake_responses([
            {
                "returncode": 1,
                "jsonl": [
                    {
                        "type": "turn.failed",
                        "error": {"message": "Model not found", "code": "model_not_found"},
                    }
                ],
            }
        ])
        r_model = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base,
                "--intent", "Bad model", "--checks", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        self.assertEqual(r_model["status"], "blocked")
        self.assertTrue(r_model["unavailable"])
        self.assertFalse(r_model["retried"])
        self.assertIn("unsupported or rejected model", r_model["blocker_reason"])
        self.assertEqual(len(self.get_fake_calls()), 1)

        # Terminal blocked session rejects reply
        bad_reply = self.run_cli("reply", "--session", r_model["session"], "--ledger", "retry")
        self.assertEqual(bad_reply.returncode, 2)

    def test_resume_fallback_includes_prior_findings_and_tracks_usage(self) -> None:
        self.set_fake_responses([
            {
                "jsonl": [
                    {"type": "thread.started", "thread_id": "t-r1"},
                    {"type": "turn.completed", "usage": {"input_tokens": 500, "output_tokens": 50}},
                ],
                "output": "VERDICT: CHANGES\nS1 [blocker] app.py:1 Unique claim ABC. Fix: patch.\n",
            },
            # Round 2 resume transient failure (empty output)
            {
                "returncode": 0,
                "jsonl": [{"type": "turn.completed", "usage": {"input_tokens": 600, "output_tokens": 60}}],
                "output": "",
            },
            # Round 2 fresh fallback succeeds with new thread ID
            {
                "jsonl": [
                    {"type": "thread.started", "thread_id": "t-r2-fresh"},
                    {"type": "turn.completed", "usage": {"input_tokens": 400, "output_tokens": 40}},
                ],
                "output": "S1 resolved\nVERDICT: APPROVE\n",
            },
        ])

        r1 = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base,
                "--intent", "Fix bug", "--checks", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        r2 = json.loads(
            self.run_cli("reply", "--session", r1["session"], "--ledger", "S1 fixed: patched").stdout
        )
        self.assertEqual(r2["status"], "ok")
        self.assertEqual(r2["mode"], "resume-fallback")
        self.assertTrue(r2["retried"])
        self.assertEqual(r2["verdict"], "APPROVE")
        # Resume attempt delta = 100/10, fresh attempt = 400/40 => round 2 = 500/50
        self.assertEqual(r2["usage"], {"input_tokens": 500, "output_tokens": 50})

        calls = self.get_fake_calls()
        self.assertEqual(len(calls), 3)
        self.assertIn("Prior round findings:", calls[2]["argv"][-1])
        self.assertIn("Unique claim ABC", calls[2]["argv"][-1])
        self.assertIn("S1 fixed: patched", calls[2]["argv"][-1])

        rcpt = json.loads(self.run_cli("receipt", "--session", r1["session"]).stdout)
        self.assertEqual(rcpt["usage_total"], {"input_tokens": 1000, "output_tokens": 100})
        self.assertTrue(rcpt["usage_complete"])

    def test_resume_unavailable_skips_fresh_fallback_and_preserves_usage(self) -> None:
        self.set_fake_responses([
            {
                "jsonl": [
                    {"type": "thread.started", "thread_id": "t-net"},
                    {"type": "turn.completed", "usage": {"input_tokens": 300, "output_tokens": 30}},
                ],
                "output": "VERDICT: CHANGES\nS1 [should] app.py:1 Bug. Fix: fix.\n",
            },
            {"returncode": 1, "stderr": "Error: network is unreachable\n"},
        ])
        r1 = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base,
                "--intent", "Net", "--checks", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        r2 = json.loads(
            self.run_cli("reply", "--session", r1["session"], "--ledger", "S1 fixed").stdout
        )
        self.assertEqual(r2["status"], "blocked")
        self.assertTrue(r2["unavailable"])
        self.assertFalse(r2["retried"])
        self.assertEqual(len(self.get_fake_calls()), 2)

        rcpt = json.loads(self.run_cli("receipt", "--session", r1["session"]).stdout)
        self.assertEqual(rcpt["usage_total"], {"input_tokens": 300, "output_tokens": 30})
        self.assertTrue(rcpt["usage_complete"])

    def test_fresh_flag_clears_stale_thread_and_budget_extension_and_lock(self) -> None:
        self.set_fake_responses([
            {
                "jsonl": [{"type": "thread.started", "thread_id": "t-old"}],
                "output": "VERDICT: CHANGES\nS1 [should] app.py:1 Auth bug. Fix: fix.\n",
            },
            # --fresh returns no thread_id -> must clear t-old
            {"jsonl": [], "output": "S1 still open: still broken\nVERDICT: CHANGES\n"},
            {"jsonl": [], "output": "S1 still open: check edge\nVERDICT: CHANGES\n"},
            {"jsonl": [], "output": "S1 resolved\nVERDICT: APPROVE\n"},
        ])
        r1 = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base,
                "--intent", "Auth fix", "--checks", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )

        # Session lock prevents concurrent reply
        lock_path = os.path.join(r1["session"], ".review.lock")
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            r_locked = self.run_cli("reply", "--session", r1["session"], "--ledger", "S1 fixed")
            self.assertEqual(r_locked.returncode, 2)
            self.assertIn("already running", r_locked.stderr)
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)

        r2 = json.loads(
            self.run_cli("reply", "--session", r1["session"], "--ledger", "S1 attempt", "--fresh").stdout
        )
        self.assertEqual(r2["mode"], "fresh")
        r3 = json.loads(
            self.run_cli("reply", "--session", r1["session"], "--ledger", "S1 attempt 2").stdout
        )
        self.assertEqual(r3["mode"], "fresh")  # did not resume stale t-old

        # Round 4 blocked at default budget 3
        r_exhaust = json.loads(
            self.run_cli("reply", "--session", r1["session"], "--ledger", "S1 attempt 3").stdout
        )
        self.assertEqual(r_exhaust["status"], "budget_exhausted")

        # Extending without --extend-reason exits 2
        bad_ext = self.run_cli(
            "reply", "--session", r1["session"], "--ledger", "S1 attempt 3", "--max-rounds", "5"
        )
        self.assertEqual(bad_ext.returncode, 2)
        self.assertIn("--extend-reason", bad_ext.stderr)

        # Extending with reason succeeds
        r4 = json.loads(
            self.run_cli(
                "reply", "--session", r1["session"], "--ledger", "S1 fixed auth",
                "--max-rounds", "5", "--extend-reason", "auth defect still open",
            ).stdout
        )
        self.assertEqual(r4["status"], "ok")
        self.assertEqual(r4["round"], 4)
        self.assertEqual(r4["verdict"], "APPROVE")

    def test_timeout_retry_and_input_validation(self) -> None:
        self.set_fake_responses([
            {
                "jsonl": [{"type": "turn.completed", "usage": {"input_tokens": 75}}],
                "sleep_after": 2,
            },
            {
                "jsonl": [{"type": "turn.completed", "usage": {"input_tokens": 25}}],
                "output": "VERDICT: APPROVE\n",
            },
        ])
        r_to = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base,
                "--intent", "Timeout test", "--checks", "ok",
                "--timeout", "1", "--codex-bin", self.fake_codex,
            ).stdout
        )
        self.assertEqual(r_to["status"], "ok")
        self.assertTrue(r_to["retried"])
        self.assertEqual(r_to["usage"], {"input_tokens": 100})

        # Empty tree base works
        empty_tree = subprocess.check_output(
            ["git", "hash-object", "-t", "tree", "/dev/null"], cwd=self.repo, text=True
        ).strip()
        self.set_fake_responses([{"jsonl": [], "output": "VERDICT: APPROVE\n"}])
        r_empty = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", empty_tree,
                "--intent-file", "-", "--checks", "ok", "--codex-bin", self.fake_codex,
                stdin_text="Initial commit review\n",
            ).stdout
        )
        self.assertEqual(r_empty["status"], "ok")
        self.assertEqual(r_empty["verdict"], "APPROVE")

        # Duplicate stdin rejected
        dup_stdin = self.run_cli(
            "start", "--repo", self.repo, "--base", self.base,
            "--intent-file", "-", "--checks-file", "-",
            stdin_text="x",
        )
        self.assertEqual(dup_stdin.returncode, 2)
        self.assertIn("stdin", dup_stdin.stderr)

        # Session dir inside repo rejected
        inside = self.run_cli(
            "start", "--repo", self.repo, "--base", self.base,
            "--intent", "x", "--checks", "ok", "--session-dir", os.path.join(self.repo, "scratch"),
        )
        self.assertEqual(inside.returncode, 2)
        self.assertIn("outside the repository", inside.stderr)

        # Invalid session dir does not create .review.lock
        empty_dir = os.path.join(self.root, "not-a-session")
        os.makedirs(empty_dir)
        no_sess = self.run_cli("reply", "--session", empty_dir, "--ledger", "x")
        self.assertEqual(no_sess.returncode, 2)
        self.assertFalse(os.path.exists(os.path.join(empty_dir, ".review.lock")))

    def test_git_rm_cached_and_python39_syntax_and_doc_alignment(self) -> None:
        # git rm --cached file appears in both diff and untracked scoped paths
        spaced = " lead.py"
        with open(os.path.join(self.repo, spaced), "w", encoding="utf-8") as fh:
            fh.write("a = 1\n")
        subprocess.run(["git", "add", "--", spaced], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "add spaced"], cwd=self.repo, check=True)
        base_sp = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo, text=True).strip()
        subprocess.run(["git", "rm", "-q", "--cached", "--", spaced], cwd=self.repo, check=True)

        self.set_fake_responses([{"jsonl": [], "output": "VERDICT: APPROVE\n"}])
        r_sp = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", base_sp,
                "--intent", "Untrack file", "--checks", "ok",
                "--path", spaced, "--codex-bin", self.fake_codex,
            ).stdout
        )
        self.assertEqual(r_sp["status"], "ok")
        prompt = self.get_fake_calls()[0]["argv"][-1]
        self.assertIn(f"- git diff {base_sp} -- ' lead.py'", prompt)
        self.assertIn("- read untracked scoped files directly: ' lead.py'", prompt)

        # Python 3.9 syntax check via AST
        for src_path in (REVIEW_CLI, os.path.abspath(__file__)):
            with open(src_path, "r", encoding="utf-8") as fh:
                ast.parse(fh.read(), filename=src_path, feature_version=(3, 9))

        # Skill docs alignment
        self.assertTrue(os.path.isfile(REVIEW_CLI))
        self.assertTrue(os.access(REVIEW_CLI, os.X_OK))
        with open(os.path.join(SOL_LOOP_DIR, "SKILL.md"), encoding="utf-8") as fh:
            skill_md = fh.read()
        with open(os.path.join(REPO_ROOT, "README.md"), encoding="utf-8") as fh:
            readme_md = fh.read()

        for token in ("bin/review", "gpt-6.2-sol", "xhigh", "blocked", "budget_exhausted", "receipt"):
            self.assertIn(token, skill_md)
        for stale in ("gpt-6.1-sol", "appease", "tl;dr", "model blurb"):
            self.assertNotIn(stale, skill_md)
        self.assertIn("gpt-6.2-sol", readme_md)
        self.assertIn("`sol-loop` runs a read-only GPT Sol review loop through its `bin/review` CLI", readme_md)


if __name__ == "__main__":
    unittest.main()
