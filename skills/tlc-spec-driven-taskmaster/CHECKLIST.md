Checklist for `tlc-spec-driven-taskmaster` skill, sequential:

1. **Validate tag** — check `.specs/features/{TAG}/spec.md` exists + matching tag in `.taskmaster/tasks/tasks.json`. Missing spec → stop, report. Missing taskmaster tag → tell user run `tlc-tasks-to-taskmaster` first, or proceed w/o sync.
2. **Read spec-driven skill** — read `skills/tlc-spec-driven/SKILL.md` + `references/implement.md` once. Load execution conventions (auto-sizing, batching threshold, Verifier contract).
3. **Run Execute phase** — invoke tlc-spec-driven's Execute unmodified (auto-sized: inline Small/Medium, sub-agent batch ~7-8 tasks Large/Complex, always-on Verifier). No wave-parallel, no worktree isolation, no extra evaluator loop.
4. **Sync taskmaster per unit** — after each task/batch commits, call `set_task_status` (tag required). Incremental, not batched at end.
5. **Sync on Verifier outcome** — PASS: tasks stay `done`. Gap found → fix task syncs back `pending`/`blocked`, re-sync `done` after fix commit.
6. **Sync docs** — invoke `generate-docs` (update mode) scoped to diff/commits, if warranted. Skip silently if no doc-worthy change.
7. **Summary** — report tlc-spec-driven output + taskmaster sync confirmation (ids updated) + docs sync outcome. User does final commit/push.

Status mapping: committed+gate pass → `done` | Verifier gap → `pending` | deferred → `deferred` | skipped → `cancelled` | blocked → `blocked`.
