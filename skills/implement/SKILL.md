---
name: implement
description: Implement requested work and verify it green, leaving the changes uncommitted.
disable-model-invocation: true
---

Implement the work the user requests, using any supplied plan, spec, ticket, brief, or acceptance criteria.

Honour the requested scope, acceptance criteria, constraints, exclusions, and verification requirements. Where absent, derive observable success/boundary examples from the request and use the repository's checks. Ask only where ambiguity changes the outcome. Green means checks pass, acceptance is demonstrated, and constraints hold.

Run the cheapest relevant baseline check. Use `tdd` where possible, at pre-agreed seams. Run focused checks regularly and the full relevant suite at the end; exercise the API or UI when needed to prove acceptance.

Reconcile discoveries before dependent implementation. Correct internal implementation choices within approved constraints; ask before changing approved behaviour, including a contract's prototype reference, public contracts, persistent data, security/privacy, deployment, external services, ongoing cost, or an expensive-to-reverse choice.

Record what future readers of the code need, such as a non-obvious constraint, in the code or a test. Leave the changes uncommitted and report the changed paths, verification evidence, blockers, and notes for the commit message, such as why you chose an approach.

If blocked, preserve the baseline, owned changes, and evidence; report the missing prerequisite or decision.
