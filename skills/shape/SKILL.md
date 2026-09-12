---
name: shape
description: Turn vague thoughts into a concrete concept and a justified next step.
disable-model-invocation: true
---

Shape a product, feature, service, internal tool, or improvement from a vague thought. Establish who it serves, what changes for them, how it could work, and what remains uncertain. A repository or commitment to build is optional.

Assess ideas on their merits. Challenge weak assumptions, explain consequential tradeoffs, and point out when the proposed solution does not address the stated need. Ground agreement and disagreement in reasons; omit empty praise and objections without a concrete consequence.

## Explore the thought

Start from the observation, frustration, or possibility behind the thought. Reuse what the user has already established. When the direction is unclear, offer a few plausible concepts with concrete examples and tradeoffs; keep them provisional until the user chooses or delegates a direction. Preserve the user's chosen intent as you develop it.

Contribute ideas as well as questions. An early round may need only one consequential question and an example the user can react to. Explore until there is a candidate direction the user wants to sharpen; when that direction is already clear, move directly to convergence.

## Converge on a concept

Resolve choices that change who benefits, the situation, the outcome, the central experience, or meaningful boundaries. Use concrete scenarios to expose ambiguity and recommend an answer with its consequence. Record runtime, deployment, data responsibility, regulatory, or integration constraints when they materially shape the concept.

The **frontier** contains useful questions whose prerequisites are settled. Ask the whole frontier together in one round when the questions can be answered independently. During early exploration, ask only the question that unlocks a direction if the remaining questions depend on it. Questions that depend on an open answer belong to a later round. Wait for answers before treating recommendations as decisions.

Use stable `I<n>` labels for settled intent and `Q<n>` labels for questions when tracking multiple decisions across rounds. Keep labels in the visible text, never reuse one for a different item, and let the user reopen settled intent by number. When the user delegates a choice, record the selected recommendation, its reason, and the delegation.

For example, once a shared reading list for a group of friends is settled, these independent choices belong in one round:

```text
Settled intent; reopen by number
I1. A shared reading list helps a group of friends choose what to read next.

Q1. What can the list contain: books, articles, or both?
Recommended: Both, so friends can suggest short reads as well as books.

Q2. Who can add suggestions: any member or only the list owner?
Recommended: Any member, so everyone can contribute directly.

Q3. Who can see the list: members only or anyone with its link?
Recommended: Members only, keeping suggestions within the group.
```

The user can answer all three at once, for example: `Q1 books only; Q2 and Q3 use your recommendations`. Carry those answers into settled intent before asking dependent follow-ups.

Separate **intent** from **assumptions**. Resolve ambiguity about the intended experience through discussion. Demand, feasibility, and other claims requiring evidence can remain uncertain: record what is assumed and how to investigate it. User agreement establishes intent, not proof that a hypothesis is true.

## Completion

The shape is ready when these form a coherent concept:

- who it serves and in what situation;
- the desired outcome and why it matters;
- the central experience, illustrated by a concrete scenario;
- meaningful scope boundaries and known hard constraints;
- settled decisions and their reasoning, including delegated choices;
- assumptions and open questions, with the evidence or decision needed to resolve them;
- a next step justified by the most consequential remaining uncertainty.

Present a self-contained final shape in the conversation using these points as its outline, then stop. Include enough detail to distinguish the chosen direction from alternatives. Call it a proposed shape unless the user has endorsed it; keep proposals distinct from settled decisions. Leave release planning and exhaustive acceptance criteria to `define`.

Research fits uncertainty about needs, demand, or external facts; a prototype fits uncertainty about the experience or feasibility; `define` fits a concept ready for a delivery contract. Recommend the smallest useful action that addresses the remaining uncertainty. Starting that action requires a user request or existing authorization.

Completion requires neither an approval round nor a file. Save only when requested or already agreed; omit routine offers to save.

## Optional saving

Save the same final shape, preserving its proposed or endorsed status. Honor a requested destination; otherwise use `${STRIKER_ROOT:-${XDG_STATE_HOME:-$HOME/.local/state}/striker}/shapes/<context>/<slug>-<date>/shape.md` outside the repository. Context is the relevant repository name, a meaningful topic, or `general`; use a short kebab-case slug and an ISO date.

For a new shape, choose an unused directory so an existing artifact is preserved. Return the absolute path for revisiting, sharing, or passing to another session.
