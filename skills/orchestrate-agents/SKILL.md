---
name: orchestrate-agents
description: "Analyze a task specification or taskmaster task and dynamically orchestrate work across available specialist agents. Updates specifications with agent recommendations and integrates with taskmaster to assign agents to subtasks."
argument-hint: "[spec_path_or_task_id]: Path to a specification file or taskmaster task ID. The skill analyzes the content and orchestrates agent assignments directly in the original file/task."
---

# Orchestrate Agents Skill

## Overview

This skill intelligently distributes work across available specialist agents by:

1. **Dynamically discovering** all available agents in `agents/` directory
2. **Analyzing specifications** (PRD, SRS, task specs) or **taskmaster tasks** for subtasks and requirements
3. **Mapping each subtask** to the most appropriate agent(s) based on domain expertise
4. **Updating the original content**:
   - For specifications: Adds agent recommendation sections directly to the spec file
   - For taskmaster: Updates each subtask with assigned agent information

## Key Principles

- **No extra files**: All changes integrate directly into existing specifications or taskmaster entries
- **Dynamic agent discovery**: Agents are discovered at runtime from `agents/` directory, not hardcoded
- **Intelligent matching**: Uses domain analysis, technical requirements, and agent descriptions to select best-fit agents
- **Preserves original structure**: Adds new sections without disrupting existing content

## Execution Flow

### Phase 1: Input Analysis

1. Determine if input is a **file path** or **taskmaster task ID**
2. Parse content to extract:
   - Main objective and scope
   - All subtasks/implementation steps
   - Technical requirements (languages, frameworks, domains)
   - Dependencies and constraints

### Phase 2: Dynamic Agent Discovery

1. Scan `agents/` directory for all `.agent.md` files
2. Extract agent names and descriptions from YAML frontmatter
3. Build expertise matrix based on agent names and descriptions:
   - Map agent name keywords to domain expertise
   - Identify primary and secondary specializations
   - Note supported tech stacks

### Phase 3: Subtask-to-Agent Mapping

For each subtask, evaluate available agents:

1. Score agents based on:
   - **Domain alignment**: Does agent name/description match subtask domain?
   - **Tech stack fit**: Do agent capabilities match required technologies?
   - **Specialization match**: Does agent's primary focus match subtask needs?
   - **Complementary expertise**: Can agent handle cross-cutting concerns?

2. Select:
   - **Primary agent**: Best overall fit for the subtask
   - **Support agents** (if applicable): For complex/multi-domain subtasks

3. Scoring criteria:
   - Domain match: 40% weight
   - Tech fit: 30% weight
   - Specialization: 20% weight
   - Complexity handling: 10% weight

### Phase 4: Integration with Original Content

#### For Specification Files

Add a new section after task overview:

```markdown
## Agent Orchestration

| Subtask   | Primary Agent | Support Agents             | Rationale                                                 |
| --------- | ------------- | -------------------------- | --------------------------------------------------------- |
| Subtask 1 | agent-name-1  | agent-name-2, agent-name-3 | Domain expertise in [area], proven experience with [tech] |
| Subtask 2 | agent-name-x  | agent-name-y               | Specializes in [area], handles [complexity] complexity    |
```

#### For TaskMaster Tasks

Update each subtask with agent assignment using taskmaster CLI:

```
mcp_taskmaster-ai_update_subtask --id=<subtask_id> --metadata="assigned_agents: [agent1, agent2]"
```

## Agent Domain Mapping

Agents are matched based on their specialization keywords:

- **-specialist**: Core domain expert
- **developer-specialist**: General implementation
- **planning/architect**: Design and analysis
- **security/cybersecurity**: Security concerns
- **database**: Data layer
- **testing/coverage**: Test strategy and coverage
- **documentation/docs**: Documentation and guides
- **frontend/refactor/figma**: Frontend and UI
- **ai/generative**: AI/ML features
- **git**: Version control and CI/CD
- **review/refactor**: Code quality and improvement
- **skill**: Framework and tooling

## Output Integration

**For files:** Adds Agent Orchestration section directly to specification

