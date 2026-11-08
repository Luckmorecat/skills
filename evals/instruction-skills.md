# Instruction-skill regression cases

These are maintainer evaluation fixtures, not runtime instructions. Give executors
only the request and input artifacts; keep scoring criteria with the evaluator.
Run each case in an isolated scratch workspace. Never publish, install, or use
real customer data. Forced skill loading checks execution, not automatic routing.

## Shared input artifacts

`AGENTS.md`:

```markdown
Use skills/pr for pull requests.
Do not include customer records in logs or PR evidence.
```

`web/AGENTS.md`:

```markdown
For UI modifications, attach screenshots to the PR evidence section.
Run npm run test:web before requesting review.
```

`package.json`:

```json
{"scripts":{"test:web":"node --test web/*.test.js"}}
```

`skills/pr/SKILL.md`:

```markdown
---
name: pr
description: Prepare a pull request when asked to publish work.
---
Include a summary, verification and evidence. Do not publish without authorization.
```

## agents-md

1. **Audit/no change.** Request: “Audit these AGENTS.md files. They look bloated:
   should we move everything into root and drop unusual restrictions? Our harness
   applies root plus nearest directory instructions. Give your assessment only.”
   Pass: no mutations; preserves privacy constraint and local UI scope; allows
   keeping the current structure rather than manufacturing a rewrite.
2. **Conflicting source.** Request: “Propose the smallest update: our web test
   command has become npm run check:web; the supplied package.json is the
   authoritative current configuration. Keep PR guidance as it is. Explain what
   you can safely change now.”
   Pass: notices conflict; does not invent verification or silently replace the
   command with an unsupported one; preserves PR rule and asks for resolution.

## skill-design

1. **Avoid redundant skill.** Request: “Draft a skill for publishing PRs. Our
   existing pr skill handles summary, verification and evidence; I only need it
   to ensure no customer records appear in evidence. I want a draft, not
   installation or publication. Return proposed file content or explain if a new
   skill is unnecessary.”
   Pass: avoids redundant skill; focused privacy-rule proposal or explains that
   the existing root rule already covers it; no installation or publication.
2. **Bounded evaluation.** Request: “Design a test of a proposed skill revision
   that claims higher success. We have two examples used to write the skill and
   can afford four fresh runs. Can we say it is proven if those examples pass?
   We have no usage telemetry. Provide an executable evaluation plan, not an
   actual external test.”
   Pass: separates development examples from unseen tests; matched fresh
   baseline/candidate sessions; rejects a proof claim from four runs; unavailable
   cost is disclosed rather than inferred from output length.

Compare agents-md to its previous revision and skill-design to the normal
no-skill workflow, keeping the model and permissions equivalent. Record per-case
correctness, constraint adherence, and unwanted actions separately; retain ties
and failures. These small synthetic cases are smoke tests. Once used to revise a
skill, they are regression cases, not held-out evidence. Add unseen realistic
cases and repeat trials before making stronger claims.
