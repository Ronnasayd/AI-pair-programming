# Hook Conventions (this repo)

Read when writing the script in Phase 2. Every hook in `hooks/scripts/` follows this.

## Skeleton

```python
#!/usr/bin/python3
"""
<Name> Hook

<Event> hook for <matcher>. <One paragraph: what it does, what it injects/gates.>

Dedupe: <if applicable — per session, re-announce only every NOTIFY_EVERY calls.>
"""

import json
import os
import sys
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_by_key, get_hooks_logger, get_session_id_short  # noqa: E402

logger = get_hooks_logger("<Name>")

MAX_STDIN = 1024 * 1024


def main() -> None:
    try:
        stdin_data = sys.stdin.read(MAX_STDIN)
    except OSError:
        sys.exit(0)

    try:
        data = json.loads(stdin_data)
    except (json.JSONDecodeError, TypeError):
        logger.debug("Failed to parse stdin JSON, exiting.")
        sys.exit(0)

    tool_name = get_by_key(data, "tool_name") or ""
    if tool_name not in ("Edit", "Write"):   # your matcher
        sys.exit(0)

    tool_input = get_by_key(data, "tool_input") or {}
    file_path = get_by_key(tool_input, "file_path")
    if not file_path:
        sys.exit(0)

    # ... compute ...

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("<name> hook failed")
        sys.exit(0)
```

## Rules

- **Never crash the tool call.** Every failure path — bad stdin, missing field, subprocess error, exception — is `sys.exit(0)` with no stdout. The outer `try/except logger.exception` is mandatory.
- **Payload access via `get_by_key`** — it normalizes `tool_input` / `toolInput` / `TOOL_INPUT`. Don't index the dict directly.
- **Project root**: `os.environ["AI_PROJECT_DIR"]` (deployed) — but tolerate its absence in evals; fall back to `data`'s `cwd` or a repo-root walk. The `KeyError: 'AI_PROJECT_DIR'` regression in `skill_activation.py` came from a bare `os.environ[...]`.
- **Logger name** is the `[Name]` that shows up in `/tmp/hooks.log`. Use `get_hooks_logger("Name")`; `--log-file` support comes free.
- **stdin cap** `MAX_STDIN = 1024*1024`.

## `utils` helpers available

- `get_by_key(data, key)` — format-agnostic key lookup
- `get_hooks_logger(name, log_file=...)` — file logger
- `get_session_id_short(session_id)` — first 8 chars, timestamp fallback
- `extract_query_text(payload)` — pulls text from a `UserPromptSubmit` **or** an `AskUserQuestion` `PostToolUse` payload (use this if the hook should fire on both — several hooks were fixed to cover `AskUserQuestion`)
- `split_on_operators(command)` — split a shell command on `&&`, `||`, `|`, `;` (use for `Bash` matcher hooks that inspect subcommands)

## Output shapes

**Inject context** (PreToolUse / PostToolUse / SessionStart / UserPromptSubmit):

```python
sys.stdout.write(json.dumps({"hookSpecificOutput": {
    "hookEventName": "<PreToolUse|PostToolUse|SessionStart|UserPromptSubmit>",
    "additionalContext": json.dumps({"note": "...", "data": ...}),
}}))
```

`additionalContext` is itself a JSON **string**, not an object.

**Gate a tool** (PreToolUse only):

```python
print("Reason shown to agent + user", file=sys.stderr)
sys.exit(2)   # deny. exit 0 = allow.
```

## Dedup / back-off pattern

When a hook would otherwise re-announce the same thing on every call:

```python
NOTIFY_EVERY = 25
cache_path = Path(f"/tmp/<name>_{session_id}.json")
cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
skip = cache.get(key)
if skip is None or skip >= NOTIFY_EVERY:
    cache[key] = 0
    # ...report...
else:
    cache[key] = skip + 1
cache_path.write_text(json.dumps(cache))   # write atomically if concurrent hooks share it
```

Concurrent writers (e.g. jest coverage hooks) → write to a temp file + `os.replace`.

## settings.json wiring

Path is `$AI_PROJECT_DIR/.claude/hooks/scripts/<name>.py`. Add under the matching event block, next to sibling hooks. `log_hooks.py` stays last in each block. Example PostToolUse `Edit|Write` addition:

```json
{
  "matcher": "Edit|Write",
  "hooks": [
    {
      "type": "command",
      "command": "$AI_PROJECT_DIR/.claude/hooks/scripts/<name>.py"
    }
  ]
}
```
