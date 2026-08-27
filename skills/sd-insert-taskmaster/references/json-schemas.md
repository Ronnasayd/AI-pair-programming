# JSON Schemas & Examples

## tasks.json tag wrapper

```json
{
  "<tag>": {
    "tasks": [...]
  }
}
```

Default tag `"master"` if user doesn't specify one.

## Wave calculation example

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

Critical path traversal example: `T01 → T02 → T05 → T06 → T08 → T12 → T20 → T22 → T23 → T24`

## Task field mapping

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

## Full task entry example (tasks.json)

```json
{
  "<tag>": {
    "tasks": [
      {
        "id": 1,
        "title": "...",
        "description": "...",
        "status": "pending",
        "priority": "...",
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

**IMPORTANT**: Do NOT overwrite `tasks.json` directly. Use `scripts/merge-tasks.py` to preserve existing tags.
