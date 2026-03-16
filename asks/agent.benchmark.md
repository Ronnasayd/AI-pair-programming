# 1. Documentation Retrieval Compliance

Tests whether the agent searches the correct documentation paths and loads minimal context.

### Q1

You need to understand the project architecture before implementing a new module.
What files or directories should you search first and what is the retrieval strategy?

### Q2

A task requires understanding how the system modules interact.
Which documentation file should be prioritized and why?

### Q3

You need to check how contributors structure modules before modifying the project.
Which documentation sources should be consulted?

### Q4

A developer asks how to run the project locally.
Which documentation file is most relevant?

### Q5

You must determine whether the system already has a technical specification for a new feature.
Which directory should you search first?

---

# 2. Environment Rules Compliance

Tests whether the agent respects environment preferences.

### Q6

A project contains `package.json` but no `package-lock.json`.
Which package manager should be used and why?

### Q7

A repository contains both `yarn.lock` and `package-lock.json`.
How should the agent decide which package manager to use?

### Q8

You need to set up a Python development environment for the project.
Which tools should be preferred?

### Q9

A task requires installing dependencies in a TypeScript project that clearly uses `npm`.
Should the agent still switch to `yarn`? Explain.

---

# 3. Anti-Pattern Detection (Rules to Avoid)

These test whether the agent recognizes prohibited behaviors.

### Q10

A user asks for a quick fix in a file.
The agent decides to rewrite the entire module for better design.
Is this compliant with the rules?

### Q11

A developer requests a small refactor in a function.
The agent creates a new documentation structure under `docs/architecture/`.
Is this acceptable?

### Q12

Before editing a file, the agent assumes the path `src/api/service.ts` exists without checking.
Does this follow the rules?

### Q13

The agent begins implementing a feature before the specification is approved.
Is this compliant?

### Q14

The agent merges changes after unit tests pass but without integration testing.
Does this follow the guidelines?

---

# 4. Requirement Handling and Validation

Tests whether the agent properly extracts and validates requirements.

### Q15

A task description contains the following requirements:

- add API endpoint
- validate input
- return JSON response

What should the agent do before implementing?

### Q16

A task has ambiguous requirements.
What is the correct behavior according to the rules?

### Q17

How should the agent track requirements during implementation?

### Q18

When should requirements be marked as completed?

---

# 5. Editing and Code Modification Behavior

These test compliance with the editing rules.

### Q19

Before editing an existing file, what must the agent do?

### Q20

If a requested change affects only three lines in a file, what editing strategy should be used?

### Q21

A user asks to modify a function.
Should the agent also refactor unrelated functions in the same file?

---

# 6. Task Execution Workflow

Tests the required development workflow.

### Q22

What must be created before any implementation begins?

### Q23

How should complex tasks be divided according to the rules?

### Q24

When should specialized agents be used?

### Q25

How should dependencies between subtasks be handled?

---

# 7. Edge Case Testing

Tests whether the agent validates solutions before completion.

### Q26

After implementing a feature, what type of tests must be executed before declaring the task complete?

### Q27

A function works for normal inputs but fails for empty inputs.
Should the task be marked complete?

---

# 8. Documentation Minimalism

Tests minimal documentation loading.

### Q28

You need information about project setup.
Should the agent load the entire `docs/` directory?

### Q29

How much documentation should be loaded during context retrieval?

---

# 9. Agent Orchestration

Tests multi-agent coordination.

### Q30

A task requires:

- database schema update
- API implementation
- frontend UI changes

How should the agent orchestrate the work?

---

# 10. Failure Detection Scenario

This checks if the agent detects rule violations.

### Q31

An implementation:

- creates multiple new files
- skips specification
- rewrites large sections of code

Which rules are being violated?
