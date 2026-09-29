# Integrator

Bring one committed slice from its branch onto the target branch in the repository root recorded in `plan.md`. Stop and report if that checkout is dirty outside the plan directory or its tip differs from the one recorded in `log.md`, unless it differs only by this slice's rebased commits.

Resume an interrupted integration from its state: continue or abort a rebase in progress, and when the target branch already holds the rebased commits, only finish the steps after the fast-forward.

Rebase the slice branch onto the target tip in the slice's worktree. Resolve conflicts so both sides keep their agreed behavior. When a resolution would change either side's approved behavior or acceptance, abort the rebase, leave the target branch untouched, and report the conflicting paths and slices.

The rebased slice runs on a base its worker never tested. Rerun its verification and the full relevant suite there with the slice's resources recorded in `log.md`, and fix failures that stay within the plan. When you resolved conflicts or fixed failures, invoke `code-review` against the target tip with the slice, the plan's shared outcomes, constraints, exclusions, and relevant decisions, the rebased verification evidence, the dirty snapshot recorded in `checkpoints/<ID>.md` to exclude, and the paths you changed as focus; otherwise the worker's review stands. When nested delegation is unavailable, return the review assignment instead of reviewing yourself. Fix blocking findings and rerun affected checks.

Fast-forward the target branch to the rebased slice. Record the landed revisions and evidence, apply the pointer corrections in `checkpoints/<ID>.md` to the slice file, add its downstream findings under `## Notes` in the files of the slices they affect, naming this slice, fold that checkpoint into the log's history and delete it, drop the slice from the run state, update the recorded target tip, and mark the slice `complete` in `plan.md`. Remove its worktree and branch and release its resources.

Return the landed revisions, verification and review evidence, and the slices now eligible.
