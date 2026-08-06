---
name: tlc-tasks-to-taskmaster
description: Convert tasks.md spec files into TaskMaster JSON format (.taskmaster/tasks/tasks.json for task list, .taskmaster/execution/metadata.json for strategy). When only spec.md exists (no formal tasks.md, e.g. Small/Medium features where tlc-spec-driven's auto-sizing skipped the Tasks phase), derives one taskmaster task per requirement/acceptance-criterion from spec.md instead, purely for tracking/registry purposes. Use when user says "convert tasks.md to taskmaster json", "transform tasks.md to .taskmaster format", "converta tasks.md em tasks.json", "registra essa spec no taskmaster", or wants to generate TaskMaster JSON from a tasks or spec file. Do NOT use for creating task specs, executing tasks, or non-TaskMaster conversions.
metadata:
  author: Ronnasayd Machado - github.com/Ronnasayd
  version: 1.2.0
---

# tasks-md-to-taskmaster-json

Converts a `tasks.md` spec into two files: `.taskmaster/tasks/tasks.json` (TaskMaster-compatible task list, merge-safe) and `.taskmaster/execution/metadata.json` (execution strategy: waves, critical path, parallelization notes). Split keeps `tasks.json` TaskMaster-compatible while giving executor agents reasoning context without recomputing the graph.

When the feature only has `spec.md` (no `tasks.md` -- tlc-spec-driven's auto-sizing decided the feature is Small/Medium and skipped the Tasks phase), this skill still registers it in taskmaster for tracking, via the spec-only fallback (Step 0.5) -- taskmaster stays a complete progress log regardless of feature size, even though execution itself stays inline and unbatched for these features.

## Steps

| #   | Step                   | Action                                                                                                | Output / Gate                                                                                                   |
| --- | ---------------------- | ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| 0   | Resolve tag            | Ask user for root key tag (skip if given); default `"master"`                                         | tag stored for steps 6-7 — see [json-schemas.md](references/json-schemas.md) for wrapper shape                  |
| 0.5 | Check for tasks.md     | If `.specs/features/{TAG}/tasks.md` is missing but `spec.md` exists, switch to the spec-only fallback | See "Spec-only fallback" below — skip steps 1-4, go straight to Step 5 with synthetic tasks                     |
| 1   | Read tasks.md fully    | Read Execution Diagram, task tables, cross-checks before writing any JSON                             | diagram + cross-checks are source of truth, not just `Depends on` (which may omit transitive deps)              |
| 2   | Build dependency graph | Directed edges: `task_id → [deps]`                                                                    | validate every dep against the ASCII diagram                                                                    |
| 3   | Calculate waves (BFS)  | Wave 1 = no deps; Wave N+1 = deps all in waves ≤N                                                     | tasks in same wave have zero deps between each other — example in [json-schemas.md](references/json-schemas.md) |
| 4   | Identify critical path | Bottom-up traversal: longest sequential dependency chain                                              | determines minimum execution time                                                                               |
| 5   | Map fields             | Task → JSON schema                                                                                    | field mapping table in [json-schemas.md](references/json-schemas.md)                                            |
| 6   | Assemble output        | Build both files                                                                                      | schemas + examples in [json-schemas.md](references/json-schemas.md)                                             |
| 7   | Create + validate      | Run scripts (below)                                                                                   | both files must pass validation before delivery                                                                 |

## Spec-only fallback (Step 0.5)

For Small/Medium features with only `spec.md`:

1. Read `spec.md` fully -- extract every requirement ID and its acceptance criteria.
2. Create one synthetic task per requirement/AC: `title` = requirement summary, `description` = the AC text, `id` assigned sequentially in spec order.
3. All synthetic tasks go in `wave 1` with `dependencies: []` -- there is no real dependency graph to compute, this is a registry, not an execution plan.
4. `metadata.onCriticalPath` = `false` for all (no critical path concept applies).
5. `testStrategy` = `"none"` unless the AC itself specifies a test/verification method.
6. `metadata.json`'s `executionWaves` becomes `{ "wave1_serial": [all ids] }`, `criticalPath` = `[]`, `parallelizationNotes` notes this is a spec-only registry, not a real execution plan.
7. Proceed to Step 5 (field mapping is already done above) then Steps 6-7 unchanged.

### Step 7 commands

```bash
mkdir -p .taskmaster/tasks .taskmaster/execution
cp <skill-path>/index.html .taskmaster/index.html   # Kanban viewer, static asset

python3 <skill-path>/scripts/merge-tasks.py \
  .taskmaster/tasks/tasks.json "<tag>" '<tasks_json_string>'

# metadata.json is execution-wide — direct overwrite is safe (no merge needed)

python3 <skill-path>/scripts/validate-tasks.py tasks .taskmaster/tasks/tasks.json
python3 <skill-path>/scripts/validate-tasks.py metadata .taskmaster/execution/metadata.json
```

- `merge-tasks.py` preserves all existing tags while adding/updating the new one.
- If validation fails, fix and re-validate before confirming delivery.

## Final Checklist

### tasks.json

- [ ] All tasks.md tasks present (count matches) -- or, for spec-only fallback, all requirement/AC ids present
- [ ] `dependencies` are integer ids, not `"T01"` strings
- [ ] Same-wave tasks have zero deps between each other
- [ ] `testStrategy` non-empty where tests exist
- [ ] `priority: "high"` only for critical-path/system-blocking tasks
- [ ] Each task has `metadata: { wave, onCriticalPath }`
- [ ] Valid JSON (`validate-tasks.py tasks` passes)
- [ ] New tag merged without overwriting existing tags
- [ ] Root key = resolved tag (default `"master"`); `tasks` nested under it, no global metadata

### metadata.json

- [ ] Critical path matches longest diagram chain -- or `[]` for spec-only fallback
- [ ] `executionWaves` keys use `waveN_serial` / `waveN_parallel`
- [ ] All wave task IDs match tasks.json
- [ ] `criticalPath` is array of ints
- [ ] `parallelizationNotes` explains each wave bottleneck -- or notes spec-only registry for fallback
- [ ] `source` points to original tasks.md or spec.md relative path
- [ ] Valid JSON (`validate-tasks.py metadata` passes), ISO-8601 timestamps

## Reference files

- [references/json-schemas.md](references/json-schemas.md) — tag wrapper, field mapping table, wave/critical-path examples, full tasks.json + metadata.json schema examples
- [references/walkthrough-example.md](references/walkthrough-example.md) — end-to-end worked example (input → actions → result)
