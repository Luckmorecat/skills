---
name: mewto
description: Assess and harden unit tests with mutation testing after writing or changing them, or when asked to assess existing unit tests.
---

# Mewto

Judge tests by the required behavior they protect, without a mutation-score target.

## 1. Scope and baseline

Use the selected function/module or the production code exercised by selected tests; otherwise use the current task's production and test changes. Include existing unit tests that exercise the affected behavior. Resolve the scope to concrete production paths and test commands; if no bounded scope is identifiable, obtain one before mutating.

Establish intended behavior from requirements, contracts, and calling code. Flag conflicting or missing intent; assess the unambiguous behavior without turning the current implementation into a requirement.

Establish a passing baseline with the same test selection and execution environment used for mutation checks, including the mutation harness when using tooling ([baseline caveats](https://pitest.org/faq/)). Confirm that the intended tests are discovered and exercise the intended production code. A failing or unavailable baseline blocks conclusions for the affected tests; report the blocker. Preserve the starting production content so temporary edits can be reversed without losing existing work. Isolate temporary mutations from concurrent edits.

## 2. Challenge the behavior

Use existing mutation tooling appropriate to the project's language and test runner, scoped to the selected production code. If it is absent or unusable, introduce targeted mutations yourself. Keep tool installation and persistent configuration changes outside this pass. When useful, recommend a compatible tool without delaying targeted checks.

Before execution, select a bounded set of representative behaviors and faults and set an effort limit appropriate to the task. Prioritize distinct ways behavior could break over variations of the same fault. Use targeted mutations if tooling cannot stay within those bounds. Account for every selected fault as detected, addressed and rechecked, explained, inconclusive, or unassessed with a reason when the limit is reached. Report relevant code and fault types omitted by [tool filters](https://mutmut.readthedocs.io/en/latest/#configuration), sampling, or unsupported mutations.

For targeted checks, change production code one mutant at a time, run the relevant tests, and restore the mutation before the next experiment.

For either method, record the changed behavior and observed result. Count a kill as evidence only when a test detects that behavioral fault; keep tool status separate from that judgment. Build errors, setup failures, and unexplained timeouts are inconclusive. When attribution is doubtful, rerun the original and mutant under matching conditions; unstable results remain inconclusive. When assessing a particular test, distinguish faults it catches from faults caught only by other tests.

## 3. Improve the tests

For surviving, uncovered, or uncertain results, read [Interpreting results](references/interpreting-results.md) to diagnose undetected faults and justify survivor explanations. Address meaningful gaps within the selected faults and effort limit; report unresolved gaps.

Derive test expectations from required behavior rather than copying production logic or merely rejecting the mutant's result. [Assert the correct outcome at the appropriate interface](https://mutants.rs/using-results.html#what-to-do-about-missed-mutants).

Review the scoped tests for duplication, mock-only assertions, and dependence on implementation details. A mock assertion can protect a required interaction; judge what it proves. Replace or remove weak tests directly after identifying any required behavior they protect. With the candidate excluded, verify that retained or replacement tests pass on the unmutated code and detect the relevant faults. Use fresh evidence from the final test set, bypassing [cached verdicts](https://mutants.rs/iterate.html#caution) that could still credit removed or weakened tests. If the candidate protects no required behavior, explain why it can be removed. If protection is uncertain, retain it and report the concern.

After strengthening a test, verify that it passes against the unmutated code and fails against the fault it now protects against. Keep lasting edits to tests; report suspected production defects separately.

## 4. Finish

Restore all temporary mutations, verify that production content matches the starting content, and run the relevant tests with the final test changes. If the assessed code changes afterward, rerun affected mutation checks and relevant tests before relying on the results.

Report scope and method, the behaviors challenged and their outcomes, tests strengthened or removed with the retained protection, verification results, and explained survivors or remaining gaps. Describe the limits of both targeted checks and bounded tool runs; conclusions apply to the faults actually assessed. Completion requires restored production code and passing final tests; otherwise report the incomplete work and blocker.
