# Figma-to-Code Agentic Skill

Convert Figma designs into production-ready component code using an agentic refinement loop.

## Overview

This skill automates the design-to-development handoff by:

1. **Reading Figma designs** — extracts layout, colors, typography, spacing via Figma MCP
2. **Generating code** — creates React, Vue, or vanilla HTML components matching the spec
3. **Validating visually** — renders component and compares screenshot to Figma using SSIM (Structural Similarity Index)
4. **Iterating intelligently** — refines code based on visual diff until SSIM ≥ 0.9 (max 10 iterations)
5. **Delivering confidence** — returns pixel-perfect code with validation score

## Quick Start

### For Skill Creators

1. **Review the SKILL.md** — The complete skill definition with workflow, best practices, and examples.
2. **Check the evals/** — Test cases validating different scenarios (React card, Vue header, vanilla hero).
3. **Run test cases** — Spawn subagents to validate the skill against real prompts.

### For End Users (once integrated)

**Trigger the skill by:**

```
"Generate a React component from this Figma design: [link]. The card should have an image, title, description, and two buttons. Match the design pixel-perfect."
```

The skill will:

- Parse Figma layout and styling
- Generate component code
- Take screenshot and compare to original
- Refine iteratively if needed
- Return code with SSIM validation score

## File Structure

```
figma-to-code-agentic/
├── SKILL.md                    # Complete skill definition
├── README.md                   # This file
├── evals/
│   └── evals.json             # Test cases (3 scenarios)
├── scripts/
│   ├── compare_ssim.py        # SSIM comparison utility
│   ├── agentic_loop.py        # Loop controller logic
│   └── ...                    # Helper scripts
└── references/
    ├── browser-automation.md   # Taking screenshots
    └── ...                    # Other references
```

## Key Features

### Framework Agnostic

- **Auto-detect**: Infers React, Vue, vanilla HTML from context/codebase
- **Styling flexible**: Uses project conventions (Tailwind, CSS Modules, styled-components, plain CSS)
- **Single output file**: Component code in one `.jsx`, `.vue`, or `.html` file

### Visual Validation via SSIM

- **0.9+ score**: Production-ready, pixel-perfect
- **0.90–0.94**: Likely fine, review with designer
- **< 0.90**: Issues, escalate to designer

### Intelligent Iteration

- **Up to 10 rounds** of refinement
- **Diff analysis** identifies specific issues (spacing, colors, fonts, shadows)
- **Convergence detection** stops early if score stalls

### Browser Automation

- Uses **Playwright**, **Puppeteer**, or **Chrome MCP** to render and screenshot components
- Compares pixel-for-pixel against Figma design

## Test Cases

The skill includes 3 realistic test scenarios:

### 1. React Card Component

- **Task**: Generate a product card with image, title, description, and CTA buttons
- **Framework**: React + Tailwind CSS
- **Validation**: Cards should match Figma pixel-perfect

### 2. Vue Header/Navigation

- **Task**: Build a navbar with logo, menu items, and search bar
- **Framework**: Vue 3 SFC
- **Validation**: Responsive (desktop + mobile hamburger menu)

### 3. HTML Hero Section

- **Task**: Landing page hero with gradient, headline, and CTA button
- **Framework**: Vanilla HTML + CSS + JS
- **Validation**: Full viewport height, centered content

## How to Test the Skill

Once the skill is ready for evaluation:

```bash
# Run all test cases
python -m scripts.aggregate_benchmark ./figma-to-code-agentic-workspace/iteration-1 --skill-name figma-to-code-agentic

# Compare SSIM manually
python scripts/compare_ssim.py figma_design.png component_screenshot.png --json

# Simulate agentic loop
python scripts/agentic_loop.py component.jsx figma_screenshot.png --framework react --max-iterations 10
```

## Dependencies

**Required MCPs:**

- **Figma MCP** - Extract design specs (colors, layout, typography)
- **Browser MCP** (Playwright, Puppeteer, or Chrome) - Screenshot rendering

**Python packages:**

- `opencv-python` — Image processing
- `scikit-image` — SSIM calculation
- `playwright` or `puppeteer` — Browser automation

**Install all:**

```bash
pip install opencv-python scikit-image playwright
playwright install chromium
```

## Workflow Example

**User Input:**

> "I have a Figma design for a checkout form. It has text inputs for email and password, a "Remember me" checkbox, and a blue submit button. The background is light gray. Generate a React component that matches this exactly."

**Skill Execution:**

```
1. Parse Figma → Extract colors (#E5E7EB bg, #2563EB button), spacing, fonts
2. Generate React + Tailwind code
3. Render component in browser → screenshot_iter_1.png
4. Compare with Figma → SSIM = 0.89
5. Identify diff → "Button text too small (14px vs 16px), input borders need softening"
6. Refine code → adjust font-size, border-radius
7. Take screenshot → screenshot_iter_2.png
8. Compare → SSIM = 0.94
9. Analyze diff → "Minor anti-aliasing difference on button shadow, acceptable"
10. Compare → SSIM = 0.96 ✓ PASS
11. Return code with score: "CheckoutForm.jsx | SSIM: 0.96 (✓ Production-ready)"
```

**Output:**

```jsx
// CheckoutForm.jsx
// SSIM Match: 0.96 ✓

export function CheckoutForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-200">
      <form className="w-full max-w-sm bg-white p-6 rounded-lg">
        <input
          type="email"
          placeholder="Email"
          className="w-full px-4 py-2 border border-gray-300 rounded-md mb-4 text-base"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          className="w-full px-4 py-2 border border-gray-300 rounded-md mb-4 text-base"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <label className="flex items-center mb-6">
          <input
            type="checkbox"
            className="mr-2"
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
          />
          <span className="text-sm text-gray-700">Remember me</span>
        </label>
        <button
          type="submit"
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-md transition-colors text-base"
        >
          Sign In
        </button>
      </form>
    </div>
  );
}
```

## Limitations & Known Issues

1. **Complex Animations** — Generates static structure; animations must be coded separately
2. **Image Assets** — References images as placeholders; provide actual URLs
3. **Single Viewport** — Validates at one breakpoint; document all responsive sizes
4. **SSIM Sensitivity** — Can be sensitive to font rendering and anti-aliasing (0.92+ is often fine)
5. **System Fonts** — Rendering varies; use web fonts (Google Fonts) for consistency

## Troubleshooting

| Issue               | Solution                                             |
| ------------------- | ---------------------------------------------------- |
| SSIM stuck at 0.88  | Font rendering mismatch; switch to web fonts         |
| Screenshot is blank | Check component code for errors; verify dependencies |
| Colors don't match  | Verify hex values match Figma in browser DevTools    |
| Layout breaks       | Roll back to previous iteration; smaller refinements |
| Max iterations hit  | Design too ambiguous; escalate to designer           |

## Next Steps

1. **Review SKILL.md** for complete workflow and best practices
2. **Check assertions** in evals.json for what will be validated
3. **Run test cases** with subagents (set up iteration-1 workspace)
4. **Collect feedback** using the HTML viewer
5. **Iterate skill** based on results
6. **Optimize description** for better triggering accuracy

## Performance Targets

- **Speed**: 3–5 min for typical card/hero component (including screenshot/compare)
- **Accuracy**: SSIM ≥ 0.9 in 2–4 iterations on well-specified designs
- **Coverage**: Works with React, Vue, vanilla HTML; auto-configures styling

## Author Notes

This skill bridges the design-to-code gap by adding rigor: instead of designers hoping developers will match the spec, the skill validates implementation automatically. This is especially valuable for:

- **Design systems** — ensuring component consistency
- **Handoffs** — reducing back-and-forth iterations
- **Quality** — catching visual bugs early
- **Confidence** — SSIM score as a "design approval" marker

---

For questions or improvements, refer to SKILL.md or contact the skill maintainer.
