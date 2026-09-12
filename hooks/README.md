# Hooks

Claude Code hook scripts for this repo. Wiring lives in
[`claude/settings.json`](../claude/settings.json) — that file is the source of
truth for which script fires on which event/matcher. `hooks.json` in this
directory is a stale template (paths point to `.github/hooks/scripts/`,
which doesn't exist) and is not loaded by Claude Code.

Scripts live in [`scripts/`](scripts) and run via
`uv run --project $AI_PROJECT_ROOT_DIR .../scripts/<name>.py` unless noted.

## SessionStart

| Script                         | Purpose                                                                                       |
| ------------------------------ | --------------------------------------------------------------------------------------------- |
| `caveman-activate.js`          | Loads caveman-mode state at session start.                                                    |
| `start_embedding_daemon.py`    | Starts the persistent embedding daemon (`embedding_daemon.py`) used by semantic search hooks. |
| `start_context.py`             | Logs tool calls / seeds session context.                                                      |
| `start_memory_rules.py`        | Injects durable ai-memory pages (rules, feedback, gotchas) into context.                      |
| `taskmaster_next_task.py`      | Surfaces the next pending Taskmaster task per tag.                                            |
| `ai-memory` session-start hook | Fetches pending cross-session handoff.                                                        |
| `mcp_manager_context`          | Injects mcp-manager server/tool catalog.                                                      |

## UserPromptSubmit

| Script                              | Purpose                                                            |
| ----------------------------------- | ------------------------------------------------------------------ |
| `skill_activation.py`               | Matches the prompt against local skills, suggests which to invoke. |
| `checklist_context_watch.py`        | Re-surfaces the active skill's `CHECKLIST.md`.                     |
| `context7_search.py`                | Looks up Context7 docs relevant to the prompt.                     |
| `caveman-mode-tracker.js`           | Tracks caveman-mode state across turns.                            |
| `mcp_manager_context`               | Re-injects mcp-manager catalog.                                    |
| `ai-memory` user-prompt-submit hook | Records the prompt as a memory observation.                        |

## PreToolUse

| Matcher             | Script                        | Purpose                                                                                                                       |
| ------------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `AskUserQuestion`   | `notify_sound.py`             | Plays an alert sound when the user is asked a question.                                                                       |
| `Bash`              | `rtk-rewrite.sh`              | Rewrites commands through the RTK token-saving proxy.                                                                         |
| `Bash`              | `smart_approve.py`            | Decomposes compound bash commands and checks each against allow/deny patterns.                                                |
| `Bash`              | `protect_branches.py`         | Denies git operations that would mutate a protected branch (main/master/develop/homolog) outside a PR flow.                   |
| `Bash`              | `dev_server_tmux_check.py`    | Blocks dev-server commands run outside tmux/screen.                                                                           |
| `Edit\|Write`       | `md_language_check.py`        | Reminds the agent to write markdown in English.                                                                               |
| `Edit\|Write`       | `context_refs.py`             | Injects reference-file contents into context when a matched file is about to be edited.                                       |
| `Edit\|Write`       | `similar_code_ref.py`         | Surfaces similar existing code (rag-rat or ripgrep) for content about to be written.                                          |
| `Write`             | `md_location_check.py`        | Warns when a `.md` file is created outside standard locations.                                                                |
| `Read\|Edit\|Write` | `dir_context_refs.py`         | Walks parent dirs for `CONTEXT.md`/`CLAUDE.md`/`AGENTS.md` and announces them.                                                |
| `Read`              | `large_file_read_warning.py`  | Warns when reading a large file without offset/limit.                                                                         |
| _(all)_             | `tooluse_context_rules.py`    | Generic rule engine: injects `additionalContext` when a rule's `match(payload)` is true.                                      |
| _(all)_             | `subagent_guidelines.py`      | Injects guidelines when a subagent starts.                                                                                    |
| _(all)_             | `protect_files.py`            | Blocks reads/writes/exfiltration of protected paths (secrets, home dir, etc.), hardened against compound/obfuscated commands. |
| _(all)_             | `ai-memory` pre-tool-use hook | Records tool-call observation.                                                                                                |
| _(all)_             | `agent-flow/hook.js`          | External agent-flow integration hook.                                                                                         |

## PostToolUse

| Matcher           | Script                                      | Purpose                                                                                   |
| ----------------- | ------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `AskUserQuestion` | `skill_activation.py`, `context7_search.py` | Re-run after the question resolves.                                                       |
| `EnterWorktree`   | `worktree_init.py`                          | Symlinks `node_modules` from the main repo into a new worktree.                           |
| `Edit\|Write`     | `typescript_lint.py`                        | Runs `tsc`/ESLint on touched JS/TS files.                                                 |
| `Edit\|Write`     | `python_lint.py`                            | Runs `mypy`/`ruff` on touched Python files.                                               |
| `Edit\|Write`     | `golang_lint.py`                            | Runs `go vet`/`golangci-lint`/`gofmt` on touched Go files.                                |
| `Edit\|Write`     | `jest_coverage_incremental.py`              | Runs scoped `jest --coverage` in the background and merges it into project coverage.      |
| `Edit\|Write`     | `jest_coverage_report.py`                   | Reports the touched file's existing coverage numbers via `additionalContext`.             |
| `Edit\|Write`     | `jest_related_files_report.py`              | Reports which tests cover a touched source file (or which sources a touched test covers). |
| `Edit\|Write`     | `impact_surface_hint.py`                    | Asks rag-rat's `impact_surface` for blast-radius hints after an edit.                     |
| _(all)_           | `checklist_context_watch.py`                | Re-checks active skill checklist state.                                                   |
| _(all)_           | `tooluse_context_rules.py`                  | Same rule engine as PreToolUse.                                                           |
| _(all)_           | `ai-memory` post-tool-use hook              | Records tool-result observation.                                                          |

## Stop / SubagentStop

| Script                               | Purpose                                                                                             |
| ------------------------------------ | --------------------------------------------------------------------------------------------------- |
| `question_tool_enforcer.py`          | If the last assistant message asked a plain-text question, nudges toward `AskUserQuestion` instead. |
| `ai-memory` stop/subagent-stop hooks | Closes out the session/subagent observation stream.                                                 |

## SessionEnd

| Script                         | Purpose                                                            |
| ------------------------------ | ------------------------------------------------------------------ |
| `jest_coverage_session_end.py` | Runs a full (non-incremental) `jest --coverage` in the background. |
| `ai-memory` session-end hook   | Finalizes session memory.                                          |

## SubagentStart

| Script                          | Purpose                                                    |
| ------------------------------- | ---------------------------------------------------------- |
| `ai-memory` subagent-start hook | Starts a memory observation stream scoped to the subagent. |

## PreCompact

| Script                       | Purpose                                     |
| ---------------------------- | ------------------------------------------- |
| `ai-memory` pre-compact hook | Snapshots memory before context compaction. |

## Shared utilities

- `utils.py` — shared helpers (logging, payload parsing) used by most scripts above.
- `embedding_daemon.py` — SentenceTransformer daemon over a Unix socket, backing semantic-search hooks.
- `merge_coverage.py` — merges a partial Istanbul coverage run into the project's coverage dir; used by `jest_coverage_incremental.py`.
- `log_hooks.py` — logs every hook invocation (wired on nearly every event, with `JSON_COLORIZE=1`).
- `unused/` — retired scripts, not wired anywhere.

Cross-cutting hooks not in `scripts/` (external, run via `node`/shell directly
from `claude/settings.json`): `caveman-activate.js`, `caveman-mode-tracker.js`,
`agent-flow/hook.js`, `rtk-rewrite.sh`, and the `ai-memory` hook set under
`~/.local/share/ai-memory/hooks/claude-code/`.
