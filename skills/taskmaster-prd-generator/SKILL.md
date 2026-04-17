---
name: taskmaster-prd-generator
description: |
  Generate structured Product Requirements Documents (PRDs) for development projects in the `.taskmaster/prds/` directory. Use this skill whenever the user: says "create a PRD", "write requirements", "document this spec", "plan this project", or "help me structure this idea"; pastes a project description, rough notes, or spec file and wants it organized; mentions wanting to run `task-master parse-prd`; or describes a feature, app, or system they want to build — even casually. Trigger on intent to plan or document a project, not just the word "PRD". When in doubt, use this skill.

compatibility: |
  - Requires: File system access to create `.taskmaster/prds/` and write `.md` files
  - Optional: `task-master` CLI for downstream parse-prd usage
---

## Overview

This skill transforms rough ideas, text descriptions, pasted specs, or uploaded files into well-structured PRDs optimized for `task-master parse-prd`. It follows three phases:

1. **Extract & Ask** — Parse what's given, extract what's known, ask targeted questions only for genuine gaps
2. **Structure** — Organize into a standard PRD template with parse-prd-critical sections done right
3. **Review & Save** — Show a preview, apply feedback section-by-section, then save with an auto-generated filename

---

## Phase 1: Extract & Ask

### 1a. Parse the input first

Before asking anything, scan the input — whether it's a sentence, a paragraph, a pasted spec, or a file — and extract:

- The core problem or goal
- Who the users are (if mentioned)
- Features or capabilities described
- Technical hints (stack, platform, constraints, existing systems)
- Timeline, scale, or urgency signals
- Anything already scoped out or explicitly excluded

**If the user uploads or pastes a detailed spec**, extract thoroughly. A 500-word spec might answer 80% of the template. Only ask about genuine gaps — don't re-ask what's already there.

### 1b. Ask targeted clarifying questions

Ask **only** about gaps that would materially change the PRD. Aim for **3–5 focused questions**. Never ask a question if the answer is already inferable from context.

Prioritize gaps in this order:

| Priority | Gap                              | Why it matters                                                 |
| -------- | -------------------------------- | -------------------------------------------------------------- |
| 1        | **Who are the users?**           | Shapes UX, onboarding, and complexity decisions                |
| 2        | **What's the core pain point?**  | Distinguishes solution from symptom                            |
| 3        | **What's the true MVP?**         | Keeps Phase 0 honest; prevents scope creep                     |
| 4        | **What does success look like?** | Makes the goal measurable, not aspirational                    |
| 5        | **Hard constraints?**            | Tech stack locked? Compliance? Existing systems to integrate?  |
| 6        | **What exists today?**           | Competitors, internal tools, prior attempts to avoid repeating |

**Handling vague answers**: Accept "not sure" or "TBD". Note it explicitly in Open Questions and move on. A PRD with honest TBDs is more useful than one with invented specifics.

### 1c. Scale depth to input quality

| Input quality                     | Questions to ask                       | Notes                                             |
| --------------------------------- | -------------------------------------- | ------------------------------------------------- |
| 1–2 sentences, very vague         | 5–6 questions                          | Don't draft until you have enough to work with    |
| 1–3 paragraphs                    | 3–4 targeted follow-ups                | Extract what's there; ask only about genuine gaps |
| Detailed spec or pasted doc       | 1–2 gap-fillers                        | Most info is already there; extract aggressively  |
| Code, mockups, or diagrams pasted | Ask about _intent and users_, not tech | The how is visible; the why usually isn't         |

---

## Phase 2: Structure

Use this template. Keep length proportional to project complexity — a simple CRUD app needs 600 words, a platform needs 1500. Avoid padding.

