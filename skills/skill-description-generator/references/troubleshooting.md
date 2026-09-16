# Troubleshooting

## Error: Description over 1024 characters

Cause: Too many phrases, too much explanation in opening
Solution: Trim opening to essentials. Remove redundant phrases.

## Error: User says trigger phrase but skill doesn't activate

Cause: Phrase too vague or contradicts another loaded skill
Solution: Make phrase more specific (not "generate docs" but "generate PRD"). Check overlap — if two skills have same trigger, agent may pick wrong one.

## Error: skill activates on unrelated prompts (false positive)

Cause: Description text — including any "Do NOT use for X" clause — feeds the same embedding/BM25 matcher as the positive triggers. Matchers don't parse negation, so naming X in a negative clause can itself boost activation on X.
Solution: Don't add "Do NOT use for" clauses to the description. Keep the description purely positive and concrete; put scope exclusions in the skill body (SKILL.md instructions), which loads after activation, not before.

## Error: No XML brackets but description still invalid

Cause: YAML parser sees special characters as syntax
Solution: Escape if needed. Test description in actual frontmatter before delivery.
