---
name: codebase-linguistic-analysis-to-csv-export
description: Identify all non-English text in a codebase (specifically Portuguese characters) and export findings to a structured CSV for translation/remediation workflows.
---

# Codebase Linguistic Analysis to CSV Export

## Objective

Identify all non-English text in a codebase (specifically Portuguese characters) and export findings to a structured CSV for translation/remediation workflows.

---

## Phase 1: Discovery & Analysis

### Step 1: Define Search Pattern

- Identify target language characteristics (e.g., accented characters for Portuguese: `á é í ó ú â ê ô ã õ ç`)
- Define regex pattern: `[áéíóúâêôãõç]` captures Portuguese-specific Unicode characters
- This pattern catches comments, strings, and identifiers containing Portuguese text

### Step 2: Scope File Types

- Restrict search to source code files: `*.ts`, `*.js`, `*.tsx`, `*.jsx`
- Exclude `node_modules/` and other dependency directories
- Search directory: `/src` (main source) or equivalent project structure

### Step 3: Execute Initial Search

- Run: `grep -rn "[áéíóúâêôãõç]" <source_dir> --include="*.ts" --include="*.js"`
- Flags:
  - `-r`: recursive search
  - `-n`: output line numbers
  - `--include`: filter by file extension
- Output: `file:line:content` format

### Step 4: Quantify Findings

- Count total matches: `grep -rn "[áéíóúâêôãõç]" <source_dir> | wc -l`
- Result: Total line count with Portuguese text
- Group by file: `cut -d: -f1 | sort | uniq -c | sort -rn`
- Result: Prioritized file list (highest count first)

---

## Phase 2: Categorization

### Step 5: Classify by Context

For each matched line, determine context:

- **Comment**: Lines matching `^\s*//` or `^\s*/\*` or `\*/`
- **String/Code**: Lines containing quoted strings or inline text
- **Generated**: Files known to be auto-generated (e.g., `api.d.ts` from OpenAPI)

Logic:

```
IF line contains "// " OR "/* " OR "*/" → type = "comment"
ELSE → type = "string/code"
```

### Step 6: Extract Line Details

For each match, capture:

1. **file**: Full path from repository root
2. **line_number**: Line number in file
3. **type**: Context classification (comment/string/code)
4. **portuguese_text**: Exact line content

---

## Phase 3: CSV Generation

### Step 7: Create CSV Header

```csv
file,line_number,type,portuguese_text
```

### Step 8: Build CSV Rows

For each grep result:

1. Parse: `file:line_number:content`
2. Escape: Replace `"` with `""` in content (CSV standard)
3. Quote: Wrap all fields in `"` to handle special characters
4. Format: `"file","line","type","content"`
5. Append to output

### Step 9: Write to File

- Destination: `<scratchpad>/portuguese_translation_table.csv`
- Format: UTF-8 with BOM support (if language requires)
- Validation: Ensure row count = grep result count + 1 (header)

### Step 10: Generate Summary

Create supplementary markdown with:

- File-by-file breakdown (sorted by match count)
- Sample rows per high-priority file
- Context for auto-generated vs. manual code
- Type distribution (comments vs. strings)

---

## Phase 4: Output & Validation

### Step 11: Validate CSV

- Row count check: `wc -l <csv_file>`
- Sample check: `head -n 20 <csv_file>`
- Encoding check: Confirm UTF-8 compatibility

### Step 12: Create Actionable Index

Sort findings by:

1. **By file** (descending line count) → identifies highest-effort files
2. **By type** (comments first, then strings) → guides translation strategy
3. **By auto-generated status** → flag files that regenerate from source

### Step 13: Document Strategy

For each category, recommend action:

- **Auto-generated files**: Translate source, not output
- **Service/util files**: High-value translation (impacts users)
- **Test files**: Medium priority (improves developer experience)
- **Error messages**: High priority (user-facing)

---

## Reusable Parameters

| Parameter          | Purpose                              | Example                   |
| ------------------ | ------------------------------------ | ------------------------- |
| `LANGUAGE_PATTERN` | Regex for target language characters | `[áéíóúâêôãõç]`           |
| `SOURCE_DIR`       | Root directory to search             | `/src`                    |
| `FILE_TYPES`       | Extensions to include                | `*.ts,*.js,*.tsx,*.jsx`   |
| `EXCLUDE_DIRS`     | Directories to skip                  | `node_modules,dist,build` |
| `OUTPUT_DIR`       | CSV destination                      | `<scratchpad>/`           |

---

## Success Criteria

✅ CSV generated with all matches
✅ Row count matches grep result count
✅ All fields properly escaped and quoted
✅ File paths are consistent (relative or absolute)
✅ Line numbers are accurate
✅ Summary markdown highlights priority files
✅ Auto-generated vs. manual code is flagged

---

## Example Workflow Command Sequence

```bash
# 1. Search & count
grep -rn "[áéíóúâêôãõç]" /src --include="*.ts" --include="*.js" > raw_results.txt
wc -l raw_results.txt  # Total findings

# 2. Aggregate by file
cut -d: -f1 raw_results.txt | sort | uniq -c | sort -rn

# 3. Generate CSV
echo 'file,line_number,type,portuguese_text' > output.csv
while IFS=: read -r file line_num text; do
  TYPE=$( [[ "$text" =~ "//" ]] && echo "comment" || echo "string" )
  TEXT_ESCAPED="${text//\"/\"\"}"
  echo "\"$file\",\"$line_num\",\"$TYPE\",\"$TEXT_ESCAPED\"" >> output.csv
done < raw_results.txt

# 4. Validate
wc -l output.csv
head -20 output.csv
```

---

## Notes for Future Reuse

- **Adapt pattern** for different languages (e.g., `[äöüß]` for German, `[àâäæèéêëôœ]` for French)
- **Scale filtering** for large codebases (grep is fast; piping to `sort | uniq` reduces duplicates)
- **Integrate with translation tools** by parsing CSV into CAT (Computer-Aided Translation) software
- **Track changes** by comparing baseline CSV to future runs (diff against previous exports)
