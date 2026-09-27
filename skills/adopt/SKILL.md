---
name: adopt
description: Adopt a chosen prototype, UI or logic, as the source of truth by reconciling it with the use cases the current system supports, and settle the gaps before or during implementation.
disable-model-invocation: true
---

Make a chosen prototype safe to implement as the source of truth for what it settles. A prototype settles what it shows; the current system supports more than any prototype shows. Find where the two disagree or where the prototype is silent, and settle what should happen there. Start from the chosen prototype or artifact, the conversation that chose it, and any supplied contract, plan, or reported discrepancies. Diagnose and recommend; do not change product code.

Identify the prototype's kind before anything else: `ui` for an interface, `logic` for a state model, algorithm, data flow, or API shape. A prototype can be both; apply each kind to the part it covers. [KINDS.md](KINDS.md) gives each kind's evidence, inventory, conflicts, and default precedence.

Pin the reference before comparing. Commit the prototype's code, or an artifact's source, and its evidence as listed in [KINDS.md](KINDS.md), to a branch off main; record the branch, commit SHA, path, and variant key. Do not push the branch unless asked. Outside a Git repository, save them under `${STRIKER_ROOT:-${XDG_STATE_HOME:-$HOME/.local/state}/striker}/references/<slug>-<date>/` instead. When the choice combines parts of several variants, ask for one converged variant or describe the combination precisely.

Dispatch subagents for independent discovery. Give each a bounded question, the kind's checklist from [KINDS.md](KINDS.md), and request concise findings with evidence: file references, screenshots, traces, or source URLs.

- **Inventory**: list the use cases the current system supports in the prototype's scope, from code and the running system, covering the kind's inventory checklist.
- **Reference**: from both the prototype's code and its evidence, list what it demonstrates, per the kind's reference checklist. Report cases its code handles that no evidence shows.

Map every inventoried use case against the reference as `kept`, `changed`, `unshown`, `dropped`, or `conflicting` (with a constraint named for the kind). Treat `unshown` and `dropped` with most suspicion. Deliberate changes already settled in conversation need no question.

Settle precedence first, so defaults resolve most gaps without a question. Recommend the kind's defaults from [KINDS.md](KINDS.md), unless the user has decided otherwise, and these for every kind: current behavior wins on what the prototype does not show; unshown cases follow existing project patterns; where the prototype's code and its approved evidence disagree, the evidence wins; and name which choices to delegate to implementation, with constraints.

Ask about the remaining consequential gaps with options and a recommendation. Group independent questions and defer dependent ones until their prerequisites settle. Wait for answers before treating recommendations as decisions.

Use numbered questions with explicit lettered choices (`A`, `B`, `C`) on separate lines. Keep question numbers unique across rounds; restart choice letters at `A` for each question. Give each a recommendation that names its choice letter, ties it to the mapping or a precedence rule, and explains its main tradeoff.

```markdown
❓ **Q1 — Where does per-row edit go in the new table?**

- **A.** An action revealed on row hover
- **B.** An overflow menu on each row
- **C.** Edit only from the detail page

➡️ **Recommended: A** — Current behavior lets editors act on
permitted rows directly; a hover action keeps that capability while
preserving the prototype's clean rows, at the cost of discoverability on touch.
```

Accept brief replies such as `Q1 A`, custom answers, and modifications to choices. Record answers before moving to dependent questions.

During implementation, settle reported discrepancies and decisions awaiting review the same way; an overturned decision names its replacement and the work it affects.

Record each settled gap as a `D<n>` ledger entry: what came up, decision, reason, and status `settled` or `overturned`. With a supplied contract, amend its prototype reference section, preserving approval and identifiers, and name the planned work the change affects. Without one, finish with a recap for the contract: the pinned reference and its kind, mapping, precedence, delegated discretion, ledger entries, and open gaps.
