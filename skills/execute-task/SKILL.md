---
name: execute-task
description: "A skill for executing a specified task based on a provided task specification. This skill will read the task specification from a markdown file, analyze the requirements and steps outlined in the specification, and then execute the necessary actions to complete the task. The execution process will involve reasoning through the steps sequentially, utilizing available tools and resources, and delegating tasks to expert agents when appropriate. The goal is to efficiently and effectively complete the task as defined in the specification while adhering to any constraints or guidelines provided."
argument-hint: "[spec_file]: A file path to a markdown file containing the task description, [task_id]: The unique identifier of the task to be executed."
---

Read the {spec_file} file when provided to gather the necessary information to execute the task. Then, get the task to the system using the get_task tool with the {task_id} and reason step-by-step using the sequentialthinking tool to execute the task. Finally, create a task list using the todos tool to execute the task. When available, delegate task execution to the expert developer agent or subagent.
