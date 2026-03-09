# Optimization Techniques

## Technique 1: Content Abstraction

### Goal

Reduce token consumption by reading abstracted representations instead of full content.

### Approach

**Before** (Full Content):

```typescript
// Read entire 200KB file
// 50,000 tokens used
class ComplexAuthModule {
  constructor(
    private passwordHasher: PasswordHasher,
    private sessionManager: SessionManager,
    // ... 50 more properties
  ) {}

  // 1000s of lines of implementation
}
```

**After** (Abstracted):

```typescript
// Read just the interface/class structure
class ComplexAuthModule {
  // Constructor with key dependencies
  // Main public methods:
  // - login(credentials): Promise<Session>
  // - logout(sessionId): Promise<void>
  // - validateToken(token): Promise<ValidationResult>
  // - refreshSession(sessionId): Promise<Session>
}

// Read implementation details only for specific methods
```

**Token savings**: 60-80%

### Implementation

```python
# Extract structure without full implementation
def extract_structure(code_content):
    """Keep structure, remove implementation details."""
    lines = []
    in_implementation = False

    for line in code_content.split('\n'):
        # Keep: imports, class/function signatures, comments
        if line.strip().startswith((
            'import', 'from', 'class', 'def', 'function',
            'interface', 'type', 'export', '//', '/*', '#'
        )):
            lines.append(line)
        # Skip: function bodies, long implementations
        elif in_implementation:
            continue

    return '\n'.join(lines)
```

## Technique 2: Selective Line Range

### Goal

Calculate optimal line ranges to answer specific questions.

### Approach

```
Question: "How does error handling work?"
File size: 5000 lines, 500KB

1. Search for "error" or "catch"
2. Get locations: lines 234, 567, 890, 1023
3. Read context around each:
   - lines 220-250 (30 lines)
   - lines 550-600 (50 lines)
   - lines 875-925 (50 lines)
   - lines 1010-1050 (40 lines)

Total read: 170 lines (~4KB)
Tokens: 1000 (vs 125K for full file)
Savings: 99%
```

### Live Example

```python
def calculate_optimal_range(file_lines, search_term, context=50):
    """Find optimal lines to read around search matches."""
    matches = []

    # Find all occurrences
    for i, line in enumerate(file_lines, 1):
        if search_term.lower() in line.lower():
            matches.append(i)

    # Build optimal ranges
    ranges = []
    for match_line in matches:
        start = max(1, match_line - context)
        end = min(len(file_lines), match_line + context)
        ranges.append((start, end))

    # Merge overlapping ranges
    merged = merge_ranges(ranges)
    return merged

def merge_ranges(ranges):
    """Merge overlapping line ranges."""
    if not ranges:
        return []

    sorted_ranges = sorted(ranges)
    merged = [sorted_ranges[0]]

    for start, end in sorted_ranges[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end + 1:  # Overlapping or adjacent
            merged[-1] = (prev_start, max(end, prev_end))
        else:
            merged.append((start, end))

    return merged
```

## Technique 3: Language-Specific Compression

### Python

```python
# ❌ Verbose (more tokens)
def calculate_user_score(user):
    """
    Calculate the user's total score based on various factors.
    This is a comprehensive scoring system that considers
    multiple aspects of user engagement and activity.
    """
    engagement_score = calculate_engagement(user)
    activity_score = calculate_activity(user)
    quality_score = calculate_quality(user)

    total_score = (
        engagement_score * 0.4 +
        activity_score * 0.35 +
        quality_score * 0.25
    )

    return total_score

# ✅ Compressed (fewer tokens, same info)
def calculate_user_score(user):
    """Score = engagement(0.4) + activity(0.35) + quality(0.25)"""
    return (
        calculate_engagement(user) * 0.4 +
        calculate_activity(user) * 0.35 +
        calculate_quality(user) * 0.25
    )
```

### TypeScript

```typescript
// ❌ Verbose (more tokens)
interface UserProfile {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  createdAt: Date;
  updatedAt: Date;
  isActive: boolean;
  isPremium: boolean;
  subscriptionType: string;
}

// ✅ Compressed (key info)
interface UserProfile {
  name: { first: string; last: string };
  email: string;
  isActive: boolean;
  subscription: { isPremium: boolean; type: string };
  dates: { created: Date; updated: Date };
}
```

**Token savings**: 15-30%

## Technique 4: Comment Removal

### When Safe

```
Safe to remove:
✅ Descriptive comments (explain obvious code)
✅ Commented-out code (not needed)
✅ TODO comments (if not blocking understanding)

Keep:
❌ Why comments (explain non-obvious decisions)
❌ Algorithm comments (complex logic)
❌ Documentation comments
```

### Script

