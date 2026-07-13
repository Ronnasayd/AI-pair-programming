# Merge & Conflict Rules (Phase 4)

Read this file when starting Phase 4 (consolidation), after Phases 1-3 have each produced their own intermediate document.

## Precedence order when sources disagree silently

`commit history (B) > spec/PRD (C) > session transcripts (A)`

Rationale: commits are ground truth of the currently implemented state (code that actually merged). Specs/PRD express design intent but can go stale relative to what shipped. Transcripts are the noisiest, least-reviewed signal.

But **never resolve a disagreement by silently picking the higher-precedence source and discarding the other**. Every disagreement on a concrete fact (a number, a behavior, an endpoint, a threshold) goes in the Conflicts section (see below), even if precedence tells you which one is _probably_ right. Precedence only decides which side gets the "likely correct" label in the conflict entry — it does not delete the conflict.

## Final document structure

Use exactly two top-level content sections plus a checklist, never mix requirement rows with conflict prose in the same table:

1. **Requirements (RF-xxx / RNF-xxx)** — grouped into short domain subsections (5-15 rows per table). Each row: `ID | one-line requirement | source tags (A/B/C) | status (✅ done / 🟡 partial-iterative / ❌ open)`. An ID whose status depends on an unresolved conflict gets 🟡 or ❌ and a cross-reference to the conflict entry, e.g. "ver conflito §3.2" — do not explain the conflict inline in this table.
2. **Conflicts** — one self-contained entry per disagreement: name it, quote what each disagreeing source actually claims, state what decision/verification is still needed. Cross-reference back to the RF/RNF ID(s) it affects.
3. **Action checklist** — one checkbox per conflict entry that implies a concrete next step. This section is a mechanical derivation of section 2; never add an item here that doesn't trace back to a conflict entry, and never let the two drift out of sync when either is edited later.

## ID numbering scheme

- Prefix `RF-` for functional requirements, `RNF-` for non-functional/quality requirements.
- Group ranges by subsystem/domain (e.g. `RF-040`-`RF-049` for one screen/feature area) so future insertions don't force a renumber.
- If a source document already has its own formal IDs (`REQ-xxx`, `TASK-xxx`, `R-xx`), keep them visible inline next to the new RF/RNF ID for traceability — never discard an existing ID scheme by replacing it outright.

## Status vocabulary — keep exactly these three

- ✅ **Implemented** — confirmed by at least one of: a commit that closes it, a spec marked done, explicit "resolved" language with no later contradiction.
- 🟡 **Partial / iterative** — actively being tuned (e.g. a performance parameter with several follow-up commits and no final value), or status depends on an open conflict.
- ❌ **Open** — reported (bug or requested feature) with no implementation evidence found in any source.

Do not invent additional states — a requirement under active tuning is 🟡, not a fourth category.

## What counts as a genuine conflict (vs. just "old info")

A **conflict** is two sources making a factual claim about the _same_ subject that cannot both be true at once (a threshold of 3 vs 5 attempts; portrait vs landscape; endpoint X vs endpoint Y). A **stale/superseded fact** (e.g. an old PRD documents an endpoint that was later migrated, and the migration spec + commits agree) is not a live conflict — resolve it as ✅ in the requirements table, but still note the stale document in the conflicts section as a documentation-hygiene item so someone updates it. Both belong in section 2, but phrase the second kind as "documental, not functional" so the reader doesn't waste time debating already-settled facts.

## Timestamp reconciliation

When a transcript (source A) reports a bug and a commit (source B) claims a fix, compare dates/times, not just which document you read first. Same-day timestamps are not proof of order — if you cannot establish which happened first from the data available, mark it as "incerto — requer validação manual", not as resolved either way.
