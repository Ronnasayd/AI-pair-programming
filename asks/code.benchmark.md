# 1. Context Compliance (Code vs Review Separation)

### Q1

A user asks:
“Analyze this code and list potential improvements.”
Should the agent generate new code or only perform analysis?

### Q2

A request says:
“Check whether this function has security issues.”
Is the agent allowed to rewrite the function?

### Q3

A user asks:
“Generate a secure API endpoint for user login.”
Does this instruction file apply?

### Q4

A task asks to inspect a diff and evaluate quality.
Should code generation rules be applied?

---

# 2. Clarification Requirements

Tests whether the agent detects ambiguity before coding.

### Q5

A user asks:
“Create a service to process files.”
No language, architecture, or file type is specified.
What should the agent do?

### Q6

A user asks:
“Implement authentication.”
No authentication method is specified.
Should the agent choose one automatically?

### Q7

A task conflicts with project architecture guidelines.
Should the agent implement anyway or ask for clarification?

---

# 3. Production-Quality Code Expectations

### Q8

A generated function works but contains no error handling.
Is this compliant with the rules?

### Q9

A code example works but uses deprecated APIs.
Does this violate the rules?

### Q10

The agent generates code that works but ignores project naming conventions.
Is this acceptable?

### Q11

The agent implements functionality but ignores performance implications.
Does this violate the rules?

---

# 4. Naming and Readability

### Q12

Which identifier is acceptable according to the rules?

```
a) doStuff()
b) processUserRegistration()
c) x1()
```

### Q13

A variable name is `temp`.
Is this acceptable for production code?

### Q14

A function has a clear purpose but a vague name.
Should the agent refactor the name?

---

# 5. Commenting and Documentation

### Q15

A complex algorithm is implemented without comments.
Is this compliant?

### Q16

Should comments explain architectural decisions when relevant?

### Q17

Should comments contain slang or informal language?

---

# 6. Error Handling

### Q18

A function reads a file but does not handle file-system errors.
Is this compliant?

### Q19

A network call assumes success and ignores failures.
Does this violate the rules?

### Q20

Is catching `Exception` without explanation recommended?

---

# 7. Security Practices

### Q21

User input is used directly in a SQL query.
Does this violate the rules?

### Q22

An API endpoint lacks authentication checks.
Is this acceptable?

### Q23

A cryptographic function uses a deprecated algorithm.
Does this violate the rules?

---

# 8. Code Structure and Architecture

### Q24

A single function handles:

- validation
- database logic
- formatting
- logging

Is this compliant?

### Q25

A module directly accesses private members of another class.
Does this violate the rules?

### Q26

Two modules depend on each other creating a circular dependency.
Is this allowed?

---

# 9. Code Duplication and Reuse

### Q27

The agent copies the same logic across three files instead of extracting a utility function.
Does this violate the rules?

### Q28

Should stable libraries be preferred over custom implementations?

### Q29

When is reimplementing library functionality acceptable?

---

# 10. Testability and Validation

### Q30

A new feature is implemented without tests or validation examples.
Is this compliant?

### Q31

A function is tightly coupled to external systems and cannot be unit tested.
Does this violate the rules?

### Q32

When should usage examples be included?

---

# 11. Backend-Specific Expectations

### Q33

An API endpoint accepts user input but performs no validation.
Is this acceptable?

### Q34

A database query is executed inside a loop causing heavy load.
Does this violate the performance guidelines?

### Q35

Sensitive data is logged in plaintext.
Does this violate security principles?

---

# 12. Frontend-Specific Expectations

### Q36

A UI component works on desktop but breaks on mobile.
Is this compliant?

### Q37

A component ignores accessibility attributes (ARIA/WCAG).
Does this violate the rules?

### Q38

A feature works only in one browser.
Is this acceptable?

---

# 13. Dependency and Imports

### Q39

A module imports dependencies inside a function without justification.
Is this allowed?

### Q40

A file imports unused libraries.
Is this acceptable?

---

# 14. Magic Values and Constants

### Q41

The code contains `if (status == 3)` without explanation.
Does this violate the rules?

### Q42

Should named constants be used instead of magic values?

---

# 15. Dead Code and Maintenance

### Q43

A file contains commented-out legacy code.
Is this compliant?

### Q44

Unused variables remain in the code after refactoring.
Does this violate the rules?

---

# 16. Configuration and Environment

### Q45

A database password is hardcoded in the source code.
Is this acceptable?

### Q46

Absolute paths are used in production code.
Does this violate the rules?

---

# 17. Workflow for Significant Code Changes

### Q47

Before implementing a large feature, what must the agent do first?

### Q48

Should the agent immediately apply large code changes without confirmation?

### Q49

What must be shown before applying significant changes?

### Q50

After applying changes, what should the agent provide?

---

# 18. Agent Delegation

### Q51

A task involves database design, API logic, and UI work.
Should specialized agents be used?

### Q52

When should the agent delegate work to specialists?

---

# 19. Backward Compatibility

### Q53

A new version breaks existing API clients without warning.
Is this compliant?

### Q54

If backward compatibility must be broken, what must be provided?

---

# 20. Performance and Critical Paths

### Q55

A function repeatedly performs expensive operations inside loops.
Does this violate the rules?

### Q56

Should performance be evaluated in critical paths?

---

# 21. Plan-Before-Implementation Enforcement

### Q57

A large feature request arrives.
What sequence should the agent follow?

### Q58

Should the agent generate full code immediately?

---

# 22. Confirmation Gates

### Q59

When should explicit user confirmation be required?

### Q60

If the user provides feedback on the proposed plan, what should the agent do?
