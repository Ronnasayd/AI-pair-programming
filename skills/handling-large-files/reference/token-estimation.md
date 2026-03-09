# Token Estimation Strategies

## Quick Token Calculation

### Formula for English Text

```
Estimated tokens ≈ character_count / 4
or
Estimated tokens ≈ byte_count × 0.25
```

### Why This Works

- Average English token: ~4 characters
- Claude tokenizer: ~1.3 tokens per word
- Code: Slightly higher (1.5-1.7 tokens per word)

### Examples

```
File Size | Est. Tokens | Reading Time
----------|------------|-------------
10 KB     | ~2,500     | Very fast
50 KB     | ~12,500    | Fast
100 KB    | ~25,000    | Moderate
500 KB    | ~125,000   | Slow (risky)
1 MB      | ~250,000   | Very slow (avoid)
```

## Accurate Token Counting

### Using Python (if available)

```python
import os

def estimate_tokens(file_path):
    """Estimate tokens in a file."""
    size_bytes = os.path.getsize(file_path)
    # Rough estimate: 0.25 tokens per byte
    estimated_tokens = int(size_bytes * 0.25)
    return {
        'file': file_path,
        'bytes': size_bytes,
        'estimated_tokens': estimated_tokens,
        'readable_size': format_bytes(size_bytes),
        'recommendation': get_recommendation(estimated_tokens)
    }

def format_bytes(bytes_size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"

def get_recommendation(tokens):
    if tokens < 5000:
        return "✅ Safe - Read fully"
    elif tokens < 15000:
        return "⚠️  Consider - Use ranges"
    elif tokens < 50000:
        return "🔴 Large - Use search first"
    else:
        return "❌ Huge - Divide and conquer"
```

### Using Shell Commands

```bash
#!/bin/bash
# Estimate tokens for all files in current directory

for file in $(find . -type f); do
    bytes=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
    tokens=$((bytes / 4))
    echo "$file: $bytes bytes (~$tokens tokens)"
done | sort -t: -k2 -rn | head -20
```

## Language-Specific Adjustments

### Code Files

Code generally uses more tokens than plain text:

```
Language | Multiplier | Example (10KB)
----------|-----------|---------------
Python   | 1.3x      | ~3,300 tokens
JavaScript | 1.4x    | ~3,500 tokens
TypeScript | 1.4x    | ~3,500 tokens
Go       | 1.3x      | ~3,300 tokens
Java     | 1.5x      | ~3,750 tokens
SQL      | 1.2x      | ~3,000 tokens
HTML     | 1.2x      | ~3,000 tokens
Markdown | 1.1x      | ~2,750 tokens
```

### Content Type Impact

```
Type          | Token Density | Optimization Tip
--------------|--------------|-----------------
Code          | High (1.3-1.5x) | Skip comments/tests
Tests         | Very high (1.6x) | Read selectively
Comments      | Low (0.8x)      | Can be safely skipped
Whitespace    | None (0)        | Already minimal
Docs/README   | Medium (1.0x)   | Skim structure first
Logs/Errors   | High (1.4x)     | Grep specific patterns
data/JSON     | Very high (1.8x)| Read min. required
```

## Budget Planning

### Example: 30,000 Token Budget

```
Task breakdown:
- Context/setup: 2,000 tokens
- Initial search: 1,000 tokens
- Implementation: 18,000 tokens
- Validation/output: 5,000 tokens
- Buffer: 4,000 tokens

File reading budget: 18,000 tokens
Max readable file: ~72 KB (assuming code)
```

### Risk Assessment

```
Token % Used | Risk Level | Action
-------------|-----------|--------
0-70%        | ✅ Safe   | Proceed normally
70-85%       | ⚠️  Caution | Be selective with reads
85-95%       | 🔴 High   | Use only essential reads
95-100%      | ❌ Critical | Stop and handle differently
```

## Practical Measurement

### Verify Estimates

When working with actual tokens:

```
Actual tokens / Estimated tokens ratio:

Ratio < 1.0: Overestimated (good buffer)
Ratio 0.9-1.1: Accurate estimate
Ratio > 1.1: Underestimated (adjust future estimates)
```

### Adjust Multipliers

Track your own patterns:

```python
# Track what actually happened
actual_estimate_ratio = actual_tokens / estimated_tokens
language_multiplier = actual_estimate_ratio * 0.25

# Update for future estimates
print(f"Adjusted multiplier for Python: {language_multiplier}")
```

## Tools for Token Analysis

### VS Code Extensions

- **Token Counter**: Real-time token count for opened files
- **Claude Token Counter**: Specific to Claude's tokenizer

### Online Tools

- [Tokenizer Browser](https://platform.openai.com/tokenizer) - Close approximation
- [Claude Tokenizer](https://claude.ai/tokens) - Official (requires login)

### Script: Batch Analysis

```python
#!/usr/bin/env python3
import os
import sys
from pathlib import Path

def analyze_directory(directory, extensions=None):
    """Analyze token usage in directory."""
    if extensions is None:
        extensions = ['py', 'js', 'ts', 'go', 'java', 'md', 'txt']

    total_bytes = 0
    file_count = 0

    for file_path in Path(directory).rglob('*'):
        if file_path.suffix.lstrip('.') not in extensions:
            continue
        if file_path.is_file():
            size = file_path.stat().st_size
            total_bytes += size
            file_count += 1
            tokens = int(size * 0.25)
            print(f"{file_path}: {size:,} bytes (~{tokens:,} tokens)")

    total_tokens = int(total_bytes * 0.25)
    print(f"\nTotal: {file_count} files, {total_bytes:,} bytes (~{total_tokens:,} tokens)")

if __name__ == '__main__':
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    analyze_directory(directory)
```

## Estimation Confidence

Your estimates improve with experience:

```
After 10 files: ±30% accuracy
After 50 files: ±15% accuracy
After 100+ files: ±5% accuracy
```

Track your estimates vs. actual to calibrate.