```markdown
# [Project Title]

## Overview

[2–3 sentences: what problem it solves, who it's for, and why now. No feature lists here — those go in Core Features. Think elevator pitch, not changelog.]

## Problem Statement

[The specific pain point or gap, written from the user's perspective. Include: what users do today (the workaround), why that's painful or costly, and what changes if this is built. Avoid builder-centric language like "we will implement".]

## Core Features

### [Feature Name]

- **What it does**: [One sentence — the observable behavior]
- **Why it matters**: [One sentence — the user value or business reason]
- **How it works**: [2–3 sentences — the mechanism or flow, high-level only. Enough for a developer to estimate effort.]

[Repeat for each major MVP feature. Aim for 3–6. Move stretch goals to the Roadmap.]

## User Experience

- **Target Users**: [Specific personas — role, technical level, context. "SMB finance managers with no SQL experience" beats "business users".]
- **Key User Flows**:
  1. [Primary happy path — start to value. E.g. "User connects store → sees first dashboard → exports report, all in under 5 min"]
  2. [Secondary or return flow — E.g. "Returning user receives digest email, clicks through to drill down on a metric"]
- **UI/UX Considerations**: [Platform (web/mobile/desktop), responsiveness, accessibility requirements, any branding or design system constraints]

## Technical Architecture

- **System Components**: [Major pieces — e.g. "REST API, React SPA, Postgres, Redis cache, S3 for file storage, SendGrid for email"]
- **Data Models**: [Key entities and relationships. E.g. "User → many Projects → many Tasks; Task has status, assignee, due_date"]
- **Technology Stack**: [Languages, frameworks, key libraries. Mark unknowns as TBD — don't invent a stack.]
- **Integration Points**: [Third-party APIs, auth providers, webhooks, data sources, internal systems]
- **Non-functional Requirements**: [Concrete targets where possible — e.g. "p95 response < 500ms", "GDPR compliant", "99.9% uptime SLA", "data retained 7 years"]

## Development Roadmap

> ⚠️ `task-master parse-prd` reads these checkboxes to generate tasks. Use `- [ ]` format for every actionable item. Be specific — "Set up auth with JWT" not "Authentication".

### Phase 0 — Foundation (MVP)

[The minimum thing that proves the core value. Prioritize the riskiest assumptions first.]

- [ ] [Concrete task — e.g. "Implement user auth (email/password + JWT)"]
- [ ] [Concrete task]
- [ ] [Concrete task]

### Phase 1 — [Short label, e.g. "Core Workflows"]

[Builds on the validated MVP. Addresses the next most important user needs.]

- [ ] [Concrete task]
- [ ] [Concrete task]

### Phase 2 — [Short label, e.g. "Scale & Polish"]

[Nice-to-haves, performance, advanced features. If it's not needed for product-market fit, it goes here.]

- [ ] [Concrete task]
- [ ] [Concrete task]

## Dependency Chain

[This section is critical for `task-master parse-prd` — it uses it to infer task ordering and blockers. Be explicit.]

Format each dependency as: **[Component/Phase X]** must be complete before **[Component/Phase Y]** because **[reason]**.

Example:

- **Auth system** must be complete before **any personalized features** because user identity is required for data scoping.
- **Data ingestion pipeline (Phase 0)** must be stable before **analytics dashboards (Phase 1)** because dashboards read from the pipeline's output.
- **API contract** must be frozen before **mobile client development** can begin; web and mobile clients can then be built in parallel.

## Risks & Mitigations

| Risk                                                             | Likelihood | Impact | Mitigation                                             | Fallback                        |
| ---------------------------------------------------------------- | ---------- | ------ | ------------------------------------------------------ | ------------------------------- |
| [e.g. Third-party API rate limits or deprecation]                | Medium     | High   | Cache aggressively; add retry/backoff logic            | Queue-based async processing    |
| [e.g. Scope creep from stakeholders]                             | High       | Medium | Lock MVP scope in this doc; defer additions to Phase 2 | Explicit change-request process |
| [e.g. Key technical unknown — e.g. "real-time sync feasibility"] | Low        | High   | Spike in Phase 0 before committing to architecture     | Async-first fallback design     |

## Open Questions

[Anything unresolved that affects design or build decisions. Be specific about owner and deadline where known. Don't leave this empty — at minimum, list anything marked TBD above.]

- [ ] [Question — e.g. "Do we need GDPR compliance at launch? @legal to confirm by end of Q2"]
- [ ] [Question — e.g. "Stack TBD: evaluate Next.js vs Remix before Phase 0 kickoff"]

## Appendix

- **Out of Scope**: [Explicitly list what this PRD does NOT cover. This prevents parse-prd from generating off-target tasks and prevents scope drift in planning. E.g. "Mobile app (web-only for MVP)", "Multi-tenancy", "Offline mode"]
- **References**: [Links to design files, competitor analysis, prior docs, related PRDs]
- **Glossary**: [Domain terms a new developer would need. Skip if the domain is self-evident.]
```

### Critical template rules

**Roadmap checkboxes are not optional.** `task-master parse-prd` parses `- [ ]` items as tasks. Prose descriptions without checkboxes will be ignored or misread. Every actionable item must use this format.

**Dependency Chain must be explicit.** Vague statements like "phases are sequential" give parse-prd nothing to work with. Write each dependency as a named blocker relationship with a reason.

**Out of Scope belongs in Appendix, not buried.** It prevents parse-prd from generating tasks for things you don't want. Populate it even if the list is short.

**Mark unknowns as TBD, never omit.** A missing section causes parse errors or silent gaps. A TBD field is skipped cleanly.

---

## Phase 3: Review & Save

### 3a. Show the full preview

Render the complete PRD in Markdown. Then say:

> "Here's your PRD. Let me know if any section needs changes — or say 'looks good' and I'll save it."

### 3b. Handle feedback section-by-section

