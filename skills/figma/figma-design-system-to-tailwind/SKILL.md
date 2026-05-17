---
name: figma-design-system-to-tailwind
description: Extract and convert a Figma Design System to Tailwind CSS v4 configuration with semantic component mapping. Use when migrating design tokens, colors, typography, spacing, and components from Figma to a code-based Tailwind theme. Optimized for small-to-medium design systems (< 20 components) with complete token coverage.
metadata:
  mcp-server: figma
  frameworks: tailwind, react, vue, svelte
  output-formats: tailwind.config.js, app/globals.css, design-tokens.json, component-mapping.json
---

# Figma Design System to Tailwind CSS v4 Skill

## Overview

This skill provides a comprehensive workflow for extracting design systems from Figma and converting them into production-ready Tailwind CSS v4 configurations. It bridges the gap between design tokens (colors, typography, spacing, shadows, etc.) and code-based theme definitions.

Use this skill to:

- **Extract design tokens** from Figma variables and styles (colors, spacing, typography, shadows, border radius)
- **Map Figma components** to semantic code patterns (e.g., Button/Primary → `btn-primary`)
- **Generate Tailwind configurations** in both modern CSS `@theme` format and `tailwind.config.js`
- **Create component mapping documentation** for future Code Connect automation
- **Maintain design-to-code fidelity** with validation and cross-referencing

## Prerequisites

- **Figma Design System File** (URL or file key)
- **Figma MCP Server** connected and functional
- **Tailwind CSS v4** or v3 compatible project
- **Node.js environment** for generating and validating Tailwind configuration

## Architecture: Token-First Extraction

The extraction workflow uses a **three-tier batching strategy** to optimize token consumption and paralelization:

```
Figma Design System
    ↓
[Batch 1] Metadata Structure Mapping
[Batch 2] Design Variables (colors, spacing, typography, shadows, radius)
[Batch 3] Component Extraction + Component Mapping
[Batch 4] (Optional) Variations & Dark Mode
    ↓
Normalized Token Set (JSON)
    ↓
[1] tailwind.config.js or app/globals.css
[2] component-mapping.json
[3] design-tokens.json (reference)
```

## Detailed Workflow

### Phase 1: Discovery & Structure Mapping

**Goal:** Understand the Figma design system hierarchy and identify token locations.

**Steps:**

1. **Get Figma Metadata**
   - Call `get_metadata` with the design system file key
   - Identify token sections (e.g., "Design Tokens", "Colors", "Typography", "Spacing")
   - Identify component sections (e.g., "Components", "Buttons", "Forms")
   - Document the file structure in a mental model or outline

2. **Identify Token Categories**
   - Colors (primary, secondary, neutrals, semantic)
   - Typography (font families, sizes, weights, line heights)
   - Spacing (margin, padding scales)
   - Shadows (drop shadows, elevation)
   - Border radius (corner size scales)

3. **Locate Variables**
   - Note: Figma variables are stored in specific sections or variable panels
   - Some tokens may be embedded in component styles; separate extraction required

**Example Output:**

```markdown
## Figma Structure

- **Design Tokens** (section/folder)
  - Colors (page or folder)
  - Typography (page or folder)
  - Spacing (page or folder)
  - Shadows (page or folder)
- **Components** (section/folder)
  - Buttons (with Primary, Secondary, Tertiary variants)
  - Forms (with Input, Select, etc.)
  - Cards (with variants)
```

---

### Phase 2: Strategic Chunking (3-4 Parallel Batches)

**Goal:** Extract design tokens efficiently, minimizing token consumption and maximizing parallelization.

**Batch Strategy:**

| Batch        | Content                                                         | Tools                                  | Priority   |
| ------------ | --------------------------------------------------------------- | -------------------------------------- | ---------- |
| 1            | Design Variables (colors, spacing, typography, shadows, radius) | `get_variable_defs`                    | **High**   |
| 2            | Component context & visual inspection                           | `get_design_context` (per component)   | **High**   |
| 3            | Component structure & variations                                | `get_metadata` (component nodes)       | **Medium** |
| 4 (Optional) | Dark mode variants, advanced features                           | `get_design_context` (dark mode nodes) | **Low**    |

**Execution:**

- Launch Batch 1 and 2 in parallel (independent operations)
- Process Batch 1 results before moving to Batch 2
- Batch 3 and 4 depend on Batch 2 completion

---

### Phase 3: Extract Design Variables

**Goal:** Extract all design variables (tokens) from Figma in structured format.

