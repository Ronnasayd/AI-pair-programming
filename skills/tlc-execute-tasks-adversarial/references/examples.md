# Examples

## Execute auto-null-cancellation (wave-parallel, adversarial loop)

**User:** `tag="auto-null-cancellation"`

1. Validate + load spec.md/design.md/metadata.json.
2. Taskmaster → [T0, T1, T2, T3] pending.
3. Wave groups: Wave 0 PARALLEL (T0, T1), Wave 1 SEQUENTIAL (T2, T3).
4. Plan shown, user confirms yes.
5. **Wave 0**: spawn executor+evaluator pairs for T0, T1 in one message. Each pair loops (exec→eval→score) independently.
   - T0: iteration 1, score 9 → APPROVED.
   - T1: iteration 1 score 5 (CONDITIONAL) → relay findings, iteration 2 score 8 → APPROVED.
   - Apply both worktree diffs sequentially, no conflicts. `set_task_status` T0/T1 → done.
6. **Wave 1** (sequential, no worktree):
   - T2: iteration 1-2 score stuck at 5, same finding both rounds → stagnation. Ask user R/S/A → user picks Skip. Status = cancelled.
   - T3: iteration 1 score 9 → APPROVED. Status = done.
7. Summary: "Wave 0: 2/2 done. Wave 1: 1/2 done, 1 skipped (stagnation). Total: 3/4."

**Result:** taskmaster updated per-wave; user retry/skip/abort only invoked on cap/stagnation, not on ordinary rejections mid-loop.
