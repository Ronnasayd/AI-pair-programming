---
name: figma-capture
description: Captures a screenshot and reference JSX code from a Figma node URL and saves both to `.figma/` as `<node-id>.png` and `<node-id>.jsx`. Use when the user says "captura esse nó do figma", "salva a imagem e o código de [url figma]", "usa o figma mcp para salvar [url]", "capture this figma node", or any variation requesting to save a Figma design locally. Do NOT use for generating new designs, syncing components, or code-connect mapping workflows.
metadata:
  author: Ronnasayd Machado - github.com/Ronnasayd
  version: "1.1.0"
---

# figma-capture

Captures a screenshot and JSX reference code from a Figma node and saves both to `.figma/`. `.figma/` is the output target — never place files elsewhere.

## Steps

| #   | Step                  | Action                                                                                                                                                                | Output / Gate                                                                            |
| --- | --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| 1   | Parse URL             | Extract `fileKey` (segment after `/design/`) and `nodeId` (`node-id=` param, `-`→`:`) from `https://www.figma.com/design/<fileKey>/<name>?node-id=<nodeId>`           | e.g. `fileKey=DMbeBBhuefhTTdJlXBK1S6`, API nodeId `248:11379`, filename form `248-11379` |
| 2   | Fetch context         | Call `mcp_figma_get_screenshot(fileKey, nodeId)` + `mcp_figma_get_design_context(fileKey, nodeId, clientFrameworks="unknown", clientLanguages="unknown")` in parallel | screenshot temp `image_url` + design XML                                                 |
| 3   | Download screenshot   | `mkdir -p .figma && curl -s -o .figma/<outName>.png "<image_url>"` immediately — URL expires in hours                                                                 | `.figma/<outName>.png`                                                                   |
| 4   | Handle oversized node | If context is sparse: identify first-level sublayer IDs from XML, call `get_design_context` on each, 2-3 in parallel; merge results, no need to cover deep sublayers  | merged design context                                                                    |
| 5   | Write JSX             | Build `.figma/<outName>.jsx` per [jsx-template.md](references/jsx-template.md)                                                                                        | `.figma/<outName>.jsx`                                                                   |
| 6   | Copy viewer           | `cp -n <skill_dir>/index.html .figma/index.html` (no-clobber — never overwrite existing)                                                                              | `.figma/index.html`                                                                      |
| 7   | Verify                | `ls -lh .figma/<outName>.* .figma/index.html`                                                                                                                         | confirm all 3 files exist, non-empty                                                     |

## Examples

**Standard**: URL with `node-id=248-11379` → parse → parallel fetch → download png → write jsx → copy viewer → verify. Result: `.figma/248-11379.png`, `.figma/248-11379.jsx`, `.figma/index.html`.

**Oversized root frame**: `get_design_context` returns sparse XML with sublayer IDs `248:1380`, `248:1381`, `248:1382` → fetch `1380`+`1381` in parallel, then `1382` → merge all three into one `.jsx`.

## Notes

- Image assets at `figma.com/api/mcp/asset/...` expire in ~7 days — note this in JSX header.
- Use `rtk` for terminal commands when available (e.g. `rtk ls -lh .figma/`); `curl` exempt (no verbose output).

## Reference files

- [jsx-template.md](references/jsx-template.md) — full JSX skeleton + content rules for Step 5.