**Steps:**

1. **Call `get_variable_defs`**

   ```
   get_variable_defs(
     fileKey: "your-figma-file-key",
     nodeId: null  // Entire file
   )
   ```

2. **Process Response**
   - Capture variable name, value (HEX for colors, px for spacing), type
   - Flatten or nest by category (colors.primary.500, spacing.lg)

3. **Output Structure**
   ```json
   {
     "colors": {
       "primary": { "50": "#f0f9ff", "500": "#0ea5e9", "900": "#0c2d6b" },
       "secondary": { "50": "#fef2f2", "500": "#ef4444", "900": "#7c2d12" },
       "neutral": { "50": "#fafafa", "500": "#737373", "900": "#171717" }
     },
     "spacing": {
       "xs": "0.25rem",
       "sm": "0.5rem",
       "md": "1rem",
       "lg": "1.5rem",
       "xl": "2rem"
     },
     "typography": {
       "fontFamily": { "sans": "Inter", "mono": "Fira Code" },
       "fontSize": {
         "xs": "0.75rem",
         "sm": "0.875rem",
         "base": "1rem",
         "lg": "1.125rem"
       },
       "fontWeight": { "normal": 400, "medium": 500, "bold": 700 }
     },
     "shadows": {
       "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
       "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
     },
     "radius": {
       "none": "0",
       "sm": "0.125rem",
       "md": "0.375rem",
       "lg": "0.5rem"
     }
   }
   ```

---

### Phase 4: Extract Components & Build Mapping

**Goal:** Extract component context and build a mapping from Figma components to code patterns.

**Steps:**

1. **Iterate Over Each Component**
   - For each component in the "Components" section:
     ```
     get_design_context(
       fileKey: "your-figma-file-key",
       nodeId: "component-node-id",
       outputFormat: "tailwind"  // Request Tailwind classes
     )
     ```

2. **Extract Component Metadata**
   - Component name (e.g., "Button/Primary")
   - Visual properties (size, color, shadow, border radius)
   - Tailwind classes suggested
   - Props/variants (size, state, color variant)

3. **Build Component Mapping**
   ```json
   {
     "Button/Primary": {
       "code_pattern": "btn-primary",
       "base_classes": ["btn", "btn-primary"],
       "props": { "size": ["sm", "md", "lg"], "disabled": "boolean" },
       "tailwind_classes": "px-4 py-2 bg-blue-500 text-white rounded-md font-medium hover:bg-blue-600"
     },
     "Button/Secondary": {
       "code_pattern": "btn-secondary",
       "base_classes": ["btn", "btn-secondary"],
       "props": { "size": ["sm", "md", "lg"] },
       "tailwind_classes": "px-4 py-2 bg-gray-200 text-gray-900 rounded-md font-medium hover:bg-gray-300"
     },
     "Card": {
       "code_pattern": "card",
       "base_classes": ["rounded-lg", "shadow-md", "p-4", "bg-white"],
       "props": { "variant": ["default", "elevated"] }
     }
   }
   ```

---

### Phase 5: Normalize & Standardize Naming

**Goal:** Convert Figma naming conventions to standardized Tailwind/code patterns.

**Naming Convention Rules:**

| Category   | Figma Pattern            | Code Pattern          | Example                              |
| ---------- | ------------------------ | --------------------- | ------------------------------------ |
| Colors     | `Primary/Blue/500`       | `primary`, `blue-500` | `colors.primary.500` → `primary`     |
| Spacing    | `Space/16px`             | `spacing.base`        | `spacing.md` → `md`                  |
| Typography | `Font/Heading/Large`     | `text-heading-lg`     | `typography.fontSize.lg` → `text-lg` |
| Components | `Button/Primary/Desktop` | `btn-primary`         | Remove device modifiers              |

**Steps:**

1. **Map Variable Names**
   - Figma: `Color/Semantic/Primary/Default` → Code: `colors.primary`
   - Figma: `Spacing/Scale/Medium` → Code: `spacing.md`

2. **Enforce kebab-case**
   - All token names in code: lowercase, dash-separated
   - Example: `Primary Color 500` → `primary-500` (avoid spaces)

3. **Group Hierarchically**

   ```js
   colors: {
     primary: { 50: '...', 500: '...', 900: '...' },
     secondary: { ... },
     error: { ... }
   }
   ```

4. **Document Mapping**
   - Create a `naming-conventions.json` with mappings
   - Reference for future conversions or team onboarding

