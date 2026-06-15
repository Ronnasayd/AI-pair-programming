---
name: skill-description-generator
description: Generate skill description fields that trigger correctly with specific phrases and clear negatives. Use when creating new skills and need description copy following trigger rules. Do NOT use for entire SKILL.md files, architecture docs, or non-description content.
license: CC-BY-4.0
metadata:
  author: Ronnasayd
  version: 1.0.0
---

# Skill Description Generator

Create skill description fields that trigger on exact user phrases and avoid overlap with other skills.

## Instructions

### Step 1: Gather Skill Details

Collect from user:

1. **What the skill does** — one-sentence purpose
2. **Use cases** — 2-3 concrete scenarios (e.g., "user says 'convert X to Y'")
3. **Negative triggers** — what it should NOT do (e.g., "don't use for creating specs")
4. **Related skills** — other skills it might overlap with (names matter)

Expected output: Structured input ready for generation.

### Step 2: Generate Description

Apply pattern: `[What] + [When with phrases] + [When NOT]`

Rules to enforce:

- **Under 1024 characters** — count strictly
- **No XML brackets** — no `< >` allowed
- **Single line** — no line breaks in YAML
- **Trigger phrases** — include real words user would say (English + Portuguese if relevant)
- **Multiple languages** — one trigger per language, separated by comma
- **Specific negatives** — name actual overlaps, not "any other"
- **File types** — mention if relevant (.md, .json, etc.)
- **Pushy tone** — "Use for X" not "Can be used for"

Expected output: One complete description line.

### Step 3: Validate

Check:

- [ ] Starts with action verb (Convert, Generate, Create, etc.)
- [ ] Includes 3+ trigger phrases (mix languages if relevant)
- [ ] "Do NOT use for..." section specific (names skills, not vague)
- [ ] No `< >` brackets
- [ ] Under 1024 chars
- [ ] Single line (no YAML multiline `>` or `|`)

If any fail, regenerate.

Expected output: Valid description field, ready for frontmatter.

## Examples

### Example 1: Convert JSON

User input:

- Purpose: Convert tasks.md to TaskMaster JSON
- Cases: User wants to transform task specs, generate JSON from markdown
- Negatives: Don't use for creating task specs, executing tasks
- Related: create-task-spec, execute-task

Generated:

```
Convert tasks.md spec files into TaskMaster JSON format (.taskmaster/tasks/tasks.json for task list, .taskmaster/execution/metadata.json for strategy). Use when user says "convert tasks.md to taskmaster json", "transform tasks.md to .taskmaster format", "converta tasks.md em tasks.json", or wants to generate TaskMaster JSON from a tasks file. Do NOT use for creating task specs, executing tasks, or non-TaskMaster conversions.
```

### Example 2: Document Generation

User input:

- Purpose: Generate PRDs using 5-battery framework
- Cases: User needs product spec, wants structured requirements
- Negatives: Not for architecture, not for technical specs
- Related: architecture-designer, technical-spec-writer

Generated:

```
Create product requirement documents using 5-battery framework with structured outputs. Use when user says "create PRD", "write product spec", "generate requirements", "build feature outline", or "crea PRD". Do NOT use for architecture decisions, technical specifications, or system design.
```

## Troubleshooting

### Error: Description over 1024 characters

Cause: Too many phrases, too much explanation in opening
Solution: Trim opening to essentials. Remove redundant phrases. Keep negatives concise.

### Error: User says trigger phrase but skill doesn't activate

Cause: Phrase too vague or contradicts another loaded skill
Solution: Make phrase more specific (not "generate docs" but "generate PRD"). Check overlap — if two skills have same trigger, agent may pick wrong one. Refine negatives to be more specific about what NOT to do.

### Error: No XML brackets but description still invalid

Cause: YAML parser sees special characters as syntax
Solution: Escape if needed. Test description in actual frontmatter before delivery.
