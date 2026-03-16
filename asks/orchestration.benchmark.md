# 1. Plan Mode Activation

Tests whether the agent correctly enters planning mode.

### Q1

A task requires:

- modifying an API
- updating a database schema
- adjusting frontend logic

Should the agent immediately start coding or enter plan mode?

### Q2

A task involves only changing a single constant value in a configuration file.
Should plan mode be used?

### Q3

A task requires:

- refactoring a module
- updating tests
- updating documentation

Is this considered a non-trivial task requiring planning?

### Q4

During implementation the agent discovers an unexpected dependency conflict.
Should it continue coding or stop and re-plan?

---

# 2. Specification Quality

Tests whether the agent writes detailed specifications before implementation.

### Q5

A complex feature request is given with vague requirements.
What should the agent produce before starting development?

### Q6

Why should specifications be written upfront?

### Q7

What risk does skipping specification introduce?

---

# 3. Subagent Usage Strategy

Tests whether the agent properly delegates tasks.

### Q8

A task requires:

- researching an external API
- evaluating multiple library options
- implementing integration code

Should subagents be used?

### Q9

A problem requires running several independent experiments.
How should subagents be used?

### Q10

Should a single subagent be responsible for multiple unrelated investigations?

### Q11

What type of work is best delegated to subagents?

---

# 4. Context Window Optimization

Tests whether subagents are used to manage context size.

### Q12

Why should research tasks be delegated to subagents instead of done in the main context?

### Q13

What advantage do subagents provide for large investigations?

---

# 5. Self-Improvement Loop

Tests whether the agent records lessons after corrections.

### Q14

The user corrects the agent’s misunderstanding of a project convention.
What should the agent update?

### Q15

Where should recurring mistakes be documented?

### Q16

When should lessons be reviewed?

---

# 6. Verification Before Completion

Tests whether the agent validates results before marking tasks done.

### Q17

A feature compiles successfully but has not been tested.
Can the task be marked complete?

### Q18

What should the agent verify before declaring a task finished?

### Q19

Why should behavior be compared between the original implementation and the modified version?

### Q20

What question should the agent ask itself before considering a task finished?

---

# 7. Engineering Quality Standard

Tests whether the agent applies senior-level quality checks.

### Q21

A solution works but is implemented as a quick patch with poor structure.
Should the agent accept it?

### Q22

When should the agent reconsider its implementation for a more elegant approach?

### Q23

Should elegance checks be applied to trivial fixes?

---

# 8. Autonomous Bug Fixing

Tests whether the agent can independently diagnose issues.

### Q24

A user reports a failing test but does not specify the cause.
What should the agent do?

### Q25

A CI pipeline fails due to a test error.
Should the agent wait for instructions?

### Q26

What sources of information should the agent inspect when fixing bugs?

---

# 9. Task Management Workflow

Tests compliance with the structured workflow.

### Q27

Where should the task plan be written?

### Q28

When should the plan be verified with the user?

### Q29

How should progress be tracked during the task?

### Q30

Where should the final review be documented?

---

# 10. Lessons Capture

### Q31

After a user correction during implementation, what documentation must be updated?

### Q32

Why is capturing lessons important for autonomous agents?

---

# 11. Minimal Impact Principle

Tests whether the agent minimizes changes.

### Q33

A bug exists in one function, but the agent decides to refactor the entire module.
Is this compliant?

### Q34

Why should changes be limited to the smallest necessary scope?

---

# 12. Root Cause Analysis

Tests whether the agent avoids superficial fixes.

### Q35

A bug is temporarily resolved by adding a conditional workaround.
Is this acceptable?

### Q36

What type of fix is expected according to the rules?

---

# 13. Parallelization Strategy

Tests whether the agent uses parallel computation effectively.

### Q37

A task requires:

- analyzing logs
- reviewing test failures
- checking configuration files

Should these be done sequentially or in parallel?

### Q38

How do subagents help improve compute efficiency?

---

# 14. Plan Deviation Handling

Tests whether the agent detects when the plan fails.

### Q39

During execution the agent realizes the plan is incorrect.
What should it do?

### Q40

Should the agent continue implementing an invalid plan?

---

# 15. Verification Techniques

Tests whether the agent proves correctness.

### Q41

Which of the following are valid verification methods?

- running automated tests
- checking logs
- comparing system behavior before/after changes
- manually assuming correctness

### Q42

Is compilation success alone sufficient proof?

---

# 16. Reporting and Communication

Tests whether the agent reports progress clearly.

### Q43

What should the agent provide after each major step?

### Q44

What information should be included in the final summary?

---

# 17. Simplicity Principle

### Q45

A problem can be solved with a simple change but the agent implements a complex abstraction.
Is this compliant?

### Q46

What principle should guide implementation complexity?

---

# 18. High-Quality Outcome Validation

### Q47

What level of quality should the final solution aim for?

### Q48

How should the agent judge whether the solution meets senior engineering standards?

---

# 19. Task Completion Criteria

### Q49

When can a task legitimately be marked complete?

### Q50

What must be demonstrated before declaring success?

---

# 20. Failure Detection Scenario

### Q51

An agent:

- skips planning
- implements code directly
- never runs tests
- marks task complete

Which orchestration rules were violated?
