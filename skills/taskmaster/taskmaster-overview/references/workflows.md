# Task Master Development Workflows

## Requirement-to-Execution Workflow

### 1. Project Initialization
Always start by checking if Task Master is initialized. If not, run `task-master init`.
- Result: Creates `.taskmaster/` folder.

### 2. PRD Parsing
Once you have a Product Requirements Document (PRD), use `parse_prd` to generate tasks.
- Tip: Use `prd-generator-specialist` or similar to create the PRD first.

### 3. Task Selection
Use `next_task` to find the highest priority task with all dependencies met.
- Workflow: `get_tasks --status pending` -> `next_task`.

### 4. Task Expansion
Before starting a complex task, expand it into actionable subtasks.
- Tool: `expand_task --id <id>`.

### 5. Implementation Cycle
For each task:
- Set status to `in-progress`.
- Perform research if needed (`research`).
- Implement changes.
- Verify through tests.
- Set status to `done`.

### 6. Complexity and Risks
Run `analyze_project_complexity` periodically to identify high-risk areas.
- Tip: Use this info to prioritize tasks and allocate more time to complex components.
