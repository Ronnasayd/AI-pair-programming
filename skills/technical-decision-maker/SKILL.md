---
name: technical-decision-maker
description: Helps make informed technical decisions by presenting viable options with pros/cons analysis, context searches, and decomposition of complex problems into smaller sub-problems.
argument-hint: Describe the technical problem or question, project context, constraints, and any relevant information about previously considered alternatives.
---

# Technical Decision Maker

## Purpose

Help developers make informed technical decisions through:

- Structured identification of viable options
- Clear analysis of pros and cons for each option
- Context search (web, documentation, community)
- Decomposition of complex problems into sub-problems
- Recommendations based on technical analysis

## Workflow

### Phase 1: Understand the Problem

1. **Gather context**:
   - What decision needs to be made?
   - What is the specific problem to solve?
   - Constraints (performance, cost, time, compatibility)?
   - Current technologies/stack?
   - Non-functional requirements?

2. **Identify complexity**:
   - If problem is complex → decompose into 2-3 smaller sub-problems
   - Solve sub-problems independently
   - Integrate solutions at the end

### Phase 2: Search for Context

1. **Information research**:
   - If specific technologies are mentioned → search official documentation
   - If decision involves multiple options → search comparisons
   - If problem is new → search current patterns/practices in community
   - Use `fetch_webpage` for articles, documentation, benchmarks

2. **Check real examples**:
   - Open-source projects on GitHub using each option
   - Comparative studies or benchmarks
   - Experiences from companies/communities

### Phase 3: Present Options

For each viable option:

**Structured format**:

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

**Minimum 2-3 viable options** for meaningful comparison.

### Phase 4: Comparative Analysis

Create **comparison matrix** considering:

- **Implementation complexity** (low/medium/high)
- **Learning curve** for the team
- **Performance** (if relevant)
- **Long-term maintainability**
- **Available community/support**
- **Alignment** with current architecture
- **Cost** (time, resources, tools)
- **Technical risk**

### Phase 5: Recommendation

Present:

1. **Recommended option** with clear justification
2. **Implementation plan** (next steps)
3. **Success metrics** (how to validate decision)
4. **Viable alternative** (in case 1st option doesn't work)

## Usage Example

**Question**: "Should I use [lib A], [lib B], or [lib C] for state management in React?"

**Workflow**:

1. Search docs/comparisons for each lib
2. Present 3 options with pros/cons
3. Compare against project requirements
4. Recommend + next steps

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

## When to Use This Skill

✅ **Use for**:

- Choosing between 2+ technologies/architectures
- Deciding whether to implement feature internally or use external lib
- Evaluating trade-offs of different approaches
- Planning migrations/refactors
- Choosing pattern/approach for recurring problems

❌ **Don't use for**:

- Debugging specific code (use specialist agents)
- Tactical implementation (use developer-specialist)
- Problems that already have established patterns in the project

## Output Structure

```markdown
# Technical Analysis: [Decision]

## Problem

[Summary of problem in 2-3 lines]

## Context

[Constraints, requirements, current stack]

[If complex: sub-problems and solutions]

## Option 1: [Name]

[standard structure]

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

## Usage Tips

1. **Be specific in your question**: The more context provided, the better the analysis
2. **Mention constraints**: Budget, deadline, project size, team skill level
3. **Provide examples**: "In project X we did it this way..."
4. **If unsure**: Decompose - one big problem is N small problems
5. **Validate decisions**: Implement decision-maker as ongoing reflection, not one-time
