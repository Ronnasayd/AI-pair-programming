---
name: taskmaster-prd-generator
description: |
  Generate structured Product Requirements Documents (PRDs) for development projects in the `.taskmaster/prds/` directory. Use this skill whenever the user wants to create a PRD, has a project idea they want to document, needs to convert specs or descriptions into a formal PRD, or mentions they want to plan a project's requirements. The skill accepts text descriptions OR spec files, asks clarifying questions to fill information gaps, extracts key requirements, and lets the user review a preview before saving the file with timestamp format `dd-yy-MMMM-<short-description>.md`.

compatibility: |
  - Requires: File system access to create files in `.taskmaster/prds/`
  - Optional: Markdown syntax understanding for formatting output
---

## Overview

This skill helps you transform rough ideas, text descriptions, or specification files into well-structured PRDs. It works in three phases:

1. **Extract & Ask** — Parse input and ask clarifying questions to fill gaps
2. **Structure** — Organize information into a standard PRD template
3. **Review & Save** — Show preview and save to `.taskmaster/prds/` with auto-generated filename

## When to Use This Skill

- User says: "create a PRD for..." or "document this project spec"
- User provides a description or file with project requirements
- User wants to structure informal specs into a formal document
- User needs a PRD to feed into Task Master's `parse-prd` command

## Input Formats

The user can provide input in two ways:

### 1. Text Description

Single or multi-line description of the project. Examples:

- "A dashboard that shows real-time sales metrics"
- "Mobile app for tracking daily habits with notifications and analytics"
- A longer paragraph describing the project scope and goals

### 2. Specification File

Link or reference to an existing file containing specs (e.g., `.txt`, `.md`, or plain text pasted into the conversation)

## The Three-Phase Process

### Phase 1: Extract & Ask

**Your job:**

1. Parse the user's input (text or file)
2. Extract what you already know:
   - Problem/goal
   - Target users (if mentioned)
   - Key features (if mentioned)
   - Any technical hints
3. Ask 5-8 clarifying questions about missing pieces:
   - Who exactly are the users? (personas/roles)
   - What specific problem does it solve?
   - What's the first MVP — what's the minimum viable feature set?
   - Are there integration points or dependencies?
   - What's success? (measurable outcomes)
   - Technical constraints or platform preference?
   - Any existing solutions this competes with?
   - Realistic scope/timeline estimate?

**Don't demand perfect answers** — accept "not sure" or high-level responses and work with what you get.

### Phase 2: Structure

Generate PRD content using this template:

```
# Project: [Title]

## Overview
[High-level summary: what problem it solves, who it's for, why it's valuable]

## Core Features
[List each major feature with:
- What it does (1 sentence)
- Why it's important
- How it works (high-level, 2-3 sentences)]

## User Experience
- **Target Users**: [Personas/roles]
- **Key User Flows**: [1-2 main workflows users will do]
- **UI/UX Considerations**: [Responsiveness, accessibility, platform-specific notes]

## Technical Architecture
- **System Components**: [Major pieces: API, database, frontend, etc.]
- **Data Models**: [Key entities and relationships, if applicable]
- **Technology Stack**: [Languages, frameworks, key libraries]
- **Integration Points**: [Any external services or dependencies]

## Development Roadmap

### Phase 0: Foundation / MVP
[Minimal viable feature set to get something working]
- Task 1
- Task 2

### Phase 1: [Next logical phase]
[Build on MVP]
- Task 1
- Task 2

### Phase 2+: [Future enhancements]
[Nice-to-haves and advanced features]
- Task 1
- Task 2

## Logical Dependency Chain
[Brief explanation of feature/task ordering]

## Risks and Mitigations
- **Risk 1**: [Description]
  - Mitigation: [How to address]
  - Fallback: [Plan B]
- **Risk 2**: ...

## Appendix
- **References**: [Relevant docs, similar projects, research]
- **Glossary**: [Domain-specific terms]
- **Open Questions**: [Things to resolve later]
```

### Phase 3: Review & Save

1. **Show the preview** to the user — full rendered PRD in Markdown
2. **Ask for feedback**: "Does this look right? Any sections to revise?"
3. **Accept edits** (user can ask you to rewrite sections)
4. **Generate filename**: `dd-yy-MMMM-<short-description>.md`
   - `dd` = day of month (zero-padded: "01", "15", "31")
   - `yy` = 2-digit year ("26" for 2026)
   - `MMMM` = full month name ("March", "January", etc.)
   - `<short-description>` = slugified 2-4 word summary (kebab-case, lowercase)
   - Example: `20-26-March-dashboard-sales-metrics.md`
5. **Save to `.taskmaster/prds/`** with full path confirmation
6. **Confirm outcome**: "✅ Saved to `.taskmaster/prds/20-26-March-dashboard-sales-metrics.md`"

## Handling Edge Cases

**Very vague input** ("make a project plan"):

- Ask more initial questions before structuring
- Work with user iteratively to narrow scope

**Incomplete user answers**:

- Use reasonable defaults or note as "TBD" in the PRD
- Don't block on perfect information

**User wants major revisions**:

- Go back to Phase 2 and regenerate sections
- Show new preview
- Confirm before saving

**User provides detailed spec file**:

- Parse it thoroughly in Phase 1
- Ask only follow-up questions for gaps, not everything

## Output Notes

- **Always use Markdown** for the PRD file
- **Keep it concise** — aim for 500-1000 words total for simple PRDs
- **Be practical** — avoid over-engineering or unnecessary complexity
- **Make it Task-Master-ready** — structure so `task-master parse-prd` can extract tasks from sections

## Example Conversation

```
User: "I need a PRD for a note-taking app with collaboration"

You (Phase 1):
Q1: Who are the main users?
Q2: Is this for teams, individuals, or both?
Q3: What's the MVP — just create/edit/share notes, or include versioning?
Q4: Any platform preference (web, mobile, desktop)?
... etc

User: [answers questions]

You (Phase 2):
Generate full PRD using template

You (Phase 3):
Here's your PRD preview:
[full PRD content]

Does this look good? Any sections to revise?

User: [approves or asks for changes]

You: ✅ Saved to `.taskmaster/prds/20-26-March-note-collab-app.md`
```

## Tips for Success

1. **Ask follow-ups early** — the better your Phase 1 questions, the better the PRD
2. **Don't pretend to know technical details** — if user doesn't specify, leave as TBD or make reasonable assumptions
3. **Keep the roadmap realistic** — break into 2-3 phases max for clarity
4. **Link to existing docs** — if user mentions existing specs or architecture, reference them in Appendix
5. **Filename slug should be memorable** — "20-26-March-dashboard-sales" not "20-26-March-proj-v2-update"
