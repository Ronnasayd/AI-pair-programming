---
name: tlc-tasks-to-taskmaster
description: Converts a tasks.md spec file into TaskMaster-compatible structure with two outputs — .taskmaster/tasks/tasks.json (task list with task-level metadata) and .taskmaster/execution/metadata.json (global execution strategy). Use when user says "converta tasks.md em tasks.json", "transforme tasks.md em .taskmaster/tasks/tasks.json", "gere o tasks.json a partir do tasks.md", "convert task spec to taskmaster json", or "turn this tasks file into taskmaster format". Do NOT use for creating tasks.md specs (use create-task-spec), executing tasks (use execute-task), or any other conversion.
license: CC-BY-4.0
metadata:
  author: Ronnasayd Machado - github.com/Ronnasayd
  version: 1.0.0
---

# tasks-md-to-taskmaster-json

Converts a `tasks.md` specification file into a TaskMaster-compatible structure:

1. **`.taskmaster/tasks/tasks.json`** — task list with task-level metadata (wave, onCriticalPath)
2. **`.taskmaster/execution/metadata.json`** — global execution strategy (waves, critical path, parallelization notes)

This two-file approach keeps `tasks.json` TaskMaster-compatible while providing execution context for agents.

## Instructions

### Step 0 — Resolve the output tag

Before reading or processing anything, determine the **tag** that will wrap the output JSON.

- If the user explicitly provided a tag (e.g. `"use tag feature/auth"`), use it verbatim.
- Otherwise, ask the user:

  > What tag should be used as the root key in `tasks.json`? (default: `master`)

- If the user does not answer or confirms the default, use `"master"`.

The tag will be the root key in `.taskmaster/tasks/tasks.json`:

```json
{
  "<tag>": {
    "tasks": [...]
  }
}
```

Example with default tag:

```json
{
  "master": {
    "tasks": [...]
  }
}
```

(Global metadata goes in separate file `.taskmaster/execution/metadata.json` — see Step 6.)

Store the resolved tag for use in Steps 6 and 7.

### Step 1 — Read the entire tasks.md before writing anything

Read `tasks.md` from start to finish. You need three sections before starting conversion:

- **Execution Diagram** (the ASCII dependency graph)
- **Tables for each task** (fields: What, Where, Depends on, Tests, Done when, Gate, Cmd)
- **Cross-checks at the end** (diagram × definition validation)

Do not generate any JSON before reading everything. The diagram and cross-checks are the source of truth for dependencies — not just the `Depends on` field, which sometimes omits transitive dependencies.

### Step 2 — Build the dependency graph

Construct a directed edge structure:

```
task_id → [dependencies]
1  → []
2  → [1]
3  → [1]
4  → [3]
...
```

Validate against the ASCII diagram. If the `Depends on` field says `T02, T10, T08, T12, T16` for T18, confirm all 5 appear in the diagram downstream from T18's position.

### Step 3 — Calculate execution waves (BFS / topological sort)

Algorithm:

1. Wave 1 = tasks with no dependencies
2. Wave N+1 = tasks whose **all** dependencies are already in waves ≤ N
3. Repeat until all tasks are assigned

Example output:

```
Wave 1:  T01             (no deps)
Wave 2:  T02, T03, T11, T26   (deps = {T01})
Wave 3:  T04, T05, T07        (T04→{T03}, T05+T07→{T02})
Wave 4:  T06, T09, T10, T14, T16
Wave 5:  T08, T13, T15, T17, T19, T21
Wave 6:  T12             (convergence bottleneck)
Wave 7:  T18, T20
Wave 8:  T22, T25
Wave 9:  T23, T27
Wave 10: T24, T28, T29
```

Tasks in the same wave must have zero dependencies between each other.

### Step 4 — Identify the critical path

The critical path is the longest chain of sequential dependencies — it determines minimum execution time.

Traverse the graph bottom-up: for each task, add 1 to the maximum critical path length of its dependents.

The critical path is the longest such chain, e.g.: `T01 → T02 → T05 → T06 → T08 → T12 → T20 → T22 → T23 → T24`.

### Step 5 — Map each task to JSON schema

| JSON field     | Source in tasks.md                                                                                     |
| -------------- | ------------------------------------------------------------------------------------------------------ |
| `id`           | Task number (T01 → 1, T26 → 26)                                                                        |
| `title`        | Part after `—` in the section heading                                                                  |
| `description`  | **What** field                                                                                         |
| `status`       | Always `"pending"`                                                                                     |
| `priority`     | `"high"` if on critical path or system-blocking; `"medium"` otherwise; `"low"` for optional/peripheral |
| `dependencies` | **Depends on** field converted to array of ints                                                        |
| `details`      | Combine: **Where** + **Done when** + **Gate** + **Cmd**                                                |
| `testStrategy` | **Tests** field — describe test cases if present; `"none"` if absent                                   |
| `subtasks`     | Always `[]`                                                                                            |
| `metadata`     | Object with `wave` (number) and `onCriticalPath` (boolean)                                             |

