---
name: slice
description: Break settled context into verifiable vertical slices with explicit dependencies, or revise an existing breakdown.
disable-model-invocation: true
---

Turn the agreed feature into slices an agent can implement and verify in a fresh session. Work from the conversation, supplied contract, or existing plan. Reuse settled decisions and carry their approval or delegation status, delegated discretion, precedence rules, and any prototype reference into the plan, whichever the source; surface missing choices that change scope, behavior, constraints, or dependencies before preparing affected work.

Inspect the relevant implementation and project conventions. Ground the breakdown in current behavior and known constraints. Separate facts from proposed changes.

Prefer vertical slices: each delivers one narrow behavior across the layers it actually needs, with acceptance that can be demonstrated before later slices exist. Size by the context needed to understand, implement, and review the result. Split slices that combine independent outcomes or require several unrelated investigations.

Declare only genuine blockers. A prerequisite must supply behavior, an interface, or evidence the slice needs; a preferred order alone is not a dependency. Outline the whole scope and cover every agreed outcome and boundary. Include integration checks where independently passing slices do not prove the combined experience.

Sequence enabling work where it is needed. A setup slice leaves a runnable, testable baseline. For broad migrations, preserve compatibility while adding the new form, migrating consumers in bounded groups, and removing the old form after its last consumer moves. Each committed slice must remain verifiable and keep the relevant checks passing.

Prepare slices when their outcome, acceptance, prerequisites, and verification are clear. Missing future file paths or commands alone do not prevent preparation. If evidence is needed to choose what to build, identify the affected slices and an investigation with one question, an effort limit, and an observable result. Continue preparing independent work.

Present a compact breakdown with each slice's outcome and blockers so the user can judge granularity and ordering. Resolve decisions requiring their judgment; existing authorization is sufficient for decomposition within the agreed scope.

Save the plan in the layout [PLAN-FORMAT.md](PLAN-FORMAT.md) describes. Below, `plan <command>` means `python3 <cli> --plan <dir> <command>`, where `<dir>` is the plan directory and `<cli>` is this skill's `bin/plan` as an absolute path; `init` and `import` take the directory as their argument instead of `--plan`. `plan <command> --help` documents each command. Write the prose files yourself: `plan.md`'s shared context, outside its status block, and the slice files. Record every slice, its dependencies with what each supplies, and its status only through `plan`, which keeps them in `state.json` and regenerates the status block. Record decisions in `plan.md`'s prose with their approval status, a proposal marked as proposed; use `plan decide` only when your caller asks. Scheduling constraints (`plan constrain`) belong to the skills that run the plan.

- **New plan.** Write `plan.md`'s shared context ending with a `## Slices` heading, then run `python3 <cli> init <dir> --repo <root> --target <branch>`, which appends the status block. Write each slice file, then record it with `plan slice add <ID> --file <file> --outcome <outcome> --blocked-by <ID>:<what it supplies>...`, adding `--status blocked --reason <what resolves it>` for a blocked slice.
- **Revision.** When the directory has no `state.json`, run `python3 <cli> import <dir>` first; if the import fails, stop and report its error. Read the current state with `plan status`. Present the changed breakdown for approval as above, unless your caller passes an approved revision. Keep IDs stable and carry amended decisions, discretion, precedence, and ledger entries into the shared context. Change an existing slice's file, outcome, or dependencies with `plan slice edit <ID>`, and add new work with `plan slice add`.
  - Leave completed slices, their evidence in `log.md`, and started slices' baselines (fixed point and dirty snapshot) as they are. Change status only for slices that have not started and that your caller has not paused, between `ready` and `blocked`; your caller resumes the slices it paused. Starting, blocking, resuming, and completing belong to the skills that run the plan.
  - Record why each change to unfinished work was made by passing `--note <why>` to its `plan slice add|edit`; for a change to a slice file's prose alone, run `plan slice edit <ID> --note <why>`.
  - For a slice in progress, leave its checkpoint to the skill running it: return the change to your caller, or report it to the user when invoked directly, so that skill picks it up.

Finish with `plan validate`, and check that `plan status` lists the breakdown you present. Return the plan path, breakdown, and any unresolved blockers.
