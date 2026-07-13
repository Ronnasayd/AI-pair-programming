---
name: extract-software-requirements
description: Extracts and consolidates software requirements from a project's Claude Code session transcripts, git commit history, and formal spec/PRD markdown files into a single traceable RF-xxx/RNF-xxx requirements document with an explicit unresolved-conflicts section. Use when the user asks to "extract requirements from this project", "generate a requirements doc from commits", "extract requirements from transcripts", "consolidate PRD and specs into one doc", "what requirements were implemented vs still pending", or wants a cross-source requirements audit with traceability between conversations, code history, and formal specs. Do NOT use for writing a brand-new PRD from scratch with no existing project history (use prd-generator instead), or for pure implicit-requirement gap analysis on a single already-written PRD (use prd-get-implicit-requirements instead).
license: CC-BY-4.0
metadata:
  author: Ronnasayd
  version: 1.0.0
---

# Extract Software Requirements

Mines and consolidates software requirements from three independent, differently-shaped sources in a project: unstructured session transcripts, structured commit history, and formal spec documents. Produces one final RF-xxx/RNF-xxx requirements document with a dedicated section for conflicts found between sources.

Each of the 4 phases below is independent — run only the phase(s) the user asks for. If the user asks for "requirements from commits", do only Phase 2 and stop; don't force Phase 4 merge with sources that don't exist yet.

## Instructions

### Step 1: Extract from session transcripts (if requested)

Session transcripts live at `~/.claude/projects/<url-encoded-cwd>/*.jsonl`, one file per session UUID.

1. Read one raw line where `type == "user"` from any `.jsonl` in the target project directory and inspect `message.content` and the `promptSource` field. **Do this every time before running the script** — schema can differ across Claude Code versions, and tool-result/system content is also stored under `role: "user"`, so you cannot assume `promptSource == "typed"` still isolates real human input without checking first.
2. Run `scripts/extract_user_prompts.py` against all session files for the project:
   ```
   python3 scripts/extract_user_prompts.py "$HOME/.claude/projects/<project-dir>/*.jsonl" --out /tmp/user_prompts_only.txt
   ```
3. Read the output file in full (paginate with offset/limit if it exceeds a single read) — do not sample. Classify each line into: noise (pasted stack traces/logs used only as bug context), process/meta talk ("proceed", "yes", skill usage questions), or real requirements signal (feature requests, bug reports with expected-vs-actual behavior, explicit scope decisions).
4. Cluster the signal into a domain taxonomy as it emerges (e.g. core scope, external API integration, persistence, UX/screens, non-functional/quality, observability). Assign `RF-`/`RNF-` IDs per Step 4's numbering scheme even if Phase 4 won't run yet — this keeps output format consistent.
5. Close with an explicit "still pending / open" subsection — cross-reference the most recent timestamps and any user follow-up language ("continua aparecendo", "isso não deve acontecer", "ainda não") to flag items as unresolved rather than done.

Expected output: a Markdown file with source-tagged, ID-prefixed requirements plus an open-items list.

### Step 2: Extract from git commit history (if requested)

1. Dump the full log, bypassing any shell hook or token-saving proxy that might silently truncate `git` output:
   ```
   bash scripts/dump_git_log.sh /tmp/commits_full.txt <repo-path>
   ```
   The script self-verifies commit count vs `===END===` marker count and prints a warning if they disagree — **do not proceed past a warning without investigating** (see Troubleshooting).
