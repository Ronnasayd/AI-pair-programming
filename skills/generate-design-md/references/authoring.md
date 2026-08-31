# Authoring a DESIGN.md

## YAML front matter template

```yaml
version: alpha
name: <Product Name>
description: <one line on the visual direction> # optional
colors:
  primary: "#1A73E8"
  onPrimary: "#FFFFFF"
  surface: "#FFFFFF"
  onSurface: "#1A1C1E"
  # semantic names, not raw palette names
typography:
  display:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: 32px
    fontWeight: 700
    lineHeight: 1.2
  body:
    fontFamily: "{typography.display.fontFamily}"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.5
rounded:
  sm: 4px
  md: 8px
  lg: 16px
spacing:
  1: 4px
  2: 8px
  3: 12px
  4: 16px
components:
  button:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.onPrimary}"
    rounded: "{rounded.md}"
    padding: "{spacing.3}"
  buttonHover:
    backgroundColor: "#1B66C9"
```

## Front matter rules

| Rule               | Detail                                                                                                     |
| ------------------ | ---------------------------------------------------------------------------------------------------------- |
| Token references   | Brace path `{colors.primary}`, `{spacing.3}`. Must resolve — unresolved = `broken-ref` error.              |
| Color naming       | Semantic role (`surface`, `onSurface`, `danger`), not hue. Any CSS color (hex, `rgb()`, `oklch()`, named). |
| Dimensions         | number + unit (`48px`, `0.75rem`). `spacing` may use bare numbers.                                         |
| Component variants | Separate entries: `button`, `buttonHover`, `buttonPressed`.                                                |
| Component props    | `backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`.             |
| Required           | A `primary` color + ≥1 typography token (else lint warns).                                                 |
| Contrast           | Text/bg pairs ≥ 4.5:1 WCAG AA (`contrast-ratio` warning).                                                  |
| No orphans         | Every token referenced somewhere or explained in body (`orphaned-tokens` warning).                         |
| Deliberate skips   | List skipped sections in `omitted:` to silence `missing-sections`.                                         |

## Markdown body — sections (`##`, this exact order)

| #   | Section           | Contains                                                                     |
| --- | ----------------- | ---------------------------------------------------------------------------- |
| 1   | Overview          | Visual direction, brand personality, the feel. Why it looks this way.        |
| 2   | Colors            | What each semantic color _does_, when to use it. Light/dark handling.        |
| 3   | Typography        | Type scale logic, hierarchy, when each style applies.                        |
| 4   | Layout            | Grid, spacing scale intent, responsive behavior.                             |
| 5   | Elevation & Depth | How depth is signaled (shadow, contrast, layering), when to raise a surface. |
| 6   | Shapes            | Border-radius language, geometric consistency.                               |
| 7   | Components        | Behavioral guidance per pattern: states, compose do/don't.                   |
| 8   | Do's and Don'ts   | Explicit guardrails + decision criteria for cases the tokens don't cover.    |

Write intent and constraints, not a value dump — values live in the front
matter. Each section should let an AI agent choose correctly when no explicit
rule exists.
