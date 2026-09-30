# Output Template

Keep tables to files that matter: ≤ 10 rows per table, ranked by impact, not alphabetically.
Tables other than "Files to Modify" may be prose ("None found.") when empty.

```markdown
## Context Map

### Task Interpretation

- Restated task: ...
- Task type: feature | fix | refactor | config | docs
- Assumptions: ...
- Anchors: `symbol` (path) — confirmed by: semantic_search, grep

### Files to Modify

| File         | Purpose     | Changes Needed |
| ------------ | ----------- | -------------- |
| path/to/file | description | what changes   |

### Dependencies (may need updates)

| File        | Relationship                 |
| ----------- | ---------------------------- |
| path/to/dep | imports X from modified file |

### Test Files

| Test         | Coverage                     |
| ------------ | ---------------------------- |
| path/to/test | tests affected functionality |

### Reference Patterns

| File            | Pattern           |
| --------------- | ----------------- |
| path/to/similar | example to follow |

### Prior Decisions / Gotchas

- memory page or rule that constrains the change (omit if none)

### Risk Assessment

- [ ] Breaking changes to public API
- [ ] Database migrations needed
- [ ] Configuration changes required
- [ ] No test coverage for anchor(s)

### Not Checked

- areas skipped, depth cut-offs, stale/missing index, unverified paths
```
