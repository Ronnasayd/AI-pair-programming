---
name: taskmaster-task-validator
description: Validate taskmaster tasks against requirements and ensure 100% coverage of all requisites. Use when you need to verify that created tasks fully address all requirements from a PRD or specification. Triggers on phrases like "validate my tasks", "check task coverage", "verify tasks against requirements", "validate task completeness", "ensure tasks meet requirements", or when assessing whether a task structure comprehensively addresses a given specification. This skill will analyze requirements in parallel using isolated subagents to validate different aspects (requirement coverage, task structure, dependencies, traceability, and test adequacy), generate a comprehensive gaps report, and after user approval, iteratively update and improve tasks and subtasks until they meet all parameters.
compatibility: Requires taskmaster CLI tools and access to .taskmaster/tasks.json and requirement documents (PRD, specification files).
---

# Task Validator

## Overview

This skill ensures that tasks created in taskmaster **completely satisfy all requirements** from a PRD or specification document. It performs multi-aspect validation using parallel subagent analysis, then guides you through iterative refinement until 100% coverage is achieved.

**When to use:**

- After generating tasks from a PRD and you want to verify completeness
- Before starting implementation, to ensure task structure addresses all requirements
- To audit existing task sets against current specifications
- To identify gaps, missing subtasks, or incomplete descriptions

## Validation Workflow

### Phase 1: Requirement Analysis

1. **Extract Requirements**: Parse the PRD or specification file to identify all explicit and implicit requirements
2. **Classify Requirements**: Categorize each requirement by type (functional, non-functional, technical, infrastructure, etc.)
3. **Index Requirements**: Create a traceability matrix mapping requirements to task IDs

### Phase 2: Multi-Aspect Parallel Validation

Using isolated subagents, validate tasks against 5 key aspects:

**Aspect 1 — Requirement Coverage**

- Does every requirement map to at least one task or subtask?
- Are implicit requirements captured?
- Are edge cases and constraints addressed?

**Aspect 2 — Task Structure**

- Do tasks have clear title, description, details, and test strategy?
- Is description and details aligned (minimal duplication)?
- Are all necessary technical parameters specified?

**Aspect 3 — Dependencies & Sequencing**

- Are dependencies correctly declared?
- Is execution order logically sound?
- Are implicit dependencies missing?

**Aspect 4 — Traceability**

- Can each task be traced back to a specific requirement?
- Is the mapping bidirectional (requirement → task, task → requirement)?
- Are there orphaned tasks (no requirement) or orphaned requirements (no task)?

**Aspect 5 — Test Adequacy**

- Does each task have a testStrategy defined?
- Are test strategies verifiable and executable?
- Do strategies cover acceptance criteria?

### Phase 3: Gaps Report

Generate a structured report containing:

```
# Task Validation Report

## Executive Summary
- Total Requirements: N
- Total Tasks/Subtasks: M
- Coverage Rate: X%
- Critical Gaps: K
- Status: ✓ COMPLETE | ✗ GAPS FOUND

## Requirement Coverage Matrix
| Requirement ID | Requirement Text | Task ID | Mapping Status | Notes |
|---|---|---|---|---|
| REQ-001 | [text] | TASK-1 | ✓ Covered | |
| REQ-002 | [text] | None | ✗ Missing | Action: Create subtask |

## Gaps Analysis
### Missing Requirements (not mapped to tasks)
- REQ-XXX: [description]
- REQ-YYY: [description]

### Incomplete Tasks (missing details, testStrategy, dependencies)
- TASK-3: Missing testStrategy
- TASK-5.2: Unclear success criteria

### Dependency Issues
- TASK-4 depends on TASK-6 (reverse order detected)
- TASK-8: Missing dependency on TASK-3

### Orphaned Tasks
- TASK-12: No requirement mapping (action: remove or clarify)

## Recommendations
1. Create new subtask for REQ-002
2. Update TASK-3 with explicit test strategy
3. Fix dependency order for TASK-4/6
```

### Phase 4: User Review & Approval

Present the gaps report to you. You can:

- **Approve as-is**: If coverage is 100% and you accept the gaps analysis
- **Suggest adjustments**: Provide context for orphaned tasks or feedback on categorization
- **Request modifications**: Point to specific gaps to address

### Phase 5: Iterative Task Refinement

