---
name: taskmaster-prd-generator
description: |
  Generate structured Product Requirements Documents (PRDs) for development projects in the `.taskmaster/prds/` directory. Use this skill whenever the user wants to create a PRD, has a project idea they want to document, needs to convert specs or descriptions into a formal PRD, or mentions they want to plan a project's requirements. The skill accepts text descriptions OR spec files, asks targeted clarifying questions to fill information gaps, extracts key requirements, and lets the user review a preview before saving the file with timestamp format `yyyy-mm-dd-<short-description>.md`.

compatibility: |
  - Requires: File system access to create files in `.taskmaster/prds/`
  - Optional: Markdown syntax understanding for formatting output
---

## Overview

This skill transforms rough ideas, text descriptions, or spec files into well-structured PRDs. It follows three phases:

1. **Extract & Ask** — Parse input, extract what's known, ask targeted questions for the rest
2. **Structure** — Organize into a standard PRD template optimized for `task-master parse-prd`
3. **Review & Save** — Show a preview, incorporate feedback, then save with an auto-generated filename

---

## When to Use This Skill

- User says "create a PRD for…", "write up requirements for…", "document this spec"
- User provides a project description, file, or rough notes and wants them structured
- User mentions wanting to run `task-master parse-prd` on a requirements doc
- User needs to plan a feature or project before breaking it into tasks

---

## Input Formats

**Text description** — anything from a single sentence to a multi-paragraph writeup:

> "A dashboard that shows real-time sales metrics"
> "Mobile app for tracking daily habits with streaks, notifications, and weekly analytics"

**Spec file** — reference or paste an existing `.txt`, `.md`, or similar file. Extract what you can and ask only about the gaps.

---

## Phase 1: Extract & Ask

### 1a. Parse the input

Before asking anything, extract every detail already present:

- The core problem or goal
- Who the users are (if mentioned)
- Features or capabilities described
- Any technical hints (stack, platform, constraints)
- Timeline or scale hints

### 1b. Ask targeted clarifying questions

Ask **only** about the gaps — don't ask for information the user already provided. Aim for **3–6 focused questions**, not a generic checklist. Prioritize in this order:

1. **Who are the users?** — role, technical level, how they'll discover the product
2. **What's the core problem?** — the pain point or opportunity, not just the feature
3. **What's the MVP?** — the absolute minimum that delivers value; distinguish from nice-to-haves
4. **What does success look like?** — a measurable outcome (e.g. "users complete onboarding in under 3 min")
5. **Are there hard constraints?** — tech stack, integrations, budget, timeline, compliance
6. **What already exists?** — competitors, internal tools, prior attempts

**Don't demand perfect answers.** Accept "not sure" or vague responses — note them as TBD and move on.

### 1c. Adjust depth to input quality

| Input quality         | Your approach                              |
| --------------------- | ------------------------------------------ |
| Vague (1–2 sentences) | Ask 5–6 questions before drafting          |
| Medium (paragraph)    | Ask 3–4 targeted follow-ups                |
| Detailed spec file    | Ask only 1–2 gap-fillers; extract the rest |

---

## Phase 2: Structure

Use this template. Keep total length to **500–1000 words** for simple PRDs; more is fine for complex projects but avoid padding.

