# Blank projects

Use the contract's approved runtime and tooling choices. An unresolved choice that blocks setup returns to `define`.

Prefer a thin demonstrable use case that initializes only the tooling it needs. If setup needs its own slice, leave a runnable project: installation, build or typecheck where applicable, tests, and a smoke check all pass. Add only infrastructure needed for that slice.

Mark verification commands that do not yet exist `to create`; the slice creates them. Include startup instructions so later sessions can verify the baseline.
