## Sync AGENTS.md with docs/SUMMARY.md

1. **Read source of truth.** Load the project's canonical doc summary (e.g. `docs/SUMMARY.md`) to see full scope: tech stack, architecture layers, features, commands, testing.

2. **Read target file.** Load existing agent-instruction file (e.g. `AGENTS.md`) to see current structure and avoid duplication.

3. **Filter for relevance.** From source doc, extract only what changes agent behavior day-to-day:
   - Stack/framework + versions
   - Architecture/layering pattern (one line)
   - Storage/state/video-or-domain-specific tech choices
   - Dev commands (install/run/test/lint/typecheck)
   - Skip: feature lists, testing philosophy prose, "next steps," support sections — these don't change how an agent should act.

4. **Compress to minimal prose.** One short paragraph for description, one line for commands. No headers-within-headers, no repeating what skills sections already say.

5. **Insert at top-level, before existing sections.** Add as a new `## Project` section right after title/before first existing section (e.g. before `## Recommended Skills`), so agents get orientation before tool guidance.

6. **Edit via targeted string replace**, not full rewrite — preserves rest of file untouched.

7. **Ask if links to source docs are missing.** If user flags omission (e.g. "should link relevant files"), add a `Docs:` line linking index + key module/architecture files — gives agents a path to deeper info without inlining it.

8. **Confirm completeness, resist over-adding.** When asked "anything else?", check remaining source content against the "changes agent behavior" filter from step 3. If remaining items (error handling conventions, session mgmt, testing detail) are already implied by existing rules/skills, decline to add — keep file terse per project's own stated formatting rule ("não deve adicionar muito texto").

**Reusable principle:** sync docs → agent-instructions by extracting only operationally-relevant facts, compressing hard, linking rather than duplicating, and stopping once marginal additions no longer change agent behavior.