```markdown
# [Project Title]

## Overview

[2–3 sentences: what problem it solves, who it's for, and why it matters now. Avoid feature lists here — those go in Core Features.]

## Problem Statement

[The specific pain point or gap this addresses. Written from the user's perspective, not the builder's. Include any relevant context: current workarounds, scale of the problem, cost of inaction.]

## Core Features

### [Feature Name]

- **What it does**: [One sentence]
- **Why it matters**: [One sentence on user value or business reason]
- **How it works**: [2–3 sentences on the mechanism or flow — high-level only]

[Repeat for each major feature. Aim for 3–6 features for the MVP; move stretch features to the Roadmap.]

## User Experience

- **Target Users**: [Personas or roles — be specific. "SMB finance managers, non-technical" is better than "business users".]
- **Key User Flows**:
  1. [Primary flow — e.g. "User signs up, connects their store, sees first dashboard in under 5 min"]
  2. [Secondary flow — e.g. "Returning user receives a daily digest email and clicks through to drill down"]
- **UI/UX Considerations**: [Platform (web/mobile/desktop), responsiveness, accessibility notes, branding constraints]

## Technical Architecture

- **System Components**: [List major pieces — API, frontend, background jobs, external services]
- **Data Models**: [Key entities and their relationships. E.g. "User → many Projects → many Tasks"]
- **Technology Stack**: [Languages, frameworks, key libraries. Mark as TBD if not decided.]
- **Integration Points**: [Third-party APIs, auth providers, data sources, webhooks]
- **Non-functional Requirements**: [Performance targets, SLA, data retention, security/compliance]

## Development Roadmap

### Phase 0 — Foundation (MVP)

[The minimum working thing. Focus on the riskiest assumptions to validate first.]

- [ ] Task 1
- [ ] Task 2

### Phase 1 — [Short label, e.g. "Core Workflows"]

[Build on the MVP. Address the next most important user needs.]

- [ ] Task 1
- [ ] Task 2

### Phase 2 — [Short label, e.g. "Scale & Polish"]

[Nice-to-haves, performance work, advanced features. Deprioritize anything not needed for product-market fit.]

- [ ] Task 1
- [ ] Task 2

## Dependency Chain

[2–4 sentences explaining the sequencing logic. Why does Phase 0 come before Phase 1? What unlocks what? This is the section `task-master parse-prd` uses to infer task ordering — be explicit about blockers and prerequisites.]

Example: "Auth must be in place before any personalized features. The data pipeline (Phase 0) must be stable before building analytics on top of it (Phase 1). Mobile clients can be built in parallel with the web client once the API contract is frozen."

## Risks & Mitigations

| Risk                                 | Likelihood | Impact | Mitigation                                             | Fallback                        |
| ------------------------------------ | ---------- | ------ | ------------------------------------------------------ | ------------------------------- |
| [e.g. Third-party API rate limits]   | Medium     | High   | Cache aggressively, add retry logic                    | Queue-based async processing    |
| [e.g. Scope creep from stakeholders] | High       | Medium | Lock MVP scope in this doc; defer additions to Phase 2 | Explicit change-request process |

## Open Questions

[Anything unresolved that will affect design or build decisions. Be specific about who needs to answer and by when if known.]

- [ ] [Question 1 — e.g. "Do we need GDPR compliance at launch? @legal to confirm by end of Q2"]
- [ ] [Question 2]

## Appendix

- **References**: [Links to related docs, prior art, competitor analysis, design files]
- **Glossary**: [Domain-specific terms a new developer would need to know]
- **Out of Scope**: [Explicitly list what this PRD does NOT cover, to prevent scope drift]
```

### Template notes

- **Checkbox tasks in the Roadmap** (`- [ ]`) are intentional — `task-master parse-prd` parses these as actionable items.
- **The Dependency Chain section is critical** for Task Master. Don't skip it or write it vaguely.
- **Out of Scope in the Appendix** prevents scope creep and helps parse-prd ignore irrelevant content.
- Mark anything unknown as `TBD` rather than omitting it — a missing section is harder to spot than a TBD field.

---

## Phase 3: Review & Save

### 3a. Show the full preview

Render the complete PRD in Markdown. Tell the user:

> "Here's your PRD preview. Let me know if any section needs changes — or say 'looks good' and I'll save it."

### 3b. Collect feedback

Accept edits section by section. Common requests:

- "Expand the roadmap" → add more tasks, split phases further
- "Simplify the technical section" → reduce to bullet points
- "Add a competitor comparison" → add to Appendix

Regenerate only the affected section unless the user asks for a full rewrite.

### 3c. Generate the filename

Format: `YYYY-MM-DD-short-description.md`

| Part                | Format                     | Example                   |
| ------------------- | -------------------------- | ------------------------- |
| `DD`                | Day of month, zero-padded  | `09`                      |
| `YYYY`              | 4-digit year               | `2026`                    |
| `MM`                | 2-digit month, zero-padded | `04`                      |
| `short-description` | 2–4 word kebab-case slug   | `sales-metrics-dashboard` |

**Full example**: `2026-04-09-sales-metrics-dashboard.md`

**Slug rules**:

