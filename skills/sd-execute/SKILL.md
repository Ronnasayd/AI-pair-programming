---
name: sd-execute
description: "Thin wrapper around tlc-spec-driven's Execute phase that adds taskmaster status sync. Main agent reads tlc-spec-driven/SKILL.md, runs its normal Execute flow (implement.md, auto-sized batching, always-on Verifier) unmodified, and after each task/batch calls taskmaster's set_task_status so the taskmaster tag mirrors real progress. Taskmaster is a read-only dashboard here -- it never drives what gets executed or in what order; tlc-spec-driven's own auto-sizing and batching decide that. Use: 'execute feature <tag>' or run tasks for <tag> when the feature already has a taskmaster tag to keep in sync. Do not use for direct task management (taskmaster skill), spec creation (tlc-spec-driven), or when there is no taskmaster tag to sync (just call tlc-spec-driven directly)."
metadata:
  author: Ronnasayd Machado - github.com/Ronnasayd
  version: "2.0.0"
---

# Execute Feature Tasks

Taskmaster is a mirror, not a driver. This skill does not reimplement execution -- it calls tlc-spec-driven's Execute phase exactly as documented in its own references/implement.md (auto-sized: inline for Small/Medium, sub-agent batching of ~7-8 tasks for Large/Complex, single always-on Verifier at the end), and layers one thing on top: syncing task status to taskmaster after each unit of work completes, so the taskmaster tag stays an accurate read-only log of what's done.

No wave-parallel dispatch, no worktree isolation, no adversarial per-task evaluator loop -- tlc-spec-driven's own batching and Verifier already cover reliability; duplicating that logic here only causes drift between the two.

## Steps

Add the following steps as tasks using the `TaskCreate`, `TaskUpdate`, `TaskGet`, and `TaskList` tools. Update the status as you progress through each step to keep the user informed.

| #   | Step                                      | Action                                                                                                                                                                                                               | Output / Gate                                                                                                                                    |
| --- | ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Validate tag                              | Confirm `.specs/features/{TAG}/spec.md` exists (design.md/tasks.md optional per auto-sizing) and a matching tag exists in `.taskmaster/tasks/tasks.json`                                                             | Missing spec.md -> report, stop. Missing taskmaster tag -> tell user to run `sd-insert-taskmaster` first, or proceed without sync if they prefer |
| 2   | Read spec-driven skill                    | Read `skills/tlc-spec-driven/SKILL.md` and its `references/implement.md` once                                                                                                                                        | Execution conventions loaded -- auto-sizing, batching threshold, Verifier contract                                                               |
| 3   | Run Execute phase                         | Invoke tlc-spec-driven's Execute exactly as documented -- no modification. Sub-agent batching offer, atomic commits, gate-before-done, Verifier at the end all apply unchanged                                       | Feature implemented and verified per tlc-spec-driven's own contract                                                                              |
| 4   | Sync taskmaster after each completed unit | As each task (inline mode) or batch (sub-agent mode) finishes and its commit lands, call `set_task_status` for the corresponding taskmaster id(s) -- `tag` is required, omitting it silently no-ops                  | Taskmaster tag reflects real progress incrementally, not batched at the very end                                                                 |
| 5   | Sync on Verifier outcome                  | Verifier PASS -> tasks stay `done`. Verifier flags a gap that becomes a fix task -> sync that task back to `pending` (or `blocked` if user chooses not to fix now), then re-sync to `done` once the fix commit lands | Taskmaster reflects fix-loop iterations, not just the first pass                                                                                 |
| 6   | Sync docs                                 | Invoke `generate-docs` skill in **update mode**, scoped to the diff/commits produced by this run, if the changes warrant a docs update                                                                               | `docs/` reflects the implemented feature -- skip silently if `generate-docs` determines no doc-worthy changes occurred                           |
| 7   | Summary                                   | Report what tlc-spec-driven reported, plus taskmaster sync confirmation (ids updated) and docs sync outcome                                                                                                          | User does the final commit/push -- tlc-spec-driven's own contract, unchanged here                                                                |

## Status mapping

| Outcome                             | `set_task_status` value        |
| ----------------------------------- | ------------------------------ |
| Task committed and gate passed      | `done`                         |
| Verifier found a gap, fix pending   | `pending` (revert from `done`) |
| User chose not to fix / deferred    | `deferred`                     |
| Task skipped by user decision       | `cancelled`                    |
| Task blocked on external dependency | `blocked`                      |

## Reference files

- `references/troubleshooting.md` -- common failure symptoms and fixes
