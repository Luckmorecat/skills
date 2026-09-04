---
name: shape-project
description: Turn an open project idea into an approved intent brief that settle can plan.
disable-model-invocation: true
---

Shape product intent before implementation planning. Use the user's attention on externally meaningful choices, finish with a brief they approve, then hand that brief to the `settle` skill.

This skill decides what the project should do. It does not choose file paths, code structure, test placement, or other implementation details. Record runtime, deployment, data, regulatory, or integration constraints when they are part of the user's intent. Leave their implementation to `settle`.

## Find the product frontier

Build a decision tree from the user's idea. The frontier contains every product decision whose prerequisites are already settled. Ask the whole frontier in one round, then wait. Hold questions whose meaning depends on an answer still open in that round.

A question belongs here when its answer changes an observable outcome, the actor or caller, a use case, data responsibility, a hard operating constraint, or the first release boundary. Propose a concrete recommendation for each question. Do not run a fixed questionnaire or ask about capabilities the stated use cases do not need.

Use specific examples to expose ambiguity. "Can two people edit the same item?" is useful when collaboration is in scope. "What consistency model do you want?" is premature implementation language unless the user's scenario makes it a product concern.

Print each round as:

```text
Settled intent
I1. <decision already established and why>

Q1. <product fork and its concrete options>
Recommended: <answer and consequence>
```

When the user reopens an `I<n>` decision, return it to the frontier.

When the user defers a question to you, record your recommendation as the decision, with its reason and the fact that they deferred it. Deferring answers the fork; it does not leave one open.

## Completion

The shape is ready when all of these are concrete:

- the actor or caller;
- the outcome they receive;
- the first-release use cases and acceptance examples;
- hard constraints and data responsibility that affect those use cases;
- what is out of scope.

Implementation choices may remain open. Present the complete intent brief and wait for approval.

## Write the approved brief

Create the brief outside the project, so a commit of it is out of reach rather than merely against the rules. Override the root with `STRIKER_ROOT`:

```bash
striker_root="${STRIKER_ROOT:-${XDG_STATE_HOME:-$HOME/.local/state}/striker}"
if repo_root=$(git rev-parse --show-toplevel 2>/dev/null); then
  repo=$(basename "$repo_root")
else
  repo=$(basename "$PWD")
fi
slug="oauth-device-flow"   # replace with a short kebab-case summary
mkdir -p "$striker_root/shapes/$repo"
mkdir "$striker_root/shapes/$repo/$slug-$(date +%F)"
```

The leaf is created without `-p` so an existing directory stops you rather than being written over: choose a more specific slug and retry.

Write `shape.md` in that directory with:

- **Intent**: the outcome and why it matters.
- **Actor or caller**: who receives the outcome.
- **Use cases**: user-demonstrable behaviour at full depth.
- **Acceptance examples**: concrete success and boundary scenarios.
- **Constraints**: product, runtime, deployment, data, legal, or integration constraints the user settled.
- **Decisions**: every interview answer and its reasoning.
- **Out of scope**: exclusions for the first release.
- **Unresolved**: `None`. An unresolved product fork means the interview is not complete.

Tell the user the absolute path and to invoke `settle` with it next.
