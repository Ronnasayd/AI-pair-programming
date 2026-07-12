---
name: image-mockup-recreator
description: Recreate a reference screenshot or mockup image as a live HTML/CSS artifact, using headless-browser screenshots, an SSIM visual diff score, and pixel-grid overlays to iteratively close the gap between the render and the original. Use when someone uploads a UI screenshot, app screen, or design mockup and asks to "recreate this as an artifact", "build this in HTML", "make a mockup of this image", "match this design", or wants automatic adjustment/refinement toward a reference image without a Figma file. Do NOT use when a Figma file/node URL is available (use a Figma-to-code skill instead) or when the user just wants a design critique without building anything (use design-image-diff instead).
license: CC-BY-4.0
metadata:
  author: Ronnasayd Machado - github.com/Ronnasayd
  version: "1.0.0"
---

# Image Mockup Recreator

Turn one reference image into a live HTML/CSS artifact through a measured iterate-and-score loop, not a single guess. Combines a Sequential Workflow (setup → build → publish) with an Iterative Refinement inner loop (render → score → adjust).

## When to Use

- User uploads a UI screenshot/mockup and asks to recreate, rebuild, or "match" it as code.
- User wants an artifact that gets automatically refined toward a reference image.
- No Figma source is available — this works from a flat image only.

## Step 1 — Stage the reference

Copy the source image into a scratch directory as `target.<ext>`. Read its exact pixel size (e.g. `python3 -c "from PIL import Image; print(Image.open('target.png').size)"`). That size is the fixed viewport for every render — never let it drift between iterations, or the SSIM score becomes meaningless.

## Step 2 — Build the first-pass HTML

Inspect the image and translate obvious structure into a single self-contained HTML file sized exactly to the target dimensions (`width`/`height` in px on `html,body`). Cover every major region (background, header/logo, primary content blocks, side panels, footer) with absolute-positioned elements at estimated coordinates. Don't chase fine detail on pass one — get every region present and roughly placed first.

Avoid CSS `filter: brightness(0) invert(1)` tricks to force-monochrome colored emoji — this corrupts glyph rendering in headless Chromium into solid blocks. Use inline hand-drawn SVG icons (`stroke="currentColor"`, `fill="none"`) for any icon that must render as a clean single color.

## Step 3 — Render and score

```bash
python3 scripts/screenshot.py <html_path> <out.png> --width <W> --height <H> \
  --executable-path /usr/bin/google-chrome   # only if the bundled Playwright browser isn't installed
python3 scripts/compare_ssim.py target.<ext> <out.png> --json --output-diff heatmap.png
```

`compare_ssim.py` returns an SSIM score (0-1), a verdict, and up to 5 diff-region bounding boxes sorted by area — use those boxes to know _where_ to look, not just that something's off. `--output-diff` writes a heatmap image (hot = high diff, cool = good match); send it to the user directly when they want to see mismatch location rather than just the number.

If Playwright errors with a missing browser executable, do not run `playwright install` blind — first check for a system Chrome/Chromium binary (`which google-chrome chromium chromium-browser`) and pass it via `--executable-path`; it's usually already present.

## Step 4 — Iterate

Loop: read the current screenshot, compare visually + via diff-region coordinates against the target, make **one focused category of change** per round (background/glow shape, icon set, font weight, spacing, a single element's position), re-render, re-score. Keep score as a signal, not a target to game — a drop can mean a real regression, or it can mean the metric penalizing a legitimately better structural fix (e.g. replacing a flat placeholder texture with something closer to the real photo). Compare the new screenshot against the previous one before deciding which to keep.

Stop the loop when:

- Score plateaus across 2 consecutive rounds with no category left to try, OR
- The user says the structure/spacing is good enough (see Step 5), OR
- ~8-10 rounds have passed (diminishing returns).

## Step 5 — Use a pixel grid for precise placement

When rough coordinates aren't converging, overlay a fixed-spacing grid on both the target and the current render:

```bash
python3 scripts/grid_image.py target.<ext> target_grid.png --spacing 50 --color "#ff00ff"
python3 scripts/grid_image.py <out.png> out_grid.png --spacing 50 --color "#ff00ff"
```

View both side by side and read off pixel offsets directly (e.g. "menu block starts one grid cell too far right") instead of guessing from unmarked screenshots. This is the fastest way to fix relational spacing complaints like "these two elements should be closer together" — change only the specific offset/gap property involved, don't re-derive the layout.

## Step 6 — Clarify scope if ambiguous

If it's unclear whether the user wants pixel/texture-level fidelity (real photos, exact gradients, font hinting) or just structural fidelity (layout, spacing, proportions, correct components present), ask before burning more iterations. SSIM is texture-sensitive — plateauing once structure is confirmed correct is expected and acceptable when the user has scoped to structure, not a failure of the loop.

## Step 7 — Publish

Publish the HTML file as an Artifact. On every later change, republish the **same file path** so the URL stays stable across the whole refinement session — the user should be able to bookmark one link instead of getting a new one each round.

## Example

User uploads a smart-TV home-screen screenshot, says "recreate this as an artifact and keep adjusting until it's close."

1. Stage `target.jpeg` (1600x720), build `index.html` at 1600x720 with logo, card grid, side menu, footer.
2. Render iter1, score 0.62. Diff regions point at the icon area and background — icons were colorful emoji, target uses white line icons.
3. Swap emoji for inline SVG icons (fixes a `filter` rendering bug in the process). Re-render: 0.63, icons now correct.
4. User flags "the icons don't look like the mockup" — read screenshot, notice generic icon shapes vs target's TV+remote glyph; swap the specific SVG path, not the whole card.
5. User says focus on structure, not texture — stop chasing background photo fidelity, confirm layout via grid overlay instead, treat flat SSIM as expected.
6. Publish artifact; republish same path after each fix so the link stays live.

## Troubleshooting

**SSIM script errors "Missing dependencies"**: `pip install opencv-python scikit-image numpy` (or `opencv-python-headless` in a headless environment).

**Screenshot is blank or errors on `file://` load**: confirm the HTML path passed to `screenshot.py` is absolute, not relative — Playwright's `goto` needs a fully-qualified `file://` URI.

**Score won't climb past ~0.6 despite matching layout**: likely a background-texture ceiling (real photo vs CSS pattern) — confirm with the user whether structural fidelity is actually the goal (Step 6) before spending more iterations on it.
