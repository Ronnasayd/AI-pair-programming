# Troubleshooting

### Error: "Tag directory not found"

**Cause:** `@.specs/features/{TAG}/` does not exist or the naming does not match.

**Solution:** Verify the tag format (kebab-case) and ensure the spec files exist in the project. Check `@docs/feature-verification-process.md` for the expected structure.

---

### Error: "Taskmaster MCP returned empty tasks array"

**Cause:** The tag exists but has no tasks in taskmaster, or the tag is not recognized by MCP.

**Solution:** Fall back to `@.specs/features/{TAG}/tasks.md` if it exists. Parse it manually (T0, T1, T2, ...). If no tasks.md exists either, ask the user whether the tag is correct.

---

### Error: "tlc-spec-driven failed to execute task"

**Cause:** A task execution error occurred in tlc-spec-driven (code error, test failure, etc.).

**Solution:** Show the error to the user and let them choose `[R]etry`, `[S]kip`, or `[A]bort`. Retry executes the same task again. Skip marks it as `"skipped"` and continues. Abort stops execution.

---

### Error: "Taskmaster MCP set_task_status failed"

**Cause:** MCP connection issue, invalid task ID, or missing `tag` parameter.

**Solution:** Log the error and continue execution (do not block on status updates). Ensure `tag` parameter is always passed to set_task_status. Report it in the summary:

```text
Note: some status updates may not have synchronized with taskmaster. Please verify manually.
Verify via: taskmaster list --tag={TAG}
```
