---
name: test-coverage-review
description: "A skill for performing a deep analysis of test coverage for either a task specification (pre-implementation) or a completed task (post-implementation). Use this skill to identify missing scenarios, edge cases, and error paths, and to ensure that the testing strategy is robust and follows best practices."
argument-hint: "[target]: A string containing the task specification, a file path to a task spec, or a description of the implemented changes/tests to be analyzed."
---

MANDATORY: Use test-coverage-specialist agent
MANDATORY: execute the **$0** argument as the target for coverage analysis and follow the specialist's instructions.

Your objective is to provide a critical evaluation of the testing strategy or implemented tests, ensuring no behavioral gaps exist.

====================
PHASE 1 — CONTEXT GATHERING
====================

1. If the target is a **Task Specification**:
   - Analyze the proposed "Testing Strategy" section.
   - Cross-reference with the "Problem Summary" and "Proposed Action Plan" to identify all logic branches.
2. If the target is a **Completed Task**:
   - Locate the modified source files and their corresponding test files in the @workspace.
   - Analyze the implementation logic to map out all `if/else`, `switch`, and `try/catch` blocks.
   - Read the existing tests to see which scenarios are actually covered.

====================
PHASE 2 — COVERAGE ANALYSIS
====================

Evaluate the target against the following dimensions:

- **Happy Path**: Are the primary success flows covered?
- **Alternate Paths**: Are secondary success scenarios addressed?
- **Edge Cases**: Are boundary values, empty states, and null/undefined handled and tested?
- **Error Paths**: Are failures (API errors, timeouts, invalid inputs) tested?
- **Assertion Quality**: Do the tests actually verify the outcome, or just execute the code?

====================
PHASE 3 — REPORT GENERATION
====================

Generate a report and save it as:
`docs/agents/reviews/coverage/dd-MM-YYYY-<short-description>.md`

The report MUST follow this structure:

<format>

# Test Coverage Review: <Task Title>

## Summary of Analysis

Brief overview of the current coverage state (e.g., "Good happy path coverage, but missing error handling tests").

## Identified Scenarios & Coverage Status

| Scenario Type | Description | Status | Missing/Improvement          |
| ------------- | ----------- | ------ | ---------------------------- |
| Happy Path    | ...         | [x]    | -                            |
| Edge Case     | ...         | [ ]    | Missing test for empty input |
| Error Path    | ...         | [ ]    | No test for 500 API error    |

## Critical Logic Branch Mapping

List key decision points in the code/spec and whether they have tests.

## Recommended Test Cases

Specific descriptions of tests that should be added.

| Level | Description | Inputs | Expected Output |
| ----- | ----------- | ------ | --------------- |
| Unit  | Handle null | null   | Throw error     |

## Best Practices & Quality Feedback

Feedback on AAA pattern, naming, mocking, and assertion precision.

</format>

====================
PHASE 4 — VERIFICATION
====================

Present the report to the user and ask for feedback.
If the analysis was on a **Task Specification**, suggest updating the spec with the recommended tests before proceeding with implementation.
