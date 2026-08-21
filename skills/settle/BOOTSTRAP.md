# Blank projects

Read this only when `settle` finds no implementation, build configuration, or tests.

## Decide whether to shape first

Continue in `settle` when the request provides enough intent to name:

- an observable outcome;
- the actor or caller that receives it;
- at least one demonstrable use case;
- a boundary for the first green slice.

The request may leave runtime, framework, storage, and other implementation forks open. Those belong in the `settle` interview.

When the product itself is still open, report what is missing and suggest:

```text
This needs product shaping before implementation planning: <missing decisions>.
Run `$shape-project`, approve its intent brief, then pass that brief to `$settle`.
```

Wait for the user. Do not invoke `$shape-project` on their behalf. Do not redirect a concrete request merely because its directory is empty.

## Inventory the absence

Inspect the working directory, including hidden project files. Distinguish an empty folder from an empty Git repository. A README, note, or approved shape brief may settle intent, but it does not establish an implementation convention.

State the evidence state once:

```text
Evidence state: blank project. No implementation, build configuration, or tests found.
```

Do not invent empty `file:line` citations.

## Default narrowly

Record a `D<n>` default only when it is invisible outside the implementation and can be reversed within one slice before another emitted slice depends on it. Give its reason and concrete reversal cost.

Folder names, local naming, test placement after the test tool is chosen, and similarly local organization usually qualify.

Ask when a choice affects the framework, runtime, deployment, public contracts, persistent data, authentication, authorization, privacy, external services, ongoing cost, or several slices. Ask only the decisions the requested use cases actually need.

## Plan the first green state

Prefer a walking use case: initialize the minimum project, implement one observable path, and verify it in the same slice.

Use a separate bootstrap slice only when the toolchain cannot reach green at a use-case boundary. Its verification must prove the project installs, builds or typechecks where applicable, runs its tests, and passes one smoke check. Keep later infrastructure out.

In the plan:

- mark the evidence state as blank;
- write `None` under the code-backed ledger;
- label every path as `Create`, `Read`, or `Modify`;
- separate `Existing traversal` from `Planned traversal` in `map.md`;
- label planned traversal as unverified until the first implementing slice creates and checks it.
