---
description: Lessons learned from past mistakes, corrections, and feedback. This file is for self-improvement and continuous learning to avoid repeating the same errors in future tasks.
applyTo: "**/*"
---

## Mandatory: Avoid

- Over-Engineering in the First Iteration
- Creating Unsolicited Files (e.g., IMPLEMENTATION_SUMMARY.md, test files without explicit request)
- Ignoring or Misinterpreting Feedback
- Not Verifying Current Content Before Editing
- Creating Documentation Structure When Not Requested
- Mixing Concepts (Skill ≠ Agent ≠ Task; each has role distinct)
- Unnecessary Complexity in Logic
- Not Testing Requirements Against Results
- Rushing into implementation before specification is approved
- Merging code without full integration test validation
- Assuming file paths and locations without verification

## Mandatory: Follow

- List each requirement as a checklist
- Validate each requirement
- Make incremental adjustments based on feedback
- Never rewrite everything, only specific segments
- Always confirm current content before editing
- Create detailed specification BEFORE implementation (Phase 1: Context Discovery)
- Use agent orchestration to parallelize independent subtasks (e.g., T1.2 and T1.3 can run concurrently)
- Establish clear checkpoints/gates between phases (code review after T1.1, tests after T1.2+T1.3)
- Define dependencies between subtasks explicitly (T1.2 and T1.3 depend on T1.1)
- Use try-finally for guaranteed cleanup in async operations (always execute in critical paths)
- Test edge cases before marking task complete (UTF-8 multibyte, threshold boundaries, concurrent calls)
- Delegate specialized work to expert agents (developer-specialist, test-coverage-specialist, review-refactor-specialist)
- Verify file existence and line numbers in code references before making edits
- Keep functions focused and single-responsibility (helper vs cleanup vs integration)
