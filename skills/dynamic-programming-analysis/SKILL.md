---
name: dynamic-programming-analysis
description: >
  Use this skill whenever the user presents a problem, challenge, decision, or complex question
  that needs to be broken down into smaller, manageable sub-problems, just like dynamic programming
  in computer science. Triggers include: any problem that feels too big or overwhelming, strategic
  planning questions, optimization challenges (what is the best way to...), multi-step processes,
  decision trees, architectural designs, research questions, business or personal dilemmas, or any
  situation where the user says they do not know where to start. Always use this skill when
  decomposition, step-by-step reasoning, or structured problem-solving would help, even if the user
  does not mention dynamic programming explicitly. The goal is to model the DP mindset: identify
  base cases, define sub-problems, find overlapping structure, and build toward the solution
  bottom-up.
---

# Dynamic Programming Analysis

This skill transforms any complex problem into a structured analysis inspired by **dynamic programming**: break the larger problem into smaller sub-problems, identify dependencies, solve from the bottom up, and avoid redundant work.

---

## Core Philosophy

Dynamic Programming (DP) solves complex problems using two fundamental principles:

1. **Optimal Substructure** — the solution to the larger problem depends on the solutions to smaller sub-problems.
2. **Overlapping Sub-problems** — sub-problems recur; by identifying them, we avoid repeated work (memoization).

Apply this logic to _any_ domain: business, personal decisions, software architecture, research, learning, and projects.

---

## Analysis Protocol

When presented with a problem, always follow this pipeline:

### 1. 🎯 Define the Main Problem

- Restate the problem precisely: what exactly needs to be solved?
- Identify the desired **final state** (what does "solved" look like?)
- Identify explicit and implicit **constraints**

### 2. 🧩 Decompose into Sub-problems

- Break the problem into smaller, independent (or nearly independent) parts
- For each sub-problem, ask: "Can this problem be broken down further?"
- Continue until reaching the **base cases** — simple problems with direct solutions

**Output Format:**

```text
Main Problem
├── Sub-problem A
│   ├── Sub-problem A.1 (base case)
│   └── Sub-problem A.2
│       ├── Sub-problem A.2.1 (base case)
│       └── Sub-problem A.2.2 (base case)
└── Sub-problem B
    ├── Sub-problem B.1 (base case)
    └── Sub-problem B.2 (base case)
```

### 3. 🔁 Identify Overlaps (Memoization)

- Which sub-problems appear in multiple branches?
- Which partial solutions can be **reused**?
- Which insights, once discovered, eliminate repeated effort?

Mark these explicitly — they represent the greatest efficiency gains.

### 4. ⬆️ Resolution Order (Bottom-Up)

- List the base cases first (lowest dependency)
- Order sub-problems by dependency: solve prerequisites before dependents
- Create a clear **execution sequence**

### 5. 🛠️ Solve Each Sub-problem

For each sub-problem (from smallest to largest):

- Present the direct solution or required reasoning
- If multiple options exist, compare them briefly
- Indicate which higher-level problem this solution supports

### 6. 🔗 Compose the Final Solution

- Combine the sub-problem solutions back into the original problem
- Show how the pieces fit together
- Validate: does the composed solution solve the original problem?

### 7. ✅ Verification and Edge Cases

- What could fail? (extreme cases, incorrect assumptions)
- Are there external dependencies outside your control?
- Is the solution optimal, or simply good enough?

---

## Standard Response Format

Use this template when responding:

```markdown
## 🧠 Dynamic Programming Analysis

### Main Problem

[precise definition]

### Sub-problem Tree

[hierarchical text/tree structure]

### Base Cases

[list of the simplest sub-problems and their direct solutions]

### Identified Overlaps

[repeated sub-problems and reusable solutions]

### Resolution Sequence (Bottom-Up)

[recommended order of execution]

### Composed Solution

[how the solutions combine to solve the original problem]

### Risks and Edge Cases

[what to watch for]
```

---

## Adaptations by Problem Type

### Decision Problems

- Sub-problem = each decision criterion
- Base case = verifiable facts, not opinions
- Overlap = criteria affecting multiple options
- Composition = decision table or matrix

### Planning / Project Problems

- Sub-problem = each deliverable or milestone
- Base case = atomic tasks (1 person, 1 day)
- Overlap = shared dependencies between phases
- Composition = schedule / roadmap

### Technical / Architecture Problems

- Sub-problem = each component or module
- Base case = primitive functions / services
- Overlap = utilities, libraries, reusable patterns
- Composition = integration diagram

### Learning Problems

- Sub-problem = each prerequisite concept
- Base case = knowledge requiring no prerequisites
- Overlap = fundamentals that unlock multiple topics
- Composition = ordered learning path

### Business / Strategy Problems

- Sub-problem = each strategic lever
- Base case = observable metrics and concrete actions
- Overlap = capabilities that support multiple strategies
- Composition = integrated strategic plan

---

## Quality Principles

- **Be granular enough**: a well-defined sub-problem has a clear answer.
- **Avoid pseudo-decomposition**: do not merely rename the original problem — break it down genuinely.
- **Name dependencies**: always make clear which sub-problem depends on which.
- **Prioritize bottom-up resolution**: solving larger problems before smaller ones leads to rework.
- **Highlight reuse**: when one partial solution supports another, state it explicitly.

---

## Quick Example

**Problem**: "How should I structure my career to transition into AI within 18 months?"

```text
Main Problem: Transition into AI within 18 months
├── Sub-problem A: What does the AI industry require?
│   ├── A.1: In-demand technical skills (base case)
│   └── A.2: In-demand non-technical skills (base case)
├── Sub-problem B: Where am I today?
│   ├── B.1: Inventory of current skills (base case)
│   └── B.2: Gap analysis vs. A (depends on A + B.1)
└── Sub-problem C: How do I close the gap in 18 months?
    ├── C.1: Available resources (time, money) (base case)
    ├── C.2: Study and practice plan (depends on B.2 + C.1)
    └── C.3: Networking and portfolio strategy (depends on C.2)

Overlap: Python fundamentals appear in A.1, B.1, and C.2 — solve once and reuse.
Bottom-Up Order: A.1 → A.2 → B.1 → B.2 → C.1 → C.2 → C.3
```