Regenerate only the affected section unless the user asks for a full rewrite. Common requests and how to handle them:

| Request                              | Action                                                                           |
| ------------------------------------ | -------------------------------------------------------------------------------- |
| "Expand the roadmap"                 | Add more tasks, split phases, make task descriptions more specific               |
| "Simplify the tech section"          | Reduce to a tight bullet list; remove speculation                                |
| "Add more risks"                     | Add 2–3 rows to the Risks table using project-specific scenarios                 |
| "The problem statement is too vague" | Rewrite from the user's perspective; add the "cost of inaction" angle            |
| "Change the stack to X"              | Update Technical Architecture and any roadmap tasks that reference the old stack |
| Major structural change              | Regenerate full PRD, show new preview before saving                              |

### 3c. Run the quality checklist before saving

Don't skip this — catch issues before the file is written.

- [ ] Problem Statement is written from the **user's perspective**, not the builder's — no "we will implement" language
- [ ] MVP (Phase 0) contains only the minimum needed to validate the core value — no Phase 1 features sneaking in
- [ ] Every roadmap task uses `- [ ]` checkbox format and is specific enough to estimate (not just "Authentication")
- [ ] Dependency Chain has explicit named blocker relationships with reasons — not just "phases are sequential"
- [ ] Open Questions is not empty — at minimum, lists anything marked TBD
- [ ] Out of Scope in Appendix is populated — even a short list prevents scope drift
- [ ] Filename slug is specific and memorable — `habit-tracker-mobile` not `project-v2`

### 3d. Generate the filename

Format: `YYYY-MM-DD-short-description.md`

| Part                | Format                     | Example                   |
| ------------------- | -------------------------- | ------------------------- |
| `YYYY`              | 4-digit year               | `2026`                    |
| `MM`                | 2-digit month, zero-padded | `04`                      |
| `DD`                | Day of month, zero-padded  | `17`                      |
| `short-description` | 2–4 word kebab-case slug   | `sales-metrics-dashboard` |

**Full example**: `2026-04-17-sales-metrics-dashboard.md`

**Slug rules**: lowercase, hyphens only (no underscores or spaces), 2–4 words, descriptive not generic.

### 3e. Check directory, save, confirm

```bash
mkdir -p .taskmaster/prds/
```

Save to `.taskmaster/prds/<filename>.md`, then confirm:

> ✅ Saved to `.taskmaster/prds/2026-04-17-sales-metrics-dashboard.md`
>
> You can now run: `task-master parse-prd .taskmaster/prds/2026-04-17-sales-metrics-dashboard.md`

### 3f. Post-save revisions

If the user requests changes after saving, regenerate the affected sections, show the updated preview, then **overwrite the same file** (don't create a new one unless the user asks):

> ✅ Updated `.taskmaster/prds/2026-04-17-sales-metrics-dashboard.md`

---

## Edge Case Handling

**Very vague input** ("I want to build an app"):
Ask 5–6 questions before drafting anything. A bad first draft creates more work than a good set of upfront questions.

**Detailed spec provided**:
Extract aggressively. Ask only 1–2 follow-ups for genuine gaps. Never re-ask what's already in the file.

**User pastes code, mockups, or diagrams**:
The implementation is visible; ask about intent, users, and what problem this solves. Don't ask them to explain the code.

**User answers "not sure" to most questions**:
Use reasonable defaults, mark unknowns as TBD, and populate Open Questions with the unresolved items. Never block on perfect information.

**Major revisions after preview**:
Go back to Phase 2, regenerate the full PRD, show the new preview before saving.

**Multiple PRDs in one session**:
Complete Phase 3 (save) for the first before starting Phase 1 for the second. Keep filenames distinct.

**`.taskmaster/prds/` doesn't exist**:
Create it automatically. Mention it in the confirmation: "✅ Created `.taskmaster/prds/` and saved `2026-04-17-collab-notes.md`"

**User asks for a PRD but doesn't want the full template**:
Ask which sections they need. A lean PRD with solid Roadmap and Dependency Chain sections is better than a forced full template with padded content.

---

## Anti-patterns to Avoid

- **Invented specifics**: If the stack isn't mentioned, mark it TBD. Don't fill in "React + Node.js" because it's common.
- **Feature-list overviews**: The Overview section is an elevator pitch, not a changelog. Features belong in Core Features.
- **Vague roadmap tasks**: "Set up database" is not a task. "Set up Postgres with migrations for User, Project, and Task tables" is.
- **Prose-only dependencies**: "Phase 1 follows Phase 0" tells parse-prd nothing. Name the blocker and explain why.
- **Empty Open Questions**: Every PRD has unknowns. If this section is empty, it means they weren't surfaced — not that they don't exist.
- **Generic slugs**: `2026-04-17-new-project.md` is useless in a directory with 10 PRDs. Make it specific.
