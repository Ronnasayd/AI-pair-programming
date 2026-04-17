---
name: srs-generator
description: Generates complete Software Requirements Specification (SRS) documents, following the standard template based on ISO/IEC/IEEE 29148:2018. Use this skill whenever the user asks to create, write, generate, or document an SRS, software requirements specification, requirements document, or mentions terms such as "SRS", "software specification", "functional and non-functional requirements", "requirements document", or requests to document a software system/product in a structured way. Also use it when the user provides information about a system and asks to structure it into formal documentation. The skill accepts text descriptions OR spec files, asks targeted clarifying questions to fill information gaps, extracts key requirements, and lets the user review a preview before saving the file with timestamp format at `docs/srs/yyyy-mm-dd-<short-description>.md`
---

# SRS Generator

Generates complete and well-structured SRS documents in Markdown, based on the ISO/IEC/IEEE 29148:2018 standard.

## Workflow

1. **Collect information** — If the user does not provide enough details, ask key questions before generating (see elicitation section below).
2. **Generate the document** — Fill in the Markdown template with the collected information. Use descriptive placeholders for fields the user did not provide.
3. **Present and offer adjustments** — Display the generated document and ask if there are sections to refine.

## Information Elicitation

If the user provides only the system name/general description, ask at minimum:

- **Main objective** of the system
- **Target users** (who will use it)
- **Main functionalities** (3–5 core functions)
- **Relevant technical constraints** (language, database, platform)

Do not block generation waiting for complete answers — generate with what is available and mark gaps with `> ⚠️ To be defined: [description of what is missing]`.

## Markdown Template

Generate the document following **exactly** this structure:

```markdown
# SRS — {Software Title}

**Document ID:** {document_id}
**Version:** {version}
**Status:** {status}
**Date:** {date}
**Authors:** {authors}

---

## Revision History

| Version   | Date   | Changes   |
| --------- | ------ | --------- |
| {version} | {date} | {changes} |

---

## 1. Introduction

### 1.1 Purpose

{purpose}

### 1.2 Scope

{scope}

### 1.3 Definitions, Acronyms, and Abbreviations

| Term   | Description   |
| ------ | ------------- |
| {term} | {description} |

### 1.4 References

{list of references}

### 1.5 Document Overview

{overview}

---

## 2. Overall Description

### 2.1 Product Perspective

{product_perspective}

### 2.2 Product Functions

{list of functions}

### 2.3 User Characteristics

| User Type | Skills/Profile |
| --------- | -------------- |
| {type}    | {skills}       |

### 2.4 Constraints

{list of constraints}

### 2.5 Assumptions and Dependencies

{list of assumptions}

### 2.6 Apportioning of Requirements

{apportioning}

---

## 3. Specific Requirements

### 3.1 External Interfaces

#### {id} — {type}

**Description:** {description}

### 3.2 Functional Requirements

#### {id} — {description}

- **Priority:** {priority}
- **Dependencies:** {dependencies}

### 3.3 Usability Requirements

#### {id}

{description}

### 3.4 Performance Requirements

#### {id}

{description}

### 3.5 Database Requirements

#### {id}

{description}

### 3.6 Design Constraints

{list of constraints}

### 3.7 Standards Compliance

{list of standards}

### 3.8 System Attributes

| Attribute       | Specification     |
| --------------- | ----------------- |
| Reliability     | {reliability}     |
| Security        | {security}        |
| Maintainability | {maintainability} |
| Portability     | {portability}     |

### 3.9 Verification

{list of verification criteria}

### 3.10 Supporting Information

{list of supporting artifacts}

---

## 4. Appendices

### 4.1 Traceability Matrix

| User Story | Related Requirements   |
| ---------- | ---------------------- |
| {US_ID}    | {list of requirements} |

### 4.2 Glossary

| Term   | Definition   |
| ------ | ------------ |
| {term} | {definition} |

### 4.3 Pending Items and Ambiguities

{list of open items}

### 4.4 Additional References

{list of references}
```

## Generation Rules

- **Requirement IDs**: Use standard prefixes — `FR-XXX` (functional), `NFR-XXX` (non-functional), `UR-XXX` (usability), `PR-XXX` (performance), `DBR-XXX` (database), `INT-XX` (interface).
- **Priority**: Use `High`, `Medium`, or `Low`.
- **Gaps**: Mark with `> ⚠️ To be defined: [what is missing]` in _italics_ — never invent critical technical information.
- **Language**: Write in formal English, active voice, using "The system shall..." for functional requirements.
- **Minimum completeness**: Always generate at least 3 functional requirements, 1 usability, 1 performance, and fill in system attributes.
- **Standard references**: Always include `ISO/IEC/IEEE 29148:2018` in references.

## Example of a Well-Written Functional Requirement

```markdown
#### FR-001 — User Authentication

The system shall allow users to authenticate using email and password, with support for JWT-based authentication.

- **Priority:** High
- **Dependencies:** FR-002 (User Registration)
```

## After Generating

1. Suggest reviewing items marked as `⚠️ To be defined`.
2. Ask if the user wants to review the generated SRS before saving.
3. Save the file in `docs/srs/` with the format `yyyy-mm-dd-<short-description>.md`.
