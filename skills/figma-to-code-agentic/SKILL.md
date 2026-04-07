---
name: figma-to-code-agentic
description: |
  Convert Figma designs into production-ready component code using an agentic loop that validates implementation against the design.

  Use this skill whenever you need to: generate code from Figma designs, create React/Vue/HTML components that match pixel-perfect designs, iterate on component implementation until it matches the Figma spec, validate UI implementations against design screenshots, or bridge the gap between design and development.

  The skill uses Figma MCP to read design specs, generates code (detecting framework automatically), takes screenshots via browser automation, compares visuals using SSIM (Structural Similarity Index), and loops up to 10 times refining code until it reaches 95% visual similarity to the original design. This is perfect for design-system components, landing pages, or any UI that needs to match a Figma spec precisely.
---

# Figma-to-Code Agentic

Generate pixel-perfect component code from Figma designs, automatically iterating and refining until the implementation matches the spec.

## When to Use This Skill

**TRIGGERS:**

- User provides a Figma link/file and asks to generate code for a component, page, or entire design system
- User says: "generate this Figma design as React code", "convert this Figma to HTML", "build a component from this design"
- User mentions needing code that "matches the design", "looks exactly like Figma", or "validates against the spec"
- Design-to-development handoff: user has Figma designs and wants to ensure code is pixel-perfect
- Any variant: "create a Vue component", "turn this into a landing page", "build the checkout flow from Figma"

**PREREQUISITES:**

- Figma file/link with component or page design
- Target framework (React, Vue, vanilla HTML/CSS) — skill auto-detects from context
- Browser environment (for screenshot validation)
- Figma MCP and browser automation MCP available (Playwright, Puppeteer, or Chrome via MCP)

## High-Level Workflow

```
1. Parse Figma Design
   ↓
2. Generate Initial Code
   ↓
3. Render Component (screenshot)
   ↓
4. Compare vs Original (SSIM score)
   ↓
5. Score >= 0.95?
   └─ YES → Return refined code
   └─ NO → Refine code, loop back to step 3 (max 10 iterations)
```

## Step-by-Step Process

### Phase 1: Analysis & Code Generation

1. **Read Figma Design**
   - Use Figma MCP to extract design specs: layout, colors, typography, spacing, shadows, borders, responsive behavior
   - Note any constraints (min/max widths, breakpoints, interactions)

2. **Detect Framework & Styling Approach**
   - If no explicit framework: check codebase for hints (package.json, existing components, imports)
   - Default stack: React + Tailwind (if neutral) OR match project conventions
   - Styling: inspect the codebase to use the same approach (Tailwind, CSS Modules, styled-components, plain CSS)

3. **Generate Component Code**
   - Create a single `.jsx`, `.tsx`, `.vue`, or `.html` file with:
     - All necessary imports
     - Responsive classes/logic
     - Proper spacing, colors, fonts matching Figma exactly
     - Accessibility attributes where applicable
   - Include comments explaining non-obvious design decisions

4. **Create a Render Test Page** (internally)
   - Wrap the component in a minimal page (white background, standard viewport)
   - Similar viewport dimensions to Figma's export (e.g., 1280×720)

### Phase 2: Validation Loop (up to 10 iterations)

For each iteration:

5. **Take Screenshot**
   - Use browser automation MCP (Playwright, Puppeteer, Chrome MCP, or similar) to render the component
   - Capture at same dimensions as Figma export
   - Save as a PNG

6. **Calculate Similarity**
   - Load Figma design screenshot and component screenshot
   - Compute SSIM (Structural Similarity Index) score using `scikit-image` or OpenCV
   - SSIM ranges from 0 (completely different) to 1.0 (identical)
   - Score = 1.0 is perfect match; 0.95+ is "production-ready"

7. **Analyze Differences** (if score < 0.95)
   - Visually inspect both images side-by-side
   - Identify discrepancies: spacing, colors, font sizing, shadows, borders, layout breaks
   - Generate a diff report with specific issues (e.g., "button text too large", "padding on left side is 2px too small")

8. **Refine Code**
   - Update component code based on diff report
   - Make surgical edits: adjust sizing, spacing, colors—don't rewrite unnecessarily
   - Re-test (go to step 5)

9. **Convergence**
   - **Success**: SSIM score ≥ 0.95 → return final code
   - **Stalled**: No progress after 2 consecutive iterations → increase tolerance or escalate to human review
   - **Max iterations hit**: Stop at iteration 10, return best version so far

### Output Format

**Single-file component:**

```
[component-name].jsx/.tsx/.vue/.html
```

Include:

- Full, runnable code
- All imports and dependencies listed
- Comments explaining design-to-code decisions
- Responsive behavior documented
- SSIM validation score: `// Figma match score: 0.97 (✓ production-ready)`

**Metadata** (provide separately):

```
Framework: React, Language: TypeScript
Styling: Tailwind CSS
Figma Link: https://figma.com/...
SSIM Score: 0.97
Iterations: 3
Viewport: 1280×720
```

## Best Practices

### Code Quality

- Match existing project conventions (indentation, naming, structure)
- Use semantic HTML (proper heading hierarchy, ARIA labels)
- Keep components focused and reusable
- Prefer composition over deep nesting

### Styling

- Never hardcode colors if design system exists—reference tokens
- Use grid/flexbox instead of absolute positioning (unless required by design)
- Ensure mobile responsiveness, test breakpoints
- Respect Figma's constraints (fixed width, fluid, fill, etc.)

### Iteration Strategy

