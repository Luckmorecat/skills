import os
import signal
import subprocess
import sys
import textwrap
import time
import unittest

from support import PLAN_PATH, PlanTestCase, plan_cli

ADD_LOOP = textwrap.dedent("""
    import importlib.machinery, importlib.util, sys
    loader = importlib.machinery.SourceFileLoader("plan_cli", {path!r})
    spec = importlib.util.spec_from_loader("plan_cli", loader)
    plan = importlib.util.module_from_spec(spec)
    loader.exec_module(plan)
    prefix, count, plan_dir = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    for n in range(count):
        code = plan.main(["slice", "add", f"{{prefix}}{{n}}", "--file", "f", "--outcome", "o", "--plan", plan_dir])
        if code:
            sys.exit(code)
""").format(path=PLAN_PATH)

# Loads the CLI, makes the final rename of state.json kill the process, then writes.
CRASH_ON_REPLACE = textwrap.dedent("""
    import importlib.machinery, importlib.util, os, signal, sys
    loader = importlib.machinery.SourceFileLoader("plan_cli", {path!r})
    spec = importlib.util.spec_from_loader("plan_cli", loader)
    plan = importlib.util.module_from_spec(spec)
    loader.exec_module(plan)
    real_replace = os.replace
    def crash(src, dst):
        if dst.endswith("state.json"):
            os.kill(os.getpid(), signal.SIGKILL)
        real_replace(src, dst)
    plan.os.replace = crash
    plan.main(["slice", "add", "99", "--file", "f", "--outcome", "o", "--plan", sys.argv[1]])
""").format(path=PLAN_PATH)

# Adds one slice, announcing on stdout when it is about to wait on the plan lock.
SIGNALLING_WRITER = textwrap.dedent("""
    import importlib.machinery, importlib.util, sys
    loader = importlib.machinery.SourceFileLoader("plan_cli", {path!r})
    spec = importlib.util.spec_from_loader("plan_cli", loader)
    plan = importlib.util.module_from_spec(spec)
    loader.exec_module(plan)
    real_flock = plan.fcntl.flock
    def announce(fd, op):
        print("waiting", flush=True)
        real_flock(fd, op)
    plan.fcntl.flock = announce
    sys.exit(plan.main(["slice", "add", "01", "--file", "f", "--outcome", "o", "--plan", sys.argv[1]]))
""").format(path=PLAN_PATH)

# Reads status --json without the lock until the stop file appears; fails on any unparsable read.
READ_LOOP = textwrap.dedent("""
    import contextlib, importlib.machinery, importlib.util, io, json, os, sys
    loader = importlib.machinery.SourceFileLoader("plan_cli", {path!r})
    spec = importlib.util.spec_from_loader("plan_cli", loader)
    plan = importlib.util.module_from_spec(spec)
    loader.exec_module(plan)
    plan_dir, stop = sys.argv[1], sys.argv[2]
    reads = 0
    while not os.path.exists(stop) or reads == 0:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = plan.main(["status", "--json", "--plan", plan_dir])
        if code:
            sys.exit(code)
        json.loads(out.getvalue())
        reads += 1
    print(reads)
""").format(path=PLAN_PATH)

# Takes the plan lock the way a writer does, reports it, then waits to be killed.
HOLD_LOCK = textwrap.dedent("""
    import fcntl, os, sys, time
    fd = os.open(os.path.join(sys.argv[1], ".plan.lock"), os.O_RDWR | os.O_CREAT)
    fcntl.flock(fd, fcntl.LOCK_EX)
    print("locked", flush=True)
    time.sleep(60)
""")