- Lowercase, hyphens only (no underscores or spaces)
- 2–4 words that uniquely identify the project
- Descriptive, not generic: `habit-tracker-mobile` not `project-v2-update`

### 3d. Check and create the directory

Before saving, verify `.taskmaster/prds/` exists. If not, create it:

```bash
mkdir -p .taskmaster/prds/
```

### 3e. Save and confirm

Save to `.taskmaster/prds/<filename>.md` and confirm:

> ✅ Saved to `.taskmaster/prds/09-26-April-sales-metrics-dashboard.md`

### 3f. Handling post-save revisions

If the user asks for changes after saving, re-generate the relevant sections, show the updated preview, then **overwrite the same file** (don't create a new one unless the user asks). Confirm the overwrite:

> ✅ Updated `.taskmaster/prds/09-26-April-sales-metrics-dashboard.md`

---

## Edge Case Handling

**Very vague input** ("I want to build an app"):

- Ask 5–6 questions before attempting to structure anything.
- A rough draft from too little information is worse than no draft.

**User provides a spec file with most details**:

- Extract thoroughly in Phase 1.
- Ask only 1–2 follow-ups for genuine gaps.
- Don't re-ask what's already in the file.

**User answers "not sure" to most questions**:

- Use reasonable defaults or mark as TBD.
- Note at the top of the PRD: "Several fields are TBD — see Open Questions."
- Don't block on perfect information.

**User wants major revisions after preview**:

- Go back to Phase 2, regenerate the full PRD.
- Show the new preview before saving again.

**User wants to create multiple PRDs in one session**:

- Complete Phase 3 (save) for the first before starting Phase 1 for the second.
- Keep filenames distinct.

**`.taskmaster/prds/` doesn't exist**:

- Create it automatically with `mkdir -p` before saving.
- Mention it in the confirmation: "✅ Created `.taskmaster/prds/` and saved `09-26-April-sales-metrics-dashboard.md`"

---

## Full Example Conversation

```
User: "I need a PRD for a note-taking app with real-time collaboration"

You (Phase 1 — extract then ask):
I can see this is a collaborative note-taking app. A few things will shape the PRD:

1. Who are the primary users — individuals, small teams, or enterprise orgs?
2. What's the MVP — just create/edit/share notes, or does real-time sync need to be in v1?
3. Any platform priority — web-first, or do you need mobile from the start?
4. Are there any existing tools this replaces or integrates with (Notion, Confluence, etc.)?

User: [answers]

You (Phase 2 — draft):
[Generates full PRD using template above]

You (Phase 3 — preview + save prompt):
Here's your PRD. Let me know if anything needs adjusting — or say "looks good" and I'll save it.

User: "Expand the roadmap a bit, then save"

You: [Expands roadmap section, shows updated preview]
✅ Saved to `.taskmaster/prds/09-26-April-collab-note-taking.md`

You can now run: task-master parse-prd .taskmaster/prds/09-26-April-collab-note-taking.md
```

---

## Quality Checklist (before saving)

Run through this mentally before finalizing:

- [ ] Problem Statement is written from the **user's perspective**, not the builder's
- [ ] MVP is clearly scoped — no phase 2 features sneaking into phase 0
- [ ] Dependency Chain explains **why** the phases are ordered this way
- [ ] Roadmap tasks use `- [ ]` checkboxes (required for `task-master parse-prd`)
- [ ] Open Questions section is not empty — at minimum, list anything marked TBD
- [ ] Out of Scope is populated — prevents parse-prd from generating off-target tasks
- [ ] Filename slug is memorable and specific

---

## Tips

1. **Ask early, ask well** — a great Phase 1 cuts revision loops in half. The more specific your questions, the more useful the output.
2. **Optimize for parse-prd** — the Roadmap checkboxes and Dependency Chain are the sections Task Master cares about most. Keep them crisp and well-structured.
3. **Leave explicit TBDs** — they're better than omissions. Parse-prd skips TBD fields; missing sections can cause parse errors.
4. **Scope is a feature** — a tight MVP with a clear Out of Scope section is more valuable than an ambitious plan that's hard to execute.
5. **One PRD per project** — if the user describes two distinct products, create two separate PRDs in the same session.
