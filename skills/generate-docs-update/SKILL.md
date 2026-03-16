---
name: generate-docs-update
description: "A skill for generating structured documentation updates based on git diffs and specialist instructions. Use this skill to analyze code changes, identify required documentation adjustments, and generate detailed update reports that comply with the system's guidelines for clear, concise, and accurate documentation."
argument-hint: "[git_diff_command]: A string command containing the git diff output to be analyzed for documentation updates."
---

MANDATORY: Use documentations-specialist agent
MANDATORY: execute the **$0** argument as a git diff command or any other command that produces a diff-like output or a code file and analyze the output according to the system instructions.

## TASK:

Based on the modifications and instructions provided, adjust the documentation accordingly. Review existing documentation files (check the docs/ folder and docs/SUMMARY.md if they exist) and see which ones need updating based on the changes made.

Preferably update existing files, but create new ones if necessary. Only update files if the changes are relevant to the file's content type. Don't add text just for the sake of adding it. Before any modification, show what will be added and ask if you should proceed.
