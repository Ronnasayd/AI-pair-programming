---
name: figma-requirements-conformance
description: >
  Verify conformance between a software requirements specification (SRS) document and a Figma screen design.
  Use this skill whenever the user wants to audit whether a design screen matches its requirements,
  check if requirements are reflected in a Figma mockup, find gaps between an SRS and a UI design,
  validate design compliance with specification, or identify over/under-specified areas in requirements vs design.
  Triggers on phrases like: "check if the design matches the requirements", "audit this Figma screen against the spec",
  "what's missing in the design", "verify requirements vs Figma", "conformance check", "SRS vs design",
  "does the design cover all requirements", "gap analysis between spec and Figma", or when the user provides
  a document path and a Figma URL and asks whether they agree.
  Always use this skill when BOTH a requirements document path AND a Figma reference are present in the request,
  even if the user doesn't use the word "conformance" or "audit".
metadata:
  mcp-server: figma
---

# Figma Requirements Conformance

Audit a software requirements specification (SRS or technical spec) against a Figma screen, producing a structured conformance report that highlights what matches, what's missing from the design, and what design elements lack a corresponding requirement.

## Inputs

| Input                 | Format                                                | Example                                             |
| --------------------- | ----------------------------------------------------- | --------------------------------------------------- |
| Requirements document | File path (`.md`, `.txt`, any readable text)          | `docs/requirements/login-screen.md`                 |
| Figma reference       | Full URL with `node-id` **or** `fileKey` + frame name | `https://figma.com/design/abc123/App?node-id=10-25` |

If the Figma reference is a full URL, parse `fileKey` and `nodeId` from it. If the user provides only a `fileKey` and `frame name`, use `get_metadata` first to locate the node by name.

---

## Phase 1 — Ingest the Requirements

Read the requirements document from the provided path. Accept any text-based format (Markdown, plain text, SRS-style).

**Extract and normalize requirements into a flat list.** Each requirement should have:

- An **ID** — use the document's own (`REQ-001`, `FR-3`, user story number, etc.) or assign sequential ones if absent
- A **statement** — what the system/screen must do or show
- A **type** hint: `functional`, `visual`, `content`, `behavior`, `constraint`

### Extraction heuristics

Look for these patterns in the document (in order of reliability):

1. Numbered sections with "shall", "must", "should" (e.g., `3.1 The login button shall be disabled when the form is invalid`)
2. Explicit requirement IDs (e.g., `REQ-042:`, `FR-3`, `UC-12`)
3. User stories (`As a [user], I want [action] so that [benefit]`)
4. Bulleted/numbered lists under headings that describe a specific screen or feature
5. Tables with "Requirement" / "Description" columns

**Do not generate requirements** that are not in the document — only extract what is stated explicitly or clearly implied. If a section is ambiguous, note it in the report.

---

## Phase 2 — Extract the Figma Design Context

Use the Figma MCP to retrieve design information for the specified screen.

### Step 2a — Verify MCP connection

Before calling any tool, confirm the Figma MCP server is available. If not, inform the user that the MCP connection is required and stop.

### Step 2b — Get the design context

Run both of these to get complementary views:

```
get_metadata(fileKey, nodeId)      # Structural XML of all layers
get_design_context(fileKey, nodeId) # CSS/layout/component representation
```

If `get_screenshot(fileKey, nodeId)` is available, also capture a screenshot. It can help identify visible labels, icons, or UI states that the metadata might not describe clearly.

### Step 2c — Catalog design elements

From the metadata/context output, extract a **flat catalog of design elements**:

- Named layers / frames / groups (especially meaningful names like `Button/Submit`, `Input/Email`, `ErrorMessage`)
- Visible text labels (buttons, headings, placeholders, error messages, tooltips)
- Interactive controls (inputs, buttons, checkboxes, selects, links)
- States explicitly modeled (hover, disabled, error, loading, empty)
- Navigation endpoints implied by the design (e.g., links labeled "Forgot password?")
- Validation or conditional elements (e.g., `Error state` frames, required field indicators)
- Structural sections (header, footer, form, modal, sidebar)

