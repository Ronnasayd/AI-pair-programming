---
name: figma-requirements-screen-mapper
description: >
  Map software requirements to Figma screens, producing a table that shows which requirements
  belong to each screen, and which requirements don't belong to any screen.
  Use this skill whenever the user provides a requirements document (SRS, PRD, technical spec)
  AND a Figma file with multiple screens/frames and wants to understand which requirements
  apply to each screen.
  Triggers on phrases like: "map these requirements to the Figma screens",
  "which requirements belong to each screen", "create a requirements matrix for these screens",
  "relate my spec to each Figma frame", "which spec items apply to each screen",
  "trace requirements to screens", "requirements traceability matrix",
  "which requirements are covered per screen", "organize requirements by screen",
  or when the user provides a requirements doc path AND a Figma file URL and wants a mapping/matrix.
  Also triggers when the user asks "which requirements don't belong to any screen" or
  "what requirements are cross-cutting / non-UI".
  Always use this skill when BOTH a requirements document AND a multi-screen Figma reference
  are present and the user wants a mapping, matrix, or traceability table — even if they
  don't use the exact words "requirements screen mapper".
metadata:
  author: Ronnasayd Machado - github.com/Ronnasayd
  version: "1.0.0"
---

# Requirements ↔ Screen Mapper

Given a requirements document and a Figma file with multiple screens, produce a structured mapping table that shows:

1. **Per-screen requirement list** — for each Figma screen, which requirements are relevant
2. **Orphaned requirements** — requirements that don't clearly belong to any screen (cross-cutting concerns, back-end constraints, non-UI items)

---

## Inputs

| Input                 | Format                                                           | Example                                 |
| --------------------- | ---------------------------------------------------------------- | --------------------------------------- |
| Requirements document | File path (`.md`, `.txt`, `.pdf`, any readable text)             | `docs/specs/accounting-module.md`       |
| Figma reference       | Full URL to file **or** `fileKey` (full file, not a single node) | `https://figma.com/design/abc123/MyApp` |

Parse `fileKey` from the URL if needed. If a `node-id` is present in the URL, treat it as a hint to the starting page/frame — but still enumerate all sibling frames on that page.

---

## Decomposition into Sub-Problems

Break the task explicitly into five sub-problems and work through them sequentially. This structure helps avoid confusing requirements that apply to multiple screens or that have no screen correspondence.

### Sub-Problem 1 — Extract Requirements

Read the requirements document and extract a **flat, numbered list** of requirements.

Normalize each requirement to:

```
ID    | Statement (what the system must do/show)        | Type
------|--------------------------------------------------|-------------------
REQ-1 | The login form must validate e-mail format       | functional
REQ-2 | Error messages must appear in red below the field| visual/constraint
```

**Extraction heuristics** (apply in order of reliability):

1. Explicit IDs like `REQ-001`, `FR-3`, `UC-12`
2. Lines with "shall", "must", "should", "will"
3. User stories: `As a [role], I want…`
4. Bulleted/numbered lists under screen-titled headings
5. Tables with "Requirement" / "Description" columns

Keep the IDs from the document when they exist. Assign sequential ones (`REQ-N`) when absent.

Do **not** invent requirements — only extract what is stated explicitly or strongly implied.

### Sub-Problem 2 — Enumerate Screens

Use the Figma MCP to list all top-level frames in the file.

```
get_metadata(fileKey)   # Sparse XML of the entire file tree
```

From the XML, collect all **top-level frames** (direct children of a Page node). These are the screens. Extract:

