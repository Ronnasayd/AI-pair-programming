---
description: Comprehensive guide to generate code with copilot
applyTo: "**/*"
---

<rules>
Generate code that follows recognized industry best practices and is optimized for performance, security, and scalability.
Ensure the code is clean, well-structured, readable, and easy to maintain.
Strictly follow coding conventions, naming standards, and the style guidelines of the project or chosen language.
Avoid obsolete or deprecated methods, APIs, or libraries; always prefer current, well-supported alternatives.
Include explanatory comments for complex logic, architectural decisions, known limitations, and non-trivial code sections.
Consider the context of the existing codebase, integrating new implementations in a compatible way and following established patterns.
Avoid changes that break backward compatibility unless absolutely necessary; in such cases, provide detailed documentation of changes and migration instructions.
When creating functions, methods, classes, or modules, use clear, descriptive, and consistent names that accurately reflect their purpose and avoid ambiguity.
Implement robust error handling and input validation at all relevant points, covering both expected errors and unexpected exceptions.
Ensure the code is testable, including examples, automated tests, or instructions for manual validation whenever possible.
For front-end code, ensure components are responsive, accessible, compatible across different browsers and devices, and follow modern web usability recommendations and standards (WCAG, ARIA, etc.).
For back-end code, prioritize security (protection against injections, authentication, authorization, encryption), scalability, and efficient access to data and resources.
If the request is ambiguous, incomplete, or contradictory, ask the user for clarification before generating code, specifying your questions objectively.
Avoid slang, informal language, or excessive abbreviations in comments, documentation, and log messages.
Adopt defensive programming principles, modularization, reuse, and separation of concerns.
Include clear and objective documentation whenever there are significant changes, new components, endpoints, or public interfaces.
Consider internationalization/localization requirements if applicable to the project.
Whenever possible, use native language features or widely used libraries instead of implementing solutions from scratch without a solid technical justification.
</rules>

<avoid>
Avoid confusing, generic, or abbreviated names for variables, functions, classes, or modules (e.g., `x`, `temp1`, `doStuff`, `data1`).
Do not write code without comments in complex sections, non-trivial algorithms, or non-standard decisions.
Avoid code duplication; prefer abstraction and reuse through functions, methods, or modules.
Do not ignore error handling or assume success in critical operations such as access to external resources, I/O, or data manipulation.
Do not use magic values (hardcoded numbers, strings) without explanation or defining them as named constants or enums.
Avoid mixing multiple responsibilities in a single function, class, or module; practice the Single Responsibility Principle.
Do not implement code without basic tests, behavior validations, or usage examples.
Do not ignore performance in critical parts, such as inefficient loops, heavy queries, or blocking synchronous operations.
Never trust user input without proper validation or protection against vulnerabilities (XSS, CSRF).
Do not leave dead code, commented-out code, unused functions, or obsolete snippets in the project.
Do not reimplement functionality already available in stable, well-tested libraries without relevant technical justification.
Do not disregard style guides, structure, project conventions, or team recommendations.
Avoid excessive nested conditionals (many if-elif-else); prefer alternatives such as polymorphism, dictionaries/dispatch maps, or design patterns.
Never import modules outside the top level of the file unless explicitly necessary (e.g., conditional imports or plugins).
Do not catch overly broad exceptions (e.g., `except Exception`) without need; prefer catching specific exceptions.
Do not access protected or private members outside the originating class or module.
Avoid leaving variables, arguments, or parameters unused in the code.
Do not use overly generic or too-permissive typing (e.g., `any`, unconstrained types) without a clear reason.
Avoid circular dependencies, excessive coupling between modules, and violations of the Dependency Inversion Principle.
Do not use outdated security practices, obsolete cryptographic algorithms, or insecure authentication/authorization methods.
Do not ignore internationalization/localization requirements in projects that require multi-language support.
Avoid inconsistencies between development, test, and production environments (e.g., hardcoded configurations, absolute paths, different permissions).
</avoid>

<update_documentation>
Whenever you are asked to document modifications made after an implementation, use the MCP tool `my_generate_docs_update`, passing the correct `rootProject` (the project’s root directory) and a command that describes the changes made (e.g., `git diff`). Follow the tool’s instructions to update the documentation.
</update_documentation>

<add_techs>
Whenever new technologies, frameworks, or libraries are introduced into the project, generate documentation with usage references, best practices, and useful links using a research tool or MCP Context7. Save this documentation in `docs/techs/<technology-name>.md`.
</add_techs>

<task_master>
Whenever you are asked to implement a new task using MCP Task Master, request the task details from MCP Task Master, create a new branch `task-<TASK_ID>`, and follow the checklist below:

- [ ] Analyze the task scope in MCP Task Master
- [ ] Update the task status to "In Progress" in MCP Task Master
- [ ] Execute one subtask at a time, following the checklist below for each subtask:
  - [ ] Update the subtask status to "In Progress" in MCP Task Master
  - [ ] Create a detailed action plan for the subtask
  - [ ] Present the action plan to the user and wait for confirmation
  - [ ] Generate a preview of the code to be implemented and wait for the user's confirmation
  - [ ] Implement the subtask according to the approved action plan
  - [ ] Wait for the user's "okay" and update the subtask status to "Completed" in MCP Task Master
- [ ] Make a commit with a clear, descriptive message
- [ ] After approval, merge the task branch into the main branch
- [ ] Close the task branch after the merge
      </task_master>

<style_guides>
When generating code, always adhere to the specific style guides and conventions of the programming language or framework being used. This includes indentation, spacing, brace styles, naming conventions, and file organization. If the project has an established style guide (e.g., PEP 8 for Python, Google Java Style Guide), follow it strictly. If no specific style guide is provided, use widely accepted community standards for the respective language.

References to search for style guides:
golang: https://google.github.io/styleguide/go/index.html
html: https://google.github.io/styleguide/htmlcssguide.html
css: https://google.github.io/styleguide/htmlcssguide.html
python: https://google.github.io/styleguide/pyguide.html
typescript: https://google.github.io/styleguide/tsguide.html
javascript: https://google.github.io/styleguide/jsguide.html
markdown: https://google.github.io/styleguide/docguide/style.html
</style_guides>

<preview_code>
Whenever making any significant addition, deletion, or modification to code, show a preview of the code that will be produced. Show only the key points of the generated code and include well-explained comments on each line. Wait for the user's confirmation before proceeding. If the user adds suggestions, consider them carefully and adjust the code before making the actual modification.
</preview_code>

<show_action_plan>
Whenever making any significant addition, deletion, or modification to code, explain what will be done and why the change is needed. Wait for the user's confirmation before proceeding. If the user adds suggestions, consider them carefully and adjust the plan as necessary.
</show_action_plan>
