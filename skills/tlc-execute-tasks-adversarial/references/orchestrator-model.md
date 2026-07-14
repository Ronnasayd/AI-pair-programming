# Main-Agent-as-Orchestrator Model

When executing PARALLEL waves (2+ independent tasks), the main agent coordinates directly — no intermediate orchestration skill:

1. **Wave Grouping**: Pending tasks are grouped by `metadata.wave` from metadata.json
2. **Direct Dispatch**: For each wave with 2+ tasks, the main agent calls the Agent tool once per task, all in a single message, so they run concurrently
3. **Execution Context**: Each subagent receives:
   - Task object (id, title, description, dependencies)
   - Full spec.md content (problem statement, goals, requirements)
   - Full design.md content (architecture, complexity, scope)
   - TAG value and any coding conventions
   - metadata.json is NOT passed — it's orchestrator-only (waves, critical path, dependencies live at the main-agent level, not needed for a single task's execution)
4. **Self-Contained Execution**: Each subagent runs `tlc-spec-driven` with `mode="execute"` for its single task, independently; it does NOT need to consult the main thread
5. **Wave Synchronization**: The main agent waits for every subagent in a wave to return before it fires the next wave's Agent calls
6. **Status Reporting**: After each wave completes, the main agent sends status updates to taskmaster via `set_task_status` with the `tag` parameter
7. **Single-Task Waves**: Waves with only 1 task (or no wave metadata) still go through one Agent call — same self-contained context, just no need to batch calls

**Performance benefit**: Multi-task waves execute in true parallel (wall-clock time = longest task, not sum of all tasks).
