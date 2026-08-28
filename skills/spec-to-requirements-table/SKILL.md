---
name: spec-to-requirements-table
description: Derive a flat, self-contained requirements review table from a feature's spec.md, design.md and tasks.md — one row per acceptance criterion, tagged success or error path — so a non-implementer can scan it and judge whether each rule makes sense. Use when the user says "the spec is too technical", "quero uma tabela de requisitos", "make a requirements table", "review sheet for these requirements", "listar os requisitos para revisar", or supplies a table template and asks to fill it from an existing spec. Do NOT use for authoring the spec, design or tasks themselves, for generating test code, or for implementation planning.
---

# Spec → Requirements Review Table

Derive a reviewer-facing table from the implementer-facing spec set. Reviewer asks
"does this rule make sense?", not "is this implementable?". Every row judgeable
alone, no lookup.

## The one rule that matters

**Express conditions as properties, never as concrete identifiers.** A row naming
a specific id, name or sample value forces a lookup and stops being self-contained.

```
Wrong: Then only records with status = "active" are loaded And record 4071 is not loaded
Right: Then only records with status = "active" are loaded And records with status != "active" are not loaded

Wrong: When "ACME Holdings Ltd." is submitted Then the result is 4071
Right: When a value differs from the stored one only in letter casing Then it matches that stored record
```

Test: assume the reviewer has never seen example data. Every row still reads → rule holds.

## Sources

Read all three in full before writing a row. Partial reading yields rows that
restate criteria without rationale — a reformatted spec, not a review sheet.

| Document    | Read it for                                                                         | Lands in                                        |
| ----------- | ----------------------------------------------------------------------------------- | ----------------------------------------------- |
| `spec.md`   | acceptance criteria, edge cases, decision table, open notes, out-of-scope table     | Scenario + Expression; Complement; Consequences |
| `design.md` | rationale, mechanism, architecture decisions, risk table, trade-offs                | Complement; Consequences                        |
| `tasks.md`  | "done when" checklists (behaviors no criterion states); phase order → section order | extra rows; grouping                            |

`bdd.md` / Gherkin is a **supplement** — confirm nothing missed, check phrasing.
Never the primary input: it carries the register this artifact replaces.

Project names files differently → map by role: criteria = spec, rationale =
design, work breakdown = tasks.

## Procedure

| #   | Step                    | Action                                                                                                                   | Gate                                                                    |
| --- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------- |
| 1   | Read sources            | All three end to end; extract behaviors, rationale, consequences separately                                              | rationale + consequences captured, not just criteria                    |
| 2   | Settle format decisions | **Ask, don't assume**: language (spec's ≠ user's often), id scheme                                                       | both global; retrofitting = full rewrite                                |
| 3   | Enumerate               | One row per criterion; sweep `tasks.md` for uncovered "done when" items                                                  | six cases existing for six reasons = six rows, never merged             |
| 4   | Group                   | Sections follow system execution order, not story order                                                                  | each section readable given only sections above it                      |
| 5   | Write rows              | Per rules below                                                                                                          | every row self-contained                                                |
| 6   | Consequences section    | Numbered prose entries, each naming the rows producing it                                                                | every uncomfortable trade-off named explicitly, not implied across rows |
| 7   | Format + verify         | Run project markdown formatter if present (wide tables realign — expected, don't revert); then verification checks below | all checks pass                                                         |
| 8   | Report entry point      | Name rows most likely wrong or most expensive if wrong                                                                   | reviewer has a starting place                                           |

**Id scheme (step 2)**: prefer sequential (`FR-001`, `FR-002`, …). Spec ids repeat
across many rows and defeat "one row, one decision".

**Row rules (step 5)**:

| Rule                                       | Why                                                                               |
| ------------------------------------------ | --------------------------------------------------------------------------------- |
| State both sides of an exclusion (**And**) | Positive-only leaves the reviewer inferring the negative                          |
| Rationale explains, doesn't cite           | `REQ-03 / AC-1.3` is unevaluable; "a stray space must not create a new record" is |
| Translate out of EARS register             | "The system SHALL…" is written for implementers                                   |
| Tag SP / EP                                | Reviewer skims for failure modes — where contentious decisions sit                |

**Consequences (step 6)** — behaviors correct per-row but costly in combination.
Usually the highest-value part: the only place the design's cost is stated plainly.
Typical members: validation rules rendering existing records uneditable; data absent
until an out-of-band migration; deliberate divergence between two stored
representations of one fact; fail-closed availability/correctness trades; breaking
contract changes needing coordinated deploy; policies deferred to a later decision.

**Verification (step 7)** — by test, not inspection:

- Reviewer has seen no example data. Does every row still read?
- Three random rows — judgeable without scrolling elsewhere?
- Every `spec.md` criterion maps to ≥1 row?
- Consequences names every trade-off, or does one appear only implicitly?

## Output shape

Write to the feature's own directory, beside its sources — typically
`requirements.md` next to `spec.md`.

```
Header: links to spec.md / design.md / tasks.md, status, date, one-line reading guide
Section 1..N: one table per behavioral area, columns per the user's template
Consequences: numbered prose entries, each naming the rows that cause it
Glossary: expansion of every abbreviation used
```

Default columns when no template supplied:

| Requiriment | Scenario | Expression | Complement | Path |
| ----------- | -------- | ---------- | ---------- | ---- |

- `Expression` — condition + outcome, keywords bolded (`**Given** … **When** … **Then** … **And** …`), stated as properties
- `Complement` — why the rule exists, plain words
- `Path` — `SP` success / `EP` error

Glossary: `FR` functional requirement, `NR` non-functional requirement, `SP`
success path, `EP` error path.

## Anti-patterns

| Anti-pattern                                    | Why it fails                                           |
| ----------------------------------------------- | ------------------------------------------------------ |
| Concrete ids or sample values in the Expression | Forces a lookup; row stops being self-contained        |
| Citing spec requirement codes as the rationale  | Cites instead of explains; a code is unevaluable       |
| Deriving rows from a bdd.md instead of the spec | Inherits the technical register the table must replace |
| Copying EARS phrasing verbatim from the spec    | Same: written for implementers, not reviewers          |
| Merging several distinct cases into one row     | Hides distinct decisions behind one line               |
| Reading only the spec and skipping the design   | Yields behaviors with no rationale — nothing to review |
| Omitting the consequences section               | The costliest information is the least visible per-row |
| Choosing language or id scheme mid-writing      | Both global; retrofitting costs a full rewrite         |
