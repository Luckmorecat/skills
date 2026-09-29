# Worker

Complete one slice in its worktree. Read the supplied `next-slice/SKILL.md`, resolving its relative links from its directory, and follow it for this slice only, with these changes:

- The worktree is a deliberate checkout change, and the supplied base revision is its fixed point.
- Keep the checkpoint `next-slice` keeps in `log.md` in `checkpoints/<ID>.md` in the plan directory, together with stale-pointer corrections and the downstream findings `next-slice` would add to other slice files; leave every other plan file untouched. The slice is already `in-progress`; it is new unless that file holds a checkpoint.
- Commit to the slice branch and stop without marking the slice `complete`; it completes only when integrated.
- Before recording the dirty snapshot, prepare the worktree as a fresh checkout needs without changing tracked files, such as with a frozen-lockfile install; report when you cannot. Use only the resources assigned to you.
- Never ask the user directly: where `next-slice` or its recovery would ask or resolve an uncertainty with the user, or hand back to `slice`, checkpoint and report the question or blocker instead.
- When nested delegation is unavailable, return required subagent assignments with their context instead of substituting self-review, and resume with their results.

Return your outcome, evidence, slice-branch commits, checkpoint file, remaining blockers, and findings for `slice`.
