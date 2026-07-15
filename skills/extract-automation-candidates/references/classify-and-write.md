# Classify & Write Rules (Phase 4)

Read this file when starting Phase 4, after Phases 1-3 (whichever were run) have produced a candidate list.

## Qualification gate (apply before classifying)

A candidate only proceeds if it meets one of:

- **Recurrence** — appears in ≥2 distinct sources or sessions (two transcript sessions, or one transcript + one commit, etc).
- **High cost** — a single occurrence, but the session shows an unusually long/painful manual process: 15+ manual steps, repeated trial-and-error before landing on an approach, or the user having to re-explain the same workaround in detail.

Anything weaker gets dropped silently from the final output — do not write a weak artifact "just in case" and do not mention rejected candidates unless the user asks why something wasn't included.

## Classification heuristic: skill vs command vs instruction

- **Instruction** — a single standing rule that should always apply, with no branching logic and no multi-step procedure. "Never use `--no-verify`", "always run tests before committing this repo's X module". Goes into `AGENTS.md` (or the project's canonical instruction file) as one line, not a new file.
- **Command** — a short, parametrizable, one-shot action: takes 0-3 inputs, executes in essentially one pass, no phases/conditional branching. Example: "summarize this PR's diff into a changelog entry". Goes into `<workdir>/agents/commands/<name>.md`.
- **Skill** — a multi-step workflow with phases, conditional logic, or decision points that vary by situation (this very skill is an example). Goes into `<workdir>/agents/skills/<name>/SKILL.md`, following the same frontmatter shape as other skills in this repo (`name`, `description` with explicit trigger phrases and negative scope, `license`, `metadata.author`/`version`).

When a candidate sits on the boundary (e.g. a command that's grown a couple of conditional branches), prefer the simpler classification (command over skill, instruction over command) unless the branching genuinely needs separate phases to stay readable.

## Target paths

- Skill: `<workdir>/agents/skills/<kebab-name>/SKILL.md` (plus `scripts/`/`references/` subdirs only if the workflow actually needs them — don't scaffold empty dirs).
- Command: `<workdir>/agents/commands/<kebab-name>.md`.
- Instruction: append one bullet to the project's `AGENTS.md` under the most relevant existing section, or a new short section if none fits. Never touch the user's private `~/.claude/CLAUDE.md`.

If `<workdir>/agents/skills` or `<workdir>/agents/commands` don't exist yet, create them — this is the first artifact for that project, not an error.

## Updating an existing artifact instead of overwriting

Before writing, check if a same-named (or clearly same-purpose) artifact already exists at the target path.

- If yes: read it fully first. Only touch the instructional body if the new evidence reveals the existing artifact is wrong or incomplete — never blindly overwrite a working artifact just because it was found again.
- If no: write fresh, following the target-path convention above.

## What NOT to write

- Do not write an artifact for a candidate that's actually a one-time migration, a project-specific bugfix, or anything tied to a single piece of code that won't recur (that's a normal commit, not an automation candidate).
- Do not write a skill when a command would do — bloats the skill list and adds unnecessary phase overhead for something that's really one action.
- Do not duplicate an instruction that's already effectively stated elsewhere in `AGENTS.md`, even if worded differently — check the whole file first.
