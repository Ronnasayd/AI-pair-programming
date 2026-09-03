---
model: sonnet
---

Verify that a Claude Code hook script actually works end to end. Argument: the hook script path (e.g. `hooks/scripts/jest_coverage_report.py`) or its name.

Do this:

1. **Read the hook** and its entry in `claude/settings.json` — note the event (`PreToolUse` / `PostToolUse` / `SessionStart` / `Stop` / `UserPromptSubmit` / …) and matcher it is wired to. If it is not in `settings.json`, say so and stop.
2. **Run its evals if they exist.** Check `hooks/evals/<name>.json`. If present:
   ```
   python3 hooks/evals/eval.py hooks/evals/<name>.json
   ```
   Report pass/fail counts. Any FAIL is a defect — diagnose it.
3. **Live-trigger the hook.** Perform the real action that fires it (edit/create a throwaway file for `Edit|Write` hooks, run a matching `Bash` command for `Bash` hooks, etc.) and confirm you received the expected `additionalContext` / decision. Quote the exact hook output you got back. Clean up any throwaway file.
4. **Validate the payload is correct**, not just present: does the returned context match what the hook is supposed to compute for that input? Check against the hook's docstring intent.
5. **Check the log.** `grep` the hook's logger name in `/tmp/hooks.log` (or its `--log-file`) for the run you just triggered; confirm it logged without exceptions.

Report: eval result, live-trigger output (verbatim), whether the payload was correct, and any bug found with a concrete fix. If the hook produced nothing when it should have, that is the finding — trace why (matcher mismatch, missing env like `AI_PROJECT_DIR`, dedup window, silent exception).
