# Update Mode — Sync Docs With a Code Diff

Diff-driven documentation sync. Selected when `docs/` already exists and the request references a diff, patch, or set of changes (see mode-selection table in [SKILL.md](../SKILL.md)).

**Argument:** `{change_source}` — how the changes are identified. Can be a shell command (e.g. `git diff HEAD~1`, `git diff main...feature/my-branch`, `cat patch.diff`), a raw diff/file, a list of changed file paths, or code snippets/excerpts the user points to — any form is fine as long as it lets you determine what changed and how it impacts documentation.

Shared writing standards, anti-patterns, the module symlink rule, and the quality checklist live in [shared.md](shared.md) — read that alongside this file, don't duplicate it here.

---

## Core Principles

- **Diff-first** — always analyze the provided diff completely before touching any documentation file.
- **Minimal and relevant** — only update files whose content is directly relevant to the changes. If a change does not affect a doc, leave it alone.
- **Preview before write** — before modifying or creating any file, show exactly what will be added, changed, or removed, and wait for confirmation.
- **Prefer updating over creating** — update existing files whenever possible; create new files only when no existing file covers the topic.
- **Consistency** — after every update, verify cross-links and ensure `docs/SUMMARY.md` still accurately reflects the docs/ hierarchy.

---

## Workflow

### Phase 1 — Gather and Understand the Changes

1. Obtain the change source: run `{change_source}` if it's a shell command, read the provided file/patch, or take the given list of files/snippets directly.
2. Parse the change source to extract:
   - Files added, removed, or modified.
   - Functions, classes, endpoints, models, or configuration keys that changed.
   - New dependencies or removed ones.
   - Renamed or moved modules.
   - Breaking changes vs. additive changes.
3. **Use semantic search when available** — tools such as `serena`, `rag-rat`, or any other semantic/code-intelligence tool present in the environment. Use them to understand the full context of the changes (callers, related modules, downstream impact) beyond what the raw diff text shows — this matters especially when the change source is a file list or snippet rather than a full diff.
4. If ambiguity remains after investigation (unclear module purpose, unclear target audience, or missing context no tool can resolve), use `/grilling` to ask the user targeted clarifying questions before proceeding.

### Phase 2 — Map Changes to Documentation Files

For each changed code unit, determine which doc file(s) it affects:

| Code change type                       | Likely doc files to update                                                                        |
| -------------------------------------- | ------------------------------------------------------------------------------------------------- |
| New module or folder added             | `docs/modules/<module-name>.md` (new file), `docs/SUMMARY.md`, `<module-name>/CONTEXT.md` symlink |
| Module removed or renamed              | `docs/modules/<module-name>.md`, `docs/SUMMARY.md`, `docs/usage.md`, remove stale `CONTEXT.md`    |
| New API endpoint added                 | `docs/endpoints.md`, `docs/usage.md`                                                              |
| Endpoint signature changed             | `docs/endpoints.md`, `docs/usage.md`                                                              |
| New data model or schema change        | `docs/models.md`, `docs/architecture.md`                                                          |
| Installation/env var/config change     | `docs/setup.md`                                                                                   |
| Architectural pattern change           | `docs/architecture.md`, `docs/adr/`                                                               |
| New external dependency added/removed  | `docs/setup.md`, `docs/techs/`                                                                    |
| Breaking change in public interface    | `docs/usage.md`, `docs/endpoints.md`, `docs/faq.md`                                               |
| New contributor workflow (CI, scripts) | `docs/contribution.md`                                                                            |

If no existing doc covers a new topic, note that a new file may be needed and include it in the preview.

### Phase 3 — Investigate Existing Documentation

1. Check whether `docs/` exists in the workspace.
2. Read `docs/SUMMARY.md` (if present) to understand the current doc structure.
3. Read each doc file identified in Phase 2 to understand its current content before proposing changes.

### Phase 4 — Explain Proposed Changes and Confirm

For **each** documentation file that requires an update:

1. State the file path.
2. Describe in plain language **why** this file needs updating (link it explicitly to the identified change) and **what** will change — a clear summary is enough, no diff-style text required.
3. **Ask the user to confirm** before writing anything.

> Example prompt:
> "I plan to update [docs/endpoints.md](docs/endpoints.md) to document the new `POST /users` endpoint. Shall I proceed?"

### Phase 5 — Apply Confirmed Changes

After confirmation for each file:

1. Write only the confirmed changes.
2. Preserve all existing content that is unaffected by the diff.
3. Maintain consistent Markdown style (headings, tables, code fences, Mermaid diagrams) with the rest of the file.
4. Update `docs/SUMMARY.md` if any file was added, removed, or had its top-level section titles changed.

### Phase 6 — Consistency Review

After all writes are complete:

- [ ] All modified files still have valid internal Markdown structure.
- [ ] All cross-links between docs are intact.
- [ ] `docs/SUMMARY.md` reflects the current state of the docs/ hierarchy.
- [ ] No placeholder text (`TODO`, `...`, `<fill in>`) was left behind.
- [ ] No information was duplicated across files.

---

## Decision Rules for "Should This Doc Be Updated?"

Apply these rules in order. Stop at the first match.

1. **Directly referenced** — the diff modifies code that is explicitly described in the doc (e.g., a function documented in `docs/modules/<module-name>.md`).
   → **Update.**

2. **Structurally affected** — the diff adds or removes a module, endpoint, model, or configuration key that belongs in the doc's scope.
   → **Update.**

3. **Behavior change** — the diff changes observable behavior that a user or integrator would need to know about (return values, error codes, environment variables, CLI flags).
   → **Update** the relevant usage/setup/endpoint doc.

4. **Internal refactor only** — the diff is a pure internal refactor with no visible behavioral change and no new/removed public surface.
   → **Do not update** (unless the doc currently describes the internals being refactored and the description would become inaccurate).

5. **Test or tooling change only** — the diff only touches test files, CI configuration, or developer tooling with no user-facing impact.
   → **Do not update** (unless `docs/contribution.md` explicitly covers the changed workflow).

6. **When in doubt, don't** — only touch documentation when there is **direct** impact from the identified change. Avoid speculative or "just in case" edits that aren't clearly relevant.

---

## Quality Gate

Before finishing, run the [shared.md](shared.md) Quality and Consistency Checklist and confirm none of the [shared.md](shared.md) anti-patterns are present. Also confirm Phase 6's Consistency Review checklist is fully checked.
