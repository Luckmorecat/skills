import contextlib
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

import bench

class InstrumentationTests(unittest.TestCase):
    def test_exit_and_complete_output_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            log, events = root/'run.log', root/'events.jsonl'
            script = "import sys; print('diagnostic'); print('failure', file=sys.stderr); sys.exit(7)"
            r = subprocess.run([sys.executable, str(pathlib.Path(bench.__file__)), 'run', '--cwd', directory, '--events', str(events), '--log', str(log), '--', sys.executable, '-c', script], capture_output=True, text=True)
            self.assertEqual(r.returncode, 7)
            event = json.loads(events.read_text())
            self.assertEqual(event['exit_code'], 7)
            self.assertEqual(event['output_bytes'], len(log.read_bytes()))
            self.assertIn('failure', log.read_text())
            self.assertIn('diagnostic', log.read_text())

    def usage(self, rows):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory)/'usage.jsonl'
            path.write_text(''.join(json.dumps(row)+'\n' for row in rows))
            with contextlib.redirect_stdout(io.StringIO()) as output:
                bench.usage(type('Args', (), {'input': path}))
            return json.loads(output.getvalue())

    def test_unavailable_command_is_recorded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            events = root/'events.jsonl'
            r = subprocess.run([sys.executable, str(pathlib.Path(bench.__file__)), 'run', '--cwd', directory, '--events', str(events), '--log', str(root/'missing.log'), '--', str(root/'missing-executable')], capture_output=True, text=True)
            self.assertEqual(r.returncode, 127)
            event = json.loads(events.read_text())
            self.assertIsNone(event['exit_code'])
            self.assertTrue(event['launch_error'])

    @unittest.skipUnless(os.name == 'posix', 'POSIX subprocess signal convention')
    def test_signal_is_recorded_and_mapped_to_shell_status(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            events = root/'events.jsonl'
            r = subprocess.run([sys.executable, str(pathlib.Path(bench.__file__)), 'run', '--cwd', directory, '--events', str(events), '--log', str(root/'signal.log'), '--', sys.executable, '-c', 'import os, signal; os.kill(os.getpid(), signal.SIGTERM)'], capture_output=True, text=True)
            self.assertEqual(r.returncode, 143)
            self.assertEqual(json.loads(events.read_text())['exit_code'], -15)

    def test_oracle_rejects_retained_value_mutant(self):
        with tempfile.TemporaryDirectory() as directory:
            work = pathlib.Path(directory)
            package = work/'configkit'
            package.mkdir()
            (package/'__init__.py').write_text('def merge(base, override):\n    return dict(base)\n')
            r = subprocess.run([sys.executable, str(pathlib.Path(bench.__file__).with_name('audit.py')), str(work), 'Acceptance.test_replacement_transitions'], capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
            self.assertIn('FAIL:', r.stderr)

    def test_review_probe_mutates_only_supported_handler(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source = root/'source'
            package = source/'work/configkit'
            package.mkdir(parents=True)
            (source/'BRIEF.md').write_text(bench.BRIEF)
            target = package/'__main__.py'
            supported = 'def main():\n    try:\n        pass\n    except (ValueError, OSError) as error:\n        return 2\n    return 0\n'
            target.write_text(supported)
            with contextlib.redirect_stdout(io.StringIO()):
                bench.probe(source, root/'valid', 'review')
            self.assertEqual((root/'valid/work/configkit/__main__.py').read_text(), supported.replace('return 2', 'return 0'))
            target.write_text(supported.replace('return 2', 'pass')+'\ndef other():\n    return 2\n')
            with self.assertRaises(ValueError):
                bench.probe(source, root/'invalid', 'review')

    def test_unknown_usage_is_not_zero(self):
        self.assertIsNone(self.usage([])['input_tokens'])

    def test_synthetic_usage_aggregation_and_duplicate_guard(self):
        row = dict(run_id='synthetic', agent_id='worker', request_id='1', input_tokens=100, cached_input_tokens=40, output_tokens=10)
        self.assertEqual(self.usage([row])['input_tokens'], 100)
        with self.assertRaises(ValueError):
            self.usage([row, row])
        with self.assertRaises(ValueError):
            self.usage([dict(row, cached_input_tokens=101)])
        with self.assertRaises(ValueError):
            self.usage([row, dict(row, run_id='different')])

    def test_fixture_arms_identical(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            with contextlib.redirect_stdout(io.StringIO()):
                bench.prepare(root/'baseline', 'baseline')
                bench.prepare(root/'current', 'current')
            for relative in bench.FILES:
                self.assertEqual((root/'baseline/work'/relative).read_bytes(), (root/'current/work'/relative).read_bytes())
            self.assertEqual((root/'baseline/BRIEF.md').read_text(), (root/'current/BRIEF.md').read_text())
            self.assertNotEqual((root/'baseline/skills/weave/WORKER.md').read_text(), (root/'current/skills/weave/WORKER.md').read_text())

if __name__ == '__main__':
    unittest.main()
