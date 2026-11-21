Implement configkit's layered configuration and command line interface.
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
