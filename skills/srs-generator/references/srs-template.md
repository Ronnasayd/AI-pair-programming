# SRS Markdown Template

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
- **Verification Method:** {verification_method}

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

Each requirement above is tagged with one of four verification methods per ISO/IEC/IEEE 29148:

| Method        | When to use                                                      |
| ------------- | ---------------------------------------------------------------- |
| Inspection    | Static check (visual/document review), cheap, no execution       |
| Analysis      | Simulation/calculation when Test is infeasible or unaffordable   |
| Demonstration | Practical run showing behavior qualitatively, no instrumentation |
| Test          | Formal execution with instrumentation, measurable pass/fail      |

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

## Example of a Well-Written Functional Requirement

```markdown
#### FR-001 — User Authentication

The system shall allow users to authenticate using email and password, with support for JWT-based authentication.

- **Priority:** High
- **Dependencies:** FR-002 (User Registration)
- **Verification Method:** Test
```