- Frame `nodeId`
- Frame name (the design team's label, e.g., `Login`, `Dashboard / Overview`, `Checkout – Step 2`)

If the file has multiple pages, enumerate frames on every page and note the page name as a prefix in the screen name (e.g., `Onboarding / Welcome`).

> If the metadata output is very large, paginate or use targeted sub-calls. You don't need the full tree — just the first two levels of hierarchy to discover frame names.

### Sub-Problem 3 — Extract Design Context per Screen

For each screen, call:

```
get_design_context(fileKey, nodeId)   # Layout, component names, text content
```

Optionally, also fetch a screenshot if the tool is available — it helps identify labels, icons, and UI states that metadata might not describe clearly.

Build a **screen profile** summarizing:

- Purpose inferred from the frame name and layer names
- Key UI elements (form fields, buttons, text areas, navigation items)
- Visible text / labels present in the design (copy from layer names and text nodes)

Avoid loading full CSS/React output — you need semantic understanding, not code generation.

### Sub-Problem 4 — Map Requirements to Screens

For each requirement, decide which screen(s) it is relevant to.

**Scoring guidance:**

- **Explicit mention**: The requirement text names the screen or a synonym (e.g., "login page", "checkout step 2", "profile editor") → strong match
- **Element match**: The requirement refers to a UI element present in the screen profile (e.g., "submit button" or "e-mail field" found in the Login screen) → strong match
- **Intent match**: The requirement's action/verb aligns with the screen's purpose (e.g., a requirement about "password recovery" aligns with the ForgotPassword screen) → moderate match
- **Cross-cutting**: The requirement is about non-UI behavior (e.g., API latency, data retention, security headers) or applies globally (e.g., "all pages must show a navigation bar") → orphaned or annotated as global

A requirement may map to **multiple screens** if it genuinely applies to all of them (e.g., "the navigation bar must highlight the active section" applies to every screen that has a nav bar). In that case, list it in each relevant screen's column.

### Sub-Problem 5 — Generate the Report

Produce the output in three parts.

---

## Output Format

### Part 1 — Summary

```
## Requirements ↔ Screen Mapping

- Requirements document: <path>
- Figma file: <fileKey / URL>
- Total requirements: N
- Total screens: M
- Mapped requirements: X  (requirements assigned to ≥ 1 screen)
- Orphaned requirements: Y  (requirements not assigned to any screen)
```

### Part 2 — Mapping Table

Render one row per screen:

| Screen       | Requirements        |
| ------------ | ------------------- |
| Login        | REQ-1, REQ-2, REQ-7 |
| Dashboard    | REQ-3, REQ-4, REQ-5 |
| Profile Edit | REQ-6, REQ-8        |

After the table, expand each row into a detail block to make the mapping easy to review:

#### Login

| ID    | Statement                                            |
| ----- | ---------------------------------------------------- |
| REQ-1 | The login form must validate e-mail format           |
| REQ-2 | Error messages must appear in red below the field    |
| REQ-7 | The "Forgot password" link must be visible on mobile |

_(repeat for each screen)_

### Part 3 — Orphaned Requirements

Requirements that don't belong to any specific screen:

| ID     | Statement                                    | Reason not mapped                                  |
| ------ | -------------------------------------------- | -------------------------------------------------- |
| REQ-9  | API responses must complete within 500 ms    | Backend/performance, not tied to a specific screen |
| REQ-10 | Session tokens must expire after 30 minutes  | Security/backend constraint                        |
| REQ-11 | All screens must be accessible (WCAG 2.1 AA) | Global / cross-cutting                             |

Include a **reason** for each orphaned requirement — this helps the team decide where to track it (back-end tickets, global design guidelines, etc.).

---

## Working Tips

- **Start with a quick requirements count** before diving into Figma. If the document has hundreds of requirements, tell the user upfront and suggest chunking by section rather than processing all at once.
- **Lean on frame names** — well-named frames make mapping accurate; if frame names are vague (e.g., `Frame 1`, `Frame 2`), ask the user for clarification before proceeding.
- **When in doubt, map broadly** — it is better to include a requirement under two screens than to misclassify it as orphaned. Orphaned should mean "genuinely has no UI representation", not "unclear which screen".
- **Flag ambiguous requirements** with a `⚠️` symbol in the mapping table and add a note (e.g., "Could apply to multiple screens — verify with the team").
- **Global requirements** (e.g., branding, accessibility, performance) are valid orphans; call them out as "Global/Cross-cutting" in the Reason column rather than leaving them with no context.

---

## Error Handling

| Situation                     | Action                                                                   |
| ----------------------------- | ------------------------------------------------------------------------ |
| Figma MCP not connected       | Stop immediately and tell the user to enable the Figma MCP server        |
| File key invalid / not found  | Report the error and ask the user to verify the URL or file key          |
| Requirements file not found   | Report and ask user for the correct path                                 |
| No top-level frames found     | Inform the user and ask if they want to use a specific `node-id` instead |
| Vague frame names (`Frame 1`) | Ask the user for the names/purpose of each frame before mapping          |
