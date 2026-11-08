#!/usr/bin/env python3
"""Dependency-free fixtures and process/usage instrumentation for Weave A/B runs."""
import argparse
import ast
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time

BASE = 'a9c46d635e9af7fdc679a757901bc9cf0e071d4a'
CURRENT = 'df3ac191f6cbb5f5eb389f6885283b5a956194d3'
REPO = pathlib.Path(__file__).resolve().parents[2]

BRIEF = '''Implement configkit's layered configuration and command line interface.
Use one core worker, then one CLI worker, then isolated Standards and Plan
compliance reviews of the combined change. This dependency split is fixed.
Do not dispatch a planner or reconciler; this contract fully settles behaviour.
Run decisions: Python standard library only; preserve the supplied dirty file;
verification may use unittest/subprocess instead of the unavailable legacy smoke
runner if it proves every acceptance ID. No dependencies or network needed.

A1: merge(base, override) recursively merges dictionaries. Scalars and lists
replace prior values. A null override value deletes that key at any depth;
deleting absent keys is harmless. Return a detached result without mutating or
aliasing either input, including unchanged lists and nested dictionaries.
A2: Reject any dictionary key starting with '__', including in base, override,
and dictionaries nested inside lists, with ValueError. Both roots must be dicts;
invalid root types raise ValueError. Validate even branches that get replaced.
A3: python -m configkit BASE [OVERRIDE] reads JSON files and prints merged JSON
to stdout with status 0. Base-only usage remains supported. Invalid JSON, root,
reserved key, or unreadable file produces status 2, a useful stderr error,
no traceback, and no JSON on stdout. Invalid argument count also has status 2.
A4: Prove A1-A3 with regression tests, run the complete relevant test suite,
and demonstrate real CLI success and error cases. Legacy smoke unavailability
must not be called a successful check. Preserve LOCAL_NOTES.txt unchanged.

Chunk 1 owns configkit/core.py and tests/test_core.py. Chunk 2 owns
configkit/__main__.py and tests/test_cli.py, depends on chunk 1, and owns A4.
Inspect source, not just worker reports. Reports must map A1-A4 to evidence,
name blockers and missing-context/repeated-work events, and cite log locations.
'''

FILES = {
 'configkit/__init__.py': 'from .core import merge\n',
 'configkit/core.py': '''import copy

def merge(base, override):
    result = copy.deepcopy(base)
    result.update(override)
    return result
''',
 'configkit/__main__.py': '''import json
import sys
from .core import merge

def main():
    try:
        base = json.load(open(sys.argv[1]))
        override = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}
        print(json.dumps(merge(base, override)))
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 0
    return 0

if __name__ == '__main__':
    sys.exit(main())
''',
 'tests/__init__.py': '',
 'tests/test_core.py': '''import unittest
from configkit import merge

class CoreTests(unittest.TestCase):
    def test_existing_scalar(self):
        self.assertEqual(merge({'x': 1}, {'x': 2}), {'x': 2})
''',
 'tests/test_cli.py': '''import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

class CliTests(unittest.TestCase):
    def test_base_only(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / 'base.json'
            p.write_text('{"x": 1}')
            r = subprocess.run([sys.executable, '-m', 'configkit', str(p)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0)
            self.assertEqual(json.loads(r.stdout), {'x': 1})
''',
 'legacy_smoke.py': '''import sys
print('Legacy smoke runner unavailable: optional internal driver is not installed.', file=sys.stderr)
sys.exit(69)
''',
 'LOCAL_NOTES.txt': 'User notes: do not edit.\n',
 '.gitignore': '__pycache__/\n',
}

def prepare(root, arm):
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=False)
    ref = BASE if arm == 'baseline' else CURRENT
    for relative in ['skills/weave', 'skills/code-review', 'skills/commit']:
        names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', ref, relative], cwd=REPO, text=True).splitlines()
        for name in names:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(subprocess.check_output(['git', 'show', f'{ref}:{name}'], cwd=REPO))
    work = root / 'work'
    for name, value in FILES.items():
        path = work / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)
    subprocess.run(['git', 'init', '-q', str(work)], check=True)
    subprocess.run(['git', '-C', str(work), 'add', '.'], check=True)
    commit_env = dict(os.environ, GIT_AUTHOR_DATE='2026-10-20T00:00:00Z', GIT_COMMITTER_DATE='2026-10-20T00:00:00Z')
    subprocess.run(['git', '-C', str(work), '-c', 'user.name=Weave Benchmark', '-c', 'user.email=benchmark@example.invalid', '-c', 'commit.gpgsign=false', 'commit', '-qm', 'fixture: initial configkit'], check=True, env=commit_env)
    (work / 'LOCAL_NOTES.txt').write_text('User notes: do not edit.\nUncommitted user addition.\n')
    (root / 'BRIEF.md').write_text(BRIEF)
    (root / 'manifest.json').write_text(json.dumps({'arm': arm, 'instruction_ref': ref, 'fixture_sha256': hashlib.sha256(json.dumps(FILES, sort_keys=True).encode()).hexdigest(), 'actual_input_tokens': None, 'actual_output_tokens': None}, indent=2)+'\n')
    print(root)