---

### Phase 6: Generate Tailwind v4 Output

**Goal:** Create production-ready Tailwind configuration in modern CSS-first format with JavaScript fallback.

**Option A: Modern CSS-First Approach (Recommended for v4)**

Create `app/globals.css`:

```css
@import "tailwindcss";

@theme {
  --color-primary-50: #f0f9ff;
  --color-primary-500: #0ea5e9;
  --color-primary-900: #0c2d6b;
  --color-secondary-50: #fef2f2;
  --color-secondary-500: #ef4444;
  --color-secondary-900: #7c2d12;

  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;

  --font-family-sans: "Inter", sans-serif;
  --font-family-mono: "Fira Code", monospace;

  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;

  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);

  --radius-none: 0;
  --radius-sm: 0.125rem;
  --radius-md: 0.375rem;
}

/* Component patterns */
.btn {
  @apply px-4 py-2 rounded-md font-medium transition-colors;
}

.btn-primary {
  @apply bg-blue-500 text-white hover:bg-blue-600;
}

.btn-secondary {
  @apply bg-gray-200 text-gray-900 hover:bg-gray-300;
}

.card {
  @apply rounded-lg shadow-md p-4 bg-white;
}
```

**Option B: JavaScript Config Fallback (v3 Compatible)**

Create `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./src/components/**/*.{js,ts,jsx,tsx}",
    "./src/pages/**/*.{js,ts,jsx,tsx}",
    "./src/layout/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#f0f9ff",
          500: "#0ea5e9",
          900: "#0c2d6b",
        },
        secondary: {
          50: "#fef2f2",
          500: "#ef4444",
          900: "#7c2d12",
        },
        neutral: {
          50: "#fafafa",
          500: "#737373",
          900: "#171717",
        },
      },
      spacing: {
        xs: "0.25rem",
        sm: "0.5rem",
        md: "1rem",
        lg: "1.5rem",
        xl: "2rem",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        mono: ["Fira Code", "monospace"],
      },
      fontSize: {
        xs: ["0.75rem", { lineHeight: "1rem" }],
        sm: ["0.875rem", { lineHeight: "1.25rem" }],
        base: ["1rem", { lineHeight: "1.5rem" }],
        lg: ["1.125rem", { lineHeight: "1.75rem" }],
      },
      boxShadow: {
        sm: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        md: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
      },
      borderRadius: {
        none: "0",
        sm: "0.125rem",
        md: "0.375rem",
        lg: "0.5rem",
      },
    },
  },
  plugins: [
    // require('@tailwindcss/forms'),      // Uncomment for form styling
    // require('@tailwindcss/typography'), // Uncomment for prose styling
  ],
};
```

**Intermediate Output: `design-tokens.json`**

For reference and future tooling:

```json
{
  "metadata": {
    "source": "Figma Design System",
    "extracted_at": "2024-01-15T10:30:00Z",
    "version": "1.0.0"
  },
  "tokens": {
    "colors": {
      /* ... */
    },
    "spacing": {
      /* ... */
    },
    "typography": {
      /* ... */
    },
    "shadows": {
      /* ... */
    },
    "radius": {
      /* ... */
    }
  }
}
```

---

### Phase 7: Component Mapping Documentation

**Goal:** Create a mapping file for future Code Connect setup or component library integration.

Create `component-mapping.json`:

```json
{
  "components": [
    {
      "figma_name": "Button/Primary",
      "code_name": "Button",
      "code_variant": "primary",
      "code_pattern": ".btn-primary",
      "props": [
        { "name": "size", "values": ["sm", "md", "lg"], "default": "md" },
        { "name": "disabled", "type": "boolean", "default": false },
        { "name": "icon", "type": "ReactNode", "default": null }
      ],
      "tailwind_classes": "px-4 py-2 bg-primary-500 text-white rounded-md font-medium hover:bg-primary-600 disabled:opacity-50",
      "code_connect_ready": false,
      "notes": "Primary action button, full width on mobile"
    },
    {
      "figma_name": "Button/Secondary",
      "code_name": "Button",
      "code_variant": "secondary",
      "code_pattern": ".btn-secondary",
      "props": [
        { "name": "size", "values": ["sm", "md", "lg"], "default": "md" },
        { "name": "disabled", "type": "boolean", "default": false }
      ],
      "tailwind_classes": "px-4 py-2 bg-gray-200 text-gray-900 rounded-md font-medium hover:bg-gray-300",
      "code_connect_ready": false
    },
    {
      "figma_name": "Card",
      "code_name": "Card",
      "code_variant": "default",
      "code_pattern": ".card",
      "props": [
        {
          "name": "variant",
          "values": ["default", "elevated"],
          "default": "default"
        }
      ],
      "tailwind_classes": "rounded-lg shadow-md p-4 bg-white",
      "code_connect_ready": false
    }
  ],
  "color_mappings": [
    { "figma": "Primary/500", "code": "primary-500", "value": "#0ea5e9" },
    { "figma": "Secondary/500", "code": "secondary-500", "value": "#ef4444" }
  ],
  "spacing_mappings": [
    { "figma": "Space/sm", "code": "space-sm", "value": "0.5rem" },
    { "figma": "Space/md", "code": "space-md", "value": "1rem" }
  ]
}
```

