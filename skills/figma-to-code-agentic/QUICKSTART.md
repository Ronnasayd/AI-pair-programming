# Quick Start: figma-to-code-agentic Skill

## The Skill Does

Converts Figma designs → production-ready React/Vue/HTML components by:

1. Reading Figma specs (layout, colors, typography)
2. Generating code (auto-detects framework)
3. Taking screenshots and comparing with SSIM (Structural Similarity Index)
4. Iterating up to 10x until pixel-perfect (SSIM ≥ 0.95)

## How to Trigger

**In Claude/Copilot, say something like:**

```
"Generate a React component from this Figma design: [figma-link]
The card should have [description of elements].
Make it match the design pixel-perfect."
```

Or:

- "Create a Vue component from this Figma header design"
- "Build an HTML hero section matching this Figma spec"
- "Convert this design to code that matches Figma exactly"

## What You Get

**Single-file component** with SSIM validation score:

```jsx
// ProductCard.jsx
// Figma match score: 0.96 (✓ production-ready)

export function ProductCard({ ... }) {
  // ... code matching Figma pixel-perfect
}
```

## Required Tools (MCPs)

- **Figma MCP** — reads design specs
- **Browser MCP** (Playwright/Puppeteer/Chrome) — takes screenshots
- **Python environment** — for SSIM calculation

## Scripts (For Advanced Use)

### 1. Compare Screenshots with SSIM

```bash
python scripts/compare_ssim.py figma_screenshot.png component_screenshot.png --json
```

**Output:**

```json
{
  "ssim_score": 0.96,
  "verdict": "PASS",
  "is_match": true,
  "diff_regions": []
}
```

### 2. Track Iteration History

```bash
python scripts/agentic_loop.py component.jsx figma_screenshot.png --framework react --max-iterations 10 --output-report report.json
```

**Output:** JSON report showing iteration progress and SSIM scores over time

## Success Criteria

| Score     | Status    | Recommendation                      |
| --------- | --------- | ----------------------------------- |
| ≥ 0.95    | ✅ PASS   | Ready for production                |
| 0.90–0.94 | ⚠️ REVIEW | Probably fine, review with designer |
| < 0.90    | ❌ FAIL   | Issues, escalate to designer        |

## Example Workflow

1. **User:** "Generate a checkout form from this Figma design"
2. **Skill:**
   - Extracts form fields, colors, button styles from Figma
   - Generates React + Tailwind component
   - Takes screenshot, compares to Figma
   - SSIM = 0.92 → Refines spacing, button styling
   - Takes new screenshot → SSIM = 0.96 ✓
   - Returns final code with score
3. **Result:** Production-ready checkout form in 2–3 iterations

## File Structure

```
skills/figma-to-code-agentic/
├── SKILL.md                      ← Full skill definition
├── README.md                     ← Comprehensive guide
├── evals/evals.json             ← Test cases
├── scripts/
│   ├── compare_ssim.py          ← Screenshot comparison
│   └── agentic_loop.py          ← Loop controller
└── references/
    └── browser-automation.md    ← Screenshot techniques
```

## Common Scenarios

**Scenario 1: Product Card Component**

```
Input: Figma product card design (image, title, description, buttons)
Output: React component (SSIM 0.96) in 1–2 iterations
```

**Scenario 2: Responsive Header**

```
Input: Figma navbar (desktop + mobile hamburger menu)
Output: Vue component (SSIM 0.96) with responsive breakpoints
```

**Scenario 3: Landing Page Hero**

```
Input: Figma hero section (gradient, headline, CTA)
Output: HTML file (SSIM 1.0) ready to deploy
```

## Limitations

- **Static components only** — complex interactions must be coded separately
- **Single viewport** — validates at one size (document multiple breakpoints needed)
- **Font rendering** — use web fonts (Google Fonts) for consistency across systems
- **Image assets** — generated code uses placeholders; swap in real URLs

## Troubleshooting

| Problem            | Solution                                           |
| ------------------ | -------------------------------------------------- |
| SSIM stuck at 0.88 | Use web fonts; check DPI scaling                   |
| Screenshot blank   | Verify component code syntax; check dependencies   |
| Colors mismatch    | Confirm hex values match Figma in browser DevTools |
| Layout breaks      | Roll back, make smaller refinements                |

---

**That's it!** Skill is ready to use. Just trigger it with a Figma design and describe what you need.
