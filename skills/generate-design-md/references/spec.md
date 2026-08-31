# DESIGN.md format — condensed spec

Google Labs open format (announced 2026). Machine-readable tokens + human/AI rationale in one file.

## YAML front matter schema

```yaml
version: <string> # optional, current: "alpha"
name: <string>
description: <string> # optional
omitted: <string[] | {section, reason}[]> # optional — silences missing-section lint
colors:
  <token-name>: <Color>
typography:
  <token-name>: <Typography>
rounded:
  <scale-level>: <Dimension>
spacing:
  <scale-level>: <Dimension | number>
components:
  <component-name>:
    <prop>: <string | token reference>
```

## Token types

| Type            | Format                                                                                                        | Example                           |
| --------------- | ------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| Color           | CSS color: hex, `rgb()`, `hsl()`, `oklch()`, named                                                            | `"#1A1C1E"`                       |
| Dimension       | number + unit                                                                                                 | `48px`, `0.75rem`                 |
| Token reference | brace-enclosed path                                                                                           | `{colors.primary}`, `{spacing.3}` |
| Typography      | object: `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing`, `fontFeature`, `fontVariation` | see example                       |

## Component token props

`backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`.
Variants (hover, active, pressed) = separate component entries, related key names (`button`, `buttonHover`).

## Canonical sections (Markdown `##`, this order)

1. Overview (alias: Brand & Style)
2. Colors
3. Typography
4. Layout (alias: Layout & Spacing)
5. Elevation & Depth (alias: Elevation)
6. Shapes
7. Components
8. Do's and Don'ts

## Lint rules (11)

**Error**

- `broken-ref` — unresolved token reference. Exit code 1.

**Warning**

- `missing-primary` — no `colors.primary`
- `contrast-ratio` — a color pair below WCAG AA 4.5:1
- `orphaned-tokens` — token neither referenced nor mentioned in body
- `missing-typography` — no typography token
- `section-order` — sections out of canonical order
- `unknown-key` — unrecognized key in front matter
- `token-like-ignored` — a value looks like a token but sits outside a token block

**Info**

- `token-summary` — counts
- `missing-sections` — canonical section absent and not in `omitted:`
- `omitted-rules` — reports what `omitted:` suppressed

## CLI

```bash
npx @google/design.md lint DESIGN.md          # validate, exit 1 on error
npx @google/design.md diff OLD.md NEW.md       # regression check
npx @google/design.md export DESIGN.md --format json-tailwind|css-tailwind|dtcg
npx @google/design.md spec                     # print spec + rules table
```