```python
def remove_non_essential_comments(code):
    """Remove verbose comments, keep essential ones."""
    lines = []

    for line in code.split('\n'):
        stripped = line.strip()

        # Skip obvious comment patterns
        if stripped.startswith('//'):
            if any(keyword in stripped for keyword in ['TODO', 'FIXME', 'XXX', 'NOTE']):
                lines.append(line)  # Keep
            elif len(stripped) < 80:
                lines.append(line)  # Keep short comments
            # Skip verbose comments
        elif '/*' in line or '*/' in line:
            # Keep doc comments /** */
            if '/*' in line and '*' in line:
                lines.append(line)
        else:
            lines.append(line)

    return '\n'.join(lines)
```

**Token savings**: 10-20% (use carefully)

## Technique 5: Context Caching Strategy

### Problem

Re-reading same file multiple times wastes tokens.

### Solution

Cache important findings locally:

```python
# In analysis session
context_cache = {
    "auth.ts": {
        "exports": ["authenticate", "logout", "verify"],
        "key_types": ["AuthToken", "UserSession"],
        "error_handling": "lines 234-250",
        "file_size": "150KB",
        "estimated_tokens": 37500,
        "read_count": 3,
    }
}

# Before reading again, check cache
if file in context_cache:
    cached = context_cache[file]
    if cached['read_count'] > 2:
        print(f"⚠️ Already read {cached['read_count']}x")
        # Reference previous findings instead of re-reading
```

**Token savings**: Up to 50% on multi-read scenarios

## Technique 6: Progressive Detail Levels

### Level 0: File Existence

```
bytes=$(stat -c%s file.ts 2>/dev/null)
estimated_tokens=$((bytes / 4))

→ Know: Is file big? Can I read it?
→ Cost: ~50 tokens
```

### Level 1: Structure

```
grep -E "^(class|function|interface|export)" file.ts

→ Know: What's defined in file?
→ Cost: ~200 tokens
```

### Level 2: Key Functions

```
read_file(file.ts, startLine=1, endLine=100)  # Imports & main
read_file(file.ts, startLine=500, endLine=600) # Key function

→ Know: How to use it?
→ Cost: ~5,000 tokens
```

### Level 3: Full Understanding

```
read_file(file.ts, 1, 10000)  # Entire file

→ Know: Everything
→ Cost: 25,000+ tokens
```

**Progressive approach**:

- Start at Level 0-1
- Only go deeper if needed
- Saves 80%+ of usual token consumption

## Technique 7: Batch Query Optimization

### Problem

Multiple questions about same file = multiple reads

### Solution

Ask all questions in one read cycle:

```
❌ Separate Questions (High Cost):
1. read_file(...) - "Where's the auth logic?"
2. read_file(...) - "How's error handled?"
3. read_file(...) - "What are the types?"
Total: 3 reads = 30K+ tokens

✅ Combined Question (Efficient):
1. read_file(...)
   Question: "Explain auth logic, error handling, and types"
   Answer all from single read
Total: 1 read = 10K tokens

Savings: 67%
```

## Technique 8: Format Optimization

### JSON Files

```json
// ❌ Verbose
{
  "user": {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "address": {
      "street": "123 Main St",
      "city": "Boston",
      "state": "MA",
      "zipCode": "02101"
    }
  }
}

// ✅ Sample (read schema, not all instances)
{
  "user": { "firstName": "...", "email": "..." }
}

// Cost: Read 1 example instead of 1000
```

### Logs

```
❌ Full logs (100MB)
✅ Tail/grep specific errors
   grep "ERROR\|CRITICAL" app.log | head -50

Cost: 50 lines (1K tokens) vs full logs (25M tokens)
```

## Technique 9: External Documentation

### Use When Available

```
Instead of reading 500KB codebase:

1. Check if project has:
   └─ API documentation
   └─ Architecture guide
   └─ README with examples

2. Read these first (usually 10-20KB total)
   └─ Cost: 2-5K tokens

3. Read code only for specifics

Total: 7-10K tokens vs 150K+ for full codebase
```

## Technique 10: Chunked Summarization

For unavoidable large reads:

```
1. Read chunk (e.g., 100 lines)
2. Summarize: "Main points: A, B, C"
3. Move to next chunk
4. Build complete picture from summaries
5. Only re-read chunks for details

Advantage:
- Process without context overwhelm
- Identify important sections
- Parallel chunk processing possible
```

## Quick Optimization Checklist

Before reading a file:

- [ ] Can I use search tools first?
- [ ] Do I know the line range needed?
- [ ] Is documentation available instead?
- [ ] How many times will this file be read?
- [ ] Can I read a summary instead?
- [ ] Are there imports/types only needed?
- [ ] Can I process this in chunks?
- [ ] What's my actual token budget vs estimated cost?

Use to reduce token consumption by 50-95%.
