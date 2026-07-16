# JSX reference file template

Write `.figma/<outName>.jsx` with this structure. Code does NOT need to be 100% faithful — readable reference, not production-ready.

```jsx
/**
 * FIGMA CAPTURE — REFERENCE ONLY
 * Node:    <nodeId with hyphens>
 * FileKey: <fileKey>
 * URL:     <original URL>
 * Captured: <date>
 * Fonts:   <comma-separated font family names, e.g. "Inter, Roboto Mono">
 * Tokens:  <key design tokens>
 */

// Self-contained Google Fonts loader — index.html does NOT auto-load fonts,
// so any Google Fonts family used below must be pulled in here via @import.
const FontLoader = () => (
  <style>{`
    @import url('https://fonts.googleapis.com/css2?family=<Font+Name>:ital,wght@0,300;0,400;0,600;0,700;1,400&display=swap');
  `}</style>
);

// --- Image / icon constants (local copies in .figma/assets/, downloaded in Step 5) ---
const IMAGES = { ... };

// --- Reusable sub-components (pills, cells, rows, etc.) ---
const MySubComponent = ({ ... }) => { ... };

// --- Content data separated from structure ---
const DATA = [ ... ];

// --- Main component ---
export default function CapturedNode() {
  return (
    <div>
      <FontLoader />
      { /* ... */ }
    </div>
  );
}
```

Rules:

- Extract repeated elements into sub-components (pills, table rows, cards, etc.).
- Separate content data from layout structure.
- Use Tailwind classes to approximate spacing, colors, typography.
- If root frame >20 KB of code, prioritize first-level sublayers, simplify deeper ones.
- `Fonts:` header comment must list real font family names (comma-separated) exactly as named in design context — for documentation only, `index.html` does NOT parse or auto-load it.
- For each font family available on Google Fonts, add a `FontLoader` component (as above) rendered once at the top of `CapturedNode`'s JSX, with the Google Fonts CSS2 URL built from that family name. This makes the `.jsx` self-contained — no edits to `index.html` needed.
- Fonts not on Google Fonts (proprietary/brand fonts, e.g. a custom display face) cannot be auto-loaded — leave them out of `FontLoader` and accept the system-font fallback; note this in the `Fonts:` header comment if relevant.
