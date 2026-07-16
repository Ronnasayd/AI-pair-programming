# JSX reference file template

Write `.figma/<outName>.jsx` with this structure. Code does NOT need to be 100% faithful — readable reference, not production-ready.

```jsx
/**
 * FIGMA CAPTURE — REFERENCE ONLY
 * Node:    <nodeId with hyphens>
 * FileKey: <fileKey>
 * URL:     <original URL>
 * Captured: <date>
 * Fonts:   <list from design context>
 * Tokens:  <key design tokens>
 * ⚠ Image assets (figma.com/api/mcp/asset/...) expire in ~7 days.
 */

// --- Image / icon constants ---
const IMAGES = { ... };

// --- Reusable sub-components (pills, cells, rows, etc.) ---
const MySubComponent = ({ ... }) => { ... };

// --- Content data separated from structure ---
const DATA = [ ... ];

// --- Main component ---
export default function CapturedNode() {
  return ( ... );
}
```

Rules:

- Extract repeated elements into sub-components (pills, table rows, cards, etc.).
- Separate content data from layout structure.
- Use Tailwind classes to approximate spacing, colors, typography.
- If root frame >20 KB of code, prioritize first-level sublayers, simplify deeper ones.
