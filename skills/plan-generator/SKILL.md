---
name: plan-generator
description: Generate structured plans for tasks and projects with automatic date-stamped file naming and persistent storage. Use when you need to create detailed action plans, project roadmaps, task breakdowns, or strategic plans with organized phases, timelines, and dependencies.
argument-hint: Describe the task, project, or objective for which you need a plan. Include scope, constraints, and desired output format.
---

## Overview

The Plan Generator skill creates comprehensive, structured plans for any task, project, or objective. It generates well-organized plans with clear phases, milestones, dependencies, and timelines, then automatically saves them to `docs/agents/plans/` with date-stamped filenames for easy tracking and retrieval.

## When to Use

- **Task planning**: Break down complex tasks into actionable steps with dependencies
- **Project planning**: Create roadmaps with phases, milestones, and timelines
- **Process design**: Document workflows, procedures, and implementations
- **Strategic planning**: Develop long-term plans with goals and checkpoints
- **Meeting planning**: Organize agendas and action items with ownership
- **Feature implementation**: Plan software features with technical phases
- **Research planning**: Structure investigation steps with deliverables

## Plan Structure

Generate plans with the following structure:

```markdown
# Plan: [Descriptive Title]

**Created:** DD/MM/YYYY
**Type:** [Task | Project | Process | Strategy | Other]
**Status:** In Progress | Draft | Ready for Review

## Overview

[Brief description of what the plan covers and why it matters]

## Objectives

- [ ] Primary objective 1
- [ ] Primary objective 2
- [ ] Primary objective 3

## Scope

**Included:**

- Item 1
- Item 2

**Excluded:**

- Item 1
- Item 2

## Phase 1: [Phase Name]

**Duration:** [Time estimate]
**Owner:** [Responsible party]
**Deliverables:**

- Deliverable 1
- Deliverable 2

**Tasks:**

- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

**Dependencies:** [Any dependencies from other phases]

## Phase 2: [Phase Name]

[Repeat structure above]

## Timeline

- **Phase 1**: Start - End
- **Phase 2**: Start - End
- **Completion**: Target date

## Success Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Resources Required

- [Resource type]: Description
- [Resource type]: Description

## Risks & Mitigation

| Risk   | Impact          | Mitigation          |
| ------ | --------------- | ------------------- |
| Risk 1 | High/Medium/Low | Mitigation strategy |
| Risk 2 | High/Medium/Low | Mitigation strategy |

## Dependencies & Constraints

- Dependency 1: Description
- Constraint 1: Description

## Checkpoints & Reviews

- [ ] Checkpoint 1 (Date)
- [ ] Checkpoint 2 (Date)
- [ ] Final Review (Date)

## Notes

[Additional context, assumptions, or important information]
```

## Instructions

1. **Understand the Request**: Analyze the task, project, or objective requiring a plan
2. **Identify Scope**: Clarify what's included, excluded, and any constraints
3. **Define Phases**: Break the work into logical phases with clear boundaries
4. **Set Dependencies**: Identify which phases depend on others and critical path items
5. **Estimate Timelines**: Provide realistic duration estimates for each phase
6. **Assign Ownership**: Identify who owns each phase or major task
7. **List Deliverables**: Define what each phase produces
8. **Create Tasks**: Break phases into actionable, checkable tasks
9. **Define Success**: Establish clear, measurable success criteria
10. **Generate File**: Create markdown file with name format `dd-mm-yyyy-short-description.md`
    - `dd` = day (2 digits, zero-padded)
    - `mm` = month (2 digits, zero-padded)
    - `yyyy` = year (4 digits)
    - `short-description` = kebab-case description (3-5 words max)
    - Example: `16-03-2026-api-migration-plan.md`

## Output Format

Always save the generated plan to the specified location:

```
docs/agents/plans/dd-mm-yyyy-short-description.md
```

The plan should be:

- Clear and actionable
- Organized with checkboxes for tracking progress
- Time-bound with realistic estimates
- Risk-aware with mitigation strategies
- Owner-assigned with clear responsibilities
- Success-criteria-defined for completion validation

## Example Usage

**Input:**

```
Generate a plan for migrating a legacy authentication system to OAuth 2.0.
The system has 50+ services currently using basic auth. We need to maintain
backward compatibility during transition. Team size is 4 engineers, timeline
is 8 weeks.
```

**Output File:** `docs/agents/plans/16-03-2026-auth-oauth-migration.md`

```markdown
# Plan: Legacy Auth to OAuth 2.0 Migration

**Created:** 16/03/2026
**Type:** Project
**Status:** In Progress

## Overview

Migrate 50+ microservices from basic authentication to OAuth 2.0 while maintaining
backward compatibility. Timeline: 8 weeks with 4-engineer team.

## Objectives

- [ ] Design OAuth 2.0 architecture for microservices
- [ ] Implement OAuth 2.0 provider and token service
- [ ] Migrate all services with zero downtime
- [ ] Enable both auth methods during transition
- [ ] Deprecate basic auth after full transition

## Phase 1: Architecture & Design

**Duration:** 1 week
**Owner:** Tech Lead
**Deliverables:**

- OAuth 2.0 architecture document
- Service migration order priority list
- Token service design spec

...
```

## Tips

- **Phasing Strategy**: Group related services in migration waves rather than one-by-one
- **Communication**: Include stakeholder communication checkpoints in the plan
- **Testing**: Build in validation phases between major milestones
- **Flexibility**: Mark which phases could run in parallel vs. sequentially
- **Rollback**: Include rollback procedures for critical phases
- **Documentation**: Each phase should document what was learned and any changes

## Notes

- Plans are automatically dated, making them easy to track versions
- Use checkboxes to monitor real-time progress as work unfolds
- Review and update plans at each checkpoint
- Store related plans together by using consistent naming conventions
- Archive old plans while keeping them accessible for historical reference