When a layer name is generic (e.g., `Frame 23`), rely on its content and position to interpret its purpose.

---

## Phase 3 — Conformance Analysis

Match each requirement against the design catalog, and each design element against the requirements.

### Matching strategy

A requirement is **covered** by the design when:

- A design element clearly represents the same feature, control, or content (exact or semantically equivalent match)
- Example: Requirement `FR-5: The form must have an email input field` → Design has a layer `Input/Email` with placeholder `Enter your email`

A requirement has a **design gap** when:

- No design element corresponds to it
- The design exists but is incomplete (e.g., loading state required but no loading layer found)
- Example: Requirement `FR-8: Show a success message after form submission` → No success state or confirmation layer found

A design element has a **requirements gap** when:

- It introduces behavior, content, or UI that is not described in any requirement
- Example: Design has a `Terms and Conditions` checkbox with a link → no requirement mentions this

### Ambiguous cases

If a match is uncertain, flag it as **⚠️ Uncertain** with a brief explanation. Avoid forcing matches — it's more useful to surface ambiguity than to over-report either conformance or gaps.

---

## Phase 4 — Generate the Conformance Report

Produce the report in English using the template below. Be specific — reference requirement IDs and design layer names precisely.

---

## Conformance Report

**Document:** `<path to requirements document>`
**Figma Screen:** `<Figma URL or fileKey/frame>`
**Date:** `<today>`

---

### Summary

| Category                    | Count |
| --------------------------- | ----- |
| Requirements analyzed       | N     |
| Design elements cataloged   | N     |
| ✅ Conformant               | N     |
| 🔴 Gaps in Design           | N     |
| 🟡 Gaps in Requirements     | N     |
| ⚠️ Uncertain / Needs Review | N     |

---

### ✅ Conformant Items

Items where the design clearly satisfies the requirement.

| Req ID | Requirement                  | Design Evidence                                         |
| ------ | ---------------------------- | ------------------------------------------------------- |
| FR-1   | User must see an email input | Layer `Input/Email` with placeholder "Enter your email" |
| ...    |                              |                                                         |

---

### 🔴 Gaps in Design

Requirements that have **no clear design representation**. These represent risks — the design may be incomplete or the feature was deprioritized.

For each gap, include a suggested action.

| Req ID | Requirement                            | Gap Description                               | Suggested Action                        |
| ------ | -------------------------------------- | --------------------------------------------- | --------------------------------------- |
| FR-8   | Show success message after form submit | No success state or confirmation screen found | Add a success state to the Figma screen |
| ...    |                                        |                                               |                                         |

---

### 🟡 Gaps in Requirements

Design elements that **introduce features, content, or behavior not described in any requirement**. These may be intentional additions but should be explicitly documented or removed.

| Design Element              | Description                      | Suggested Action                                |
| --------------------------- | -------------------------------- | ----------------------------------------------- |
| Checkbox `I agree to Terms` | Not mentioned in any requirement | Add requirement or confirm intentional addition |
| ...                         |                                  |                                                 |

---

### ⚠️ Uncertain / Needs Review

Items where the match between requirements and design is ambiguous and requires human judgment.

| Req ID | Requirement | Design Element | Reason for Uncertainty |
| ------ | ----------- | -------------- | ---------------------- |
| ...    |             |                |                        |

---

### Observations

Optional section for broader patterns, quality notes, or recommendations — use this when you notice systemic issues like: a whole functional area is undesigned, the design introduces a different navigation flow than described, or requirements lack enough detail to validate against any design.

---

## Output Principles

- **Be specific.** Reference requirement IDs and Figma layer names by name, not vaguely ("the button").
- **Don't fabricate.** If a requirement is vague, say so — don't invent an interpretation.
- **Coverage > perfection.** It's more useful to surface 10 genuine gaps than to force-fit everything into "conformant".
- **Prioritize actionability.** Every red and yellow item should have a concrete suggested action.
- **Stay in-scope.** Only analyze what's in the provided document and screen — do not infer requirements from other files unless the user explicitly includes them.
