---
name: memory-add
description: Adds a memory entry to the appropriate project memory file. Supports optional file association or auto-detection of available memory files.
argument-hint: "<memory_description> A clear description of the memory to store, including relevant context. [file_path] (optional) Path to a specific file to associate this memory with."
---

# Add Memory

## Goal

Persist a memory entry so it can be recalled later, either linked to a specific file or stored in the most appropriate project-level memory file.

## Behavior

**If `file_path` is provided:**
Add the memory with a direct association to the specified file. Format it so future retrieval can be scoped by that file's context.

**If `file_path` is not provided:**

1. Check which of the following memory files exist in the project root:
   - `GEMINI.md`
   - `CLAUDE.md`
   - `AGENTS.md`
   - `docs/SUMMARY.md`
2. Add the memory to whichever file(s) exist. If multiple exist, prefer the one most relevant to the memory's content.
3. If none exist, inform the user and ask which file to create or use.

## Memory Format

Write entries that are concise, specific, and self-contained — they should be understandable without needing additional context.