### Step 6 — Assemble the full output structure

Generate **two files** with complementary data:

#### File 1: `.taskmaster/tasks/tasks.json` (TaskMaster-compatible)

Wrap `tasks` under the tag resolved in Step 0. **No global metadata**:

```json
{
  "<tag>": {
    "tasks": [
      {
        "id": 1,
        "title": "...",
        "description": "...",
        "status": "pending",
        "priority": "high",
        "dependencies": [],
        "details": "...",
        "testStrategy": "...",
        "subtasks": [],
        "metadata": {
          "wave": 1,
          "onCriticalPath": true
        }
      }
    ]
  }
}
```

#### File 2: `.taskmaster/execution/metadata.json` (Execution metadata)

Global aggregated execution data:

```json
{
  "projectName": "feature-name-from-tasks-md",
  "version": "1.0.0",
  "createdAt": "ISO-8601 date",
  "updatedAt": "ISO-8601 date",
  "description": "One-line summary from tasks.md header",
  "source": "relative/path/to/tasks.md",
  "testCommands": {
    "unit": "yarn jest ...",
    "integration": "yarn jest ..."
  },
  "executionWaves": {
    "wave1_serial": [1],
    "wave2_parallel": [2, 3, 11, 26],
    "...": []
  },
  "criticalPath": [1, 2, 5, 6, 8, 12, 20, 22, 23, 24],
  "parallelizationNotes": {
    "wave2": "T02, T03, T11, T26 all depend only on T01 — safe to run in parallel",
    "wave6": "T12 is a sequential bottleneck: first task needing both T08 and T04"
  }
}
```

**Purpose**: Global metadata is the reasoning memory — executor agent reads this for parallelization strategy without recalculating the graph. Task-level metadata keeps tasks.json TaskMaster-compatible.

### Step 7 — Create files and validate

```bash
mkdir -p .taskmaster/tasks .taskmaster/execution

# Write tasks.json (TaskMaster-compatible)
# Validate JSON syntax
cat .taskmaster/tasks/tasks.json | python3 -m json.tool > /dev/null

# Write metadata.json (execution data)
# Validate JSON syntax
cat .taskmaster/execution/metadata.json | python3 -m json.tool > /dev/null
```

If JSON validation fails, fix syntax errors and re-validate before presenting the result. Both files must be valid.

## Final Checklist

Before confirming delivery, verify:

### `.taskmaster/tasks/tasks.json`

- [ ] All tasks from tasks.md have an entry (count must match)
- [ ] `dependencies` for each task are **integer ids** (not strings like "T01")
- [ ] Tasks in the same wave have zero dependencies between each other
- [ ] `testStrategy` is non-empty for tasks with tests
- [ ] `priority: "high"` only for critical path tasks or system-blocking tasks
- [ ] **Each task has `metadata: { wave: N, onCriticalPath: boolean }`**
- [ ] JSON is valid (`python3 -m json.tool` passes)
- [ ] Root key matches the resolved tag (default: `"master"`)
- [ ] `tasks` nested under tag key — **no global metadata**

### `.taskmaster/execution/metadata.json`

- [ ] Critical path matches the longest chain in ASCII diagram
- [ ] `executionWaves` keys use format `waveN_serial` or `waveN_parallel`
- [ ] All task IDs in waves match tasks in tasks.json
- [ ] `criticalPath` is array of integers
- [ ] `parallelizationNotes` explains each wave bottleneck
- [ ] `source` points to original tasks.md relative path
- [ ] JSON is valid (`python3 -m json.tool` passes)
- [ ] File exists at `.taskmaster/execution/metadata.json`

## Example

**Input:** User says "transforme `.specs/features/auth-keycloak/tasks.md` em `.taskmaster/tasks/tasks.json`"

**Actions:**

1. Ask: "What tag should be used as the root key?" → user says `"master"` (or skips → default `"master"`)
2. Read `.specs/features/auth-keycloak/tasks.md` completely
3. Extract the ASCII execution diagram and all task tables
4. Build dependency graph edges (T01→[], T02→[1], T03→[1], ...)
5. Run BFS to assign waves: wave1=[1], wave2=[2,3,11,26], ...
6. Identify critical path by traversing graph bottom-up
7. Map each task to JSON fields following Step 5 table (include `metadata: { wave, onCriticalPath }`)
8. Build two files:
   - **`.taskmaster/tasks/tasks.json`** — TaskMaster structure (no global metadata)
   - **`.taskmaster/execution/metadata.json`** — execution summary (waves, critical path, parallelization notes)
9. Write both files and validate with `python3 -m json.tool`

**Result:**

- `.taskmaster/tasks/tasks.json` — TaskMaster-compatible with task-level metadata
- `.taskmaster/execution/metadata.json` — executor can read global execution strategy without parsing individual tasks
