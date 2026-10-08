# Worker

Implement, verify, and commit one slice in its worktree. Read the supplied `next-slice/SKILL.md`, resolving its relative links from its directory, and follow it for this slice only, with these changes:

- The worktree is a deliberate checkout change, and the supplied base revision is its fixed point.
- Write the checkpoint `next-slice` would write to `log.md` to `checkpoints/<ID>.md` in the plan directory instead, along with stale-pointer corrections and the downstream findings `next-slice` would add to other slice files. That file is your only write in the plan directory. The slice is already `in-progress`; it is new unless that file holds a checkpoint.
- Commit to the slice branch and stop; the integrator marks the slice `complete`.
- Before recording the dirty snapshot, bootstrap the worktree without changing tracked files (for example, a frozen-lockfile install); report if you cannot. Use only the resources assigned to you.
- Where `next-slice` or `RECOVERY.md` would settle a choice with the user or hand back to `slice`, checkpoint and return the question or blocker instead.
- If you cannot delegate further, return each subagent assignment you need with its context, so review stays independent, and continue with their results.

Return your outcome, evidence, slice-branch commits, checkpoint file, and any questions, blockers, or findings for `slice`.
