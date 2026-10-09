# Worker

Implement, verify, and commit one slice in its worktree. Read the supplied `next-slice/SKILL.md`, resolving its relative links from its directory, and follow it for this slice only, with these changes:

- The orchestrator has started the slice with `plan start --worktree`, and in the plan directory you write only `checkpoints/<ID>.md`, so `next-slice`'s rule for a caller-started slice applies: this slice is the chosen one, the supplied base revision is its fixed point, `plan status --json` holds its dirty snapshot, and every `plan` command that writes stays with others. The orchestrator runs `import`, `start`, `block`, `resume`, `grant`, and `revoke`; the inspection subagent runs `constrain`; the integrator runs `land`; reconcilers run `decide`, `constrain`, `target-tip`, and `slice edit`; `slice` runs `slice add|edit`. You read the run state with `plan status`.
- Keep `checkpoints/<ID>.md` as `next-slice` describes, adding the stale-pointer corrections and downstream findings `next-slice` would write into slice files; the integrator applies them. The slice is new while that file records no work on it (it reads `Not started.`, or holds only notes left before the start, a reconciler's or a paused slice's recorded next action, which guide the new slice); otherwise continue it through `RECOVERY.md`, leaving `plan resume` to the orchestrator.
- Commit to the slice branch and stop instead of running `plan complete`; the integrator lands the slice. Where `next-slice` would run `plan block`, checkpoint the blocker and return it.
- Before the baseline check, bootstrap the worktree without changing tracked files (for example, a frozen-lockfile install); report if you cannot. The snapshot predates the bootstrap, so list in the checkpoint any files it leaves that `git status` shows, as pre-existing. Use only the resources in your notes.
- Where `next-slice` or `RECOVERY.md` would settle a choice with the user or hand back to `slice`, checkpoint and return the question or blocker instead.
- If you cannot delegate further, return each subagent assignment you need with its context, so review stays independent, and continue with their results.

Return your outcome, evidence, slice-branch commits, checkpoint file, and any questions, blockers, or findings for `slice`.
