**OPERATE IN SELF-CONSISTENCY MODE.**

**OBJECTIVE:** Generate **epics, stories, and tasks** from requirements by using multiple reasoning paths and consolidating the best one.

---

## PROCESS:

### 1. Base Extraction:

- Generate a list of requirements (**R-IDs**), including **type, source, actor, and dependencies**.

### 2. Generate 3 Independent Paths (Track A, Track B, Track C):

- Each track must propose: **grouping → epics → stories → tasks (high level) → preliminary prioritization**.
- Each track adopts a different primary organization criterion:

  - **Track A:** user-journey–centric.
  - **Track B:** technical bounded-context–centric.
  - **Track C:** incremental business-value–centric.

### 3. Evaluate Tracks:

- Criteria: **coverage, cohesion, granularity, independence, clarity of value, risk**.
- Assign a **score (0–5)** for each criterion.

### 4. Choose Base Track (or merge elements). Justify the choice.

### 5. Refine the Chosen Track:

- Adjust epics to be **SMART**.
- Ensure stories follow **INVEST**.
- Expand tasks with **Definition of Done (DoD)**.

### 6. Build the Final Traceability Matrix.

### 7. Validate Coverage and List Gaps.

### 8. Prioritize:

- Explain the **method and parameters** used.

### 9. Produce Final Recommendations.

---

## OUTPUT (MARKDOWN):

```
{{ TEMPLATE TO BE PROVIDED }}
```

---

## STANDARDS:

- Concrete acceptance criteria (**Given / When / Then**).
- Estimates: **Story points (Fibonacci)**; **tasks in hours**.
- Clear technical categories.

---

### BEFORE EXECUTION:

If critical data is missing (e.g., personas do not exist), **request clarification**; if proceeding anyway, **declare assumptions**.

---

### INSERT DATA BELOW:

```
[DOCUMENTS / CONTEXT]
```
