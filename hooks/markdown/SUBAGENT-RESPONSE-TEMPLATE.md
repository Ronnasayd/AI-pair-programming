## Response format (mandatory) — follow when returning to main agent

```
status: success | failure | partial
summary: 1-2 line what got done
files_changed: [list paths, empty if none]
reason: (only if failure/partial) root cause, short
evidence: (optional) test output, command result, diff snippet proving claim
gateways: (optional, define your own) checklist you set for this task, pass/fail per gate
next_steps: (optional) what main agent should do next, if anything
```

- `status`: tri-state, not binary. `partial` = did some, blocked on rest.
- `files_changed`: always present, even empty. Lets main agent verify scope stayed bounded.
- `reason`: only show when status != success. No noise on happy path.
- `evidence`: proof over claim — test pass/fail, lint output, whatever backs the status.
- `gateways`: your own checklist (e.g. "no lint errors", "tests pass", "no unused vars touched"), each with pass/fail. Free-form key-value, you pick keys relevant to your task.
- `next_steps`: blocker handoff or suggestion for main agent.
