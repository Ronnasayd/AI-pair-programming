---
name: generate-pr-description
description: "A skill for generating structured Pull Request descriptions based on git diffs and commit history. It automatically detects and uses .github/pull_request_template.md if available, otherwise it uses standard sections like ## Description, ## Task, and ## Impact. It also ensures the description is generated in the user's preferred language."
argument-hint: "[language]: (Optional) The language in which the PR description should be generated (e.g., 'English', 'Portuguese'). If not provided, the skill MUST ask the user."
---

MANDATORY: Use developer-specialist or review-refactor-specialist agent.
MANDATORY: If the **$0** (language) argument is not provided, you MUST ask the user: "Which language should I use for the PR description (e.g., English, Portuguese)?"

Your objective is to generate a professional and comprehensive Pull Request description by analyzing the staged changes and recent commit history.

====================
PHASE 1 — TEMPLATE DETECTION
====================

1. Check if `.github/pull_request_template.md` exists in the workspace.
2. If it exists, read its content and use it as the MANDATORY structure for the PR description.
3. If it does NOT exist, use the following default topics as sections:
   - ## Description: High-level overview of what this PR does.
   - ## Task: List of specific tasks or user stories addressed.
   - ## Impact: Technical and functional impact of the changes.

====================
PHASE 2 — CONTEXT GATHERING
====================

1. Identify the changes to be described:
   - Run `git diff --staged`. If not empty, use this as the primary source.
   - If `git diff --staged` is empty, run `git diff main...HEAD` (or the default branch) to see changes in the current branch.
   - If still empty, inform the user and ask for the source of changes.
2. Run `git log -n 10 --oneline` to understand the sequence of commits and their intent.
3. Search for relevant PRDs or task specifications in `.taskmaster/` or `docs/` that match the branch name or commit keywords.

====================
PHASE 3 — GENERATION
====================

Based on your analysis, generate the PR description:

1. Follow the detected or default template strictly.
2. Ensure the tone is professional and the content is accurate.
3. If a language was specified, generate the entire description in that language.
4. If no language was specified, you MUST have asked the user in advance (see MANDATORY rule).

====================
PHASE 4 — OUTPUT
====================

Present the generated PR description to the user in a Markdown block.

Example Output (Default Template):

```markdown
## Description
This PR introduces a new skill for generating PR descriptions automatically...

## Task
- Create skills/generate-pr-description/SKILL.md
- Implement template detection logic.
- Add language selection support.

## Impact
- Improves developer productivity by automating repetitive documentation tasks.
- Ensures consistent PR descriptions across the project.
```

====================
WORKFLOW
====================

- Always verify if a PR template exists before proposing a structure.
- If the `git diff --staged` is empty, inform the user that there are no staged changes to analyze.
- Use the commit history to add context that might not be obvious from the diff alone.
