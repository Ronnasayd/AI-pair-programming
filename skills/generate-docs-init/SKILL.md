---
name: generate-docs-init
description: "A skill for generating comprehensive documentation of the workspace structure and its components. This skill will analyze the tree structure of the workspace, including modules, folders, and files, and produce incremental documentation that provides an overview of the workspace organization, key components, and their relationships. The generated documentation will serve as a valuable resource for developers to understand the workspace layout and navigate through its components effectively." 
---

MANDATORY: Use documentations-specialist agent

## Task

Generate the workspace documentation in the described format. Perform the generation of this documentation incrementally. Analyze the tree structure of the workspace and break it down into smaller parts (modules, folders, files). As you iterate over each part, show which file, module, or folder of the workspace will be analyzed next and after analysis, perform the generation of the documentation incrementally as described in the instructions.
