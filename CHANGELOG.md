# Changelog

## v2025.10.29 (Initial Release / Full History)

### ✨ Features

**2025-10-29**
* Add initial changelog with features, bug fixes, documentation updates, and refactoring details ([b6a8eb6](https://github.com/Ronnasayd/AI-pair-programming/commit/b6a8eb6))

**2025-10-24**
* Enable headless mode in get_cookies function for improved automation ([cfd3629](https://github.com/Ronnasayd/AI-pair-programming/commit/cfd3629))
* Add comprehensive cybersecurity instructions for secure software development and operations ([bf17790](https://github.com/Ronnasayd/AI-pair-programming/commit/bf17790))
* Add comprehensive coding guidelines and best practices to copilot.instructions.md ([759be39](https://github.com/Ronnasayd/AI-pair-programming/commit/759be39))

**2025-10-21**
* Enhance my_search_references function to support optional rootproject and globs parameters; add ag_search function for improved codebase searching ([d8749c2](https://github.com/Ronnasayd/AI-pair-programming/commit/d8749c2))

**2025-10-20**
* Implement search functionality in search_engine module; add my_search_references tool and update developer instructions ([96cc91b](https://github.com/Ronnasayd/AI-pair-programming/commit/96cc91b))

**2025-10-13**
* Add prd generation instructions and template handling in my_generate_prd function; update documentation workflow instructions ([a0e17ce](https://github.com/Ronnasayd/AI-pair-programming/commit/a0e17ce))

**2025-10-10**
* Add my_generate_docs_init function to return documentation generation instructions ([fbd9a35](https://github.com/Ronnasayd/AI-pair-programming/commit/fbd9a35))
* Add documentation workflow instructions and enhance git diff handling in my_generate_docs_update function ([92a69c1](https://github.com/Ronnasayd/AI-pair-programming/commit/92a69c1))

**2025-10-09**
* Add input_text extraction from request body in generate_embeddings function ([9c945ad](https://github.com/Ronnasayd/AI-pair-programming/commit/9c945ad))

**2025-10-07**
* Update my_get_context function to accept multiple parameters for context generation ([1475755](https://github.com/Ronnasayd/AI-pair-programming/commit/1475755))

**2025-10-03**
* Add task implementation instructions and attachment references to prompt documentation ([b77f002](https://github.com/Ronnasayd/AI-pair-programming/commit/b77f002))

**2025-10-02**
* Add attachment extraction function and integrate it into chat completion process ([fb9c7e0](https://github.com/Ronnasayd/AI-pair-programming/commit/fb9c7e0))

**2025-10-01**
* Add meta extraction and merging functions for tasks and subtasks in my_mcp_server ([19495cb](https://github.com/Ronnasayd/AI-pair-programming/commit/19495cb))
* Add my_developer_workflow function to load and return developer workflow instructions ([fbaa6fc](https://github.com/Ronnasayd/AI-pair-programming/commit/fbaa6fc))
* Add my_styleguide function to return style guide for specified programming language ([834ee34](https://github.com/Ronnasayd/AI-pair-programming/commit/834ee34))

**2025-09-29**
* Convert call_copilot function to asynchronous and update api calls accordingly ([00b5725](https://github.com/Ronnasayd/AI-pair-programming/commit/00b5725))
* Refactor copilotapi methods to be asynchronous and update authentication flow ([3c3f31f](https://github.com/Ronnasayd/AI-pair-programming/commit/3c3f31f))

**2025-09-27**
* Implement streaming response handling in call_copilot function and add test script for openai integration ([982354a](https://github.com/Ronnasayd/AI-pair-programming/commit/982354a))
* Refactor get_cookies function to be asynchronous and update related calls in copilotapi ([812750b](https://github.com/Ronnasayd/AI-pair-programming/commit/812750b))
* Enhance logging in copilotapi chat methods for improved debugging ([5aa51fc](https://github.com/Ronnasayd/AI-pair-programming/commit/5aa51fc))
* Add logging to copilotapi methods for better traceability ([17970a5](https://github.com/Ronnasayd/AI-pair-programming/commit/17970a5))
* Add comprehensive developer instructions for software development and debugging processes ([0d22fd9](https://github.com/Ronnasayd/AI-pair-programming/commit/0d22fd9))

**2025-09-25**
* Refactor my_convert_markdown_to_tasks function to accept cwd and create tasks.json in specified directory ([815b9e3](https://github.com/Ronnasayd/AI-pair-programming/commit/815b9e3))
* Implement markdown to tasks conversion and add test script for validation ([93a5128](https://github.com/Ronnasayd/AI-pair-programming/commit/93a5128))
* Add main entry point to start mcp server and include example test calls ([951f152](https://github.com/Ronnasayd/AI-pair-programming/commit/951f152))
* Enhance task conversion functions to support markdown format and improve validation ([431c5db](https://github.com/Ronnasayd/AI-pair-programming/commit/431c5db))

**2025-09-24**
* Implement streaming response handling in copilotapi and update chat method to support streaming ([a5d8009](https://github.com/Ronnasayd/AI-pair-programming/commit/a5d8009))
* Add tokenizer capabilities and additional parameters for model configuration ([1d971df](https://github.com/Ronnasayd/AI-pair-programming/commit/1d971df))

**2025-09-23**
* Remove expand_task.json and update taskmaster.request.json with new prd processing logic; add tasksmaster-template.json for task schema validation ([e2394cc](https://github.com/Ronnasayd/AI-pair-programming/commit/e2394cc))
* Implement copilotapi and associated functionalities for github copilot integration; update requirements and add initial module files ([6a4635e](https://github.com/Ronnasayd/AI-pair-programming/commit/6a4635e))

**2025-09-22**
* Implement copilotapi class with chat and create_chat methods for github copilot integration ([920d9ba](https://github.com/Ronnasayd/AI-pair-programming/commit/920d9ba))
* Add expand_task.json with task breakdown and subtasks generation logic ([b2a7e90](https://github.com/Ronnasayd/AI-pair-programming/commit/b2a7e90))

**2025-09-19**
* Implement flexible model naming and enhance model validation in ollama api proxy server ([2fd7c2d](https://github.com/Ronnasayd/AI-pair-programming/commit/2fd7c2d))
* Enhance logging functionality in ollama api proxy server and add openai-compatible endpoints ([181d4dc](https://github.com/Ronnasayd/AI-pair-programming/commit/181d4dc))
* Implement ollama api proxy server with request logging and model management endpoints ([cf12c63](https://github.com/Ronnasayd/AI-pair-programming/commit/cf12c63))

**2025-09-18**
* Add comprehensive guidelines for creating software requirements specification (srs) documents ([0446f1a](https://github.com/Ronnasayd/AI-pair-programming/commit/0446f1a))

**2025-09-17**
* Add new plan template for project and task management with detailed structure ([11954d1](https://github.com/Ronnasayd/AI-pair-programming/commit/11954d1))

**2025-09-16**
* Add 'design' category to tasks in tasks template for improved categorization ([ea151e1](https://github.com/Ronnasayd/AI-pair-programming/commit/ea151e1))
* Remove summary and notes fields from requirements in srs and tasks templates for clarity ([f66bc18](https://github.com/Ronnasayd/AI-pair-programming/commit/f66bc18))
* Enhance srs and tasks templates with detailed user stories and requirements structure ([f7cb744](https://github.com/Ronnasayd/AI-pair-programming/commit/f7cb744))
* Remove epics, prioritization, and roadmap sections from tasks template for simplification ([0e2d557](https://github.com/Ronnasayd/AI-pair-programming/commit/0e2d557))
* Update prd structure and add prompt template file ([311b201](https://github.com/Ronnasayd/AI-pair-programming/commit/311b201))

**2025-09-12**
* Add tasks template json structure for project management ([f18372e](https://github.com/Ronnasayd/AI-pair-programming/commit/f18372e))
* Update prd and srs instructions to include structured input fields and optional parameters ([caf3f5a](https://github.com/Ronnasayd/AI-pair-programming/commit/caf3f5a))
* Add general recommendations for srs generation process ([cddf0b8](https://github.com/Ronnasayd/AI-pair-programming/commit/cddf0b8))
* Add prd and srs templates for structured documentation ([87fe8c1](https://github.com/Ronnasayd/AI-pair-programming/commit/87fe8c1))
* Update output format to markdown template for task generation instructions ([828727c](https://github.com/Ronnasayd/AI-pair-programming/commit/828727c))
* Add structured instructions for generating tasks from requirements across multiple methodologies ([01b8b81](https://github.com/Ronnasayd/AI-pair-programming/commit/01b8b81))
* Add comprehensive instructions for generating prd and srs documents ([650681a](https://github.com/Ronnasayd/AI-pair-programming/commit/650681a))

### 🐛 Bug Fixes

**2025-09-24**
* Update authorization handling in auth method to include github-bearer token for requests ([b2d1a1d](https://github.com/Ronnasayd/AI-pair-programming/commit/b2d1a1d))
* Update error handling to re-authenticate on 401 status code in copilotapi ([d985d03](https://github.com/Ronnasayd/AI-pair-programming/commit/d985d03))

**2025-09-23**
* Handle 400 response by re-authenticating and refreshing token in copilotapi ([c7e7482](https://github.com/Ronnasayd/AI-pair-programming/commit/c7e7482))

**2025-09-20**
* Update command arguments for my_run_command in my_mcp_client_stdio.py ([9c47634](https://github.com/Ronnasayd/AI-pair-programming/commit/9c47634))

**2025-09-19**
* Update remote ollama url and clear excluded paths in proxy server configuration ([ce02e42](https://github.com/Ronnasayd/AI-pair-programming/commit/ce02e42))

**2025-09-17**
* Update documentation instructions to reflect changes in file naming conventions and structure. ([f785d11](https://github.com/Ronnasayd/AI-pair-programming/commit/f785d11))

### 📚 Documentation

**2025-10-29**
* Add initial changelog entries for 2025‑10‑29 with features, bug fixes, documentation updates, and refactoring details ([ef736d1](https://github.com/Ronnasayd/AI-pair-programming/commit/ef736d1))
* Update generate-documentation instructions with detailed file purpose and structure guidelines ([56e439b](https://github.com/Ronnasayd/AI-pair-programming/commit/56e439b))

**2025-10-10**
* Enhance documentation structure and provide detailed file descriptions in generate-documentation.instructions.md ([02d25a6](https://github.com/Ronnasayd/AI-pair-programming/commit/02d25a6))

**2025-09-12**
* Update srs structure formatting for consistency across instructions ([4cb7ff5](https://github.com/Ronnasayd/AI-pair-programming/commit/4cb7ff5))

### ♻️ Refactoring

**2025-10-07**
* Update my_run_command to use rootproject instead of cwd for directory execution ([56e1614](https://github.com/Ronnasayd/AI-pair-programming/commit/56e1614))

**2025-10-02**
* Clean up attachment extraction logic and improve prompt handling in chat function ([f3efc59](https://github.com/Ronnasayd/AI-pair-programming/commit/f3efc59))
* Enhance file exclusion logic and improve read_file function parameters ([da404ef](https://github.com/Ronnasayd/AI-pair-programming/commit/da404ef))

**2025-10-01**
* Improve path handling and enhance markdown generation in my_mcp_server ([023f36a](https://github.com/Ronnasayd/AI-pair-programming/commit/023f36a))

**2025-09-30**
* Enhance logging in chat method and adjust response handling in call_copilot ([c6f009b](https://github.com/Ronnasayd/AI-pair-programming/commit/c6f009b))

**2025-09-27**
* Update logging level to info and streamline logging configuration in copilotapi and ollama ([1ced442](https://github.com/Ronnasayd/AI-pair-programming/commit/1ced442))
* Simplify chat response handling and remove unused chat_complete method ([00cd6b8](https://github.com/Ronnasayd/AI-pair-programming/commit/00cd6b8))
* Update logging configuration to debug level and replace logging calls with logger instance in copilotapi ([bff3186](https://github.com/Ronnasayd/AI-pair-programming/commit/bff3186))

**2025-09-25**
* Update my_code_review and my_convert_markdown_to_tasks functions to use rootproject parameter instead of cwd ([6747bf6](https://github.com/Ronnasayd/AI-pair-programming/commit/6747bf6))

**2025-09-12**
* Update file paths to reflect new project structure in my_mcp_server.py ([1def862](https://github.com/Ronnasayd/AI-pair-programming/commit/1def862))

### 🧹 Chores

**2025-10-09**
* Update logging file path to /tmp for consistency across modules ([67c8582](https://github.com/Ronnasayd/AI-pair-programming/commit/67c8582))

**2025-10-01**
* Update .gitignore to include .github and remove teste.py file ([f89a084](https://github.com/Ronnasayd/AI-pair-programming/commit/f89a084))

**2025-09-24**
* Update server port from 11435 to 11434 in copilot ollama api proxy ([0f88ed1](https://github.com/Ronnasayd/AI-pair-programming/commit/0f88ed1))

**2025-09-11**
* Remove install script for generating context and coverage links ([fea8448](https://github.com/Ronnasayd/AI-pair-programming/commit/fea8448))
* Update file permissions and relocate requirements file to src directory ([563d2db](https://github.com/Ronnasayd/AI-pair-programming/commit/563d2db))
* Rename markdown and python files to appropriate directories for better organization ([73d7666](https://github.com/Ronnasayd/AI-pair-programming/commit/73d7666))

### 🚧 Other Changes

**2025-09-11**
d83773e - first commit | 2025-09-11

---
Generated on 2025-10-29 13:31:59