# Templates

## Question format (fallback, no interactive tool)

```
[Question text]

A) [Option A]
B) [Option B]
C) [Option C]
Z) Other — describe freely
```

Sequential letters, always end with Z) Other. Group multiple clarifications into one block.

## Interactive tool example (vscode_askQuestions)

```json
{
  "questions": [
    {
      "header": "use_case",
      "question": "Qual é o principal caso de uso?",
      "options": [
        { "label": "Web application" },
        { "label": "Mobile application" },
        { "label": "Backend/API" },
        { "label": "Data processing" }
      ]
    },
    {
      "header": "team_size",
      "question": "Qual é o tamanho do time?",
      "options": [
        { "label": "1-2 pessoas", "recommended": true },
        { "label": "3-5 pessoas" },
        { "label": "6-10 pessoas" },
        { "label": "10+ pessoas" }
      ]
    }
  ]
}
```

## Option analysis block

```
## Option X: [Name/Technology]

### Description
[What is it, when to use]

### Pros
- ✅ Pro 1
- ✅ Pro 2
- ✅ Pro 3

### Cons
- ❌ Con 1
- ❌ Con 2
- ❌ Con 3

### Trade-offs
[What is sacrificed/gained with this choice]

### Project fit
[How it aligns with constraints and requirements]
```

Minimum 2-3 viable options required.

## Final output structure

```markdown
# Technical Analysis: [Decision]

## Problem

[Summary of problem in 2-3 lines]

## Context

[Constraints, requirements, current stack]
[If complex: sub-problems and solutions]

## Option 1: [Name]

[standard structure — see Option analysis block above]

## Option 2: [Name]

[standard structure]

## Option N: [Name]

[standard structure]

## Comparison Matrix

| Criterion | Option 1 | Option 2 | Option N |
| --------- | -------- | -------- | -------- |

## Recommendation

**[Option X]** because:

- Reason 1
- Reason 2

### Next Steps

1. [Action]
2. [Action]
3. [Action]

### Plan B

If [Option X] doesn't work → use [Option Y] because [...]
```

## Usage example

**Question**: "Should I use [lib A], [lib B], or [lib C] for state management in React?"

**Workflow**: search docs/comparisons for each lib → present 3 options with pros/cons → compare against project requirements → recommend + next steps.

**Expected output**:

```
## Analysis: State Management - React

### Context
- React app with 15+ components
- Real-time collaboration required
- Performance critical for mobile

### Option 1: Redux
[Description, pros, cons, fit]

### Option 2: Zustand
[Description, pros, cons, fit]

### Option 3: Jotai
[Description, pros, cons, fit]

### Recommendation
**Zustand** because: lightweight, low learning curve, excellent performance
Next steps: [...]
```
