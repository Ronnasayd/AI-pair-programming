# Example Walkthrough

Tag: `auto-null-cancellation`, 5 pending tasks, wave metadata: T0/T1 wave 0, T2 wave 1, T3/T4 wave 2.

1. Validate + load `spec.md`, `design.md`, `metadata.json`.
2. Fetch tasks via taskmaster MCP, filter `status != completed`.
3. Show plan, ask "Ready to execute 5 tasks?" → yes.
4. Build waves:
   ```
   Wave 0 (PARALLEL):  T0, T1     — 2 tasks
   Wave 1 (SEQUENTIAL): T2        — 1 task
   Wave 2 (PARALLEL):  T3, T4     — 2 tasks
   ```
5. Execute wave 0: two Agent calls in one message block, both running `tlc-spec-driven` (see `agent-prompts.md`). Wait for both.
6. Sync status for T0, T1 → `done`.
7. Execute wave 1: single Agent call. Wait, sync T2 → `done`.
8. Execute wave 2: two Agent calls. T3 succeeds, T4 fails (schema error) → ask user, user picks Skip → T4 set to `deferred`.
9. Sync T3 → `done`.
10. Final summary:

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

Details:
  ✓ T0: [title] — completed
  ✓ T1: [title] — completed
  ✓ T2: [title] — completed
  ✓ T3: [title] — completed
  ✗ T4: [title] — deferred (reason: schema validation error)

Next step: rerun to retry T4, or address schema error manually.
```
