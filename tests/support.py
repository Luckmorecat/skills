import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN_PATH = os.path.join(REPO_ROOT, "skills", "slice", "bin", "plan")


def load_plan_module():
    loader = importlib.machinery.SourceFileLoader("plan_cli", PLAN_PATH)
    spec = importlib.util.spec_from_loader("plan_cli", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


plan_cli = load_plan_module()

GIT_ENV = dict(
    os.environ,
    GIT_CONFIG_NOSYSTEM="1",
    GIT_CONFIG_GLOBAL=os.devnull,
    GIT_AUTHOR_NAME="Test",
    GIT_AUTHOR_EMAIL="test@example.com",
    GIT_COMMITTER_NAME="Test",
    GIT_COMMITTER_EMAIL="test@example.com",
)


def git(repo, *args):
    result = subprocess.run(
        ["git", "-C", repo, *args],
        env=GIT_ENV,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


class Result:
    def __init__(self, code, out, err):
        self.code = code
        self.out = out
        self.err = err


class PlanTestCase(unittest.TestCase):
    """Builds a temporary Git repository and plan directory per test."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="plan-test-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.repo = os.path.realpath(os.path.join(self.tmp, "repo"))
        os.makedirs(self.repo)
        git(self.repo, "init", "-q")
        git(self.repo, "symbolic-ref", "HEAD", "refs/heads/main")
        self.plan_dir = os.path.join(self.tmp, "plan")

    def commit(self, name="file.txt", content="x\n"):
        with open(os.path.join(self.repo, name), "w") as handle:
            handle.write(content)
        git(self.repo, "add", name)
        git(self.repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "c")
        return git(self.repo, "rev-parse", "HEAD")

    def run_plan(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = plan_cli.main(list(argv))
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 1
        return Result(code, out.getvalue(), err.getvalue())

    def plan(self, *argv):
        """Runs a command against the test plan directory and expects success."""
        result = self.run_plan(*argv, "--plan", self.plan_dir)
        self.assertEqual(result.code, 0, result.err)
        return result

    def plan_fails(self, *argv):
        result = self.run_plan(*argv, "--plan", self.plan_dir)
        self.assertNotEqual(result.code, 0, result.out)
        return result

    def init(self, target="main"):
        self.commit()
        result = self.run_plan("init", self.plan_dir, "--repo", self.repo, "--target", target)
        self.assertEqual(result.code, 0, result.err)
        return result

    def run_executable(self, *argv, cwd=None, timeout=60):
        return subprocess.run(
            [sys.executable, PLAN_PATH, *argv],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    def state(self):
        with open(os.path.join(self.plan_dir, "state.json")) as handle:
            return json.load(handle)

    def read(self, name):
        with open(os.path.join(self.plan_dir, name)) as handle:
            return handle.read()

    def write(self, name, content):
        os.makedirs(self.plan_dir, exist_ok=True)
        with open(os.path.join(self.plan_dir, name), "w") as handle:
            handle.write(content)
