---
name: land
description: Implement requested work, verify and review it, then commit it green.
disable-model-invocation: true
---

Implement the work the user requests, using any supplied plan, spec, ticket, or acceptance criteria.

Honour the requested scope, acceptance criteria, constraints, exclusions, and verification requirements. Where absent, derive observable success/boundary examples from the request and use the repository's checks. Ask only where ambiguity changes the outcome. Green means checks pass, acceptance is demonstrated, constraints hold, and blocking review findings are resolved.

Record the fixed point the review pins against with `git rev-parse HEAD 2>/dev/null || git hash-object -t tree /dev/null`, which yields the empty tree in a repository whose first commit has not landed. Record `git status --porcelain` too when the tree is already dirty.

Run the cheapest relevant baseline check. Use `tdd` where possible, at pre-agreed seams. Run focused checks regularly and the full relevant suite at the end; exercise the API or UI when needed to prove acceptance.

Reconcile discoveries before dependent implementation or commit. Correct internal implementation choices within approved constraints; ask before changing approved behaviour, public contracts, persistent data, security/privacy, deployment, external services, ongoing cost, or an expensive-to-reverse choice.

Once done, use `code-review`, passing the fixed point, any dirty snapshot, the complete work contract, and verification evidence. Fix blocking findings and rerun affected verification so the committed changes are verified.

Commit your work to the current branch. A fact worth keeping past this work goes into the code, a test, or the commit message.

If blocked, preserve the baseline, owned changes, and evidence; report the missing prerequisite or decision. Commit only work meeting the green criteria.
