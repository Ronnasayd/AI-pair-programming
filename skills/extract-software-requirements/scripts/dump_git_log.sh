#!/usr/bin/env bash
# Dump git log (subject + body, chronological) to a file, bypassing any
# shell hook/proxy that might silently truncate `git` output for token savings.
#
# Usage: dump_git_log.sh <output-file> [repo-path] [-n <count>]
#
# -n <count>: dump only the last N commits (still chronological, oldest-first
# within that window) instead of full history — for "last N commits" requests.
#
# Always cross-check `wc -l "$1"` against `/usr/bin/git -C <repo> log --oneline | wc -l`
# (or `-n <count>` if used — commit count, not line count) before trusting the
# dump is complete — see SKILL.md Step 2 for why this matters and how to detect truncation.

set -euo pipefail

OUT="${1:?Usage: dump_git_log.sh <output-file> [repo-path] [-n <count>]}"
shift

REPO="."
if [ $# -gt 0 ] && [ "$1" != "-n" ]; then
  REPO="$1"
  shift
fi

LIMIT=""
while [ $# -gt 0 ]; do
  case "$1" in
    -n)
      LIMIT="${2:?-n requires a count}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

LIMIT_ARGS=()
[ -n "$LIMIT" ] && LIMIT_ARGS=(-n "$LIMIT")

/usr/bin/git -C "$REPO" log \
  "${LIMIT_ARGS[@]}" \
  --pretty=format:'%h|%ad|%s%n%b%n===END===' \
  --date=short \
  --reverse \
  > "$OUT"

if [ -n "$LIMIT" ]; then
  commit_count=$(/usr/bin/git -C "$REPO" log -n "$LIMIT" --oneline | wc -l)
else
  commit_count=$(/usr/bin/git -C "$REPO" log --oneline | wc -l)
fi
end_markers=$(grep -c '^===END===$' "$OUT" || true)

echo "Commits in repo: $commit_count"
echo "===END=== markers in dump: $end_markers"
if [ "$commit_count" != "$end_markers" ]; then
  echo "WARNING: counts do not match — dump may be truncated or repo has merge commits with empty bodies. Investigate before trusting $OUT." >&2
fi
