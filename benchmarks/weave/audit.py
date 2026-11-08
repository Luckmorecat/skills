#!/usr/bin/env python3
"""Independent acceptance oracle; run on a completed fixture, never used as hints."""
import copy
import importlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

WORK = pathlib.Path(sys.argv.pop(1)).resolve()
sys.path.insert(0, str(WORK))
merge = importlib.import_module('configkit').merge

class Acceptance(unittest.TestCase):
    def test_replacement_transitions(self):
        pairs = [(1, 2), ([1], [2]), ({'x': 1}, 2), (1, {'x': 2}), ({'x': 1}, [2]), ([1], {'x': 2}), ('x', False)]
        for before, after in pairs:
            with self.subTest(before=before, after=after):
                self.assertEqual(merge({'key': before}, {'key': after}), {'key': after})
        self.assertEqual(merge({}, {'new': {'absent': None, 'kept': 2}}), {'new': {'kept': 2}})
        self.assertEqual(merge({'key': [1]}, {'key': {'absent': None}}), {'key': {}})
        self.assertEqual(merge({'nested': {'key': 1}}, {'nested': {'key': [2]}}), {'nested': {'key': [2]}})

    def test_recursive_delete_replace_and_detach(self):
        base = {'a': {'x': 1, 'y': [1, {'z': 2}]}, 'b': [3], 'gone': 1}
        override = {'a': {'x': None, 'new': [4]}, 'gone': None, 'missing': None}
        originals = copy.deepcopy((base, override))
        result = merge(base, override)
        self.assertEqual(result, {'a': {'y': [1, {'z': 2}], 'new': [4]}, 'b': [3]})
        result['a']['y'][1]['z'] = 8
        result['a']['new'].append(9)
        result['b'].append(10)
        self.assertEqual((base, override), originals)

    def test_validation_in_discarded_branches_and_lists(self):
        invalid = [{'__bad': 1}, {'x': [{'deep': [{'__bad': 1}]}]}]
        for value in invalid:
            for base, override in [(value, {}), ({}, value), ({'x': value}, {'x': 0}), ({'x': value}, {'x': None})]:
                with self.subTest(base=base, override=override), self.assertRaises(ValueError):
                    merge(base, override)

    def test_invalid_roots(self):
        for bad in [None, [], 4, 'x', True]:
            for base, override in [(bad, {}), ({}, bad)]:
                with self.subTest(base=base, override=override), self.assertRaises(ValueError):
                    merge(base, override)

    def test_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            d = pathlib.Path(directory)
            (d/'base').write_text('{"a":{"x":1,"y":2}}')
            (d/'override').write_text('{"a":{"x":null,"z":3}}')
            (d/'bad_json').write_text('{')
            (d/'bad_root').write_text('[]')
            (d/'bad_key').write_text('{"x":[{"__bad":1}]}')
            def cli(*args):
                return subprocess.run([sys.executable, '-m', 'configkit', *map(str, args)], cwd=WORK, capture_output=True, text=True)
            for args, expected in [([d/'base'], {'a': {'x': 1, 'y': 2}}), ([d/'base', d/'override'], {'a': {'y': 2, 'z': 3}})]:
                r = cli(*args)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual(json.loads(r.stdout), expected)
            for args in [[], [d/'base']*3, [d/'absent'], [d/'bad_json'], [d/'bad_root'], [d/'bad_key'], [d/'base', d/'bad_root']]:
                with self.subTest(args=args):
                    r = cli(*args)
                    self.assertEqual(r.returncode, 2, r.stderr)
                    self.assertEqual(r.stdout, '')
                    self.assertTrue(r.stderr.strip())
                    self.assertNotIn('Traceback', r.stderr)

    def test_dirty_snapshot_preserved(self):
        self.assertEqual((WORK/'LOCAL_NOTES.txt').read_text(), 'User notes: do not edit.\nUncommitted user addition.\n')
        dirty = subprocess.check_output(['git', 'status', '--porcelain'], cwd=WORK, text=True)
        self.assertEqual(dirty.strip(), 'M LOCAL_NOTES.txt')

if __name__ == '__main__':
    unittest.main()
