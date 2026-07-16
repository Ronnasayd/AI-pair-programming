---
name: skill-description-generator
description: Generate skill description fields that trigger correctly with specific phrases and clear negatives. Use when creating new skills and need description copy following trigger rules. Do NOT use for entire SKILL.md files, architecture docs, or non-description content.
metadata:
  author: Ronnasayd Machado - github.com/Ronnasayd
  version: "1.1.0"
---

# Skill Description Generator

Create skill description fields that trigger on exact user phrases and avoid overlap with other skills.

## Steps

| #   | Step                 | Action                                                                                                                               | Output / Gate                            |
| --- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------- |
| 1   | Gather details       | Collect: (1) one-sentence purpose, (2) 2-3 concrete use cases w/ phrases, (3) negative triggers, (4) related/overlapping skill names | structured input ready for generation    |
| 2   | Generate description | Apply pattern `[What] + [When with phrases] + [When NOT]`, enforcing rules below                                                     | one complete description line            |
| 3   | Validate             | Check validation list below; regenerate if any fail                                                                                  | valid description, ready for frontmatter |

## Generation rules (Step 2)

| Rule            | Requirement                                                                               |
| --------------- | ----------------------------------------------------------------------------------------- |
| Length          | Under 1024 characters — count strictly                                                    |
| Brackets        | No `< >` (XML) allowed                                                                    |
| Line breaks     | Single line — no YAML multiline `>` or `\|`                                               |
| Trigger phrases | Real words user would say; English + Portuguese if relevant, comma-separated per language |
| Negatives       | Name actual overlapping skills, not "any other"                                           |
| File types      | Mention if relevant (.md, .json, etc.)                                                    |
| Tone            | "Use for X" not "Can be used for"                                                         |

## Validation checklist (Step 3)

- [ ] Starts with action verb (Convert, Generate, Create, etc.)
- [ ] 3+ trigger phrases (mix languages if relevant)
- [ ] "Do NOT use for..." names specific skills, not vague
- [ ] No `< >` brackets
- [ ] Under 1024 chars
- [ ] Single line

## Reference files

- [references/examples.md](references/examples.md) — two worked examples (input → generated description)
- [references/troubleshooting.md](references/troubleshooting.md) — common failure causes + fixes