- Each iteration should address multiple issues from the diff report, not just one
- If SSIM score is stuck, check for:
  - Subtle anti-aliasing differences (usually OK to ignore)
  - Font rendering differences across systems (consider using web fonts)
  - Viewport or DPI mismatches
- If trapped, document issues and recommend human review (e.g., "needs design clarification on shadow blur radius")

### When to Stop

- SSIM ≥ 0.95 = ship it
- SSIM 0.90–0.94 = probably fine, review differences with designer
- SSIM < 0.90 = likely structural issues, escalate to designer or request clarification

## Example: React + Tailwind Component

**Input:** Figma design of a card component (title, description, CTA button, drop shadow)

**Generated Code:**

```jsx
// card.jsx - Match: 0.96 ✓
export function Card({ title, description, onAction }) {
  return (
    <div className="w-80 rounded-lg bg-white shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-3">{title}</h2>
      <p className="text-sm text-gray-600 mb-6 leading-relaxed">
        {description}
      </p>
      <button
        onClick={onAction}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-md transition-colors"
      >
        Learn More
      </button>
    </div>
  );
}
```

**SSIM Validation:** 0.96 (Button text padding +2px, shadow slightly softer than Figma, but within acceptable tolerance.)

## Compatibility

**Required MCPs:**

- Figma MCP (for design extraction)
- Browser automation (Playwright, Puppeteer, Chrome MCP, or equivalent)
- Python environment (for SSIM calculation via `scikit-image` or `opencv-python`)

**Optional:**

- Design tokens MCP (if design system available)
- CSS/styling linter (e.g., Stylelint)

**Supported Frameworks:**

- React (JSX/TSX) — most mature
- Vue 3 (SFC or standalone)
- Vanilla HTML + CSS + JS
- Other frameworks (auto-detect from codebase context)

## How This Skill Integrates With Its Tools

This skill uses bundled scripts and references to automate the agentic loop:

### Scripts (in `scripts/` folder)

1. **compare_ssim.py** — SSIM comparison engine
   - Called after each iteration to score visual similarity
   - Usage: `python scripts/compare_ssim.py figma_screenshot.png component_screenshot.png --json`
   - Returns: SSIM score (0–1), verdict (PASS/REVIEW/FAIL), diff regions

2. **agentic_loop.py** — Loop controller
   - Tracks iteration history, detects convergence, manages state
   - Used internally by the skill to know when to stop iterating
   - Saves iteration summary as JSON for reporting

### References (in `references/` folder)

- **browser-automation.md** — How to take screenshots with Playwright/Puppeteer/Chrome MCP
- Used by the skill when rendering components to screenshot

### Runtime Flow

```
Skill Execution:
  1. Figma MCP reads design specs
  2. Claude generates code (using skill guidance)
  3. Browser renders component → screenshot taken
  4. Python script (compare_ssim.py) invoked:
     → Compares Figma screenshot vs component screenshot
     → Returns SSIM score
  5. Agentic loop controller (agentic_loop.py) evaluates:
     → Score >= 0.95? DONE ✓
     → Score stalled? DONE (return best version)
     → Iterations < 10? Refine code and loop back to step 3
  6. Return final code + SSIM metadata
```

## Limitations & Gotchas

1. **Complex Interactions:** Skill generates static components. If design includes animations, hover states, or complex interactions, generate the visual structure and document interaction specs separately.

2. **Image Assets:** Figma may include images; skill will reference them as placeholders (`<img alt="..." />`) unless explicitly provided.

3. **Responsive Design:** Skill validates at a single viewport. If design has multiple breakpoints, document all viewport sizes and iterate per breakpoint or use media queries to handle all at once.

4. **SSIM Sensitivity:** SSIM can be sensitive to anti-aliasing, font rendering, and sub-pixel differences. A 0.92–0.95 score often looks visually identical; don't over-optimize.

5. **System Font Rendering:** Font rendering varies across OS (macOS, Windows, Linux). Web fonts (e.g., Google Fonts) are more consistent.

## Troubleshooting

| Issue                       | Cause                                           | Solution                                                           |
| --------------------------- | ----------------------------------------------- | ------------------------------------------------------------------ |
| SSIM score stuck ~0.88      | Likely font rendering or anti-aliasing mismatch | Use web fonts, ensure consistent DPI scaling                       |
| Screenshot is blank         | Browser failed to load/render                   | Check component code for errors, ensure dependencies are available |
| Colors don't match          | Color space or gamma difference                 | Verify hex/RGB values match Figma exactly; check CSS parsing       |
| Layout breaks at iterations | Over-aggressive refinement                      | Roll back last change, make smaller adjustments                    |
| Max iterations reached      | Design too complex or ambiguous                 | Escalate to designer for clarification; document open issues       |

---

## Workflow Integration

**For Teams:**

- Designer finalizes spec in Figma → pass link to developer
- Developer runs this skill → gets pixel-perfect component code
- Code review focuses on logic, accessibility, performance—not pixel matching
- SSIM score in code comment serves as "design approval stamp"

**For Solo Devs:**

- Faster iteration between design and code
- Confidence that UI matches spec
- No context switch between Figma and IDE

---

## Advanced: Customizing SSIM Threshold

If your project has different quality bars:

- **Landing pages / hero sections:** 0.93+ (some breathing room for type rendering)
- **Design system components (buttons, cards):** 0.95+ (strict, reusable)
- **Complex data tables / forms:** 0.90+ (acceptable given layout complexity)

Adjust the `iteration_config` in code generation if needed.

---

## See Also

- [Figma API Docs](https://www.figma.com/developers/api)
- [SSIM Reference](https://en.wikipedia.org/wiki/Structural_similarity)
- [Playwright / Browser MCP](https://playwright.dev/)
