---
name: taskmaster
description: AI-driven task management and project tracking using Task Master. Use when agent needs to initialize projects, parse Product Requirements Documents (PRDs), break down tasks into subtasks, or perform contextual research for technical implementations.
---

# Task Master

## Overview

This skill integrates the Claude Task Master system to manage project lifecycles, from requirement analysis to task execution. It uses the Model Context Protocol (MCP) to automate task creation, complexity analysis, and technical research.

## Core Workflow

1. **Initialize Project**: Ensure the `.taskmaster/` directory exists. If not, initialize it.
2. **Requirement Analysis**: Parse the PRD to generate high-level tasks.
3. **Task Expansion**: Break down complex tasks into manageable subtasks.
4. **Execution & Tracking**: Follow the next logical task and update status upon completion.
5. **Research**: Use integrated research tools to gather technical documentation or best practices.

## Capabilities

### 1. Project Initialization

Initialize the project structure using `task-master init` or by checking for the `.taskmaster/` folder.

### 2. PRD Parsing

Convert a PRD into a structured task list.

- **Tool**: `parse_prd`
- **Workflow**: Provide the path to `prd.txt` to automatically generate tasks.

### 3. Task Management

- **get_tasks**: List all tasks and their current status.
- **next_task**: Identify the next task to work on based on dependencies.
- **set_task_status**: Update task progress (`pending`, `in-progress`, `done`, `blocked`).
- **expand_task**: Subdivide a task into detailed implementation steps.

### 4. Complexity Analysis

Evaluate the project to estimate effort and potential bottlenecks.

- **Tool**: `analyze_project_complexity`

### 5. Contextual Research

Perform live research for technical specifications or libraries.

- **Tool**: `research`
- **Tip**: Use this before implementing unfamiliar features.

## Examples

### Initialize and Parse

> "Initialize task master and parse our PRD at .taskmaster/docs/prd.txt"

### Working on Next Task

> "What's the next task? Expand it into subtasks and let's start implementation."

### Updating Status

> "I've finished the login component. Mark task #5 as done."

## Resources

- [COMMANDS.md](references/commands.md) - Detailed tool and CLI command reference.
- [WORKFLOWS.md](references/workflows.md) - Best practices for task-driven development.