**For taskmaster:** Updates subtask metadata with `assigned_agents` field containing array of agent names

**Result:** Clear, trackable agent assignments directly in your working documents

---

## Executive Summary

[1-2 paragraph overview of the orchestration strategy, key decisions, and expected outcomes]

---

## 1. Subtask Assignment Matrix

| Subtask ID | Subtask Name | Primary Agent            | Support Agents             | Domain   | Complexity | Status  |
| ---------- | ------------ | ------------------------ | -------------------------- | -------- | ---------- | ------- |
| T1         | [Name]       | developer-specialist     | review-refactor-specialist | Backend  | High       | pending |
| T2         | [Name]       | documentation-specialist | doc-usability-specialist   | Docs     | Medium     | pending |
| T3         | [Name]       | cybersecurity-specialist | developer-specialist       | Security | Critical   | pending |

---

## 2. Detailed Agent Assignments

### Subtask T1: [Name]

**Primary Agent**: `developer-specialist`
**Support Agents**: `review-refactor-specialist`

**Rationale**:

- Domain expertise: Backend development, API implementation, core business logic
- Technology fit: [List matching technologies]
- Responsibility: Design and implement the [feature/component]

**Key Deliverables**:

- [Deliverable 1]
- [Deliverable 2]
- [Deliverable 3]

**Dependencies**:

- Requires completion of: [other subtasks]
- Blocks: [other subtasks]

**Success Criteria**:

- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] Code review passed by support agent

**Estimated Effort**: [Low/Medium/High]

---

(Repeat section above for each subtask)

---

## 3. Agent Utilization Summary

| Agent                    | Number of Assignments | Primary Role                          | Total Effort |
| ------------------------ | --------------------- | ------------------------------------- | ------------ |
| developer-specialist     | 5                     | Backend development, core features    | High         |
| documentation-specialist | 3                     | User/technical documentation          | Medium       |
| cybersecurity-specialist | 2                     | Security review, vulnerability fixes  | Critical     |
| test-coverage-specialist | 4                     | Testing strategy, coverage validation | Medium       |

---

## 4. Orchestration Strategy & Sequencing

### Phase 1: Foundation (Parallel execution possible)

- [Subtasks T1, T2 can execute in parallel - no dependencies]
- Agent: developer-specialist, documentation-specialist
- Timeline: Week 1

### Phase 2: Core Implementation (Sequential dependencies)

- [Subtasks T3, T4 depend on T1, T2 completion]
- Agent: developer-specialist, database-specialist
- Timeline: Week 2-3

### Phase 3: Integration & Quality (Parallel validation)

- [Subtasks T5, T6, T7 validate T3, T4]
- Agent: test-coverage-specialist, review-refactor-specialist
- Timeline: Week 3

### Phase 4: Documentation & Release (Final work)

- [Subtasks T8, T9 finalize documentation and deployment]
- Agent: documentation-specialist, git-specialist
- Timeline: Week 4

---

## 5. Risk & Dependency Analysis

### Critical Path

[List the sequence of subtasks that determines project completion time]

### Risk Factors

- **Technical Risk**: [Description] → Mitigation: [Agent + approach]
- **Dependency Risk**: [Description] → Mitigation: [How to parallelize or decouple]
- **Expertise Risk**: [Description] → Mitigation: [Support agent role]

### Cross-Agent Communication Points

- [ ] Developer-specialist ↔ database-specialist: Database schema review
- [ ] test-coverage-specialist ↔ developer-specialist: Test implementation handoff
- [ ] documentation-specialist ↔ developer-specialist: API documentation extraction

---

## 6. Success Criteria & Validation

**Project Success Indicators**:

- [ ] All subtasks completed by assigned agents
- [ ] Support agents' validation completed
- [ ] Dependencies satisfied in correct sequence
- [ ] Quality gates passed

**Agent Handoff Checklist** (for each subtask completion):

- [ ] Primary agent completed deliverables
- [ ] Support agent validation passed
- [ ] Test coverage met
- [ ] Documentation complete
- [ ] Ready for next phase

