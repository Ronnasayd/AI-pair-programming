**OPERATE IN TREE OF THOUGHTS MODE.**

**OBJECTIVE:** Based on the provided documents (SRS / PRD / others), generate **Epics, Stories, and Tasks** that are fully traceable, following the phases: **Analysis → Grouping → Decomposition → Detailing → Validation → Organization**.

---

## REASONING INSTRUCTIONS (TREES):

1. Extract **ALL requirements**: assign IDs (R-001…), classify them (functional / non-functional), identify **actors, use cases, and dependencies**.
2. Generate at least **3 alternative groupings** into domains / bounded contexts (**Tree A, B, C**). List **pros and cons** of each.
3. For each grouping, propose **2–3 epic options per cluster**. Use the format:
   **“As an <organization>, we want <capability> so that <objective>.”**
4. Select the **optimal combination of epics** (criteria: coverage, value, cohesion, independence, risk reduction). **Justify exclusions**.
5. For each epic, generate **INVEST-compliant stories**. Where ambiguity exists, generate **variants** and choose the best one (briefly explain).
6. For each story, generate **Given / When / Then** acceptance criteria (minimum **3**) and estimate **story points** (assume Fibonacci).
7. Decompose stories into **atomic technical tasks** (categories: frontend, backend, database, tests, DevOps, security). Define a **Definition of Done (DoD)** for each task.
8. Build the **traceability matrix**:
   **Requirement → Epic → Stories → Tasks**
9. Perform **coverage verification** (percentage), identify **gaps, conflicts, cross-dependencies, and risks** (classify as high / medium / low).
10. **Prioritize epics** (using the provided methodology or, if absent, propose and apply one). Consider **value vs effort vs risk vs dependencies**.
11. Propose an **initial release / sprint plan** (logical ordering).
12. List **recommendations and points to validate with stakeholders**.

---

## STANDARDS:

- **Epics:** SMART + business value + relative effort (T-shirt sizing).
- **Stories:** INVEST + clear persona + explicit benefit.
- **Tasks:** clear, estimable (**< 16h**), with objective DoD.
- **Acceptance criteria:** objective, testable, covering main paths and error cases.

---

## OUTPUT (MARKDOWN):

```
{{ TEMPLATE TO BE PROVIDED }}
```

---

## IF INFORMATION IS MISSING:

Before starting, clearly list **clarification questions**, grouped by category:

- Domain
- Users
- Business Rules
- Technical Constraints
- Security
- Performance

---

## DATA START:

```
[INSERT DOCUMENTS AND CONTEXT HERE]
```
