# Troubleshooting

### No diff returned / empty patch

Cause: PR may be a draft or have conflicts blocking diff generation.
Solution: use `get_status` to check merge state; if `mergeable_state` is `dirty`, report conflicts first.

### File patches truncated in get_files

Cause: large files exceed per-file patch limit.
Solution: always run `get_diff` in Step 2 — it is the authoritative source.

### Cannot find exact line numbers

Cause: relying on `get_files` patches only.
Solution: cross-reference `get_diff` unified output where every `+` line has a line number in the new file.

### get_diff or get_files output too large (persisted to protected file)

Cause: output exceeds context limit and is saved to a path outside the project, which is blocked by file protection hooks.
Solution: paginate `get_files` with `perPage: 5` and iterate pages until all files are retrieved. Never use `get_file_contents` with `ref: refs/pull/{N}/head` as a substitute — it returns the file at branch HEAD regardless of whether it was changed in the PR, leading to false findings on pre-existing code.
