# JSX preview template for non-JSX reference code

Only needed when the user's reference code is NOT already a standalone JSX/TSX component (Step 2 of SKILL.md). Write `.figma/<name>.jsx` with this structure — a faithful visual approximation, not production-ready.

```jsx
/**
 * LOCAL REFERENCE CAPTURE — PREVIEW ONLY
 * Name:     <name>
 * Source:   <original language/framework, e.g. "Vue SFC", "plain HTML/CSS", "Swift">
 * Original: <name>.original.<ext> (if a source file was preserved)
 * Captured: <date>
 * Fonts:    <comma-separated font family names, if identifiable from the original code>
 */

// Self-contained Google Fonts loader — index.html does NOT auto-load fonts,
// so any Google Fonts family used below must be pulled in here via @import.
const FontLoader = () => (
  <style>{`
    @import url('https://fonts.googleapis.com/css2?family=<Font+Name>:ital,wght@0,300;0,400;0,600;0,700;1,400&display=swap');
  `}</style>
);

// --- Reusable sub-components (translated from the original markup/structure) ---
const MySubComponent = ({ ... }) => { ... };

// --- Content data separated from structure ---
const DATA = [ ... ];

// --- Main component ---
export default function CapturedNode() {
  return (
    <div>
      <FontLoader />
      { /* translated markup, using Tailwind classes to approximate the original CSS */ }
    </div>
  );
}
```

Rules:

- Translate structure and styling as faithfully as possible from the original source — do not invent content or layout not present in the reference code.
- Use Tailwind classes to approximate the original's spacing, colors, typography, and layout.
- Extract repeated elements into sub-components.
- If the original uses fonts identifiable by name, add a `FontLoader` per Google Fonts family, same as above. Non-Google/proprietary fonts fall back to system font — note this in the `Fonts:` header if relevant.
- If the original source is large or complex, prioritize the top-level structure and simplify deeply nested pieces, noting the simplification in a comment.