---

## 7. Notes & Assumptions

- [Key assumption 1]: [Impact and mitigation if false]
- [Key assumption 2]: [Impact and mitigation if false]
- [Constraint 1]: [How it affects orchestration]

---

(End of document)

====================
PHASE 5 — TASKMASTER INTEGRATION & UPDATE
====================

1. **Update Each Subtask in TaskMaster**
   - Use `task-master update-subtask <subtask_id>` or equivalent
   - Add agent assignment metadata to each subtask
   - Format: Include agent name, rationale, and dependencies in subtask metadata/notes

   Example metadata structure to add to each subtask:

   ```
   **Agent Assignment**:
   - Primary: [Agent Name]
   - Support: [Agent Name(s)]
   - Rationale: [Why this agent]
   - Dependencies: [Blocking/blocked by – subtask IDs]
   ```

2. **Create Agent Ledger**
   - Generate a file at `.taskmaster/agents/ALLOCATION.md` that documents:
     - Which agents are assigned to which subtasks
     - Expected timeline for each agent's work
     - Points of handoff between agents
     - Communication protocol

3. **Validation**
   - Verify all subtasks have been assigned
   - Confirm no critical subtask is orphaned
   - Validate dependency chain completeness

====================
PHASE 6 — FINAL VERIFICATION & REPORTING
====================

1. **Sanity Checks**
   - [ ] Every subtask has a primary agent assignment
   - [ ] All dependencies are recorded
   - [ ] Critical path identified
   - [ ] No circular dependencies
   - [ ] Risk factors documented

2. **Generate Final Summary Report**
   - Path: `.taskmaster/reports/orchestration-summary.md`
   - Include: Agent workload, timeline, critical decisions, next steps

3. **Output to User**
   - Present the orchestration plan in a clear, human-readable format
   - Highlight: Critical path, high-risk areas, key decisions
   - Provide next steps for execution

====================
EXECUTION WORKFLOW
====================

**If input is a task specification file (.taskmaster/specs/\*.md)**:

```bash
# 1. Load and analyze specification
export SPEC_PATH="$1"

# 2. Extract content
export SPEC_CONTENT="$(cat "$SPEC_PATH")"

# 3. Analyze task, identify subtasks, and map to agents
# [Execute PHASES 1-6 above]

# 4. Save orchestration document
# .taskmaster/orchestration/<sanitized_name>-agent-orchestration.md

# 5. Update taskmaster if task exists
# task-master update-subtask <id> --metadata="..." [for each subtask]
```

**If input is a taskmaster task ID**:

```bash
# 1. Retrieve task from taskmaster
task-master get-task --id=$1

# 2. Extract subtasks
# [Parse task JSON/structure]

# 3. Analyze and map subtasks to agents
# [Execute PHASES 2-6 above]

# 4. Save orchestration document
# .taskmaster/orchestration/<task_id>-agent-orchestration.md

# 5. Update each subtask in taskmaster
# task-master update-subtask <subtask_id> --metadata="..." [for each]
```

====================
QUALITY ASSURANCE CHECKLIST
====================

Before delivering the orchestration plan:

- [ ] Task requirements fully understood
- [ ] All agent options evaluated
- [ ] Subtask assignments justified with rationale
- [ ] Dependencies correctly mapped
- [ ] No critical gaps or orphaned subtasks
- [ ] Critical path identified
- [ ] Timeline realistic and sequence-aware
- [ ] Risk factors documented
- [ ] Orchestration document complete and clear
- [ ] TaskMaster updates applied (if task ID provided)
- [ ] Final summary report generated

---

## Related Skills

- **create-task-taskmaster**: Use to initially create structured task specifications
- **append-tasks-taskmaster**: Use to add new subtasks to existing task specifications
- **context-map**: Use to understand file dependencies before agent assignment
- **taskmaster**: Core task management workflows

## Resources

- Available Agents: `.../agents/*.agent.md`
- Task Master Documentation: `skills/taskmaster/SKILL.md`
- Project Instructions: `.github/instructions/*.instructions.md`
