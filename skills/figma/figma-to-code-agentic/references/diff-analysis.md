# Reference: Diff Analysis Guide

When SSIM score is below 0.9, use this guide to systematically diagnose and fix differences.

## Step 1: Classify the Problem

Look at the `diff_regions` from `compare_ssim.py`. Regions are returned by area (largest first). Ask:

- Is the diff in a **specific element** (button, image, text) or **everywhere**?
- Is the diff **positional** (things are shifted) or **stylistic** (colors, weights)?
- Is the diff **consistent** (same offset throughout) or **isolated** (one element)?

## Step 2: Diagnosis Tree

### Large diff covering most of the component

Likely causes:

- Wrong viewport size (check Figma export dimensions vs screenshot viewport)
- Background color mismatch (white vs transparent vs off-white)
- Font family completely wrong (system font vs web font)
- Global scale/zoom difference

Fix: Check global settings first before touching individual elements.

### Diff concentrated in a specific region

Identify the element. Check in priority order:

**1. Layout / positioning**

- Is the element missing entirely? → Check if it's rendered at all (inspect HTML)
- Is the element in the wrong position? → Check `display`, `position`, `flex`/`grid` parent
- Is the element the wrong size? → Check `width`, `height`, `flex-grow`, `min/max` constraints
- Wrong stacking order? → Check `z-index`, DOM order

**2. Spacing**

- Compare Figma's padding/margin values to CSS exactly
- Note: Figma uses px; CSS may inherit or compound spacing
- Check: `padding`, `margin`, `gap`, `row-gap`, `column-gap`
- Remember: Figma's "spacing between" = CSS `gap`, not `margin`

**3. Color**

- Extract hex from Figma MCP or design spec
- CSS: use the exact hex — don't approximate (`#1E3A8A` ≠ `blue-800`)
- Check opacity: Figma opacity on a layer ≠ CSS `opacity` (may need `rgba`)
- Gradient directions: Figma uses degrees (0° = up); CSS `to top` = 0deg equivalent

**4. Typography**

- Font size: Figma px → CSS px (1:1, no conversion needed)
- Font weight: Figma "Semi Bold" = `600`, "Bold" = `700`, "Medium" = `500`
- Line height: Figma shows absolute px — convert to unitless ratio (`line-height: 1.5`)
- Letter spacing: Figma "em" or "%" → CSS `letter-spacing` in `em`
- Font family: use exact name from Figma; load via Google Fonts if needed

**5. Shadows**

- Figma shadow format: `X Y blur spread color opacity`
- CSS: `box-shadow: {x}px {y}px {blur}px {spread}px rgba({r},{g},{b},{opacity})`
- Figma "inner shadow" = CSS `inset` keyword
- Multiple shadows: comma-separate in CSS (same order as Figma layer list)

**6. Borders & radius**

- Border radius: Figma per-corner support = CSS `border-radius: TL TR BR BL`
- Border width/color: match exactly; check if Figma uses "stroke" vs fill layer
- Outline vs border: Figma strokes render inside/outside/center — CSS `outline` is always outside

### Diff only in text areas

Usually font rendering. Solutions:

- Add `font-smoothing: antialiased` (WebKit) or `-moz-osx-font-smoothing: grayscale`
- Use the exact same web font (Figma often uses Google Fonts — check font name)
- If using system fonts, accept SSIM 0.90–0.93 as "good enough" — visually identical

### Score regresses after a fix

You introduced a new bug. Steps:

1. Compare current code to previous iteration
2. Identify what changed
3. Revert just that change, or make a smaller adjustment

---

## Step 3: Verification Checklist Before Each Iteration

Before re-running screenshot, verify:

- [ ] No hardcoded pixel values that should use design tokens
- [ ] Viewport size matches Figma export
- [ ] Animations disabled in test render
- [ ] Web fonts loaded (if applicable) — add a `page.waitForTimeout(500)` after load if needed
- [ ] The component is centered/positioned the same way as in the Figma frame

---

## SSIM Score Interpretation

| Score     | Meaning                  | Action                                   |
| --------- | ------------------------ | ---------------------------------------- |
| 0.98–1.00 | Near-perfect             | Ship it                                  |
| 0.9–0.97  | Production-ready         | Ship it                                  |
| 0.92–0.94 | Minor visual differences | Review with designer; usually acceptable |
| 0.88–0.91 | Noticeable differences   | Fix before shipping                      |
| < 0.88    | Structural mismatch      | Check layout/framework fundamentals      |

**Note:** SSIM below 0.9 due to font rendering alone (not layout) is usually acceptable. Check the diff image visually — if the diff is only in text subpixels, call it done.
