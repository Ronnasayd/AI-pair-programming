#!/usr/bin/env bash
# Dump full git log (subject + body, chronological) to a file, bypassing any
# shell hook/proxy that might silently truncate `git` output for token savings.
#
# Usage: dump_git_log.sh <output-file> [repo-path]
#
# Always cross-check `wc -l "$1"` against `/usr/bin/git -C <repo> log --oneline | wc -l`
# (commit count, not line count) before trusting the dump is complete — see
# SKILL.md Step 2 for why this matters and how to detect truncation.

set -euo pipefail

OUT="${1:?Usage: dump_git_log.sh <output-file> [repo-path]}"
REPO="${2:-.}"

/usr/bin/git -C "$REPO" log \
  --pretty=format:'%h|%ad|%s%n%b%n===END===' \
  --date=short \
  --reverse \
  > "$OUT"

commit_count=$(/usr/bin/git -C "$REPO" log --oneline | wc -l)
end_markers=$(grep -c '^===END===$' "$OUT" || true)

echo "Commits in repo: $commit_count"
echo "===END=== markers in dump: $end_markers"
if [ "$commit_count" != "$end_markers" ]; then
  echo "WARNING: counts do not match — dump may be truncated or repo has merge commits with empty bodies. Investigate before trusting $OUT." >&2
fi
