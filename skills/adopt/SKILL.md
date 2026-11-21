---
name: adopt
description: Adopt a chosen prototype, UI or logic, as the source of truth by reconciling it with the use cases the current system supports, and settle the gaps before or during implementation.
disable-model-invocation: true
---

Make a chosen prototype safe to implement as the source of truth for what it settles. A prototype settles what it shows; the current system supports more than any prototype shows. Find where the two disagree or where the prototype is silent, and settle what should happen there. Start from the chosen prototype or artifact, the conversation that chose it, and any supplied contract, plan, or reported discrepancies. Diagnose and recommend; do not change product code.

## Pin and discover

Identify the prototype's kind before anything else: `ui` for an interface, `logic` for a state model, algorithm, data flow, or API shape. A prototype can be both; apply each kind to the part it covers. [KINDS.md](KINDS.md) gives each kind's evidence, inventory, conflicts, and default precedence.

Pin the reference before comparing. Commit the prototype's code, or an artifact's source, and its evidence as listed in [KINDS.md](KINDS.md), to a branch off main; record the branch, commit SHA, path, and variant key. Do not push the branch unless asked. Outside a Git repository, save them under `${STRIKER_ROOT:-${XDG_STATE_HOME:-$HOME/.local/state}/striker}/references/<slug>-<date>/` instead. When the choice combines parts of several variants, ask inline (following [Questions and decisions](#questions-and-decisions)) for one converged variant or describe the combination precisely.

Cover both discovery tracks below. Do targeted checks inline; dispatch subagents when broad or independent discovery would bloat this conversation. Give each subagent a bounded question, the kind's checklist from [KINDS.md](KINDS.md), and request concise findings with evidence: file references, screenshots, traces, or source URLs.

- **Inventory**: list the use cases the current system supports in the prototype's scope, from code and the running system, covering the kind's inventory checklist.
- **Reference**: from both the prototype's code and its evidence, list what it demonstrates, per the kind's reference checklist. Report cases its code handles that no evidence shows.

## Map and precedence

Map every inventoried use case against the reference as `kept`, `changed`, `unshown`, `dropped`, or `conflicting` (with a constraint named for the kind). Treat `unshown` and `dropped` with most suspicion. Deliberate changes already settled in conversation need no question.

Settle precedence first, so defaults resolve most gaps without a question. Recommend the kind's defaults from [KINDS.md](KINDS.md), unless the user has decided otherwise, and these for every kind: current behavior wins on what the prototype does not show; unshown cases follow existing project patterns; where the prototype's code and its approved evidence disagree, the evidence wins; and name which choices to delegate to implementation, with constraints. Finish discovery and mapping before asking gap questions.

## Questions and decisions

Treat remaining consequential gaps as a decision tree: batch independent questions whose prerequisites are settled, and defer branches that depend on unanswered choices. Wait for the user's reply before treating recommendations as decisions. When the user delegates a choice, make it and explain why.

Write every question directly in your chat reply as numbered markdown (`Q1`, `Q2`, unique across rounds): give choice questions lettered options restarting at `A` per question and a recommendation naming the letter, tying it to the mapping or a precedence rule, and explaining its main tradeoff; ask open-ended questions directly when choices would be artificial.

```markdown
❓ **Q1 — Where does per-row edit go in the new table?**

- **A.** An action revealed on row hover
- **B.** An overflow menu on each row
- **C.** Edit only from the detail page

➡️ **Recommended: A** — Current behavior lets editors act on
permitted rows directly; a hover action keeps that capability while
preserving the prototype's clean rows, at the cost of discoverability on touch.
```

During implementation, settle reported discrepancies and decisions awaiting review the same way; an overturned decision names its replacement and the work it affects.

## Done

Continue until every consequential gap is settled or explicitly left open with its impact understood.

Record each settled gap as a `D<n>` ledger entry: what came up, decision, reason, and status `settled` or `overturned` (noting delegated choices). With a supplied contract, amend its prototype reference section, preserving approval and identifiers, and name the planned work the change affects. Without one, finish with a conversational recap for the contract:

- **Pinned reference and kind**
- **Mapping and precedence**
- **Delegated discretion**
- **Ledger entries** (`D<n>`)
- **Open gaps**

Then stop so the user chooses what happens next.
