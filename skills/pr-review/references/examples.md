# Examples

### Example 1: PR with undefined variable

User says: "review this PR https://github.com/org/repo/pull/42"

1. `get` + `get_files` in parallel
2. `get_diff` for line numbers
3. Find in diff: variable used in loop body but never initialized before loop
4. Classify: 🔴 — produces wrong output silently
5. WebSearch: `[language] undefined variable runtime behavior`
6. Write fix: add `variable = initial_value` before the loop
7. Deliver report with finding, fix, and reference link

Result: structured report, fix example with exact line, merge blocked until fixed.

---

### Example 2: Architecture violation — wrong layer

User says: "analyze PR #98 in LINGOPASS/lingo_digitalpass"

1. Collect metadata + files in parallel
2. Full diff
3. Classify files: find Job file that instantiates a Controller internally
4. 🔴 — Controller has HTTP request dependencies; running it in a queue worker context fails
5. WebSearch: `[framework] job instantiate controller antipattern`
6. Fix: extract logic to Service class, inject Service into Job's handle method
7. Reference official queue docs + community article

Result: report blocks merge, shows before/after refactor, links docs.

---

### Example 3: Minor — doc/code mismatch

User says: "check PR #15"

1-3. Standard collect + diff 4. Find: comment says "runs at 23:00", scheduler sets "22:00" 5. Classify: 🟡 — no runtime impact, operational risk during incidents 6. No WebSearch needed for this finding 7. Fix: align comment with actual scheduled time

Result: finding in minor table, one-line fix, no merge block.
