---
name: figma-capture
description: Captures a screenshot and reference JSX code from a Figma node URL and saves both to `.figma/` as `<node-id>.png` and `<node-id>.jsx`. Use when the user says "captura esse nó do figma", "salva a imagem e o código de [url figma]", "usa o figma mcp para salvar [url]", "capture this figma node", or any variation requesting to save a Figma design locally. Do NOT use for generating new designs, syncing components, or code-connect mapping workflows.
metadata:
  author: ronnas
  version: 1.0.0
  mcp-server: figma
license: CC-BY-4.0
---

# figma-capture

Captures a screenshot and JSX reference code from a Figma node and saves both to `.figma/`.

## Instructions

### Step 1: Parse the Figma URL

Extract `fileKey` and `nodeId` from the URL format:

```
https://www.figma.com/design/<fileKey>/<name>?node-id=<nodeId>
```

- `fileKey` → path segment immediately after `/design/`
- `nodeId` → value of `node-id=` query param, converting `-` to `:` for API calls
- Output filename uses the original `-` form (e.g., `248-11379.png`, `248-11379.jsx`)

Example:

```
URL:     https://www.figma.com/design/DMbeBBhuefhTTdJlXBK1S6/Ecossistema-V1?node-id=248-11379
fileKey: DMbeBBhuefhTTdJlXBK1S6
nodeId:  248:11379   (for API)
outName: 248-11379   (for filenames)
```

### Step 2: Call `get_screenshot` and `get_design_context` in parallel

Call both simultaneously:

```
mcp_figma_get_screenshot(fileKey=<fileKey>, nodeId=<nodeId>)
mcp_figma_get_design_context(fileKey=<fileKey>, nodeId=<nodeId>, clientFrameworks="unknown", clientLanguages="unknown")
```

### Step 3: Download the screenshot immediately

`get_screenshot` returns a temporary `image_url` that expires in a few hours. Save it right away:

```bash
mkdir -p .figma
curl -s -o .figma/<outName>.png "<image_url>"
```

### Step 4: Handle oversized `get_design_context` responses

If the node is too large, the MCP returns sparse metadata and instructs you to call sublayers. In that case:

1. Identify the main first-level sublayer node IDs from the returned XML.
2. Call `get_design_context` on each sublayer — **2 to 3 in parallel** to stay within context limits.
3. Merge the results. You do not need to cover all deep sublayers — capture the primary blocks.

### Step 5: Create `.figma/<outName>.jsx`

Write a clean, readable JSX reference file with this structure:

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

Rules for the JSX file:

- Code does NOT need to be 100% faithful — it is a **readable reference**, not production-ready code.
- Extract repeated elements into sub-components (pills, table rows, cards, etc.).
- Separate content data from layout structure.
- Use Tailwind classes to approximate spacing, colors, and typography.
- If a root frame is very large (>20 KB of code), prioritize first-level sublayers and simplify deeper ones.

### Step 6: Verify output

```bash
ls -lh .figma/<outName>.*
```

Confirm both files exist and are non-empty.

## Examples

### Example 1: Standard node capture

User says: "captura esse nó do figma: https://www.figma.com/design/DMbeBBhuefhTTdJlXBK1S6/Ecossistema-V1?node-id=248-11379"

1. Parse: `fileKey=DMbeBBhuefhTTdJlXBK1S6`, `nodeId=248:11379`, `outName=248-11379`
2. Call `get_screenshot` + `get_design_context` in parallel
3. `curl -s -o .figma/248-11379.png "<image_url>"`
4. Write `.figma/248-11379.jsx` with header, constants, sub-components, data, main component
5. `ls -lh .figma/248-11379.*` — confirm both files exist

Expected result:

```
.figma/248-11379.png   (screenshot)
.figma/248-11379.jsx   (JSX reference)
```

### Example 2: Oversized root frame

`get_design_context` returns sparse XML with sublayer IDs `248:1380`, `248:1381`, `248:1382`.

1. Call `get_design_context` for `248:1380` and `248:1381` in parallel
2. Call `get_design_context` for `248:1382`
3. Merge all three context blocks into a single `.jsx` file

## Notes

- Image assets at `figma.com/api/mcp/asset/...` expire in ~7 days. Always note this in the JSX header.
- Use `rtk` for terminal commands when available (e.g., `rtk ls -lh .figma/`). `curl` is exempt since it produces no verbose output.
- The `.figma/` directory is the output target — do not place files elsewhere.
