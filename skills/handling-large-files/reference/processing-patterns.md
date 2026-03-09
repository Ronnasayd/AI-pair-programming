# File Processing Patterns

## Pattern 1: Range Reading

**Use case**: Specific sections in large file

```
large_file.py (1000 lines, 250KB)
├─ Imports (1-50)
├─ Configuration (51-150)
├─ Main class (151-600)  ← Need this
├─ Utilities (601-900)
└─ Tests (901-1000)

Read: lines 151-600 only
Saves: ~60% tokens
```

**Implementation**:

```python
# Instead of reading entire file
# read_file("large_file.py", startLine=1, endLine=1000)

# Read only relevant section
read_file("large_file.py", startLine=151, endLine=600)
```

## Pattern 2: Search-First

**Use case**: Finding specific functionality

```
Goal: Understand authentication flow

1. semantic_search("authentication login flow")
   ↓
   Returns: auth.ts (lines 45-120), login.ts (lines 1-50)

2. read_file("auth.ts", startLine=45, endLine=120)
   read_file("login.ts", startLine=1, endLine=50)

Token savings: 80% (searched instead of guessing)
```

**When to use**:

- Don't know file organization
- Multiple files involved
- Looking for specific patterns
- Need understanding quickly

## Pattern 3: Divide and Conquer

**Use case**: Very large files (>500KB)

```
huge_file.js (1,000,000 bytes, ~250K tokens)

Split into 5 chunks:
1. Lines 1-100 (interface/exports)
2. Lines 101-5000 (core implementation)
3. Lines 5001-10000 (utilities)  ← You need this
4. Lines 10001-15000 (helpers)
5. Lines 15001+ (tests)

Read chunk 3 only, understand in isolation
Then reference other chunks if needed
```

**Benefits**:

- Process without overwhelming context
- Parallel reads of independent chunks
- Build understanding incrementally

## Pattern 4: Structural Browsing

**Use case**: Understanding codebase organization

```
Project: monorepo (complex structure)

1. List root: /
   ├─ packages/
   ├─ src/
   ├─ tests/
   └─ docs/

2. Read package.json (understand purpose)

3. List /src/
   ├─ components/
   ├─ utils/
   ├─ hooks/
   └─ types/

4. List specific directories as needed

Total tokens: ~2000 (vs 50000+ for full read)
```

**Implementation**:

```
1. list_dir("/home/project")
2. list_dir("/home/project/src")
3. read_file("/home/project/package.json")
4. For specific directories:
   - semantic_search("what does auth module do?")
   - Then read targeted files
```

## Pattern 5: Parallel Batch Reading

**Use case**: Multiple independent files

```
Need to review: config.yaml, main.py, test.py

Sequential (slow):
Read config.yaml ──→ Wait ──→ Read main.py ──→ Wait ──→ Read test.py
Time: 3x slower

Parallel (fast):
Read config.yaml ──┐
Read main.py ──────┼──→ Process all together
Read test.py ──────┘
Time: ~Same as single read
```

**Rules**:

- Execute when independent
- Sequence only when dependent
- Never parallelize > 5 files at once

## Pattern 6: Progressive Deepening

**Use case**: Gradually building understanding

```
Question: "How does this system handle user authentication?"

Level 1 (800 tokens):
- Read main component structure
- Look for authentication-related code

Level 2 (1500 tokens):
- Deep dive into auth module
- Check dependencies

Level 3 (2000 tokens):
- Review integration points
- Understand error handling

Stop when question answered
(usually after Level 1-2)
```

## Pattern 7: Context-Aware Filtering

**Use case**: Remove noise from large files

```
Messy file: 100KB with lots of comments and whitespace

Strategy: Extract meaningful parts
├─ Imports: Keep (needed for context)
├─ Type definitions: Keep (structure understanding)
├─ Comments: Remove (explains intent, can be omitted)
├─ Whitespace: Remove (already Minimal)
├─ Implementations: Keep (need to understand)
└─ Tests: Skip (read separately if needed)

Result: ~30KB of actual content
Token savings: 70%
```

## Pattern 8: Summary-Driven Reading

**Use case**: When reading is unavoidable

```
Large file must be read (250KB)

1. Read file
2. Summarize key points:
   - Main functions/classes
   - Key algorithms
   - Important constants
   - Error handling

3. For deep questions, re-read specific sections
   (but use summary to jump to right place)
```

## Anti-Pattern: Sequential Large Reads

❌ **Bad**:

```
read_file(file1.ts)  # 100KB, ~25K tokens
wait...
read_file(file2.ts)  # 100KB, ~25K tokens
wait...
read_file(file3.ts)  # 100KB, ~25K tokens

Total: 75K tokens, slow execution
```

✅ **Good**:

```
Parallel:
  read_file(file1.ts)
  read_file(file2.ts)
  read_file(file3.ts)

Total: 75K tokens, fast execution
Process all together
```

## Anti-Pattern: Blind Full Reads

❌ **Bad**:

```
"Read this file to understand it"
read_file(mysterious_file.ts, 1, 10000)

Result: 25K tokens spent, still confused
```

✅ **Good**:

```
semantic_search("purpose of mysterious_file")
↓ Get understanding
read_file(mysterious_file.ts, relevant_lines)

Result: 5K tokens, clear understanding
```

## Pattern Selection Decision Tree

```
Facing a large file?
│
├─ Know exactly what you need?
│  ├─ YES → Use range reading (Pattern 1)
│  └─ NO → Continue...
│
├─ Know where to find it?
│  ├─ YES → Range reading (Pattern 1)
│  └─ NO → Search first (Pattern 2)
│
├─ File > 500KB?
│  ├─ YES → Divide and conquer (Pattern 3)
│  └─ NO → Continue...
│
├─ Understanding structure?
│  ├─ NO → Structural browsing (Pattern 4)
│  └─ YES → Continue...
│
├─ Multiple independent files?
│  ├─ YES → Parallel batch (Pattern 5)
│  └─ NO → Range reading (Pattern 1)
│
└─ Still reading large content?
   └─ Consider progressive deepening (Pattern 6)
```

## Token Cost Comparison

```
Task: "Review TypeScript component file (100KB)"

Pattern 1 - Range Reading:
└─ ~8K tokens (focused read)

Pattern 2 - Search First:
└─ ~12K tokens (search + read)

Pattern 4 - Structural Browsing:
└─ ~2K tokens (explore structure)
└─ ~5K tokens (read specific parts)
└─ Total: ~7K tokens

Pattern 3 - Divide & Conquer:
└─ ~8K tokens per chunk (read only needed chunks)

Most efficient: Pattern 4 (Structural) → Pattern 1 (Range)
Cost: ~7K → 8K tokens vs 25K+ (full read)
```
