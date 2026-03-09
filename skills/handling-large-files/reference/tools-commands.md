# Tools, Commands, and Quick Reference

## AI Agent Tools

### For File Analysis

| Tool              | Purpose                    | Best For               | Token Cost       |
| ----------------- | -------------------------- | ---------------------- | ---------------- |
| `file_search`     | Find files by glob pattern | Locating files         | ~500 tokens      |
| `semantic_search` | Find code by meaning       | Understanding concepts | 1-5K tokens      |
| `grep_search`     | Find by exact pattern      | Precise matching       | 1-3K tokens      |
| `read_file`       | Read file content          | Detailed analysis      | Variable (5-25K) |

### Read File Strategy

```
read_file(
    filePath="/path/to/file.ts",
    startLine=100,          # Read from line 100
    endLine=200             # To line 200 (101 lines)
)
```

**Token cost formula**:

```
tokens ≈ (endLine - startLine) * 4
Example: lines 100-200 (100 lines) ≈ 400 tokens
```

## Shell Commands

### File Size Analysis

```bash
# Single file
ls -lh file.ts                    # Show size
wc -c file.ts                     # Show bytes
stat -c%s file.ts                # Exact bytes (Linux)
stat -f%z file.ts                # Exact bytes (macOS)

# Multiple files
find . -type f -name "*.ts" -exec ls -lh {} \;  # With sizes
find . -type f | xargs wc -c | tail -1          # Total bytes

# Sorted by size (largest first)
find . -type f -exec ls -S {} \; | head -20
```

### Content Inspection

```bash
# Quick overview
head -50 file.ts          # First 50 lines
tail -50 file.ts          # Last 50 lines

# Find specific patterns
grep -n "function\|class" file.ts    # Find definitions
grep -c "import" file.ts             # Count occurrences

# Complex searching
grep -B5 -A5 "error" file.ts         # 5 lines before/after
grep -E "TODO|FIXME|XXX" file.ts     # All notices

# Count lines
wc -l file.ts                         # Total lines
grep -v "^$" file.ts | wc -l         # Non-empty lines
```

### Token Estimation

```bash
# Quick estimate (bash math)
size=$(stat -c%s file.ts 2>/dev/null || stat -f%z file.ts 2>/dev/null)
tokens=$((size / 4))
echo "$size bytes ≈ $tokens tokens"

# For all code files
find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.go" \) -exec sh -c '
  for file; do
    size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null)
    tokens=$((size / 4))
    echo "$file: $size bytes (~$tokens tokens)"
  done
' sh {} +
```

## Decision Matrix

### Which Tool to Use?

```
Goal: Find where function is defined
│
├─ Know the name? → grep_search("def function_name")
└─ Don't know location? → semantic_search("functionality")

Goal: Read file content
│
├─ Know what you need? → read_file(..., lines X-Y)
├─ Need everything? → read_file(..., 1, 10000)
└─ File > 100KB? → Search first, then read_file

Goal: Understand code organization
│
├─ Complex project? → file_search to list structure
├─ Specific directory? → list_dir(...) iteratively
└─ Looking for patterns? → grep_search("pattern")
```

## Real-World Examples

### Example 1: Find and Read Key Function

```bash
# Step 1: Search for function
grep -n "async authenticate" src/*.ts

# Output: src/auth.ts:45

# Step 2: Estimate tokens for that section
# Lines 40-100 = 60 lines ≈ 240 tokens

# Step 3: Use read_file
read_file("src/auth.ts", startLine=40, endLine=100)

# Total cost: ~500 tokens (vs 25K+ for whole files)
```

### Example 2: Analyze Large Log File

```bash
# File: app.log (50MB, 12.5M tokens!)

# Step 1: Find specific errors
grep "ERROR" app.log | head -50

# Step 2: Get line numbers
grep -n "OutOfMemory" app.log

# Step 3: Read only those sections
wc -l app.log                    # Total lines
# Read lines 1500-1600, 45000-45100, etc.

# Total cost: ~5K tokens (vs 12.5M!)
```

### Example 3: Review Pull Request Changes

```bash
# List modified files
git diff --name-only main

# For each file, estimate tokens
for file in $(git diff --name-only main); do
    size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null)
    tokens=$((size / 4))
    echo "$file: ~$tokens tokens"
done

# Priority: Read smallest files first
```

### Example 4: Understand Module Structure

```bash
# List all exported functions
grep -n "^export" module.ts

# Check imports
grep -n "^import" module.ts

# Find main class
grep -n "^export class" module.ts

# Then read relevant sections based on findings

# Total cost: ~1K tokens for structure
```

## Token-Saving Checklist

Use before every read:

```
[ ] Do I know exactly what I need to read?
    ├─ NO → Use semantic_search or grep_search first
    └─ YES → Continue

[ ] Have I estimated the token cost?
    ├─ Estimated > budget? → Use search + range reading
    └─ Within budget? → Continue

[ ] Can I read a range instead of full file?
    ├─ YES → Use startLine/endLine parameters
    └─ NO → Consider chunked reading

[ ] Is this file being read multiple times?
    ├─ YES → Cache results, reference instead of re-reading
    └─ NO → Proceed

[ ] Is documentation available?
    ├─ YES → Read doc instead of code
    └─ NO → Read code

[ ] Read decision:
    ├─ file_search → Find files quickly
    ├─ semantic_search → Understand concepts
    ├─ grep_search → Find exact matches
    └─ read_file → Read content (use carefully)
```

## Quick Reference Card

```
File Size          | Est. Tokens | Recommended Approach
-------------------|-------------|--------------------
< 10 KB            | < 2.5K      | Full read safe
10-50 KB           | 2.5-12.5K   | Range reading
50-100 KB          | 12.5-25K    | Search + read
100-500 KB         | 25-125K     | Search + targeted
> 500 KB           | > 125K      | Divide & conquer

Strategy Selection:
────────────────────────────────────
Know what you need → Range reading
Don't know → Search first
File huge → Divide and conquer
Many files → Parallel reads
Repeated reads → Cache results
```

## Environment Variables

For scripting:

```bash
# Set token budget
export TOKEN_BUDGET=15000

# Set file size warning threshold
export SIZE_WARNING_KB=100

# Set default search tool
export SEARCH_TOOL="semantic"  # or "grep"

# In script:
if [ $size_kb -gt $SIZE_WARNING_KB ]; then
    echo "⚠️ File > ${SIZE_WARNING_KB}KB, use search first"
fi
```

## Performance Tips

1. **Parallel reads** (when independent):

   ```bash
   # Faster
   read_file(file1) \
   read_file(file2) \
   read_file(file3)
   ```

2. **Chain read operations**:

   ```bash
   # Slower (sequential)
   read_file(file1)
   read_file(file2)
   ```

3. **Use tools before files**:

   ```bash
   # More efficient
   grep_search → read_file(range)

   # Less efficient
   read_file(entire_file)
   ```

4. **Cache when possible**:
   ```
   First analysis: read_file → understand
   Follow-up: reference previous → no re-read
   ```
