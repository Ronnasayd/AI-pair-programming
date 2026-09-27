# ADR-001 – Centralize skill/agent/instruction enablement in one global, explicit JSON file

> **Date:** 2026-09-27
> **Status:** Accepted
> **Deciders:** Ronnasayd

## Context

Skill/agent/instruction enablement per project was tracked across three plain-text files (`.skillsignore`, `.agentsignore`, `.rulesignore`) living inside each installed project's root, using an inverted convention (`# pattern` = enabled, bare `pattern` = disabled). Five separate scripts (`ignores.sh`, `manage-ignore-files.py`, `install.sh`, `update-external-tools.sh`, plus shell aliases) each re-implemented parsing of this format. Claude Code's own `~/.claude.json` already tracks per-project MCP server enablement in a single global JSON file, keyed by project absolute path — a precedent for this toolkit's own configuration.

## Decision

Enablement state moves into a single JSON file at `~/.claude/aipp-settings.json`, global to the machine, keyed by project absolute path, with explicit `name: boolean` entries per skill/agent/instruction (no glob/wildcard patterns). One Python module owns all reads and writes to this file.

## Considered Alternatives

| Alternative                                                          | Pros                                                                                                            | Cons                                                                                                                                                                    |
| -------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Per-project JSON file (e.g. `<project>/.agent-config.json`)          | Mirrors current per-project file location; no global single point of failure                                    | Still needs gitignore/exclude handling per project like the old files did; doesn't match the `~/.claude.json` precedent this decision is modeled on                     |
| Global JSON with wildcard/glob support (e.g. `"anthropics:*": true`) | Preserves the old files' ability to enable/disable a whole namespace in one line; smaller file for large groups | Requires match-resolution logic in every consumer (bash and Python) exactly like the system being replaced; defeats the goal of "one file, one explicit truth per item" |
| Keep three separate JSON files instead of merging into one           | Smaller migration diff per category                                                                             | Still three sources of truth instead of one; doesn't address the core complaint (fragmentation)                                                                         |

## Consequences

- **Global blast radius**: a bug or corruption in one write touches every project's configuration on the machine, not just the project being installed. Mitigated by atomic writes (temp file + `os.replace`) and loud failure on malformed JSON (see `design.md` Error Handling Strategy).
- **No wildcard convenience**: enabling/disabling a whole namespace (e.g. all `tech-leads-club:*` skills at once) now requires toggling each item individually via the TUI or editing multiple JSON keys by hand — there is no single line that grants/revokes a group. Accepted because per-item explicitness was the primary ask; a future ADR can revisit if this friction proves costly in practice.
- **No project-local gitignore concern**: since the file lives outside any project repo, no `.gitignore`/`git_exclude` bookkeeping is needed per project — one clear win from going global.
- **`jq` becomes a hard dependency** for the bash-side consumers (`ignores.sh`, status aliases) reading the file; already installed by `install.sh`, so no new burden in practice.

## Related ADRs

None — first ADR in this project.