2. Read the dump in full, chronologically (it's already `--reverse`, oldest first — this reads as a narrative: foundation → features → fixes → polish).
3. Treat these commit-body patterns as high-confidence signal: explicit IDs (`REQ-xxx`, `TASK-xxx`), "Implements requirements: ..." lines, "Gate:"/"Test gate:" lines (these are acceptance criteria), and `fix:` commits (root cause + resolution = an implicit, previously-undocumented requirement — rephrase as "system must X because Y failed when Z", not as a changelog line).
4. Cluster into the same domain taxonomy as Step 1, assign new `RF-`/`RNF-` IDs, but **keep any original `REQ-xxx`/`TASK-xxx` cited in the commit body inline** for traceability back to the source spec — never discard it.
5. Close with an open-items checklist: recurring bug themes touched by multiple fix commits, or the most recent commit on a topic being explicitly a tuning step ("increase concurrency") rather than a closure, both belong here.

Expected output: same Markdown format as Step 1, with `feat:` commits mapped to RF and lint/type/perf/test commits mapped to RNF.

### Step 3: Extract from formal spec/PRD files (if requested)

1. Locate candidate files: `find <repo-root> -iname "*.md"`, then explicitly exclude build/tooling copies (`node_modules`, mutation-test sandboxes like `.stryker-tmp/`, `.stryker/`, any path that duplicates a `.specs/` tree inside a temp build dir). Match every found file back to its real path under version control before trusting it as source.
2. Don't filter to only the exact filename pattern the user named (e.g. `*spec.md`) — also note sibling `PRD.md`, `design.md`, `tasks.md`, and casing variants (`Specs.md`, `Design.md`) in the same directories, since a spec can use a different filename convention than expected.
3. Read every candidate document in full — these are usually short; skipping sections risks missing an "Out of Scope" list or an appendix that reverses an earlier requirement.
4. Establish precedence when multiple documents overlap: check explicit dates, `status:` frontmatter (`Approved` vs `ready` vs draft), and cross-references in the text itself (a later spec stating "corrects REQ-007.9" clearly supersedes the earlier one). A kickoff-era PRD is commonly stale relative to a feature spec written after implementation began — don't treat all documents as equally authoritative by default.
5. Preserve existing requirement IDs verbatim (`REQ-xxx`, `R-xx`, `TVUI-xx`) — never invent parallel numbering when the source already has one.
6. Group the consolidated output by source document/section, not by a reinvented taxonomy — formal specs already have structure; preserve it so the result is a faithful superset, not a lossy reinterpretation.
7. Cross-check every requirement against: other requirements in the same doc, requirements in other specs on the same subsystem, and any implementation facts already known from a prior Step 1/2 pass in the same session. Flag every disagreement explicitly rather than silently picking a side.

Expected output: same Markdown format, plus a "Conflicts / points of attention" closing section listing every contradiction found, which source is likely authoritative, and what it implies (a doc to update, or code that drifted from spec).

### Step 4: Consolidate all available phase outputs into the final document

Only run this step once at least two of Steps 1-3 have produced output (a merge of one source is meaningless).

1. Read `references/merge-and-conflicts.md` now — it defines the precedence rule, the exact final document structure (Requirements / Conflicts / Action checklist as three separate sections, never interleaved), the ID numbering scheme, the fixed 3-symbol status vocabulary (✅/🟡/❌), and how to distinguish a genuine conflict from a merely-stale document.
2. Walk every requirement gathered across the available phase outputs and classify each as: a requirement row with a status, or a conflict entry. Anything that was an inline "⚠️ note" in an intermediate doc becomes one or the other — never both, never left inline in the final requirements table.
3. Build the Requirements section as short domain-scoped tables (5-15 rows each) — long single tables are the #1 readability failure mode for this deliverable.
4. Build the Conflicts section as self-contained entries, each cross-referencing the RF/RNF ID(s) it affects.
5. Build the Action checklist as a mechanical 1:1 derivation of the Conflicts section — every checklist line must trace back to exactly one conflict entry; never add items here that aren't in section 2.

Expected output: one final Markdown file, structurally: `## 1. Requisitos Funcionais (RF)` (subsections) → `## 2. Requisitos Não-Funcionais (RNF)` (subsections) → `## 3. Conflitos e Itens Não Resolvidos` → `## 4. Checklist de ações pendentes`.

## Delivery (all steps)

Write each phase's output to a scratch file and send it directly as a file — do not paste full documents into chat. Keep the chat reply to 1-2 sentences: what was produced, how many items/conflicts found, and any caveat hit along the way (e.g. truncation detected and bypassed). When iterating on an already-delivered document (e.g. "restructure this", "add X"), overwrite the same file path and resend — don't create a differently-named file for a refinement of the same deliverable.

## Examples

### Example 1: Single-source request
User says: "extrai requisitos com base nos commits"
Actions: Step 2 only — dump log, read in full, cluster, write file, send it.
Result: one Markdown file with RF/RNF tables sourced only from commits; no merge step, no Conflicts section beyond what's derivable from commits alone.

### Example 2: Full audit request
User says: "quero um documento final de requisitos cruzando specs, commits e transcrições, com conflitos"
Actions: Steps 1 → 2 → 3 → 4, in order, each producing its own file, then Step 4 consolidates all three into the final structured doc per `references/merge-and-conflicts.md`.
Result: 4 files delivered (3 intermediate + 1 final), final one has all 4 sections described in Step 4.

### Example 3: Restructure an already-delivered doc
User says: "esse documento está confuso, separa requisitos de conflitos com prefixos RF/RNF"
Actions: Re-read `references/merge-and-conflicts.md` structure rules, re-partition the existing content (don't re-run extraction), overwrite the same file, resend.
Result: same file path, new structure, no new source data pulled.

## Troubleshooting

### Commit/line counts disagree after `dump_git_log.sh`
Cause: a shell hook or CLI proxy (token-saving wrappers are common) rewrote `git` transparently and truncated output before it reached the redirect. The script already invokes `/usr/bin/git` directly to bypass this, but double-check no other wrapper sits even closer to the binary (`type git`, `alias git`) if the warning persists.

### `promptSource` field absent or all values differ from `"typed"`
Cause: transcript schema changed. Read 3-4 raw `type == "user"` lines across different timestamps and find whichever field currently discriminates real typed input from injected tool-result/system-reminder content, then adjust the filter in `extract_user_prompts.py` accordingly before running it at scale.

### Same requirement appears with contradicting facts and no timestamp lets you order them
Do not guess an order. Mark it "incerto — requer validação manual" in the Conflicts section per `references/merge-and-conflicts.md`, not as resolved either way.
