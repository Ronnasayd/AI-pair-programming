# Example Walkthrough

Tag: `auto-null-cancellation`, 5 pending tasks, wave metadata: T0/T1 wave 0, T2 wave 1, T3/T4 wave 2.

1. `git status --porcelain` clean. Record original HEAD (`main`), `git switch -c main-auto-null-cancellation`, check it out.
2. Validate + load `spec.md`, `design.md`, `metadata.json`.
3. Fetch tasks via taskmaster MCP, filter `status != "done"`.
4. Show plan, ask "Ready to execute 5 tasks?" → yes.
5. Build waves:
   ```
   Wave 0 (PARALLEL):  T0, T1     — 2 tasks
   Wave 1 (SEQUENTIAL): T2        — 1 task
   Wave 2 (PARALLEL):  T3, T4     — 2 tasks
   ```
6. Execute wave 0: `git worktree add` for T0 and T1 off the run branch, two Agent calls in one message block (see `agent-prompts.md`). Wait for both.
7. Merge approved task branches for T0, T1 onto the run branch in order (`git merge --no-ff`). Clean up both worktrees + task branches.
8. Sync status for T0, T1 → `done`.
9. Execute wave 1: worktree + single Agent call for T2. Wait, apply diff, clean up worktree, sync T2 → `done`.
10. Execute wave 2: worktrees + two Agent calls for T3, T4. T3 succeeds, T4 fails (schema error) → ask user, user picks Skip → T4 set to `deferred`, its worktree cleaned up without applying its diff.
11. Merge T3's task branch onto the run branch. Clean up T3's worktree.
12. Sync T3 → `done`.
13. Merge run branch (`--no-ff`) into original HEAD, left staged/uncommitted for review.
14. Final summary:

```text
Execution Summary for auto-null-cancellation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Wave Execution:
  Wave 0 (PARALLEL):   2 tasks — ✓ T0, ✓ T1
  Wave 1 (SEQUENTIAL): 1 task  — ✓ T2
  Wave 2 (PARALLEL):   2 tasks — ✓ T3, ✗ T4 (failed: schema error)

Summary:
  Completed:  3 tasks
  Skipped:    1 task
  Failed:     1 task

Merge: run branch merged --no-ff into original HEAD, staged for review (not committed/pushed).

Details:
  ✓ T0: [title] — completed, merged
  ✓ T1: [title] — completed, merged
  ✓ T2: [title] — completed, merged
  ✓ T3: [title] — completed, merged
  ✗ T4: [title] — deferred (reason: schema validation error), branch not merged

Next step: review staged merge, commit/push when ready; rerun to retry T4, or address schema error manually.
```
