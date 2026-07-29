# Troubleshooting

## Commit/line counts disagree after `dump_git_log.sh`

Cause: shell hook or CLI proxy (token-saving wrappers common) rewrote `git` transparently, truncated output before redirect. Script invokes `/usr/bin/git` directly to bypass this — if warning persists, check no other wrapper sits closer to binary (`type git`, `alias git`).

## `promptSource` field absent or all values differ from `"typed"`

Cause: transcript schema changed. Read 3-4 raw `type=="user"` lines across different timestamps, find whichever field currently discriminates real typed input from injected tool-result/system-reminder content, adjust filter in `extract_user_prompts.py` before running at scale.

## Same requirement appears with contradicting facts, no timestamp to order them

Don't guess order. Mark "incerto — requer validação manual" in Conflicts section per `references/merge-and-conflicts.md`, not resolved either way.
