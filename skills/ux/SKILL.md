---
name: ux
description: Audit a web or GUI interface through its users' tasks and recommend changes that make it intuitive to use.
disable-model-invocation: true
---

Find where the requested interface makes its users' tasks harder than they need to be, and settle what should change. Start from the user's context: the screens, flow, or feature in scope and any known complaints. Diagnose and recommend; do not change product code.

Frame before researching. Establish who uses the interface, the three to five tasks that matter most, and the context of use: device, frequency, and whether users arrive as experts or first-timers. Ask when these are unknown and consequential; otherwise state assumptions. These tasks become the scenarios every finding and recommendation is checked against.

Dispatch subagents for independent discovery. Give each a bounded question and request concise findings with evidence: file references, screenshots, or source URLs.

- **Inventory**: map screens, flows, components, and design tokens from the code. Report inconsistencies in controls, wording, spacing, and state handling, and the conventions the project already follows.
- **Walkthrough**: run the interface and perform each framed task step by step, capturing screenshots at every decision point. Apply the cognitive walkthrough questions from [PRINCIPLES.md](PRINCIPLES.md) and record where the user would hesitate, err, or give up. Cover empty, loading, error, and first-run states, and a narrow viewport.
- **Patterns**: research how comparable products and the platform's guidelines handle the same tasks, so recommendations match what users already expect.
- **Accessibility**: check contrast, keyboard paths, focus visibility, labels, target sizes, and motion against WCAG 2.2.

Judge the rendered interface, not the source alone. When the interface cannot be run, say so, lower confidence in walkthrough findings, and name what would confirm them.

Evaluate findings against [PRINCIPLES.md](PRINCIPLES.md) and the project's own conventions. Tie each finding to a task step, the principle it violates, and its evidence. Rate severity on the scale in [PRINCIPLES.md](PRINCIPLES.md), weighing how many users hit it, how often, and whether they can recover. Discard findings that are taste without a user consequence. Distinguish observed problems from predicted ones; expert review predicts, only users confirm.

Recommend the simplest change that removes each problem, with its tradeoff. Group related findings into a single change where one fix resolves several. Prefer platform conventions and existing project patterns over novel solutions.

Ask about consequential choices with options and a recommendation. Group independent questions and defer dependent ones until their prerequisites settle. Wait for answers before treating recommendations as decisions.

Use numbered questions with explicit lettered choices (`A`, `B`, `C`) on separate lines. Keep question numbers unique across rounds; restart choice letters at `A` for each question. Give each a recommendation that names its choice letter, ties it to a finding or principle, and explains its main tradeoff.

```markdown
❓ **Q1 — How should users discover bulk actions?**

- **A.** A persistent toolbar that activates on selection
- **B.** A contextual menu on right-click

➡️ **Recommended: A** — The walkthrough showed users selecting rows
and looking for an action above the table; a visible toolbar signals
the capability, at the cost of permanent vertical space.
```

Accept brief replies such as `Q1 A`, custom answers, and modifications to choices. Record answers before moving to dependent questions.

When a choice cannot be settled without seeing it, recommend `prototype` with the specific question it should answer and the variants worth comparing. When prototypes return, evaluate each variant against the same framed tasks. If `prototype` is unavailable, name the question and variants and leave the choice open.

Finish with a concise recap: the framed tasks, findings ranked by severity with their evidence, settled changes, open questions, and remaining uncertainties.
