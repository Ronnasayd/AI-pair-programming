# Troubleshooting

## Error: Description over 1024 characters

Cause: Too many phrases, too much explanation in opening
Solution: Trim opening to essentials. Remove redundant phrases. Keep negatives concise.

## Error: User says trigger phrase but skill doesn't activate

Cause: Phrase too vague or contradicts another loaded skill
Solution: Make phrase more specific (not "generate docs" but "generate PRD"). Check overlap — if two skills have same trigger, agent may pick wrong one. Refine negatives to be more specific about what NOT to do.

## Error: No XML brackets but description still invalid

Cause: YAML parser sees special characters as syntax
Solution: Escape if needed. Test description in actual frontmatter before delivery.
