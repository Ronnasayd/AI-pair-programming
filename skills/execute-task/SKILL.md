---
name: execute-task
description: "Execute a specified task by reading detailed specifications, analyzing requirements, planning the approach, and implementing step-by-step. Use this skill when: you have a task specification file or task ID that needs completion; the task is multi-step, involves architecture decisions, or requires tool orchestration; you need to track progress across subtasks and delegate work to specialist agents. Triggers on task execution requests, implementation assignments, feature builds, bug fixes, refactoring projects, or when a user provides a task spec .md file. Always use this skill for complex development work rather than tackling it directly —delegate to specialists and maintain progress visibility with task tracking."
argument-hint: "[task_id] - TaskMaster task ID (e.g., 'T1'), OR [spec_file] - Path to task specification markdown file"
---

## Workflow

The execute-task skill orchestrates work through this sequence:

### 1. **Load Task Context**

- If `task_id` provided: Use `get_task` to fetch full task definition (requirements, subtasks, context, links)
- If `spec_file` provided: Read the markdown file to extract requirements, acceptance criteria, and context
- If both: Get task via ID first (authoritative source), then cross-reference with spec file for additional context

### 2. **Plan the Approach**

- Use `sequentialthinking` to reason through requirements, dependencies, and edge cases
- Identify which modules/files are affected; check for existing patterns in the codebase
- Decompose the task into concrete subtasks (what needs to be built, tested, documented)
- Determine if specialist agents (developer-specialist, database-specialist, cybersecurity-specialist) are needed

### 3. **Create Progress Tracking**

- Use `manage_todo_list` to create explicit task breakdown with status tracking
- Mark tasks **in-progress** as you start each step
- Mark **completed** immediately after finishing (do not batch)
- Use this to maintain context and prevent losing work mid-task

### 4. **Execute with Delegation**

- **For code work**: Use available developer tools directly; delegate complex refactoring or architecture to `developer-specialist` agent
- **For security concerns**: Escalate to `cybersecurity-specialist`
- **For data/performance**: Escalate to `database-specialist`
- **For patterns/architecture**: Escalate to `design-pattern-specialist`
- Provide agents with clear scope: what they own, what you'll verify
- Integrate their work back into the main execution flow

### 5. **Verify and Document**

- After completing each subtask, verify it against acceptance criteria
- Check for regressions, missing edge cases, or incomplete integration
- Update task status and capture any learnings for future iterations
- Maintain a clear record of what was done and why (for reviews/documentation)

## Good Signals This Skill Should Trigger

- User provides a task ID or task spec file
- Task involves multiple files, modules, or architectural decisions
- Task requires test coverage, refactoring, or performance analysis
- User says "build", "implement", "fix", "refactor", "complete this task"
- Progress needs to be tracked across multiple steps

## Anti-Patterns (Don't Do This)

- Don't run code without understanding requirements first
- Don't skip the plan step — jumping straight to coding creates rework
- Don't mark all tasks complete at the end; mark them as you go
- Don't ignore test failures or incomplete acceptance criteria
- Don't try to do everything yourself — delegate to specialist agents when their domain expertise is clearer
- Don't lose context — always use task tracking to stay oriented
