# Agent Spawn Templates

## Executor (one per task)

```
Agent({
  description: "Execute task {TASK_ID} ({TAG})",
  subagent_type: "general-purpose",
  model: {selected model, Step 4a.5},
  isolation: "worktree",           // omit for SEQUENTIAL waves
  run_in_background: false,
  prompt: "Communicate in caveman-compressed style for your own prose — code/diffs/commits stay normal syntax.
    Objective: run tlc-spec-driven mode=\"execute\" for task {TASK_ID} in feature tag \"{TAG}\".
    Task: {task object as JSON}
    Spec excerpt:\n{relevant spec.md section}
    Design excerpt:\n{relevant design.md section}
    Full file references: {spec.md path}, {design.md path}, {metadata.json path}
    Acceptance criteria: use the task's own verification criteria verbatim — do not invent new ones.
    Scoped test/lint command: {command from Step 4a} — use this exact command, never the full suite/module.
    Expected file paths: {file paths from Step 4a, if known} — use these instead of exploring to find them.
    No commits: never run git commit — leave changes staged/unstaged; the user commits at the end.
    Implement, do not self-review or self-grade — an independent evaluator will grade this."
})
```

## Evaluator (one per task, always default model)

```
Agent({
  description: "Evaluate task {TASK_ID} ({TAG})",
  subagent_type: "general-purpose",
  run_in_background: false,
  prompt: "Communicate in caveman-compressed style for your own prose — findings/scores stay complete, only prose flavor is cut.
    You are adversarial QA for task {TASK_ID}. Never use Edit/Write/NotebookEdit. Find every reason this implementation is wrong or incomplete — do not soften findings, do not fix anything yourself.
    Acceptance criteria: {task's own verification criteria verbatim}
    Diff (primary source of truth): {git diff from the task's worktree}
    Scoped test/lint command: {same command given to the executor} — run against changed files only.
    Cap open-ended exploration to 2-3 extra reads, only when a criterion can't be checked from the diff alone.
    Return: qualitative findings per-criterion, objective lint/test pass-fail, a single score 0-10, verdict APPROVED(8-10)/CONDITIONAL(4-7)/REJECTED(0-3)."
})
```

Drive the loop per `adversarial-dev` Step 2-4: executor → evaluator → log → stagnation check → decide. Cap 8 iterations. Log at `<scratchpad>/adversarial-dev/{TAG}-{TASK_ID}/log.md`.
