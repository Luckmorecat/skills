# Integrator

Bring one committed slice from its branch onto the target branch in the repository root recorded in `plan.md`. Stop if that checkout is dirty outside the plan directory or its tip differs from the one recorded in the run state, in `log.md`'s current checkpoint, unless it differs only by this slice's rebased commits.

Resume an interrupted integration from its state: continue or abort a rebase in progress, and when the target branch already holds the rebased commits, only finish the steps after the fast-forward.

Rebase the slice branch onto the target tip in the slice's worktree. Resolve conflicts so both sides keep their approved behavior. When a resolution would change either side's approved behavior or acceptance, abort the rebase and stop.

Rerun the slice's verification and the full relevant suite on the rebased branch, with the slice's resources recorded in the run state, and fix failures whose fix stays within the plan. When you resolved conflicts or fixed failures, invoke `code-review` against the target tip with the slice, the plan's shared outcomes, constraints, exclusions, and relevant decisions, the rebased verification evidence, the dirty snapshot recorded in `checkpoints/<ID>.md` to exclude, and the paths you changed as focus; otherwise the worker's review stands. If you cannot delegate further, return the review assignments with their context, so review stays independent, and continue with their results. Fix blocking findings and rerun affected checks.

Fast-forward the target branch to the rebased slice, then:

1. record the landed revisions and evidence;
2. apply the pointer corrections in `checkpoints/<ID>.md` to the slice file;
3. add its downstream findings under `## Notes` in the files of the slices they affect, naming this slice;
4. fold that checkpoint into the log's history and delete it;
5. drop the slice from the run state and update the recorded target tip;
6. mark the slice `complete` in `plan.md`;
7. remove its worktree and branch and release its resources.

Return one of: the landed revisions, verification and review evidence, and the slices now eligible; or why you stopped (dirty checkout, tip mismatch, a conflict that changes approved behavior, or a failure outside the plan), with the conflicting paths and slices or the failing checks.
