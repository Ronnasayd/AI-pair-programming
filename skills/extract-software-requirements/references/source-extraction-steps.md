# Source Extraction Detail (Phases 1-3)

Each phase independent — run only what's asked. Common output format: Markdown, source-tagged, ID-prefixed (RF-/RNF-) requirements plus an open-items list.

## Phase 1: Session transcripts

Location: `~/.claude/projects/<url-encoded-cwd>/*.jsonl`, one file per session UUID.

| #   | Step                                                                                                                                                                                                                                                                                                                 | Output/Gate                  |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| 1   | Read one raw `type=="user"` line from any `.jsonl` in target project dir; inspect `message.content` + `promptSource`. **Do every time before running script** — schema differs across CC versions, tool-result/system content also stored under `role:"user"`, so `promptSource=="typed"` isolation can't be assumed | confirm current filter field |
| 2   | Run `scripts/extract_user_prompts.py "$HOME/.claude/projects/<project-dir>/*.jsonl" --out /tmp/user_prompts_only.txt`. For "last N sessions" requests, add `--last-n-sessions <N>` — keeps only the N most recently modified matched session files (by mtime)                                                        | raw prompts file             |
| 3   | Read output in full (paginate if needed, no sampling). Classify each line: noise (pasted stack traces/logs as bug context) / process-meta ("proceed", "yes", skill questions) / signal (feature requests, bug reports w/ expected-vs-actual, scope decisions)                                                        | classified lines             |
| 4   | Cluster signal into domain taxonomy as it emerges (core scope, external API, persistence, UX/screens, non-functional, observability). Assign RF-/RNF- IDs per Step 4 numbering even if Phase 4 won't run                                                                                                             | clustered reqs               |
| 5   | Close with explicit "still pending/open" subsection — cross-ref recent timestamps + follow-up language ("continua aparecendo", "isso não deve acontecer", "ainda não") to flag unresolved                                                                                                                            | open-items list              |

## Phase 2: Git commit history

| #   | Step                                                                                                                                                                                                                                                                                                                    | Output/Gate                                                                |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| 1   | `bash scripts/dump_git_log.sh /tmp/commits_full.txt <repo-path>` — bypasses shell hooks/token-saving proxies that could truncate `git` output. For "last N commits" requests, add `-n <count>` (e.g. `... <repo-path> -n 50`). Script self-verifies commit count vs `===END===` marker count                            | warning on mismatch → investigate, don't proceed (see Troubleshooting ref) |
| 2   | Read dump in full, chronological (`--reverse`, oldest first) — reads as narrative: foundation → features → fixes → polish                                                                                                                                                                                               | —                                                                          |
| 3   | High-confidence signal patterns: explicit IDs (`REQ-xxx`, `TASK-xxx`), "Implements requirements: ..." lines, "Gate:"/"Test gate:" lines (= acceptance criteria), `fix:` commits (root cause + resolution = implicit undocumented requirement — rephrase as "system must X because Y failed when Z", not changelog line) | tagged commits                                                             |
| 4   | Cluster into same taxonomy as Phase 1, new RF-/RNF- IDs, but **keep original `REQ-xxx`/`TASK-xxx` cited in commit body inline** — never discard                                                                                                                                                                         | traceable reqs                                                             |
| 5   | Open-items checklist: recurring bug themes across multiple fix commits; most recent commit on a topic being a tuning step ("increase concurrency") not closure                                                                                                                                                          | open-items list                                                            |

`feat:` commits → RF. lint/type/perf/test commits → RNF.

## Phase 3: Formal spec/PRD files

| #   | Step                                                                                                                                                                                                                                                                                    | Output/Gate             |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| 1   | `find <repo-root> -iname "*.md"`, exclude build/tooling copies (`node_modules`, `.stryker-tmp/`, `.stryker/`, any path duplicating a `.specs/` tree inside temp build dir). Match every file back to real version-controlled path                                                       | verified candidate list |
| 2   | Don't filter to only exact filename pattern user named (e.g. `*spec.md`) — also check sibling `PRD.md`, `design.md`, `tasks.md`, casing variants (`Specs.md`, `Design.md`)                                                                                                              | full candidate list     |
| 3   | Read every candidate in full — short docs, skipping risks missing "Out of Scope" list or appendix that reverses earlier requirement                                                                                                                                                     | —                       |
| 4   | Precedence when docs overlap: check explicit dates, `status:` frontmatter (Approved/ready/draft), cross-refs in text ("corrects REQ-007.9" supersedes earlier). Kickoff-era PRD commonly stale vs feature spec written after impl began — don't treat all docs as equally authoritative | precedence order        |
| 5   | Preserve existing requirement IDs verbatim (`REQ-xxx`, `R-xx`, `TVUI-xx`) — never invent parallel numbering when source has one                                                                                                                                                         | —                       |
| 6   | Group output by source document/section, not reinvented taxonomy — specs already structured; preserve so result is faithful superset                                                                                                                                                    | —                       |
| 7   | Cross-check every requirement against: other reqs in same doc, reqs in other specs on same subsystem, implementation facts already known from prior Phase 1/2 pass this session. Flag every disagreement explicitly, never silently pick a side                                         | conflicts flagged       |

Output adds a "Conflicts / points of attention" closing section: every contradiction found, likely-authoritative source, implication (doc to update, or code drifted from spec).

## Phase 3.5: Test files (only if a test suite exists)

Purpose: mine test **descriptions** (`describe`/`it`/`test`/`test_*` names, docstrings) for behavior no other source (transcripts, commits, specs) already surfaced — not to re-verify requirements already found (that's the Phase 4 test-file downgrade check in `references/merge-and-conflicts.md`).

| #   | Step                                                                                                                                                                                                   | Output/Gate             |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------- |
| 1   | Detect test dirs/files: `__tests__/`, `*.test.*`, `*.spec.*`, `test_*.py`, `tests/`, `spec/`. None found → skip phase entirely, don't emit an empty file or flag it missing                            | test-file inventory     |
| 2   | Read test descriptions (`describe`/`it`/`test(...)` string args, `test_*` function names, docstrings) — not full test bodies unless a description is ambiguous about what behavior it's asserting      | classified descriptions |
| 3   | Cross-reference each description against requirements already extracted in Phases 1-3 (same session). Keep only descriptions that assert behavior **not already covered** by an existing RF-/RNF- item | net-new candidates      |
| 4   | Rephrase surviving candidates as requirements ("system must X when Y"), cluster into same domain taxonomy as other phases, assign RF-/RNF- IDs, tag source as test file path + test name               | net-new reqs            |
| 5   | Open-items: skipped/`.skip`/`xit`/`TODO` tests describing unimplemented behavior — these are ❌ Open by definition, list explicitly                                                                    | open-items list         |

This phase never downgrades or verifies existing requirement status — that check already exists in `references/merge-and-conflicts.md` (Status vocabulary, test-file check). Phase 3.5 only adds requirements that were otherwise invisible.
