# Blank projects

Read this when `settle` finds no implementation, build configuration, or tests. Check hidden project files before concluding that.

## Ask wider

With nothing local to settle them, the framework, runtime, storage, external services, and ongoing cost belong to the user, and every later slice inherits them. Ask the ones the requested use cases need. Folder names, local naming, test placement once the test tool is chosen, and similarly local organization stay `D<n>` defaults.

## The first green state

Prefer a thin demonstrable use case that initializes only the tooling it needs. When setup cannot share a green boundary with that use case, allow one bootstrap slice first. It must leave a runnable project: install, build or typecheck where applicable, tests, and one smoke check all passing. It adds no infrastructure for later un-emitted use cases.

There is no environment to source a verification from, so the bootstrap slice's commands are marked `to create` and the slice creates them.
