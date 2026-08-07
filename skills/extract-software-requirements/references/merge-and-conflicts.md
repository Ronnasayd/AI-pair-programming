# Merge & Conflict Rules (Phase 4)

Read this file when starting Phase 4 (consolidation), after Phases 1-3.5 have each produced their own intermediate document.

## Precedence order when sources disagree silently

`commit history (B) > spec/PRD (C) > test files (D) > session transcripts (A)`

Rationale: commits are ground truth of the currently implemented state (code that actually merged). Specs/PRD express design intent but can go stale relative to what shipped. Test files describe intended behavior but may lag implementation or be incomplete. Transcripts are the noisiest, least-reviewed signal.

But **never resolve a disagreement by silently picking the higher-precedence source and discarding the other**. Every disagreement on a concrete fact (a number, a behavior, an endpoint, a threshold) goes in **2. Itens Abertos** as its own `OPEN-xx` row (see below), even if precedence tells you which one is _probably_ right. Precedence only decides which side gets the "likely correct" label in the `Decisão` column — it does not delete the item.

## Final document structure

Fixed template, in this exact order. Never substitute alternate section names (no generic "Conflicts"/"Action checklist" headers):

```markdown
# Requisitos Consolidados — <project-name>

Fontes: (A) transcrições de sessão Claude Code, (B) histórico de commits, (C) specs formais/PRD, (D) arquivos de teste (<list actual paths/sources found — omit letters for phases not run>).

Precedência em caso de conflito silencioso: **B (commits) > C (specs/PRD) > D (testes) > A (transcrições)**.

Última atualização: <YYYY-MM-DD> (cobre commits até `<short-sha>` e spec `<spec-name>`).

---

## Legenda de Domínio

| Código   | Domínio              |
| -------- | -------------------- |
| `<CODE>` | <domain description> |

---

## 1. Requisitos (RF + RNF)

| ID     | Domínio  | Requisito            | Fontes              | Status                   |
| ------ | -------- | -------------------- | ------------------- | ------------------------ |
| RF-xxx | `<CODE>` | one-line requirement | C (...) · B (`sha`) | ✅/🟡/❌ — evidence note |

---

## 2. Itens Abertos

| ID      | Domínio  | Descrição                     | Status           | Decisão                                |
| ------- | -------- | ----------------------------- | ---------------- | -------------------------------------- |
| OPEN-xx | `<CODE>` | what's unresolved/conflicting | Aberto/Resolvido | recommendation or resolution rationale |

---

## 3. Notas de Contexto

| Nota          | Domínio  | Descrição                                                               |
| ------------- | -------- | ----------------------------------------------------------------------- |
| <short title> | `<CODE>` | context that isn't a requirement or open item but matters for reviewers |

---

_IDs seguem faixas por criação; domínio é a chave de leitura, não o ID._
```

Section rules:

1. **Header block** — always present: Fontes line (list every source file/type actually used, don't include unused phases), Precedência line (fixed wording above), Última atualização line (real date + last commit sha + last spec name covered — not placeholder text).
2. **Legenda de Domínio** — derive domain codes from the clusters found during extraction (e.g. `AUTH`, `PWD`, `SETUP`) before writing requirements; every row's Domínio column must use a code defined here.
3. **1. Requisitos (RF + RNF)** — one row per requirement: `ID | Domínio | Requisito | Fontes | Status`. Genuine conflicts (see below) get their status cross-referenced to the matching `OPEN-xx` row instead of explained inline.
4. **2. Itens Abertos** — replaces the old standalone "Conflicts" section. Every genuine conflict (see below) AND every unresolved decision/gap becomes one `OPEN-xx` row. Status column is `Aberto` or `Resolvido` — if `Resolvido`, the Decisão column states the resolution and why (not just "done").
5. **3. Notas de Contexto** — non-requirement, non-conflict background a reviewer needs (e.g. migration side-effects, bootstrap mechanics) — never requirement rows or conflicts here.

## ID numbering scheme

- Prefix `RF-` for functional requirements, `RNF-` for non-functional/quality requirements, `OPEN-` for section 2 items.
- Group ranges by subsystem/domain (e.g. `RF-040`-`RF-049` for one screen/feature area) so future insertions don't force a renumber.
- If a source document already has its own formal IDs (`REQ-xxx`, `TASK-xxx`, `R-xx`), keep them visible inline in the Fontes column next to the new RF/RNF ID for traceability — never discard an existing ID scheme by replacing it outright.

## Status vocabulary — keep exactly these three

- ✅ **Implemented** — confirmed by at least one of: a commit that closes it, a spec marked done, explicit "resolved" language with no later contradiction.
- 🟡 **Partial / iterative** — actively being tuned (e.g. a performance parameter with several follow-up commits and no final value), or status depends on an open `OPEN-xx` item.
- ❌ **Open** — reported (bug or requested feature) with no implementation evidence found in any source.

Do not invent additional states — a requirement under active tuning is 🟡, not a fourth category.

**Test-file check (when a test suite exists in the repo):** before marking a requirement ✅, check whether a test file covers it (search by feature/module name under the repo's test dirs, e.g. `*.test.*`, `*.spec.*`, `test_*.py`, `__tests__/`). If a commit claims implementation but no matching test is found, downgrade to 🟡 and note "sem teste encontrado" in the Status evidence note — don't silently keep ✅ on commit claim alone. If the repo has no test suite at all, skip this check (don't penalize projects without tests). This check verifies/downgrades requirements already found by Phases 1-3 — it's distinct from Phase 3.5, which mines test descriptions for net-new requirements no other source surfaced.

## What counts as a genuine conflict (vs. just "old info")

A **conflict** is two sources making a factual claim about the _same_ subject that cannot both be true at once (a threshold of 3 vs 5 attempts; portrait vs landscape; endpoint X vs endpoint Y). A **stale/superseded fact** (e.g. an old PRD documents an endpoint that was later migrated, and the migration spec + commits agree) is not a live conflict — resolve it as ✅ in **1. Requisitos**, but still add an `OPEN-xx` row in **2. Itens Abertos** as a documentation-hygiene item so someone updates it, with `Status: Resolvido` and `Decisão` phrased as "documental, not functional" so the reader doesn't waste time debating an already-settled fact.

## Timestamp reconciliation

When a transcript (source A) reports a bug and a commit (source B) claims a fix, compare dates/times, not just which document you read first. Same-day timestamps are not proof of order — if you cannot establish which happened first from the data available, mark it as "incerto — requer validação manual", not as resolved either way.
