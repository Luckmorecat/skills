---
name: slice
description: Break settled context into verifiable vertical slices with explicit dependencies, or revise an existing breakdown.
disable-model-invocation: true
---

Turn the agreed feature into slices an agent can implement and verify in a fresh session. Work from the conversation, supplied contract, or existing plan. Reuse settled decisions; surface missing choices that change scope, behavior, constraints, or dependencies before preparing affected work.

Inspect the relevant implementation and project conventions. Ground the breakdown in current behavior and known constraints. Separate facts from proposed changes.

Prefer vertical slices: each delivers one narrow behavior across the layers it actually needs, with acceptance that can be demonstrated before later slices exist. Size by the context needed to understand, implement, and review the result. Split slices that combine independent outcomes or require several unrelated investigations.

Declare only genuine blockers. A prerequisite must supply behavior, an interface, or evidence the slice needs; a preferred order alone is not a dependency. Outline the whole scope and cover every agreed outcome and boundary. Include integration checks where independently passing slices do not prove the combined experience.

Sequence enabling work where it is needed. A setup slice leaves a runnable, testable baseline. For broad migrations, preserve compatibility while adding the new form, migrating consumers in bounded groups, and removing the old form after its last consumer moves. Each committed slice must remain verifiable and keep the relevant checks passing.

Prepare slices when their outcome, acceptance, prerequisites, and verification are clear. Missing future file paths or commands alone do not prevent preparation. If evidence is needed to choose what to build, identify the affected slices and an investigation with one question, an effort limit, and an observable result. Continue preparing independent work.

Present a compact breakdown with each slice's outcome and blockers so the user can judge granularity and ordering. Resolve decisions requiring their judgment; existing authorization is sufficient for decomposition within the agreed scope.

Use [PLAN-FORMAT.md](PLAN-FORMAT.md) to save the plan and slice files. On revision, preserve stable IDs, completed work, verification evidence, and interrupted work's baseline; update affected unfinished slices and record why.

Return the plan path, breakdown, and any unresolved blockers.
