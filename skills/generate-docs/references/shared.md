# Shared Reference — Writing Standards, Symlinks, Anti-patterns, Quality Checklist

Loaded by both [create.md](create.md) and [update.md](update.md). Do not duplicate this content into either mode file — link back here instead.

---

## Module Symlinks

Every module documented under `docs/modules/<module-name>.md` **must** have a symbolic link created at `<module-name>/CONTEXT.md` pointing to the corresponding docs file. This makes the module's context immediately accessible from within the module's own directory.

```bash
# Pattern (run from workspace root)
ln -s docs/modules/<module-name>.md <module-name>/CONTEXT.md
```

The canonical source of truth is always `docs/modules/<module-name>.md`; `CONTEXT.md` is only a convenience symlink — never edit or duplicate content through it.

---

## Writing Standards

| Aspect           | Rule                                                                  |
| ---------------- | --------------------------------------------------------------------- |
| Links            | Always use standard Markdown: `[label](path/to/file.md)`              |
| Lists            | Always use numbered or bulleted lists                                 |
| Headings         | Always use `#`, `##`, `###` hierarchy                                 |
| Code blocks      | Always use fenced blocks with syntax highlighting                     |
| Diagrams         | Use Mermaid (` ```mermaid `) for architecture or flow diagrams        |
| Tables           | Use Markdown tables for structured reference information              |
| File references  | Never mention files as plain text — always wrap in a Markdown link    |
| Audience clarity | State who each document/section is written for                        |
| Scope            | Only change what the task makes necessary — no padding or filler text |

---

## Quality and Consistency Checklist

Before finishing, verify each item:

- [ ] **Cohesion** — one topic per file, no mixed concerns.
- [ ] **Navigability** — every doc linked from `SUMMARY.md`; all cross-references use Markdown links.
- [ ] **No redundancy** — information lives in one canonical place; other docs link to it.
- [ ] **Uniform style** — consistent heading hierarchy, code fences, diagram style throughout.
- [ ] **Audience fit** — each file addresses its intended reader at the right level of detail.
- [ ] **Completeness** — all required files exist; optional files exist where applicable.
- [ ] **Accuracy** — all commands, paths, code snippets verified against source.
- [ ] **Mermaid diagrams** — at least one in `architecture.md` (create mode); additional ones where helpful.

---

## Anti-patterns to Avoid

- ❌ Referencing files as plain text (`docs/architecture.md`) — use links instead.
- ❌ Creating isolated files without linking from `SUMMARY.md`.
- ❌ Duplicating the same information across multiple files.
- ❌ Leaving placeholder text (`TODO`, `...`, `<fill in>`) in final output.
- ❌ Writing in a single monolithic file instead of the prescribed structure.
- ❌ Putting modules in a single `modules.md` — use individual files under `docs/modules/`.
- ❌ Including low-level implementation details in module context files — keep them high-level.
- ❌ Forgetting to create the `<module-name>/CONTEXT.md` symlink when writing a module file.
- ❌ Editing `CONTEXT.md` directly — it's a symlink; always edit the source `docs/modules/<module-name>.md`.
- ❌ Referencing module documentation as `docs/modules.md` — always use individual files under `docs/modules/<module-name>.md`.
- ❌ Forgetting to create or remove the `<module-name>/CONTEXT.md` symlink when a module is added or deleted.
- ❌ Skipping the incremental announcement step in create mode (always announce the next module/file).
- ❌ Finishing before cross-linking and consistency review is complete.
- ❌ Writing to a doc file before showing a preview and receiving confirmation (update mode).
- ❌ Updating a file whose content is unrelated to the diff (update mode).
- ❌ Adding content "just in case" or to make the docs feel more complete (update mode).
- ❌ Creating a new file when an existing file already covers the topic (update mode).
- ❌ Forgetting to update `docs/SUMMARY.md` after adding, removing, or restructuring a doc.
