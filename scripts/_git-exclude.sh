# Shared helper: append patterns to the repo's real .git/info/exclude.
# Resolves the git dir once via `git rev-parse` so it works from a subdir,
# a linked worktree, or a submodule instead of assuming ./.git/info/exclude.
# Uses --git-common-dir so all worktrees share one exclude file.
# Source this file; do not execute it.

_GIT_COMMON_DIR="$(cd "${LOCAL:-$PWD}" && git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"
GIT_EXCLUDE=""
[ -n "$_GIT_COMMON_DIR" ] && GIT_EXCLUDE="$_GIT_COMMON_DIR/info/exclude"
export GIT_EXCLUDE

git_exclude() {
  local pattern
  [ -n "$GIT_EXCLUDE" ] || return 0
  mkdir -p "$(dirname "$GIT_EXCLUDE")"
  for pattern in "$@"; do
    grep -qxF "$pattern" "$GIT_EXCLUDE" 2>/dev/null || printf '%s\n' "$pattern" >> "$GIT_EXCLUDE"
  done
}

# Absolute path to something under the real (per-worktree) git dir, e.g. hooks.
git_path() {
  local d
  d="$(cd "${LOCAL:-$PWD}" && git rev-parse --absolute-git-dir 2>/dev/null)" || return 0
  [ -n "$d" ] && printf '%s/%s\n' "$d" "$1"
}