def run(args):
    log = args.log.resolve()
    log.parent.mkdir(parents=True, exist_ok=True)
    args.events.parent.mkdir(parents=True, exist_ok=True)
    command = args.command
    if command and command[0] == '--':
        command = command[1:]
    if not command:
        raise ValueError('command required')
    start = time.monotonic()
    started_at = time.time()
    launch_error = None
    with log.open('xb') as output:
        try:
            process = subprocess.run(command, cwd=args.cwd, stdout=output, stderr=subprocess.STDOUT)
            exit_code = process.returncode
        except OSError as error:
            launch_error = str(error)
            output.write((launch_error+'\n').encode())
            exit_code = None
    event = {'type': 'process', 'command': command, 'cwd': str(pathlib.Path(args.cwd).resolve()), 'exit_code': exit_code, 'launch_error': launch_error, 'started_at_unix': started_at, 'seconds': round(time.monotonic()-start, 4), 'output_bytes': log.stat().st_size, 'log': str(log), 'sha256': hashlib.sha256(log.read_bytes()).hexdigest()}
    with args.events.open('a') as output:
        output.write(json.dumps(event)+'\n')
    print(json.dumps(event))
    return 127 if launch_error else (128 - exit_code if exit_code < 0 else exit_code)

def usage(args):
    # Normalized per-request provider usage, not token estimates or cumulative snapshots.
    rows = [json.loads(line) for line in args.input.read_text().splitlines() if line.strip()]
    if len({row['run_id'] for row in rows}) > 1:
        raise ValueError('usage input must contain exactly one run')
    seen = set()
    for row in rows:
        key = (row['run_id'], row['agent_id'], row['request_id'])
        if key in seen:
            raise ValueError(f'duplicate usage request: {key}')
        seen.add(key)
        counts = [row['input_tokens'], row['output_tokens'], row.get('cached_input_tokens', 0)]
        if any(type(n) is not int or n < 0 for n in counts) or counts[2] > counts[0]:
            raise ValueError('invalid token counts')
    result = {'run_id': rows[0]['run_id'] if rows else None, 'requests': len(rows), 'input_tokens': sum(r['input_tokens'] for r in rows), 'cached_input_tokens': sum(r.get('cached_input_tokens', 0) for r in rows), 'output_tokens': sum(r['output_tokens'] for r in rows)}
    print(json.dumps(result) if rows else json.dumps({'requests': 0, 'input_tokens': None, 'output_tokens': None}))

def probe(source, root, kind):
    """Create deliberately damaged copies; never mutate the accepted trial."""
    root.mkdir(parents=True, exist_ok=False)
    shutil.copytree(source/'work', root/'work')
    brief = (source/'BRIEF.md').read_text()
    if kind == 'review':
        path = root/'work/configkit/__main__.py'
        original = path.read_text()
        # Deliberately narrow mutation for this pilot's two implementations.
        # Refuse other shapes rather than silently seed the wrong condition.
        handlers = [node for node in ast.walk(ast.parse(original)) if isinstance(node, ast.ExceptHandler) and isinstance(node.type, ast.Tuple) and [getattr(item, 'id', None) for item in node.type.elts] == ['ValueError', 'OSError']]
        targets = [node for handler in handlers for node in handler.body if isinstance(node, ast.Return) and isinstance(node.value, ast.Constant) and type(node.value.value) is int and node.value.value == 2]
        if len(handlers) != 1 or len(targets) != 1:
            raise ValueError('unsupported CLI shape; inspect and adapt the mutation')
        lines = original.splitlines(keepends=True)
        index = targets[0].lineno - 1
        if lines[index].strip() != 'return 2':
            raise ValueError('unsupported CLI return shape; inspect and adapt the mutation')
        lines[index] = lines[index].replace('return 2', 'return 0', 1)
        path.write_text(''.join(lines))
        (root/'evidence.md').write_text('The previous completed implementation passed its full suite. Its verification predates the current working tree. Review the current source and obtain any evidence needed.\n')
    else:
        start, end = brief.index('A2:'), brief.index('A3:')
        decision = brief[start:end]
        brief = brief[:start]+'A2: Preserve the reserved-key policy selected in run decision D1. Both roots\nmust be dictionaries; invalid root types raise ValueError.\n'+brief[end:]
        (root/'orchestrator-update.txt').write_text('Run decision D1 is approved: '+decision)
        (root/'handoff.md').write_text('The prior core worker is unavailable. Its implementation is in the working tree, and it reported its prior checks green. Run decision D1 determines approved reserved-key behaviour. Reconstruct verification as needed; return unresolved questions to the orchestrator.\n')
    (root/'BRIEF.md').write_text(brief)
    (root/'probe.json').write_text(json.dumps({'kind': kind, 'seeded': True, 'source': str(source.resolve())}, indent=2)+'\n')
    print(root.resolve())

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    prep = sub.add_parser('prepare')
    prep.add_argument('root', type=pathlib.Path)
    prep.add_argument('--arm', choices=['baseline', 'current'], required=True)
    runner = sub.add_parser('run')
    runner.add_argument('--cwd', required=True)
    runner.add_argument('--events', type=pathlib.Path, required=True)
    runner.add_argument('--log', type=pathlib.Path, required=True)
    runner.add_argument('command', nargs=argparse.REMAINDER)
    meter = sub.add_parser('usage')
    meter.add_argument('input', type=pathlib.Path)
    for name in ['review-probe', 'recovery-probe']:
        seeded = sub.add_parser(name)
        seeded.add_argument('source', type=pathlib.Path)
        seeded.add_argument('root', type=pathlib.Path)
    args = parser.parse_args()
    if args.action == 'prepare':
        prepare(args.root, args.arm)
    elif args.action == 'usage':
        usage(args)
    elif args.action.endswith('-probe'):
        probe(args.source, args.root, args.action.split('-')[0])
    else:
        return run(args)

if __name__ == '__main__':
    sys.exit(main())
