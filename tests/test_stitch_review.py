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
REVIEW_CLI = os.path.join(REPO_ROOT, "skills", "stitch", "bin", "review")
STITCH_DIR = os.path.join(REPO_ROOT, "skills", "stitch")

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


class StitchReviewTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = self.tmp.name
        self.repo = os.path.join(self.root, "repo")
        os.makedirs(self.repo)
        self.xdg_config = os.path.join(self.root, "xdg-config")
        os.makedirs(self.xdg_config)

        self.fake_codex = os.path.join(self.root, "fake-codex")
        with open(self.fake_codex, "w", encoding="utf-8") as fh:
            fh.write(FAKE_CODEX_SCRIPT)
        os.chmod(self.fake_codex, os.stat(self.fake_codex).st_mode | stat.S_IXUSR)

        self.fake_state = os.path.join(self.root, "fake-codex-state.json")
        self.brief_file = os.path.join(self.root, "brief.md")
        with open(self.brief_file, "w", encoding="utf-8") as fh:
            fh.write("Goal: fix parser `$HOME` and `backticks` edge case.\nAcceptance:\n- handles empty input\n")
        self.base = self.init_git_repo()

    def set_fake_responses(self, responses: list[dict]) -> None:
        with open(self.fake_state, "w", encoding="utf-8") as fh:
            json.dump({"calls": [], "responses": responses}, fh)

    def get_fake_calls(self) -> list[dict]:
        with open(self.fake_state, "r", encoding="utf-8") as fh:
            return json.load(fh)["calls"]

    def make_env(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        env = {
            k: v
            for k, v in os.environ.items()
            if not k.startswith("STITCH_REVIEW_")
        }
        env["XDG_CONFIG_HOME"] = self.xdg_config
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

    def init_git_repo(self) -> str:
        if os.path.isdir(os.path.join(self.repo, ".git")):
            return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo, text=True).strip()
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.repo, check=True)
        tracked = os.path.join(self.repo, "app.py")
        with open(tracked, "w", encoding="utf-8") as fh:
            fh.write("x = 1\n")
        subprocess.run(["git", "add", "app.py"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=self.repo, check=True)
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo, text=True).strip()
        with open(tracked, "w", encoding="utf-8") as fh:
            fh.write("x = 2\n")
        return sha

    def test_config_precedence_and_validation(self) -> None:
        # 1. Built-in defaults
        res = self.run_cli("config")
        self.assertEqual(res.returncode, 0, res.stderr)
        data = json.loads(res.stdout)
        self.assertEqual(data["config"]["backend"], "codex")
        self.assertEqual(data["config"]["model"], "gpt-6.2-sol")
        self.assertEqual(data["config"]["effort"], "xhigh")
        self.assertEqual(data["config"]["thread_mode"], "resume")
        self.assertEqual(data["config"]["max_rounds"], 3)
        self.assertIsNone(data["config_path"])

        # 2. XDG config file overrides defaults
        xdg_file = os.path.join(self.xdg_config, "stitch", "review.json")
        os.makedirs(os.path.dirname(xdg_file), exist_ok=True)
        with open(xdg_file, "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "model": "file-model",
                    "effort": "high",
                    "thread_mode": "fresh",
                    "max_rounds": 4,
                    "codex": {"extra_args": ["--ephemeral"]},
                },
                fh,
            )

        res = self.run_cli("config")
        self.assertEqual(res.returncode, 0, res.stderr)
        data = json.loads(res.stdout)
        self.assertEqual(data["config"]["model"], "file-model")
        self.assertEqual(data["config"]["effort"], "high")
        self.assertEqual(data["config"]["thread_mode"], "fresh")
        self.assertEqual(data["config"]["max_rounds"], 4)
        self.assertEqual(data["config"]["codex"]["extra_args"], ["--ephemeral"])
        self.assertEqual(data["sources"]["model"], f"file:{xdg_file}")
        self.assertEqual(data["sources"]["thread_mode"], f"file:{xdg_file}")

        # 3. Env overrides file, CLI overrides env
        res = self.run_cli(
            "config",
            "--effort", "low",
            "--thread-mode", "fresh",
            env_extra={
                "STITCH_REVIEW_MODEL": "env-model",
                "STITCH_REVIEW_EFFORT": "medium",
                "STITCH_REVIEW_THREAD_MODE": "resume",
            },
        )
        self.assertEqual(res.returncode, 0, res.stderr)
        data = json.loads(res.stdout)
        self.assertEqual(data["config"]["model"], "env-model")
        self.assertEqual(data["sources"]["model"], "env:STITCH_REVIEW_MODEL")
        self.assertEqual(data["config"]["effort"], "low")
        self.assertEqual(data["sources"]["effort"], "cli")
        self.assertEqual(data["config"]["thread_mode"], "fresh")
        self.assertEqual(data["sources"]["thread_mode"], "cli")

        # Invalid thread_mode via env fails with exit 2
        bad_tm = self.run_cli("config", env_extra={"STITCH_REVIEW_THREAD_MODE": "invalid"})
        self.assertEqual(bad_tm.returncode, 2)
        self.assertEqual(bad_tm.stdout, "")
        self.assertIn("thread_mode", bad_tm.stderr)

        # 4. Unknown config key fails with exit 2 and empty stdout
        bad_cfg = os.path.join(self.root, "bad.json")
        with open(bad_cfg, "w", encoding="utf-8") as fh:
            json.dump({"effrot": "high"}, fh)
        res = self.run_cli("config", "--config", bad_cfg)
        self.assertEqual(res.returncode, 2)
        self.assertEqual(res.stdout, "")
        self.assertIn("effrot", res.stderr)

        # 5. Missing explicit config file fails with exit 2
        res = self.run_cli("config", "--config", os.path.join(self.root, "nope.json"))
        self.assertEqual(res.returncode, 2)
        self.assertEqual(res.stdout, "")

    def test_start_and_reply_codex_full_lifecycle_and_receipt(self) -> None:
        base = self.init_git_repo()
        # Add repo rules and an untracked file with space in name
        with open(os.path.join(self.repo, "AGENTS.md"), "w", encoding="utf-8") as fh:
            fh.write("Root rules\n")
        os.makedirs(os.path.join(self.repo, "pkg", "sub"), exist_ok=True)
        with open(os.path.join(self.repo, "pkg", "CLAUDE.md"), "w", encoding="utf-8") as fh:
            fh.write("Pkg rules\n")
        with open(os.path.join(self.repo, "pkg", "sub", "new file.py"), "w", encoding="utf-8") as fh:
            fh.write("print('hi')\n")

        self.set_fake_responses([
            {
                "jsonl": [
                    {"type": "thread.started", "thread_id": "thr-1"},
                    {"type": "turn.completed", "usage": {"input_tokens": 1000, "output_tokens": 120}},
                ],
                "output": (
                    "VERDICT: CHANGES\n"
                    "R1 [should] app.py:1 Missing validation. Fix: check empty input.\n"
                    "R2 [nit] app.py:1 Naming. Fix: rename x.\n"
                ),
            },
            {
                "jsonl": [
                    {"type": "thread.started", "thread_id": "thr-1"},
                    {"type": "turn.completed", "usage": {"input_tokens": 1400, "output_tokens": 180}},
                ],
                "output": "R1 resolved\nVERDICT: APPROVE\n",
            },
        ])

        session_dir = os.path.join(self.root, "session-1")
        res1 = self.run_cli(
            "start",
            "--repo", self.repo,
            "--base", base,
            "--brief-file", self.brief_file,
            "--owned-path", "app.py", "pkg/sub/new file.py",
            "--evidence", "pytest -> PASS",
            "--codex-bin", self.fake_codex,
            "--session-dir", session_dir,
        )
        self.assertEqual(res1.returncode, 0, res1.stderr)
        out1 = json.loads(res1.stdout)
        self.assertEqual(out1["status"], "ok")
        self.assertEqual(out1["round"], 1)
        self.assertEqual(out1["verdict"], "CHANGES")
        self.assertFalse(out1["nit_only"])
        self.assertEqual(out1["findings_summary"], {"blocker": 0, "should": 1, "nit": 1, "still_open": 0, "deferred": 0})
        self.assertEqual(out1["usage"], {"input_tokens": 1000, "output_tokens": 120})

        calls = self.get_fake_calls()
        self.assertEqual(len(calls), 1)
        argv1 = calls[0]["argv"]
        self.assertEqual(argv1[0], "exec")
        self.assertIn("-s", argv1)
        self.assertEqual(argv1[argv1.index("-s") + 1], "read-only")
        self.assertIn("-C", argv1)
        self.assertEqual(argv1[argv1.index("-C") + 1], os.path.abspath(self.repo))
        self.assertIn("-m", argv1)
        self.assertEqual(argv1[argv1.index("-m") + 1], "gpt-6.2-sol")
        self.assertIn("model_reasoning_effort=xhigh", argv1)
        self.assertTrue(calls[0]["stdin_eof"])

        # Prompt preserves verbatim brief ($HOME and backticks) + discovered rules + tracked/untracked split
        prompt1 = argv1[-1]
        self.assertIn("fix parser `$HOME` and `backticks` edge case.", prompt1)
        self.assertIn("Repo rules: AGENTS.md, pkg/CLAUDE.md", prompt1)
        self.assertIn(f"- git diff {base} -- app.py", prompt1)
        self.assertIn("- read untracked owned paths directly: pkg/sub/new file.py", prompt1)

        # Round 2 reply (adds a new test file)
        res2 = self.run_cli(
            "reply",
            "--session", session_dir,
            "--ledger", "R1 fixed: app.py:1 added validation; R2 declined: nit",
            "--changed-path", "app.py", "test_app.py",
            "--evidence", "pytest -> PASS (2 tests)",
        )
        self.assertEqual(res2.returncode, 0, res2.stderr)
        out2 = json.loads(res2.stdout)
        self.assertEqual(out2["status"], "ok")
        self.assertEqual(out2["round"], 2)
        self.assertEqual(out2["mode"], "resume")
        self.assertEqual(out2["verdict"], "APPROVE")

        calls = self.get_fake_calls()
        self.assertEqual(len(calls), 2)
        argv2 = calls[1]["argv"]
        self.assertEqual(argv2[:3], ["exec", "resume", "thr-1"])
        self.assertIn('sandbox_mode="read-only"', argv2)
        self.assertIn("test_app.py", argv2[-1])

        # Receipt aggregates usage and tracks merged owned_paths
        res_rcpt = self.run_cli("receipt", "--session", session_dir)
        self.assertEqual(res_rcpt.returncode, 0, res_rcpt.stderr)
        rcpt = json.loads(res_rcpt.stdout)
        self.assertEqual(rcpt["rounds_completed"], 2)
        self.assertEqual(rcpt["final_verdict"], "APPROVE")
        self.assertEqual(rcpt["usage_total"], {"input_tokens": 1400, "output_tokens": 180})
        self.assertTrue(rcpt["usage_complete"])
        self.assertIn("test_app.py", rcpt["owned_paths"])
        self.assertEqual(len(rcpt["response_paths"]), 2)

    def test_nit_only_and_verdict_parsing_edge_cases(self) -> None:
        # 1. Pure nit response -> nit_only=True
        self.set_fake_responses([
            {
                "jsonl": [{"type": "thread.started", "thread_id": "t1"}],
                "output": (
                    "**VERDICT: CHANGES**\n"
                    "R1 [nit] app.py:3 Minor style tweak. Fix: rename.\n"
                ),
            }
        ])
        res = self.run_cli(
            "start",
            "--repo", self.repo,
            "--base", self.base,
            "--brief-file", self.brief_file,
            "--owned-path", "app.py",
            "--evidence", "ok",
            "--codex-bin", self.fake_codex,
        )
        data = json.loads(res.stdout)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["verdict"], "CHANGES")
        self.assertTrue(data["nit_only"])

        # 2. Fenced code block mentioning VERDICT: APPROVE does NOT count as real verdict -> retries then fallback
        self.set_fake_responses([
            {"jsonl": [], "output": "```text\nVERDICT: APPROVE\n```\nNo actual verdict here.\n"},
            {"jsonl": [], "output": "VERDICT: APPROVE\nVERDICT: CHANGES\n"},
        ])
        res = self.run_cli(
            "start",
            "--repo", self.repo,
            "--base", self.base,
            "--brief-file", self.brief_file,
            "--owned-path", "app.py",
            "--evidence", "ok",
            "--codex-bin", self.fake_codex,
        )
        data = json.loads(res.stdout)
        self.assertEqual(data["status"], "fallback_needed")
        self.assertTrue(data["retried"])
        self.assertIn("missing VERDICT: line", data["fallback_reason"])
        self.assertIn("ambiguous output", data["fallback_reason"])

        # 3. Round 2 'still open' prevents nit_only even if no [blocker]/[should] tag repeated
        self.set_fake_responses([
            {
                "jsonl": [{"type": "thread.started", "thread_id": "t2"}],
                "output": "VERDICT: CHANGES\nR1 [blocker] app.py:1 Bad bug. Fix: fix.\n",
            },
            {
                "jsonl": [],
                "output": "R1 still open: still crashes on empty input\nR2 [nit] app.py:2 Minor. Fix: tidy.\nVERDICT: CHANGES\n",
            },
        ])
        s1 = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", "app.py", "--evidence", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        s2 = json.loads(
            self.run_cli("reply", "--session", s1["session"], "--ledger", "R1 fixed").stdout
        )
        self.assertEqual(s2["status"], "ok")
        self.assertFalse(s2["nit_only"])
        self.assertEqual(s2["findings_summary"]["still_open"], 1)

    def test_unavailable_errors_skip_retry_immediately(self) -> None:
        # 1. Missing binary -> immediate fallback_needed
        res = self.run_cli(
            "start",
            "--repo", self.repo,
            "--base", self.base,
            "--brief-file", self.brief_file,
            "--owned-path", "app.py",
            "--evidence", "ok",
            "--codex-bin", "/nonexistent/codex-missing",
        )
        self.assertEqual(res.returncode, 0, res.stderr)
        data = json.loads(res.stdout)
        self.assertEqual(data["status"], "fallback_needed")
        self.assertFalse(data["retried"])
        self.assertIn("not found", data["fallback_reason"])

        # 2. Unsupported model reported via nested JSONL error event -> unwrapped, no retry
        self.set_fake_responses([
            {
                "returncode": 1,
                "jsonl": [
                    {
                        "type": "error",
                        "message": json.dumps(
                            {
                                "type": "error",
                                "status": 400,
                                "error": {
                                    "type": "invalid_request_error",
                                    "message": "The 'gpt-99-sol' model is not supported.",
                                    "code": "model_not_found",
                                },
                            }
                        ),
                    }
                ],
                "stderr": "",
            }
        ])
        res = self.run_cli(
            "start",
            "--repo", self.repo,
            "--base", self.base,
            "--brief-file", self.brief_file,
            "--owned-path", "app.py",
            "--evidence", "ok",
            "--codex-bin", self.fake_codex,
        )
        data = json.loads(res.stdout)
        self.assertEqual(data["status"], "fallback_needed")
        self.assertFalse(data["retried"])
        self.assertEqual(
            data["fallback_reason"],
            "unsupported or rejected model: The 'gpt-99-sol' model is not supported. (400, model_not_found)",
        )
        self.assertEqual(len(self.get_fake_calls()), 1)

        # 3. Auth error on stderr -> no retry
        self.set_fake_responses([
            {"returncode": 1, "stderr": "Error: please run codex login (401 Unauthorized)\n"}
        ])
        res = self.run_cli(
            "start",
            "--repo", self.repo,
            "--base", self.base,
            "--brief-file", self.brief_file,
            "--owned-path", "app.py",
            "--evidence", "ok",
            "--codex-bin", self.fake_codex,
        )
        data = json.loads(res.stdout)
        self.assertEqual(data["status"], "fallback_needed")
        self.assertFalse(data["retried"])
        self.assertIn("authentication error", data["fallback_reason"])
        self.assertEqual(len(self.get_fake_calls()), 1)

    def test_transient_retry_archives_first_attempt_and_recovers(self) -> None:
        self.set_fake_responses([
            {"returncode": 0, "jsonl": [], "output": ""},  # empty output -> transient
            {
                "returncode": 0,
                "jsonl": [{"type": "thread.started", "thread_id": "thr-recovered"}],
                "output": "VERDICT: APPROVE\n",
            },
        ])
        session_dir = os.path.join(self.root, "session-retry")
        res = self.run_cli(
            "start",
            "--repo", self.repo,
            "--base", self.base,
            "--brief-file", self.brief_file,
            "--owned-path", "app.py",
            "--evidence", "ok",
            "--codex-bin", self.fake_codex,
            "--session-dir", session_dir,
        )
        data = json.loads(res.stdout)
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["retried"])
        self.assertEqual(data["verdict"], "APPROVE")
        self.assertEqual(len(self.get_fake_calls()), 2)
        self.assertTrue(os.path.isfile(os.path.join(session_dir, "r1-attempt1.md")))

    def test_resume_failure_falls_back_to_fresh_thread_and_updates_thread_id(self) -> None:
        self.set_fake_responses([
            {
                "jsonl": [{"type": "thread.started", "thread_id": "thr-old"}],
                "output": "VERDICT: CHANGES\nR1 [should] app.py:1 Bug. Fix: fix.\n",
            },
            # Round 2 resume fails transiently
            {"returncode": 1, "stderr": "session expired\n"},
            # Round 2 fresh fallback succeeds with new thread_id
            {
                "jsonl": [{"type": "thread.started", "thread_id": "thr-new"}],
                "output": "R1 still open: needs edge test\nVERDICT: CHANGES\n",
            },
            # Round 3 resumes thr-new
            {
                "jsonl": [],
                "output": "R1 resolved\nVERDICT: APPROVE\n",
            },
        ])
        session_dir = os.path.join(self.root, "session-resume-fb")
        r1 = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", "app.py", "--evidence", "ok", "--codex-bin", self.fake_codex,
                "--session-dir", session_dir,
            ).stdout
        )
        self.assertEqual(r1["status"], "ok")

        r2 = json.loads(
            self.run_cli("reply", "--session", session_dir, "--ledger", "R1 fixed: app.py:1").stdout
        )
        self.assertEqual(r2["status"], "ok")
        self.assertEqual(r2["mode"], "resume-fallback")
        self.assertTrue(r2["retried"])

        r3 = json.loads(
            self.run_cli("reply", "--session", session_dir, "--ledger", "R1 fixed: added test").stdout
        )
        self.assertEqual(r3["status"], "ok")
        self.assertEqual(r3["mode"], "resume")
        self.assertEqual(r3["verdict"], "APPROVE")

        calls = self.get_fake_calls()
        self.assertEqual(calls[1]["argv"][:3], ["exec", "resume", "thr-old"])
        self.assertEqual(calls[2]["argv"][0], "exec")
        self.assertNotEqual(calls[2]["argv"][1], "resume")
        # Combined prompt includes original Round 1 brief + Round 2 ledger
        self.assertIn("Brief (verbatim):", calls[2]["argv"][-1])
        self.assertIn("R1 fixed: app.py:1", calls[2]["argv"][-1])
        self.assertEqual(calls[3]["argv"][:3], ["exec", "resume", "thr-new"])

    def test_budget_exhaustion_and_extension(self) -> None:
        self.set_fake_responses([
            {"jsonl": [{"type": "thread.started", "thread_id": "t1"}], "output": "VERDICT: CHANGES\nR1 [blocker] a:1 x. Fix: y.\n"},
            {"jsonl": [], "output": "R1 still open: y\nVERDICT: CHANGES\n"},
            {"jsonl": [], "output": "R1 resolved\nVERDICT: APPROVE\n"},
        ])
        session_dir = os.path.join(self.root, "session-budget")
        r1 = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", "a.py", "--evidence", "ok", "--max-rounds", "2",
                "--codex-bin", self.fake_codex, "--session-dir", session_dir,
            ).stdout
        )
        self.assertEqual(r1["max_rounds"], 2)

        r2 = json.loads(self.run_cli("reply", "--session", session_dir, "--ledger", "R1 fixed").stdout)
        self.assertEqual(r2["round"], 2)

        # Round 3 blocked by budget without invoking codex
        r3_blocked = json.loads(self.run_cli("reply", "--session", session_dir, "--ledger", "R1 fixed").stdout)
        self.assertEqual(r3_blocked["status"], "budget_exhausted")
        self.assertEqual(len(self.get_fake_calls()), 2)

        # Extending past extended_max_rounds (5) is rejected with exit 2
        too_high = self.run_cli(
            "reply", "--session", session_dir, "--ledger", "R1 fixed",
            "--max-rounds", "99", "--extend-reason", "auth defect",
        )
        self.assertEqual(too_high.returncode, 2)
        self.assertEqual(too_high.stdout, "")
        self.assertIn("extended_max_rounds", too_high.stderr)

        # Extending without --extend-reason is rejected with exit 2
        no_reason = self.run_cli(
            "reply", "--session", session_dir, "--ledger", "R1 fixed",
            "--max-rounds", "5",
        )
        self.assertEqual(no_reason.returncode, 2)
        self.assertEqual(no_reason.stdout, "")
        self.assertIn("--extend-reason", no_reason.stderr)

        # Extending budget within limit with reason allows Round 3
        r3_ok = json.loads(
            self.run_cli(
                "reply", "--session", session_dir, "--ledger", "R1 fixed",
                "--max-rounds", "5", "--extend-reason", "auth defect",
            ).stdout
        )
        self.assertEqual(r3_ok["status"], "ok")
        self.assertEqual(r3_ok["round"], 3)
        self.assertEqual(r3_ok["max_rounds"], 5)
        self.assertEqual(r3_ok["verdict"], "APPROVE")

        # Lowering max_rounds is rejected
        bad = self.run_cli("reply", "--session", session_dir, "--ledger", "x", "--max-rounds", "3")
        self.assertEqual(bad.returncode, 2)
        self.assertEqual(bad.stdout, "")

    def test_retry_and_resume_fallback_retain_usage_in_receipt(self) -> None:
        self.set_fake_responses([
            # Round 1 attempt 1: missing VERDICT but exposed 100 tokens
            {
                "returncode": 0,
                "jsonl": [
                    {"type": "thread.started", "thread_id": "t-retry"},
                    {"type": "turn.completed", "usage": {"input_tokens": 100, "output_tokens": 10}},
                ],
                "output": "missing verdict line",
            },
            # Round 1 attempt 2: valid CHANGES with 20 tokens
            {
                "returncode": 0,
                "jsonl": [
                    {"type": "thread.started", "thread_id": "t-r1"},
                    {"type": "turn.completed", "usage": {"input_tokens": 20, "output_tokens": 5}},
                ],
                "output": "VERDICT: CHANGES\nR1 [should] a.py:1 bug. Fix: fix.\n",
            },
            # Round 2 resume fails after cumulative thread usage grows by 50 in / 4 out (20+50=70, 5+4=9)
            {
                "returncode": 0,
                "jsonl": [
                    {"type": "thread.started", "thread_id": "t-r1"},
                    {"type": "turn.completed", "usage": {"input_tokens": 70, "output_tokens": 9}},
                ],
                "output": "",
            },
            # Round 2 fresh fallback succeeds with 30 tokens
            {
                "returncode": 0,
                "jsonl": [
                    {"type": "thread.started", "thread_id": "t-r2"},
                    {"type": "turn.completed", "usage": {"input_tokens": 30, "output_tokens": 6}},
                ],
                "output": "R1 resolved\nVERDICT: APPROVE\n",
            },
        ])
        r1 = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", "a.py", "--evidence", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        self.assertEqual(r1["status"], "ok")
        self.assertTrue(r1["retried"])
        self.assertEqual(r1["usage"], {"input_tokens": 120, "output_tokens": 15})

        r2 = json.loads(
            self.run_cli("reply", "--session", r1["session"], "--ledger", "R1 fixed").stdout
        )
        self.assertEqual(r2["status"], "ok")
        self.assertEqual(r2["mode"], "resume-fallback")
        self.assertEqual(r2["usage"], {"input_tokens": 80, "output_tokens": 10})

        rcpt = json.loads(self.run_cli("receipt", "--session", r1["session"]).stdout)
        self.assertEqual(rcpt["usage_total"], {"input_tokens": 200, "output_tokens": 25})
        self.assertTrue(rcpt["usage_complete"])

        # Retry where attempt 1 omitted usage marks usage_complete=False
        self.set_fake_responses([
            {"returncode": 0, "jsonl": [], "output": ""},
            {
                "returncode": 0,
                "jsonl": [{"type": "turn.completed", "usage": {"input_tokens": 20}}],
                "output": "VERDICT: APPROVE\n",
            },
        ])
        r_partial = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", "a.py", "--evidence", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        rcpt_partial = json.loads(self.run_cli("receipt", "--session", r_partial["session"]).stdout)
        self.assertEqual(rcpt_partial["usage_total"], {"input_tokens": 20})
        self.assertFalse(rcpt_partial["usage_complete"])

        # Round 2 transient attempt with no usage followed by unavailable retry must mark usage_complete=False
        self.set_fake_responses([
            {
                "returncode": 0,
                "jsonl": [
                    {"type": "thread.started", "thread_id": "t-r1-u"},
                    {"type": "turn.completed", "usage": {"input_tokens": 500}},
                ],
                "output": "VERDICT: CHANGES\nR1 [should] a.py:1 bug. Fix: fix.\n",
            },
            # Round 2 resume: transient failure with no usage exposed
            {"returncode": 0, "jsonl": [], "output": ""},
            # Round 2 fresh fallback: unavailable failure with no usage exposed
            {"returncode": 1, "stderr": "Error: network is unreachable\n"},
        ])
        s_start = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", "a.py", "--evidence", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        s_reply = json.loads(
            self.run_cli("reply", "--session", s_start["session"], "--ledger", "R1 fixed").stdout
        )
        self.assertEqual(s_reply["status"], "fallback_needed")
        rcpt_mixed = json.loads(self.run_cli("receipt", "--session", s_start["session"]).stdout)
        self.assertEqual(rcpt_mixed["usage_total"], {"input_tokens": 500})
        self.assertFalse(rcpt_mixed["usage_complete"])

    def test_cumulative_codex_resume_usage_deltas_and_thread_switch(self) -> None:
        # Mirrors real codex exec / codex exec resume cumulative thread totals across 3 rounds
        self.set_fake_responses([
            {
                "jsonl": [
                    {"type": "thread.started", "thread_id": "thr-live"},
                    {"type": "turn.completed", "usage": {"input_tokens": 412666, "cached_input_tokens": 364672, "output_tokens": 2898}},
                ],
                "output": "VERDICT: CHANGES\nR1 [should] a.py:1 bug. Fix: fix.\n",
            },
            {
                "jsonl": [
                    {"type": "thread.started", "thread_id": "thr-live"},
                    {"type": "turn.completed", "usage": {"input_tokens": 710159, "cached_input_tokens": 646656, "output_tokens": 4049}},
                ],
                "output": "R1 still open: edge case\nVERDICT: CHANGES\n",
            },
            {
                "jsonl": [
                    {"type": "thread.started", "thread_id": "thr-live"},
                    {"type": "turn.completed", "usage": {"input_tokens": 956271, "cached_input_tokens": 887680, "output_tokens": 4420}},
                ],
                "output": "R1 resolved\nVERDICT: APPROVE\n",
            },
        ])
        r1 = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", "a.py", "--evidence", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        self.assertEqual(r1["usage"], {"input_tokens": 412666, "cached_input_tokens": 364672, "output_tokens": 2898})

        r2 = json.loads(self.run_cli("reply", "--session", r1["session"], "--ledger", "R1 fixed").stdout)
        self.assertEqual(r2["usage"], {"input_tokens": 297493, "cached_input_tokens": 281984, "output_tokens": 1151})

        r3 = json.loads(self.run_cli("reply", "--session", r1["session"], "--ledger", "R1 fixed edge").stdout)
        self.assertEqual(r3["usage"], {"input_tokens": 246112, "cached_input_tokens": 241024, "output_tokens": 371})

        rcpt = json.loads(self.run_cli("receipt", "--session", r1["session"]).stdout)
        self.assertEqual(
            rcpt["usage_total"],
            {"input_tokens": 956271, "cached_input_tokens": 887680, "output_tokens": 4420},
        )
        self.assertTrue(rcpt["usage_complete"])

    def test_thread_mode_fresh_and_reply_fresh_flag(self) -> None:
        # 1. --thread-mode fresh runs every round in a new codex exec thread and sums distinct thread usages
        self.set_fake_responses([
            {
                "jsonl": [
                    {"type": "thread.started", "thread_id": "t-fresh-1"},
                    {"type": "turn.completed", "usage": {"input_tokens": 1000, "output_tokens": 100}},
                ],
                "output": "VERDICT: CHANGES\nR1 [should] a.py:1 bug. Fix: fix.\n",
            },
            {
                "jsonl": [
                    {"type": "thread.started", "thread_id": "t-fresh-2"},
                    {"type": "turn.completed", "usage": {"input_tokens": 900, "output_tokens": 80}},
                ],
                "output": "R1 resolved\nVERDICT: APPROVE\n",
            },
        ])
        r1 = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", "a.py", "--evidence", "ok", "--thread-mode", "fresh",
                "--codex-bin", self.fake_codex,
            ).stdout
        )
        r2 = json.loads(self.run_cli("reply", "--session", r1["session"], "--ledger", "R1 fixed").stdout)
        self.assertEqual(r2["status"], "ok")
        self.assertEqual(r2["mode"], "fresh")
        self.assertEqual(r2["usage"], {"input_tokens": 900, "output_tokens": 80})

        calls = self.get_fake_calls()
        self.assertEqual(calls[1]["argv"][0], "exec")
        self.assertNotEqual(calls[1]["argv"][1], "resume")
        self.assertIn("Brief (verbatim):", calls[1]["argv"][-1])
        self.assertIn("R1 fixed", calls[1]["argv"][-1])

        rcpt = json.loads(self.run_cli("receipt", "--session", r1["session"]).stdout)
        self.assertEqual(rcpt["thread_mode"], "fresh")
        self.assertEqual(rcpt["usage_total"], {"input_tokens": 1900, "output_tokens": 180})

        # 2. --fresh on reply inside a resume session starts a new thread; next normal reply resumes the new thread
        self.set_fake_responses([
            {
                "jsonl": [
                    {"type": "thread.started", "thread_id": "t-a"},
                    {"type": "turn.completed", "usage": {"input_tokens": 500, "output_tokens": 50}},
                ],
                "output": "VERDICT: CHANGES\nR1 [should] a.py:1 bug. Fix: fix.\n",
            },
            {
                "jsonl": [
                    {"type": "thread.started", "thread_id": "t-b"},
                    {"type": "turn.completed", "usage": {"input_tokens": 400, "output_tokens": 40}},
                ],
                "output": "R1 still open: need test\nVERDICT: CHANGES\n",
            },
            {
                "jsonl": [
                    {"type": "thread.started", "thread_id": "t-b"},
                    {"type": "turn.completed", "usage": {"input_tokens": 650, "output_tokens": 65}},
                ],
                "output": "R1 resolved\nVERDICT: APPROVE\n",
            },
        ])
        s1 = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", "a.py", "--evidence", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        s2 = json.loads(
            self.run_cli("reply", "--session", s1["session"], "--ledger", "R1 fixed", "--fresh").stdout
        )
        self.assertEqual(s2["mode"], "fresh")
        self.assertEqual(s2["usage"], {"input_tokens": 400, "output_tokens": 40})

        s3 = json.loads(
            self.run_cli("reply", "--session", s1["session"], "--ledger", "R1 added test").stdout
        )
        self.assertEqual(s3["mode"], "resume")
        self.assertEqual(s3["usage"], {"input_tokens": 250, "output_tokens": 25})

        calls = self.get_fake_calls()
        self.assertNotEqual(calls[1]["argv"][1], "resume")
        self.assertEqual(calls[2]["argv"][:3], ["exec", "resume", "t-b"])

        rcpt2 = json.loads(self.run_cli("receipt", "--session", s1["session"]).stdout)
        self.assertEqual(rcpt2["thread_mode"], "resume")
        self.assertEqual(rcpt2["usage_total"], {"input_tokens": 1150, "output_tokens": 115})

    def test_malformed_command_templates_exit_2_without_traceback(self) -> None:
        bad_templates = [
            ["echo", "{unclosed"],
            ["echo", "{}"],
            ["echo", "{0}"],
            ["echo", "{unknown_placeholder}"],
            ["echo", "{model!z}"],
            ["echo", "{model.invalid}"],
            ["echo", "{model[0]}"],
            ["echo", "{model:d}"],
            [""],
            ["   ", "{prompt_file}"],
        ]
        for idx, tmpl in enumerate(bad_templates):
            cfg_path = os.path.join(self.root, f"bad-tmpl-{idx}.json")
            with open(cfg_path, "w", encoding="utf-8") as fh:
                json.dump({"backend": "command", "command": {"start": tmpl}}, fh)
            res = self.run_cli("config", "--config", cfg_path)
            self.assertEqual(res.returncode, 2, f"template {tmpl!r}: {res.stderr}")
            self.assertEqual(res.stdout, "")
            self.assertNotIn("Traceback", res.stderr)

    def test_hardening_fixes_for_all_review_findings(self) -> None:
        # #7: start --max-rounds above extended_max_rounds exits 2 unless ceiling is raised
        res_hi = self.run_cli("config", "--max-rounds", "6")
        self.assertEqual(res_hi.returncode, 2)
        self.assertEqual(res_hi.stdout, "")
        self.assertIn("extended_max_rounds", res_hi.stderr)
        res_ok_hi = self.run_cli("config", "--max-rounds", "6", env_extra={"STITCH_REVIEW_EXTENDED_MAX_ROUNDS": "6"})
        self.assertEqual(res_ok_hi.returncode, 0, res_ok_hi.stderr)

        # #8: codex.extra_args rejects sandbox/approval-weakening flags but allows safe flags
        forbidden_lists = [
            ["-s", "workspace-write"],
            ["--sandbox=danger-full-access"],
            ["--dangerously-bypass-approvals-and-sandbox"],
            ["--approve-for-me"],
            ["--add-dir", "/tmp"],
            ["-c", 'sandbox_mode="danger-full-access"'],
            ["-c", "profiles.dev.approval_policy=never"],
            ["-m", "other-model"],
        ]
        for idx, bad_args in enumerate(forbidden_lists):
            cfg_path = os.path.join(self.root, f"bad-extra-{idx}.json")
            with open(cfg_path, "w", encoding="utf-8") as fh:
                json.dump({"codex": {"extra_args": bad_args}}, fh)
            r_bad = self.run_cli("config", "--config", cfg_path)
            self.assertEqual(r_bad.returncode, 2, f"extra_args {bad_args!r}: {r_bad.stderr}")
            self.assertEqual(r_bad.stdout, "")

        safe_cfg = os.path.join(self.root, "safe-extra.json")
        with open(safe_cfg, "w", encoding="utf-8") as fh:
            json.dump({"codex": {"extra_args": ["--ephemeral", "--skip-git-repo-check"]}}, fh)
        self.assertEqual(self.run_cli("config", "--config", safe_cfg).returncode, 0)

        # #5a & #5b: contradictory APPROVE rejected; prose `still open` does not false-match; grouped IDs count
        self.set_fake_responses([
            {
                "jsonl": [],
                "output": "VERDICT: APPROVE\nR1 [blocker] app.py:1 Broken. Fix: fix.\n",
            },
            {
                "jsonl": [],
                "output": (
                    "VERDICT: CHANGES\n"
                    "R1 [blocker] app.py:1 Parser accepts APPROVE with a `still open` finding. Fix: reject.\n"
                ),
            },
        ])
        r_contra = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", "app.py", "--evidence", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        self.assertEqual(r_contra["status"], "ok")
        self.assertTrue(r_contra["retried"])
        self.assertEqual(r_contra["verdict"], "CHANGES")
        self.assertEqual(r_contra["findings_summary"], {"blocker": 1, "should": 0, "nit": 0, "still_open": 0, "deferred": 0})

        # #1 & #3: fresh follow-up includes prior findings text AND clears stale thread_id when none returned
        self.set_fake_responses([
            {
                "jsonl": [{"type": "thread.started", "thread_id": "t-stale"}],
                "output": "VERDICT: CHANGES\nR1 [should] app.py:9 Unique claim XYZ. Fix: patch.\n",
            },
            # Fresh reply returns NO thread_id -> must clear t-stale and include prior R1 finding text
            {
                "jsonl": [],
                "output": "- R1, R2, and R3 still open: pending\nVERDICT: CHANGES\n",
            },
            # Next normal reply must NOT resume t-stale because t-stale was cleared
            {
                "jsonl": [{"type": "thread.started", "thread_id": "t-clean"}],
                "output": "R1 resolved\nR2 [nit] app.py:1 tiny. Fix: tidy.\nVERDICT: APPROVE\n",
            },
        ])
        s1 = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", "app.py", "--evidence", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        s2 = json.loads(
            self.run_cli("reply", "--session", s1["session"], "--ledger", "R1 deferred", "--fresh").stdout
        )
        self.assertEqual(s2["status"], "ok")
        self.assertEqual(s2["mode"], "fresh")
        self.assertEqual(s2["findings_summary"]["still_open"], 3)

        s3 = json.loads(
            self.run_cli("reply", "--session", s1["session"], "--ledger", "R1 fixed").stdout
        )
        self.assertEqual(s3["status"], "ok")
        self.assertEqual(s3["mode"], "fresh")  # did not resume stale t-stale
        self.assertEqual(s3["verdict"], "APPROVE")

        calls = self.get_fake_calls()
        self.assertIn("Prior round findings:", calls[1]["argv"][-1])
        self.assertIn("Unique claim XYZ", calls[1]["argv"][-1])
        self.assertNotEqual(calls[2]["argv"][1], "resume")

        # #4: timeout preserves JSONL usage and classifies unavailable error without retrying
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
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", "app.py", "--evidence", "ok", "--timeout", "1",
                "--codex-bin", self.fake_codex,
            ).stdout
        )
        self.assertEqual(r_to["status"], "ok")
        self.assertTrue(r_to["retried"])
        self.assertEqual(r_to["usage"], {"input_tokens": 100})

        self.set_fake_responses([
            {
                "jsonl": [{"type": "error", "message": "401 Unauthorized"}],
                "sleep_after": 2,
            },
        ])
        r_to_unavail = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", "app.py", "--evidence", "ok", "--timeout", "1",
                "--codex-bin", self.fake_codex,
            ).stdout
        )
        self.assertEqual(r_to_unavail["status"], "fallback_needed")
        self.assertFalse(r_to_unavail["retried"])
        self.assertIn("authentication error", r_to_unavail["fallback_reason"])
        self.assertEqual(len(self.get_fake_calls()), 1)

        # #6, #9, #10: git base validation (commit + empty tree), ignored untracked owned file, literal pathspec, CRLF verbatim brief
        base = self.init_git_repo()
        with open(os.path.join(self.repo, ".gitignore"), "w", encoding="utf-8") as fh:
            fh.write("ignored.tmp\n")
        with open(os.path.join(self.repo, "ignored.tmp"), "w", encoding="utf-8") as fh:
            fh.write("owned ignored content\n")
        os.makedirs(os.path.join(self.repo, "src"), exist_ok=True)
        glob_file = os.path.join(self.repo, "src", "[id].py")
        with open(glob_file, "w", encoding="utf-8") as fh:
            fh.write("v = 1\n")
        subprocess.run(["git", "add", "src/[id].py"], cwd=self.repo, check=True)

        bad_base = self.run_cli(
            "start", "--repo", self.repo, "--base", "deadbeef0000", "--brief-file", self.brief_file,
            "--owned-path", "app.py", "--evidence", "ok", "--codex-bin", self.fake_codex,
        )
        self.assertEqual(bad_base.returncode, 2)
        self.assertEqual(bad_base.stdout, "")
        self.assertIn("--base", bad_base.stderr)

        crlf_brief = os.path.join(self.root, "crlf-brief.md")
        raw_brief = "Line 1\r\nLine 2\r\n\r\n"
        with open(crlf_brief, "w", encoding="utf-8", newline="") as fh:
            fh.write(raw_brief)

        empty_tree = subprocess.check_output(
            ["git", "hash-object", "-t", "tree", "/dev/null"], cwd=self.repo, text=True
        ).strip()
        self.set_fake_responses([{"jsonl": [], "output": "VERDICT: APPROVE\n"}])
        r_git = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", empty_tree, "--brief-file", crlf_brief,
                "--owned-path", "app.py", "src/[id].py", "ignored.tmp", "--evidence", "ok",
                "--codex-bin", self.fake_codex,
            ).stdout
        )
        self.assertEqual(r_git["status"], "ok")
        with open(os.path.join(r_git["session"], "brief.md"), "r", encoding="utf-8", newline="") as fh:
            self.assertEqual(fh.read(), raw_brief)
        with open(r_git["artifacts"]["prompt"], "r", encoding="utf-8", newline="") as fh:
            prompt_saved = fh.read()
        self.assertIn(raw_brief, prompt_saved)
        self.assertIn("read untracked owned paths directly: ignored.tmp", prompt_saved)
        self.assertIn(":(literal)src/[id].py", prompt_saved)

    def test_xhigh_round1_fixes(self) -> None:
        # R1: --yolo, --ignore-rules, and other hidden/unlisted flags are rejected by allowlist
        for idx, bad_args in enumerate([["--yolo"], ["--full-auto"], ["--ignore-rules"], ["-p", "dev"], ["--enable"]]):
            cfg_path = os.path.join(self.root, f"disallowed-{idx}.json")
            with open(cfg_path, "w", encoding="utf-8") as fh:
                json.dump({"codex": {"extra_args": bad_args}}, fh)
            res = self.run_cli("config", "--config", cfg_path)
            self.assertEqual(res.returncode, 2, f"extra_args {bad_args!r}: {res.stderr}")
            self.assertEqual(res.stdout, "")

        # R2 & R3: git rm --cached includes path in BOTH diff and untracked; leading space preserved
        leading = " lead.py"
        with open(os.path.join(self.repo, leading), "w", encoding="utf-8") as fh:
            fh.write("a = 1\n")
        subprocess.run(["git", "add", "--", leading], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "add leading"], cwd=self.repo, check=True)
        base_with_leading = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo, text=True).strip()
        subprocess.run(["git", "rm", "-q", "--cached", "--", leading], cwd=self.repo, check=True)

        self.set_fake_responses([{"jsonl": [], "output": "VERDICT: APPROVE\n"}])
        r_cached_rm = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", base_with_leading,
                "--brief-file", self.brief_file, "--owned-path", leading,
                "--evidence", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        self.assertEqual(r_cached_rm["status"], "ok")
        with open(r_cached_rm["artifacts"]["prompt"], encoding="utf-8") as fh:
            prompt_cached_rm = fh.read()
        self.assertIn(f"- git diff {base_with_leading} -- ' lead.py'", prompt_cached_rm)
        self.assertIn("- read untracked owned paths directly: ' lead.py'", prompt_cached_rm)

        # R4: non-git repo fails fast with exit 2
        non_git = os.path.join(self.root, "not-a-repo")
        os.makedirs(non_git)
        r_nongit = self.run_cli(
            "start", "--repo", non_git, "--base", self.base,
            "--brief-file", self.brief_file, "--owned-path", "a.py", "--evidence", "ok",
        )
        self.assertEqual(r_nongit.returncode, 2)
        self.assertEqual(r_nongit.stdout, "")

        # R5: numbered `1. R1 still open:` alongside VERDICT: APPROVE is rejected as contradictory
        self.set_fake_responses([
            {"jsonl": [], "output": "1. R1 still open: unaddressed\nVERDICT: APPROVE\n"},
            {"jsonl": [], "output": "1. R1 still open: unaddressed\nVERDICT: CHANGES\n"},
        ])
        r_num = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", "app.py", "--evidence", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        self.assertEqual(r_num["status"], "ok")
        self.assertTrue(r_num["retried"])
        self.assertEqual(r_num["verdict"], "CHANGES")
        self.assertEqual(r_num["findings_summary"]["still_open"], 1)

        # R6: structured turn.failed with generic outer message + inner unsupported model / code skips retry
        self.set_fake_responses([
            {
                "returncode": 1,
                "jsonl": [
                    {
                        "type": "turn.failed",
                        "message": "Request failed",
                        "error": {"message": "Unsupported model", "code": "model_not_found"},
                    }
                ],
            }
        ])
        r_tf = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", "app.py", "--evidence", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        self.assertEqual(r_tf["status"], "fallback_needed")
        self.assertFalse(r_tf["retried"])
        self.assertIn("Unsupported model", r_tf["fallback_reason"])
        self.assertIn("unsupported or rejected model", r_tf["fallback_reason"])
        self.assertEqual(len(self.get_fake_calls()), 1)

        # R6 (round 3): structured 401 status is preserved even when message contains substring 'req_401a'
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
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", "app.py", "--evidence", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        self.assertEqual(r_401["status"], "fallback_needed")
        self.assertFalse(r_401["retried"])
        self.assertIn("authentication error", r_401["fallback_reason"])
        self.assertIn("(401)", r_401["fallback_reason"])
        self.assertEqual(len(self.get_fake_calls()), 1)

        # R13: reply on a directory without state.json exits 2 and does NOT create .review.lock
        empty_dir = os.path.join(self.root, "not-a-session")
        os.makedirs(empty_dir)
        r_nosess = self.run_cli("reply", "--session", empty_dir, "--ledger", "x")
        self.assertEqual(r_nosess.returncode, 2)
        self.assertFalse(os.path.exists(os.path.join(empty_dir, ".review.lock")))

        # R7 & R10 & R11: fallback_needed is terminal for reply; lock blocks concurrent reply; extended_max_rounds exposed
        self.set_fake_responses([
            {
                "jsonl": [{"type": "thread.started", "thread_id": "t-term"}],
                "output": "VERDICT: CHANGES\nR1 [should] app.py:1 bug. Fix: fix.\n",
            },
            {"returncode": 1, "stderr": "401 Unauthorized\n"},
        ])
        r_ext = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", "app.py", "--evidence", "ok", "--codex-bin", self.fake_codex,
                env_extra={"STITCH_REVIEW_EXTENDED_MAX_ROUNDS": "4"},
            ).stdout
        )
        self.assertEqual(r_ext["extended_max_rounds"], 4)

        # R10: holding .review.lock causes concurrent reply to fail with exit 2
        lock_path = os.path.join(r_ext["session"], ".review.lock")
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            r_locked = self.run_cli("reply", "--session", r_ext["session"], "--ledger", "R1 fixed")
            self.assertEqual(r_locked.returncode, 2)
            self.assertIn("already running", r_locked.stderr)
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)

        # R7: reply fails -> fallback_needed; subsequent reply is rejected with exit 2 (0 extra calls)
        r_fb = json.loads(
            self.run_cli("reply", "--session", r_ext["session"], "--ledger", "R1 fixed").stdout
        )
        self.assertEqual(r_fb["status"], "fallback_needed")
        calls_before = len(self.get_fake_calls())
        r_after_fb = self.run_cli("reply", "--session", r_ext["session"], "--ledger", "R1 retry")
        self.assertEqual(r_after_fb.returncode, 2)
        self.assertEqual(r_after_fb.stdout, "")
        self.assertEqual(len(self.get_fake_calls()), calls_before)

        # R8: command backend with {output_file!s} prefers written response file over stdout
        cmd_runner = os.path.join(self.root, "out-file-conv.py")
        with open(cmd_runner, "w", encoding="utf-8") as fh:
            fh.write(
                "#!/usr/bin/env python3\n"
                "import sys\n"
                "open(sys.argv[1], 'w', encoding='utf-8').write('VERDICT: APPROVE\\n')\n"
                "print('noisy stdout without verdict')\n"
            )
        os.chmod(cmd_runner, os.stat(cmd_runner).st_mode | stat.S_IXUSR)
        conv_cfg = os.path.join(self.root, "conv-cfg.json")
        with open(conv_cfg, "w", encoding="utf-8") as fh:
            json.dump(
                {"backend": "command", "command": {"start": [sys.executable, cmd_runner, "{output_file!s}"]}},
                fh,
            )
        r_conv = json.loads(
            self.run_cli(
                "start", "--config", conv_cfg, "--repo", self.repo, "--base", self.base,
                "--brief-file", self.brief_file, "--owned-path", "app.py", "--evidence", "ok",
            ).stdout
        )
        self.assertEqual(r_conv["status"], "ok")
        self.assertEqual(r_conv["verdict"], "APPROVE")

        # R3: all-spaces filename is preserved rather than stripped/dropped
        spaces_name = "   "
        with open(os.path.join(self.repo, spaces_name), "w", encoding="utf-8") as fh:
            fh.write("spaces\n")
        self.set_fake_responses([{"jsonl": [], "output": "VERDICT: APPROVE\n"}])
        r_spaces = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", spaces_name, "--evidence", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        self.assertEqual(r_spaces["status"], "ok")
        self.assertEqual(
            json.loads(self.run_cli("receipt", "--session", r_spaces["session"]).stdout)["owned_paths"],
            [spaces_name],
        )
        with open(r_spaces["artifacts"]["prompt"], encoding="utf-8") as fh:
            self.assertIn("- read untracked owned paths directly: '   '", fh.read())

        # R12: Python 3.9 syntax compatibility check via AST
        for src_path in (REVIEW_CLI, os.path.abspath(__file__)):
            with open(src_path, "r", encoding="utf-8") as fh:
                ast.parse(fh.read(), filename=src_path, feature_version=(3, 9))

    def test_custom_command_backend_stdout_and_reply(self) -> None:
        runner = os.path.join(self.root, "custom-reviewer.py")
        with open(runner, "w", encoding="utf-8") as fh:
            fh.write(
                "#!/usr/bin/env python3\n"
                "import sys\n"
                "mode, prompt_file, out_file = sys.argv[1], sys.argv[2], sys.argv[3]\n"
                "prompt = open(prompt_file, encoding='utf-8').read()\n"
                "if mode == 'start':\n"
                "    assert 'Brief (verbatim):' in prompt\n"
                "    print('VERDICT: CHANGES')\n"
                "    print('R1 [should] app.py:1 Check bounds. Fix: clamp.')\n"
                "else:\n"
                "    assert 'R1 fixed' in prompt\n"
                "    open(out_file, 'w', encoding='utf-8').write('R1 resolved\\nVERDICT: APPROVE\\n')\n"
            )
        os.chmod(runner, os.stat(runner).st_mode | stat.S_IXUSR)

        cfg_path = os.path.join(self.root, "custom-config.json")
        with open(cfg_path, "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "backend": "command",
                    "model": "custom-model",
                    "effort": "high",
                    "command": {
                        "start": [sys.executable, runner, "start", "{prompt_file}", "{output_file}"],
                        "reply": [sys.executable, runner, "reply", "{prompt_file}", "{output_file}"],
                    },
                },
                fh,
            )

        r1 = json.loads(
            self.run_cli(
                "start", "--config", cfg_path, "--repo", self.repo, "--base", self.base,
                "--brief-file", self.brief_file, "--owned-path", "app.py", "--evidence", "ok",
            ).stdout
        )
        self.assertEqual(r1["status"], "ok")
        self.assertEqual(r1["backend"], "command")
        self.assertEqual(r1["verdict"], "CHANGES")
        self.assertIsNone(r1["usage"])

        r2 = json.loads(
            self.run_cli("reply", "--session", r1["session"], "--ledger", "R1 fixed: clamped").stdout
        )
        self.assertEqual(r2["status"], "ok")
        self.assertEqual(r2["mode"], "resume")
        self.assertEqual(r2["verdict"], "APPROVE")

        rcpt = json.loads(self.run_cli("receipt", "--session", r1["session"]).stdout)
        self.assertIsNone(rcpt["usage_total"])
        self.assertFalse(rcpt["usage_complete"])

    def test_custom_command_backend_without_reply_uses_combined_prompt(self) -> None:
        runner = os.path.join(self.root, "single-cmd.py")
        with open(runner, "w", encoding="utf-8") as fh:
            fh.write(
                "#!/usr/bin/env python3\n"
                "import sys\n"
                "prompt = open(sys.argv[1], encoding='utf-8').read()\n"
                "if 'Follow-up round:' in prompt:\n"
                "    assert 'Brief (verbatim):' in prompt\n"
                "    assert 'R1 fixed' in prompt\n"
                "    print('R1 resolved\\nVERDICT: APPROVE')\n"
                "else:\n"
                "    print('VERDICT: CHANGES\\nR1 [should] a.py:1 bug. Fix: patch.')\n"
            )
        os.chmod(runner, os.stat(runner).st_mode | stat.S_IXUSR)

        cfg_path = os.path.join(self.root, "single-cmd-config.json")
        with open(cfg_path, "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "backend": "command",
                    "command": {"start": [sys.executable, runner, "{prompt_file}"]},
                },
                fh,
            )

        r1 = json.loads(
            self.run_cli(
                "start", "--config", cfg_path, "--repo", self.repo, "--base", self.base,
                "--brief-file", self.brief_file, "--owned-path", "a.py", "--evidence", "ok",
            ).stdout
        )
        self.assertEqual(r1["verdict"], "CHANGES")

        r2 = json.loads(
            self.run_cli("reply", "--session", r1["session"], "--ledger", "R1 fixed").stdout
        )
        self.assertEqual(r2["status"], "ok")
        self.assertEqual(r2["mode"], "fresh")
        self.assertEqual(r2["verdict"], "APPROVE")

    def test_resume_unavailable_skips_fresh_thread_and_preserves_partial_usage(self) -> None:
        self.set_fake_responses([
            {
                "jsonl": [
                    {"type": "thread.started", "thread_id": "thr-1"},
                    {"type": "turn.completed", "usage": {"input_tokens": 500, "output_tokens": 50}},
                ],
                "output": "VERDICT: CHANGES\nR1 [should] a.py:1 Bug. Fix: fix.\n",
            },
            {
                "returncode": 1,
                "stderr": "Error: network is unreachable\n",
            },
        ])
        r1 = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", "a.py", "--evidence", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        r2 = json.loads(
            self.run_cli("reply", "--session", r1["session"], "--ledger", "R1 fixed").stdout
        )
        self.assertEqual(r2["status"], "fallback_needed")
        self.assertFalse(r2["retried"])
        self.assertIn("network or sandbox blocked", r2["fallback_reason"])
        self.assertEqual(len(self.get_fake_calls()), 2)  # no fresh-thread 3rd call

        rcpt = json.loads(self.run_cli("receipt", "--session", r1["session"]).stdout)
        self.assertEqual(rcpt["status"], "fallback_needed")
        self.assertEqual(rcpt["rounds_completed"], 1)
        self.assertEqual(rcpt["usage_total"], {"input_tokens": 500, "output_tokens": 50})
        self.assertTrue(rcpt["usage_complete"])

    def test_timeout_retries_and_rules_flags(self) -> None:
        with open(os.path.join(self.repo, "AGENTS.md"), "w", encoding="utf-8") as fh:
            fh.write("Root rules\n")

        self.set_fake_responses([
            {"sleep": 2, "output": "VERDICT: APPROVE\n"},
            {"jsonl": [{"type": "thread.started", "thread_id": "t-ok"}], "output": "VERDICT: APPROVE\n"},
        ])
        res = self.run_cli(
            "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
            "--owned-path", "a.py", "--evidence", "ok", "--timeout", "1",
            "--no-auto-rules", "--codex-bin", self.fake_codex,
        )
        data = json.loads(res.stdout)
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["retried"])
        self.assertIn("Repo rules: none found", self.get_fake_calls()[0]["argv"][-1])

        # --rule merges with auto-discovered rules; --no-auto-rules --rule uses only explicit rules
        self.set_fake_responses([
            {"jsonl": [], "output": "VERDICT: APPROVE\n"},
            {"jsonl": [], "output": "VERDICT: APPROVE\n"},
        ])
        self.run_cli(
            "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
            "--owned-path", "a.py", "--evidence", "ok", "--rule", "docs/RULES.md",
            "--codex-bin", self.fake_codex,
        )
        self.run_cli(
            "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
            "--owned-path", "a.py", "--evidence", "ok", "--no-auto-rules", "--rule", "docs/RULES.md",
            "--codex-bin", self.fake_codex,
        )
        calls = self.get_fake_calls()
        self.assertIn("Repo rules: AGENTS.md, docs/RULES.md", calls[0]["argv"][-1])
        self.assertIn("Repo rules: docs/RULES.md", calls[1]["argv"][-1])

        # Reply on a failed Round 1 session exits 2
        self.set_fake_responses([{"returncode": 1, "stderr": "401 Unauthorized\n"}])
        failed = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", "a.py", "--evidence", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        bad_reply = self.run_cli("reply", "--session", failed["session"], "--ledger", "x")
        self.assertEqual(bad_reply.returncode, 2)
        self.assertEqual(bad_reply.stdout, "")

    def test_input_validation_errors(self) -> None:
        # Session dir inside repo rejected
        inside = os.path.join(self.repo, "scratch")
        res = self.run_cli(
            "start", "--repo", self.repo, "--base", self.base,
            "--brief-file", self.brief_file, "--owned-path", "app.py",
            "--evidence", "ok", "--session-dir", inside,
        )
        self.assertEqual(res.returncode, 2)
        self.assertEqual(res.stdout, "")
        self.assertIn("outside the repository", res.stderr)

        # Duplicate stdin '-' rejected
        res = self.run_cli(
            "start", "--repo", self.repo, "--base", self.base,
            "--brief-file", "-", "--evidence-file", "-",
            "--owned-path", "app.py",
            stdin_text="hello",
        )
        self.assertEqual(res.returncode, 2)
        self.assertIn("stdin", res.stderr)

        # Stdin brief works when used once
        self.set_fake_responses([
            {"jsonl": [], "output": "VERDICT: APPROVE\n"},
        ])
        res = self.run_cli(
            "start", "--repo", self.repo, "--base", self.base,
            "--brief-file", "-", "--evidence", "ok",
            "--owned-path", "app.py", "--codex-bin", self.fake_codex,
            stdin_text="Brief from stdin\n",
        )
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("Brief from stdin", self.get_fake_calls()[0]["argv"][-1])

    def test_stitch_skill_docs_stay_aligned(self) -> None:
        self.assertFalse(os.path.exists(os.path.join(STITCH_DIR, "REVIEW.md")))
        for rel in ("SKILL.md", "WORKER.md", "FALLBACK.md", os.path.join("bin", "review")):
            self.assertTrue(os.path.isfile(os.path.join(STITCH_DIR, rel)), rel)

        with open(os.path.join(STITCH_DIR, "SKILL.md"), encoding="utf-8") as fh:
            skill_md = fh.read()
        with open(os.path.join(STITCH_DIR, "WORKER.md"), encoding="utf-8") as fh:
            worker_md = fh.read()
        with open(os.path.join(STITCH_DIR, "FALLBACK.md"), encoding="utf-8") as fh:
            fallback_md = fh.read()

        self.assertNotIn("REVIEW.md", skill_md)
        self.assertNotIn("REVIEW.md", worker_md)
        self.assertIn("bin/review", skill_md)
        self.assertIn("FALLBACK.md", skill_md)
        self.assertIn("bin/review", worker_md)
        self.assertIn("FALLBACK.md", worker_md)
        for token in ("VERDICT: APPROVE", "VERDICT: CHANGES", "blocker", "should", "nit", "deferred:"):
            self.assertIn(token, fallback_md)

    def test_deferred_status_and_resumed_contradiction_coercion(self) -> None:
        # 1. deferred / declined / [nit] still open allow clean APPROVE
        self.set_fake_responses([
            {
                "jsonl": [{"type": "thread.started", "thread_id": "t-def"}],
                "output": "VERDICT: CHANGES\nR1 [should] app.py:1 Bug. Fix: fix.\nR2 [should] app.py:2 Manual check.\n",
            },
            {
                "jsonl": [{"type": "thread.started", "thread_id": "t-def"}],
                "output": (
                    "R1 [should] resolved\n"
                    "R2 [should] deferred: manual sandbox check accepted\n"
                    "VERDICT: APPROVE\n"
                ),
            },
        ])
        r1 = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", "app.py", "--evidence", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        r2 = json.loads(
            self.run_cli("reply", "--session", r1["session"], "--ledger", "R1 fixed; R2 declined").stdout
        )
        self.assertEqual(r2["status"], "ok")
        self.assertFalse(r2["retried"])
        self.assertEqual(r2["verdict"], "APPROVE")
        self.assertEqual(r2["findings_summary"], {"blocker": 0, "should": 0, "nit": 0, "still_open": 0, "deferred": 1})

        # 2. Persistent contradictory APPROVE retries on same resumed thread then coerces conservatively to CHANGES
        self.set_fake_responses([
            {
                "jsonl": [
                    {"type": "thread.started", "thread_id": "t-c"},
                    {"type": "turn.completed", "usage": {"input_tokens": 500, "output_tokens": 50}},
                ],
                "output": "VERDICT: CHANGES\nR1 [blocker] app.py:1 Bug. Fix: fix.\n",
            },
            {
                "jsonl": [
                    {"type": "thread.started", "thread_id": "t-c"},
                    {"type": "turn.completed", "usage": {"input_tokens": 700, "output_tokens": 70}},
                ],
                "output": "R1 still open: unverified\nVERDICT: APPROVE\n",
            },
            {
                "jsonl": [
                    {"type": "thread.started", "thread_id": "t-c"},
                    {"type": "turn.completed", "usage": {"input_tokens": 800, "output_tokens": 80}},
                ],
                "output": "R1 still open: unverified\nVERDICT: APPROVE\n",
            },
        ])
        c1 = json.loads(
            self.run_cli(
                "start", "--repo", self.repo, "--base", self.base, "--brief-file", self.brief_file,
                "--owned-path", "app.py", "--evidence", "ok", "--codex-bin", self.fake_codex,
            ).stdout
        )
        c2 = json.loads(
            self.run_cli("reply", "--session", c1["session"], "--ledger", "R1 fixed").stdout
        )
        self.assertEqual(c2["status"], "ok")
        self.assertEqual(c2["mode"], "resume")
        self.assertTrue(c2["retried"])
        self.assertEqual(c2["verdict"], "CHANGES")
        self.assertTrue(c2["verdict_coerced"])
        self.assertIn("treated conservatively as CHANGES", c2["verdict_warning"])
        self.assertEqual(c2["usage"], {"input_tokens": 300, "output_tokens": 30})
        self.assertEqual(self.get_fake_calls()[2]["argv"][:3], ["exec", "resume", "t-c"])


if __name__ == "__main__":
    unittest.main()
