---
name: land
description: Implement a piece of work in one session and commit it green. Use when the user describes work to build now, or names a brief, plan, spec, or tickets to build from.
disable-model-invocation: true
---

Implement the work the user asks for, together with any plan, brief, spec, or tickets they name.

Honour whatever scope and verification they state: a **Build** is the contract, an **Out of scope** is the boundary even when an excursion looks cheap, a **Verify** is what proves the work green. Where they state none, build the smallest complete scope the request needs and verify with the repository's own checks. Ask only where the ambiguity would change what you build.

Record the fixed point the review pins against with `git rev-parse HEAD 2>/dev/null || git hash-object -t tree /dev/null`, which yields the empty tree in a repository whose first commit has not landed. Record `git status --porcelain` too when the tree is already dirty.

Use `tdd` where possible, at pre-agreed seams. Run typechecking and single test files regularly, and the full suite once at the end.

Once done, use `code-review`, passing the recorded fixed point, the snapshot if you took one, and the request with anything the user named. Fix every blocking finding and rerun the verification in full, so the tree you commit is the tree you verified.

Commit your work to the current branch. A fact worth keeping past this work goes into the code, a test, or the commit message.

Work that grew past one green state did not belong here. Say so, and hand what remains to `settle`.