Once approved, automatically:

1. **Create missing subtasks** for orphaned requirements
2. **Update incomplete tasks** with descriptions, test strategies, dependencies
3. **Reorganize task hierarchy** if needed for clarity
4. **Fix dependency chains** to ensure logical sequencing
5. **Revalidate** with subagents to confirm 100% coverage

Repeat until validation confirms "COMPLETE" with 0 critical gaps.

## Usage

### Basic Invocation

```
Validate my tasks against the requirements in [path-to-prd].md
```

### With Explicit Requirement File

```
Validate tasks/.taskmaster/tasks/tasks.json against requirements in docs/SPEC.md
```

### With Context

```
I created tasks for the Lingopass design system. Validate them against ACTION-PLAN.md requirements and report any gaps.
```

## Output Format

**During validation:**

- Console output showing parallel subagent progress
- Real-time gap findings by aspect

**Final deliverable:**

- Formatted gaps report (markdown or JSON)
- Updated .taskmaster/tasks/tasks.json with refinements
- Traceability matrix (CSV or JSON)
- Change summary: "3 new subtasks created, 5 tasks updated, 2 dependency chains fixed"

## Key Principles

1. **Isolation**: Each subagent operates independently to avoid bias
2. **Parallelism**: All 5 aspects validate simultaneously for speed
3. **Comprehensiveness**: Every requirement and every task is examined
4. **Auditability**: Traceability matrix makes all mappings explicit
5. **Iterative**: Gaps are refined incrementally, not in one large rewrite
6. **User-Controlled**: You approve before automated refinement occurs

## Definition of "Complete"

Tasks are considered complete and ready for implementation when:

- ✓ Coverage Rate = 100% (all requirements mapped)
- ✓ Zero orphaned requirements (every REQ has ≥1 task)
- ✓ Zero orphaned tasks (every task traces to ≥1 REQ, or is approved)
- ✓ All dependencies declared and logically ordered
- ✓ All tasks have: title, description, details, testStrategy, priority
- ✓ All subtasks have dependencies mapped
- ✓ Test strategies are verifiable and testable
- ✓ No implicit requirements left uncovered

## Examples

### Example 1: Basic Coverage Check

```
PRD: "Build a user authentication system with JWT, session refresh, 2FA, and audit logging"

Requirements extracted:
- REQ-001: Implement JWT authentication
- REQ-002: Implement session refresh mechanism
- REQ-003: Implement 2-factor authentication
- REQ-004: Log all auth events for audit compliance

Tasks submitted:
- TASK-1: Implement JWT tokens (with REQ-001, REQ-002)
- TASK-2: Add 2FA flow (with REQ-003)
- [Missing] TASK-X: Create audit logging system (REQ-004 uncovered)

Report: "1 critical gap: REQ-004 not mapped. Recommend new TASK-3 'Implement Audit Logging'."
```

### Example 2: Incomplete Task Refinement

```
Original TASK-5: "Setup database schema"
- Status: pending
- TestStrategy: (empty)

After refinement:
- Status: pending
- TestStrategy: "Verify schema migration runs without error; confirm all tables exist with correct column types and indexes"
- Details: Expanded with explicit table specs and migration framework choice
```

## Troubleshooting

**Issue**: "High orphaned task count"

- **Cause**: Tasks created outside of requirements (e.g., nice-to-haves)
- **Solution**: Clarify with user whether to: (a) add requirement for task, (b) defer task, or (c) remove task

**Issue**: "Circular dependencies detected"

- **Cause**: Task DAG has a cycle
- **Solution**: Identify cycle members and reorder or split circular tasks

**Issue**: "Vague requirement text not mapping to any task"

- **Cause**: Requirement poorly written or implicit
- **Solution**: Escalate to user for clarification; may need new requirement definition

## Next Steps After Validation

Once tasks pass complete validation (100% coverage, no critical gaps):

1. **Ready for Estimation**: Use `taskmaster estimate` to add time/complexity
2. **Ready for Execution**: Use `taskmaster next-task` to begin implementation
3. **Ready for Review**: Share validated task set with stakeholders
4. **Ready for Tracking**: Integrate with CI/CD to track progress

---

**Skill Version**: 1.0
**Last Updated**: 2026-03-22
**Maintained by**: Task Management Specialists