class ConcurrencyTest(PlanTestCase):
    def setUp(self):
        super().setUp()
        self.init()

    def test_concurrent_writers_both_succeed_without_losing_writes(self):
        count = 25
        stop = os.path.join(self.tmp, "stop")
        readers = [
            subprocess.Popen([sys.executable, "-c", READ_LOOP, self.plan_dir, stop],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for _ in range(2)
        ]
        writers = [
            subprocess.Popen([sys.executable, "-c", ADD_LOOP, prefix, str(count), self.plan_dir],
                             stderr=subprocess.PIPE, text=True)
            for prefix in ("a", "b")
        ]
        for writer in writers:
            _, err = writer.communicate(timeout=120)
            self.assertEqual(writer.returncode, 0, err)
        open(stop, "w").close()
        for reader in readers:
            out, err = reader.communicate(timeout=60)
            self.assertEqual(reader.returncode, 0, err)
            self.assertGreater(int(out), 0)
        expected = {f"{p}{n}" for p in ("a", "b") for n in range(count)}
        self.assertEqual(set(self.state()["slices"]), expected)
        plan = self.read("plan.md")
        self.assertTrue(all(f"| {sid} |" in plan for sid in expected))
        self.plan("validate")

    def test_writer_waits_for_lock_then_succeeds(self):
        holder = subprocess.Popen([sys.executable, "-c", HOLD_LOCK, self.plan_dir], stdout=subprocess.PIPE, text=True)
        self.addCleanup(holder.kill)
        self.assertEqual(holder.stdout.readline().strip(), "locked")
        writer = subprocess.Popen([sys.executable, "-c", SIGNALLING_WRITER, self.plan_dir],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(writer.stdout.readline().strip(), "waiting")
        time.sleep(0.2)
        self.assertIsNone(writer.poll(), "writer must wait while the lock is held")
        self.assertNotIn("01", self.state()["slices"])
        holder.kill()
        holder.wait()
        _, err = writer.communicate(timeout=30)
        self.assertEqual(writer.returncode, 0, err)
        self.assertIn("01", self.state()["slices"])

    def test_writer_waiting_on_a_deleted_lock_file_retries_on_the_new_one(self):
        lock_path = os.path.join(self.plan_dir, ".plan.lock")
        with plan_cli.locked(self.plan_dir):
            writer = subprocess.Popen([sys.executable, "-c", SIGNALLING_WRITER, self.plan_dir],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.assertEqual(writer.stdout.readline().strip(), "waiting")
            time.sleep(0.2)
            os.remove(lock_path)
        self.assertEqual(writer.stdout.readline().strip(), "waiting", "writer must retry on the new lock file")
        _, err = writer.communicate(timeout=30)
        self.assertEqual(writer.returncode, 0, err)
        self.assertTrue(os.path.exists(lock_path))
        self.assertIn("01", self.state()["slices"])

    def test_discard_on_error_removes_only_a_lock_file_it_created(self):
        lock_path = os.path.join(self.plan_dir, ".plan.lock")
        os.remove(lock_path)
        with self.assertRaises(RuntimeError):
            with plan_cli.locked(self.plan_dir, discard_on_error=True):
                raise RuntimeError("boom")
        self.assertFalse(os.path.exists(lock_path))
        with plan_cli.locked(self.plan_dir):
            pass
        with self.assertRaises(RuntimeError):
            with plan_cli.locked(self.plan_dir, discard_on_error=True):
                raise RuntimeError("boom")
        self.assertTrue(os.path.exists(lock_path))

    def test_crashed_writer_leaves_no_stale_lock_and_no_partial_state(self):
        self.plan("slice", "add", "01", "--file", "f", "--outcome", "o")
        before = self.read("state.json")
        crashed = subprocess.run([sys.executable, "-c", CRASH_ON_REPLACE, self.plan_dir], timeout=30)
        self.assertEqual(crashed.returncode, -signal.SIGKILL)
        self.assertEqual(self.read("state.json"), before)
        self.plan("validate")
        result = self.run_executable("slice", "add", "02", "--file", "f", "--outcome", "o",
                                     "--plan", self.plan_dir, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(sorted(self.state()["slices"]), ["01", "02"])
        self.assertNotIn("99", self.state()["slices"])

    def test_killed_lock_holder_releases_the_lock(self):
        holder = subprocess.Popen([sys.executable, "-c", HOLD_LOCK, self.plan_dir], stdout=subprocess.PIPE, text=True)
        self.assertEqual(holder.stdout.readline().strip(), "locked")
        os.kill(holder.pid, signal.SIGKILL)
        holder.wait()
        result = self.run_executable("slice", "add", "01", "--file", "f", "--outcome", "o",
                                     "--plan", self.plan_dir, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