---

### Phase 8: Validation & Cross-Reference

**Goal:** Ensure design-to-code fidelity and catch errors early.

**Validation Checklist:**

- [ ] **Token Count**: All Figma variables extracted → matching count in JSON
- [ ] **Color Accuracy**: HEX values from Figma match output (use color picker)
- [ ] **Naming Consistency**: All tokens follow kebab-case convention
- [ ] **CSS Syntax**: Run `tailwind cli --build` without errors
- [ ] **Component Coverage**: All Figma components mapped (< 20 expected)
- [ ] **Class Coverage**: All base Tailwind utilities present
- [ ] **Dark Mode**: If used in Figma, variables extracted and mapped

**Testing Steps:**

1. **Color Fidelity Test**

   ```bash
   # Render Tailwind output and compare colors visually
   npx tailwindcss build -o output.css
   # Open in browser, compare HEX values
   ```

2. **Configuration Syntax Check**

   ```bash
   # Validate JS config
   node --check tailwind.config.js
   # Or validate CSS @theme if using CSS-first
   npx tailwindcss --check
   ```

3. **Token Completeness**

   ```bash
   # Count tokens in both sources (example for colors)
   jq '.colors | keys | length' design-tokens.json
   grep 'colors:' tailwind.config.js -A 50 | grep -c ":"
   ```

4. **Component Rendering Test**
   - Create a simple HTML prototype using extracted classes
   - Visually compare against Figma design
   - Verify spacing, colors, typography match

---

## Implementation Checklist

- [ ] **1. Structure Mapping**: Use `get_metadata` to understand Figma file
- [ ] **2. Extract Variables**: Call `get_variable_defs` for tokens
- [ ] **3. Extract Components**: Call `get_design_context` for each component
- [ ] **4. Process Outputs**: Normalize names, build mappings
- [ ] **5. Generate Config**: Create `tailwind.config.js` or `app/globals.css`
- [ ] **6. Validation**: Run syntax checks, color fidelity tests
- [ ] **7. Documentation**: Create `component-mapping.json` and naming guide
- [ ] **8. Code Connect Prep** (Optional): Set up mappings for future automation

---

## Tips & Best Practices

1. **Use `get_metadata` First**: Saves tokens by avoiding full context retrieval
2. **Batch Operations**: Extract tokens and components in parallel when possible
3. **Nested Color Scales**: For shadow, elevation tokens, use hierarchy (e.g., `colors.primary.50...900`)
4. **Component Variants**: Map Figma variants to Tailwind utility combinations (size + state + style)
5. **Documentation**: Keep `component-mapping.json` updated as design system evolves
6. **Dark Mode**: If using, extract dark mode tokens separately and merge with light mode
7. **Validation Early**: Test generated Tailwind config immediately to catch naming issues
8. **Version Control**: Commit all generated files (`tailwind.config.js`, JSON mappings, CSS styles)

---

## Troubleshooting

| Issue                                                    | Solution                                                       |
| -------------------------------------------------------- | -------------------------------------------------------------- |
| Variables not extracted                                  | Check node ID is correct; may be in a specific frame or board  |
| Color format mismatch (RGB vs HEX)                       | Normalize all to HEX in post-processing                        |
| Naming conventions conflict with Tailwind reserved words | Prefix tokens (e.g., `ds-primary` for "design system primary") |
| Components with no direct Tailwind mapping               | Document as "custom component pattern" in mapping              |
| Dark mode tokens missing                                 | Run separate `get_variable_defs` on dark mode variant          |
| `tailwind.config.js` validation fails                    | Check syntax: ensure proper nesting, no trailing commas        |
