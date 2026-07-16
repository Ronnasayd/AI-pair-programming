# Examples

## Example 1: Convert JSON

User input:

- Purpose: Convert tasks.md to TaskMaster JSON
- Cases: User wants to transform task specs, generate JSON from markdown
- Negatives: Don't use for creating task specs, executing tasks
- Related: create-task-spec, execute-task

Generated:

```
Convert tasks.md spec files into TaskMaster JSON format (.taskmaster/tasks/tasks.json for task list, .taskmaster/execution/metadata.json for strategy). Use when user says "convert tasks.md to taskmaster json", "transform tasks.md to .taskmaster format", "converta tasks.md em tasks.json", or wants to generate TaskMaster JSON from a tasks file. Do NOT use for creating task specs, executing tasks, or non-TaskMaster conversions.
```

## Example 2: Document Generation

User input:

- Purpose: Generate PRDs using 5-battery framework
- Cases: User needs product spec, wants structured requirements
- Negatives: Not for architecture, not for technical specs
- Related: architecture-designer, technical-spec-writer

Generated:

```
Create product requirement documents using 5-battery framework with structured outputs. Use when user says "create PRD", "write product spec", "generate requirements", "build feature outline", or "crea PRD". Do NOT use for architecture decisions, technical specifications, or system design.
```
