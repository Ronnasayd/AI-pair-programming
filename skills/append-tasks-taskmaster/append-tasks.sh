export TASK_TAG="$2"
export TASK_PROMPT="<spec_description>\n$(cat $1)\n</spec_description>\n<extreme_programming_workflow>
# Extreme Programming Execution Workflow

## 1. Understand the Problem
- Read the specification carefully until the goal is completely clear.
- Inspect relevant source files and modules involved in the change.
- Check all *.md documentation files for architectural guidelines and conventions.
- Identify dependencies, side effects, and impacted modules.

## 2. Define the Smallest Deliverable
- Break the work into the smallest possible vertical slice.
- Each slice must produce a working, testable result.
- Ensure the slice is backward compatible with existing system flows.

## 3. Test First (TDD)
Before implementing any feature:
- Write failing tests that describe the expected behavior.
- Cover:
  - Happy paths
  - Edge cases
  - Error conditions
- Reference relevant files using code references (file#L123-L456).

## 4. Implement the Simplest Solution
- Implement only the minimum code required to make the tests pass.
- Avoid premature abstractions.
- Follow existing architectural conventions.

## 5. Run Full Test Suite
- Ensure new tests pass.
- Ensure all existing tests pass.
- Validate that no regressions were introduced.

## 6. Refactor Safely
- Improve code structure while keeping tests green.
- Remove duplication.
- Improve naming and readability.
- Ensure architecture consistency.

## 7. Documentation and References
When relevant:
- Update or create documentation in *.md files.
- Reference related files, modules, and links useful for future maintenance.

## 8. Code Review Checklist
Verify that:
- Tests cover the new behavior.
- Implementation is minimal and clear.
- No unrelated changes were introduced.
- Architecture and coding standards are respected.

## 9. Final Validation
- Run the full test suite again.
- Confirm backward compatibility.
- Confirm that the feature integrates correctly with the rest of the system.

</extreme_programming_workflow>"

task-master parse-prd --research --prompt="$TASK_PROMPT" --append --tag="$TASK_TAG"
task-master analyze-complexity
task-master expand --all --research --prompt="$TASK_PROMPT"
