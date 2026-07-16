# Example

User uploads a smart-TV home-screen screenshot, says "recreate this as an artifact and keep adjusting until it's close."

1. Stage `target.jpeg` (1600x720), build `index.html` at 1600x720 with logo, card grid, side menu, footer.
2. Render iter1, score 0.62. Diff regions point at the icon area and background — icons were colorful emoji, target uses white line icons.
3. Swap emoji for inline SVG icons (fixes a `filter` rendering bug in the process). Re-render: 0.63, icons now correct.
4. User flags "the icons don't look like the mockup" — read screenshot, notice generic icon shapes vs target's TV+remote glyph; swap the specific SVG path, not the whole card.
5. User says focus on structure, not texture — stop chasing background photo fidelity, confirm layout via grid overlay instead, treat flat SSIM as expected.
6. Publish artifact; republish same path after each fix so the link stays live.

# Troubleshooting

| Symptom                                             | Fix                                                                                                                                                                |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| SSIM script errors "Missing dependencies"           | `pip install opencv-python scikit-image numpy` (or `opencv-python-headless` in headless environments)                                                              |
| Screenshot blank or errors on `file://` load        | Confirm HTML path passed to `screenshot.py` is absolute — Playwright's `goto` needs a fully-qualified `file://` URI                                                |
| Score won't climb past ~0.6 despite matching layout | Likely background-texture ceiling (real photo vs CSS pattern) — confirm with user whether structural fidelity is actually the goal before spending more iterations |
