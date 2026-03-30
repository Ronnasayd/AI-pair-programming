# Changelog

## v2026.03.30 (Initial Release / Full History)

### **2026-03-30**

- **[✨ Features]** Refactor installation scripts to use centralized ignore handling; add ignores.sh for skill and agent removal ([efd968e](https://github.com/Ronnasayd/AI-pair-programming/commit/efd968e))
- **[✨ Features]** Add .agentsignore file and implement agent removal based on ignore patterns; improve formatting in skill.md files ([cfd9d84](https://github.com/Ronnasayd/AI-pair-programming/commit/cfd9d84))
- **[✨ Features]** Add context7 documentation lookup and figma code connect components skills; remove obsolete skill.md files ([90e6993](https://github.com/Ronnasayd/AI-pair-programming/commit/90e6993))
- **[✨ Features]** Add skillsignore functionality to remove specified skills and update gemini installation command ([29f85f2](https://github.com/Ronnasayd/AI-pair-programming/commit/29f85f2))

### **2026-03-29**

- **[🧹 Chores]** Update rtk instructions file by replacing copilot instructions with structured format ([1eb59d4](https://github.com/Ronnasayd/AI-pair-programming/commit/1eb59d4))
- **[✨ Features]** Integrate rtk initialization for copilot and gemini in installation scripts ([e64a690](https://github.com/Ronnasayd/AI-pair-programming/commit/e64a690))
- **[🧹 Chores]** Reorder rtk initialization commands and update instructions file path ([90fb428](https://github.com/Ronnasayd/AI-pair-programming/commit/90fb428))
- **[✨ Features]** Initialize rtk with gemini and copilot in install script ([fbd7c6a](https://github.com/Ronnasayd/AI-pair-programming/commit/fbd7c6a))
- **[✨ Features]** Add support for postgresql, mysql, mongodb, and sqlite in settings configuration ([f5fe9b3](https://github.com/Ronnasayd/AI-pair-programming/commit/f5fe9b3))
- **[🚧 Other Changes]** Update shebang and fix environment variable name for sqlite database path ([5dd072e](https://github.com/Ronnasayd/AI-pair-programming/commit/5dd072e))
- **[✨ Features]** Add sqlite support with new fastmcp server tool for database interaction ([685b162](https://github.com/Ronnasayd/AI-pair-programming/commit/685b162))
- **[✨ Features]** Add mongodb support with new tool for database interaction and update requirements ([4f3f11e](https://github.com/Ronnasayd/AI-pair-programming/commit/4f3f11e))
- **[✨ Features]** Add mysql support and refactor postgresql interaction in fastmcp server ([aa927fa](https://github.com/Ronnasayd/AI-pair-programming/commit/aa927fa))
- **[♻️ Refactoring]** Enhance postgresql query execution to enforce read-only sessions and improve result fetching ([4981255](https://github.com/Ronnasayd/AI-pair-programming/commit/4981255))
- **[♻️ Refactoring]** Update postgresql server configuration and enhance query execution documentation ([ce1218e](https://github.com/Ronnasayd/AI-pair-programming/commit/ce1218e))
- **[✨ Features]** Implement postgresql interaction and add fastmcp server tools for code review and context generation ([e2aca2f](https://github.com/Ronnasayd/AI-pair-programming/commit/e2aca2f))

### **2026-03-27**

- **[♻️ Refactoring]** Update documentation file patterns in check_documentation_files function ([3652ff9](https://github.com/Ronnasayd/AI-pair-programming/commit/3652ff9))
- **[♻️ Refactoring]** Remove unnecessary global statements and improve file handling in memory.py ([abaa2e3](https://github.com/Ronnasayd/AI-pair-programming/commit/abaa2e3))
- **[✨ Features]** Implement per-language helpers for quality gate checks ([afcf768](https://github.com/Ronnasayd/AI-pair-programming/commit/afcf768))
- **[🧹 Chores]** Add inputs field to vscode.mcp.json configuration ([b138a83](https://github.com/Ronnasayd/AI-pair-programming/commit/b138a83))
- **[✨ Features]** Add aftertool hook for running quality gate checks post tool usage ([e5ea08a](https://github.com/Ronnasayd/AI-pair-programming/commit/e5ea08a))
- **[✨ Features]** Add memory-add command for persisting memory entries with optional file association ([5a043df](https://github.com/Ronnasayd/AI-pair-programming/commit/5a043df))
- **[🚧 Other Changes]** Format imports and improve logging messages in quality_gate.py ([c57f449](https://github.com/Ronnasayd/AI-pair-programming/commit/c57f449))
- **[🚧 Other Changes]** Format code for consistency in check_documentation_files and get_diff_files functions ([f03c13d](https://github.com/Ronnasayd/AI-pair-programming/commit/f03c13d))
- **[🐛 Bug Fixes]** Set quality gate fix to true and strict to false by default ([3b81b01](https://github.com/Ronnasayd/AI-pair-programming/commit/3b81b01))
- **[✨ Features]** Add new agents for prd and srs generation with detailed instructions ([b58e0e4](https://github.com/Ronnasayd/AI-pair-programming/commit/b58e0e4))
- **[✨ Features]** Add symlink creation for .geminignore in gemini.install.sh ([3673688](https://github.com/Ronnasayd/AI-pair-programming/commit/3673688))
- **[✨ Features]** Add .geminignore file to exclude common development artifacts ([13d068e](https://github.com/Ronnasayd/AI-pair-programming/commit/13d068e))

### **2026-03-26**

- **[✨ Features]** Reorganize scripts and implement md2toml and toml2md converters ([78d27fd](https://github.com/Ronnasayd/AI-pair-programming/commit/78d27fd))
- **[✨ Features]** Update documentation skills for generating and syncing project documentation ([0db89a8](https://github.com/Ronnasayd/AI-pair-programming/commit/0db89a8))
- **[✨ Features]** Add rule to allow listing servers in mcp-manager ([f872b41](https://github.com/Ronnasayd/AI-pair-programming/commit/f872b41))
- **[♻️ Refactoring]** Remove unused context7 and chrome-devtools entries from mcp-server-enablement.json ([967d852](https://github.com/Ronnasayd/AI-pair-programming/commit/967d852))
- **[♻️ Refactoring]** Clean up mcpservers configuration by removing unused entries and fixing url typo ([7fb466f](https://github.com/Ronnasayd/AI-pair-programming/commit/7fb466f))
- **[♻️ Refactoring]** Remove github server configuration and add web_search_exa rule in policies ([984277b](https://github.com/Ronnasayd/AI-pair-programming/commit/984277b))
- **[🧹 Chores]** Remove commented-out server configurations from vscode.mcp.json ([a248fbd](https://github.com/Ronnasayd/AI-pair-programming/commit/a248fbd))
- **[♻️ Refactoring]** Update mcp-manager configuration and clean up commented server entries ([ca8ebc1](https://github.com/Ronnasayd/AI-pair-programming/commit/ca8ebc1))
- **[✨ Features]** Add get_diff_files function to retrieve modified files using git diff ([1b690d1](https://github.com/Ronnasayd/AI-pair-programming/commit/1b690d1))

### **2026-03-25**

- **[🐛 Bug Fixes]** Improve error handling in run_command and update version in copilot_ollama ([84a2cee](https://github.com/Ronnasayd/AI-pair-programming/commit/84a2cee))
- **[♻️ Refactoring]** Add debug logging in detect_formatter for improved traceability ([12a2408](https://github.com/Ronnasayd/AI-pair-programming/commit/12a2408))
- **[♻️ Refactoring]** Enhance resolve_formatter_bin function with logger for improved debugging ([a7484fc](https://github.com/Ronnasayd/AI-pair-programming/commit/a7484fc))
- **[♻️ Refactoring]** Add debug logging to detect_formatter for improved traceability ([d7df285](https://github.com/Ronnasayd/AI-pair-programming/commit/d7df285))
- **[♻️ Refactoring]** Enhance detect_formatter function with logging for better debugging ([0b87efb](https://github.com/Ronnasayd/AI-pair-programming/commit/0b87efb))
- **[♻️ Refactoring]** Enhance debug logging in quality gate checks for better traceability ([9834782](https://github.com/Ronnasayd/AI-pair-programming/commit/9834782))
- **[♻️ Refactoring]** Replace direct dictionary access with utility function get_by_key for improved readability and consistency ([43f07b5](https://github.com/Ronnasayd/AI-pair-programming/commit/43f07b5))
- **[♻️ Refactoring]** Update logger names and enhance utility function imports across multiple scripts ([07281ee](https://github.com/Ronnasayd/AI-pair-programming/commit/07281ee))
- **[♻️ Refactoring]** Enhance utility functions with key normalization and improved logging ([e8ab02c](https://github.com/Ronnasayd/AI-pair-programming/commit/e8ab02c))
- **[♻️ Refactoring]** Add debug logging for ruff results in quality gate checks ([678b5b3](https://github.com/Ronnasayd/AI-pair-programming/commit/678b5b3))
- **[🚧 Other Changes]** Update log message format to include logger name, level, and timestamp ([dde16ec](https://github.com/Ronnasayd/AI-pair-programming/commit/dde16ec))
- **[♻️ Refactoring]** Implement centralized logging across multiple scripts ([a1a70af](https://github.com/Ronnasayd/AI-pair-programming/commit/a1a70af))
- **[♻️ Refactoring]** Consolidate formatter detection and project root resolution logic ([745b850](https://github.com/Ronnasayd/AI-pair-programming/commit/745b850))
- **[🚧 Other Changes]** Improve session file output message for clarity ([1fd1cc2](https://github.com/Ronnasayd/AI-pair-programming/commit/1fd1cc2))

### **2026-03-24**

- **[🧹 Chores]** Remove orchestration instructions from installation scripts ([6ec9d46](https://github.com/Ronnasayd/AI-pair-programming/commit/6ec9d46))
- **[🚧 Other Changes]** Remove checklist formatting for clarity in agent instructions ([ae29740](https://github.com/Ronnasayd/AI-pair-programming/commit/ae29740))
- **[🚧 Other Changes]** Update code generation instructions for clarity and conciseness ([157aa3b](https://github.com/Ronnasayd/AI-pair-programming/commit/157aa3b))
- **[🚧 Other Changes]** Refine agent instructions by removing redundant rules and clarifying retrieval process ([5f315b9](https://github.com/Ronnasayd/AI-pair-programming/commit/5f315b9))
- **[🚧 Other Changes]** Improve clarity and consistency in agent instructions and documentation retrieval rules ([81058ca](https://github.com/Ronnasayd/AI-pair-programming/commit/81058ca))
- **[✨ Features]** Add ai-setup-audit prompt for auditing ai setup and identifying improvements ([7fdfae5](https://github.com/Ronnasayd/AI-pair-programming/commit/7fdfae5))
- **[🚧 Other Changes]** Update wording for clarity on testability and validation instructions in code generation rules ([909aa2b](https://github.com/Ronnasayd/AI-pair-programming/commit/909aa2b))
- **[🚧 Other Changes]** Update formatting for code generation rules and anti-patterns in instructions ([46277f5](https://github.com/Ronnasayd/AI-pair-programming/commit/46277f5))
- **[🚧 Other Changes]** Update formatting and wording for rules to avoid and follow in agent instructions ([e6c332a](https://github.com/Ronnasayd/AI-pair-programming/commit/e6c332a))
- **[📚 Documentation]** Add guidelines for module exports and database interactions in agent instructions ([877c26d](https://github.com/Ronnasayd/AI-pair-programming/commit/877c26d))
- **[✨ Features]** Add document summarizer skill and evaluation prompts for structured summaries ([665f4be](https://github.com/Ronnasayd/AI-pair-programming/commit/665f4be))
- **[🚧 Other Changes]** Improve code formatting and consistency across multiple skills documentation ([8a505fd](https://github.com/Ronnasayd/AI-pair-programming/commit/8a505fd))
- **[✨ Features]** Add quality gate checks to posttooluse hook for auditing ([3c98a7c](https://github.com/Ronnasayd/AI-pair-programming/commit/3c98a7c))
- **[✨ Features]** Update task prompt generation to include context from specification files ([2ac1314](https://github.com/Ronnasayd/AI-pair-programming/commit/2ac1314))

### **2026-03-23**

- **[🧹 Chores]** Remove outdated cli integration examples from taskmaster-task-validator documentation ([5e1a859](https://github.com/Ronnasayd/AI-pair-programming/commit/5e1a859))
- **[✨ Features]** Add new rules for skill activation and web search commands in auto-saved.toml ([d046ff0](https://github.com/Ronnasayd/AI-pair-programming/commit/d046ff0))
- **[🐛 Bug Fixes]** Update transcript path handling for summary extraction in session end ([738dd2e](https://github.com/Ronnasayd/AI-pair-programming/commit/738dd2e))
- **[✨ Features]** Add session end logging hook for auditing in afteragent configuration ([5b9cfca](https://github.com/Ronnasayd/AI-pair-programming/commit/5b9cfca))
- **[✨ Features]** Streamline summary extraction in session end handling for gemini and copilot transcripts ([9a66472](https://github.com/Ronnasayd/AI-pair-programming/commit/9a66472))
- **[✨ Features]** Refactor session end handling to extract summaries from gemini sessions and update hook configuration ([70dce33](https://github.com/Ronnasayd/AI-pair-programming/commit/70dce33))
- **[✨ Features]** Update memory.py and hooks.json descriptions for improved clarity on functionality ([44a5f72](https://github.com/Ronnasayd/AI-pair-programming/commit/44a5f72))
- **[✨ Features]** Enhance markdown generation in memory.py for improved session documentation ([622cbe8](https://github.com/Ronnasayd/AI-pair-programming/commit/622cbe8))
- **[✨ Features]** Replace check_available_files.py with memory.py for improved file management in hooks ([df39bf9](https://github.com/Ronnasayd/AI-pair-programming/commit/df39bf9))
- **[✨ Features]** Update get_session_id_short to accept session_id parameter for improved session identification ([f02bbf5](https://github.com/Ronnasayd/AI-pair-programming/commit/f02bbf5))
- **[✨ Features]** Add utility functions for session management and update .gitignore for session files ([d069fc0](https://github.com/Ronnasayd/AI-pair-programming/commit/d069fc0))
- **[✨ Features]** Remove notes and context sections from session summary output ([0be2c56](https://github.com/Ronnasayd/AI-pair-programming/commit/0be2c56))
- **[✨ Features]** Add session end logging and update session file structure for better auditing ([e5415ee](https://github.com/Ronnasayd/AI-pair-programming/commit/e5415ee))
- **[✨ Features]** Add support for features documentation directory in check_documentation_files ([8a7abab](https://github.com/Ronnasayd/AI-pair-programming/commit/8a7abab))
- **[✨ Features]** Update task file paths in check_documentation_files for accuracy ([cf11d72](https://github.com/Ronnasayd/AI-pair-programming/commit/cf11d72))
- **[✨ Features]** Add check_available_files command to session hooks for file availability checks ([ff1ec48](https://github.com/Ronnasayd/AI-pair-programming/commit/ff1ec48))
- **[✨ Features]** Write markdown instructions for available files to repository for easier access ([a24da80](https://github.com/Ronnasayd/AI-pair-programming/commit/a24da80))
- **[✨ Features]** Add check_available_files command to session start hook for file availability checks ([9d7e63a](https://github.com/Ronnasayd/AI-pair-programming/commit/9d7e63a))

### **2026-03-22**

- **[🧹 Chores]** Update changelog for version 2026.03.22 with recent changes and enhancements ([000c299](https://github.com/Ronnasayd/AI-pair-programming/commit/000c299))
- **[🧹 Chores]** Remove check_available_files script from session hooks for cleanup ([d1096c4](https://github.com/Ronnasayd/AI-pair-programming/commit/d1096c4))
- **[✨ Features]** Add check_available_files script to log documentation file availability in session hooks ([4c5cbdb](https://github.com/Ronnasayd/AI-pair-programming/commit/4c5cbdb))
- **[✨ Features]** Refactor log file handling to improve session log file retrieval and creation ([e86631e](https://github.com/Ronnasayd/AI-pair-programming/commit/e86631e))
- **[✨ Features]** Add check_available_files script to log documentation file availability and update session log file naming ([3b37e0e](https://github.com/Ronnasayd/AI-pair-programming/commit/3b37e0e))
- **[✨ Features]** Add session start hook to log session initiation for auditing ([070fac4](https://github.com/Ronnasayd/AI-pair-programming/commit/070fac4))
- **[🧹 Chores]** Remove deprecated javascript hooks and replace with python scripts for session management ([dc9d9b1](https://github.com/Ronnasayd/AI-pair-programming/commit/dc9d9b1))
- **[✨ Features]** Add session start and end hooks for task management and performance evaluation ([4ef8e57](https://github.com/Ronnasayd/AI-pair-programming/commit/4ef8e57))
- **[✨ Features]** Add session evaluation script to log performance metrics ([da25014](https://github.com/Ronnasayd/AI-pair-programming/commit/da25014))
- **[✨ Features]** Add precompact hook to save state before context compaction ([7313ce7](https://github.com/Ronnasayd/AI-pair-programming/commit/7313ce7))
- **[✨ Features]** Add session management features with aliases and session persistence ([41de85f](https://github.com/Ronnasayd/AI-pair-programming/commit/41de85f))
- **[✨ Features]** Add new skills for task retrospective, task validation, task management overview, and related workflows ([c345bbc](https://github.com/Ronnasayd/AI-pair-programming/commit/c345bbc))
- **[♻️ Refactoring]** Remove .git pattern from protected file patterns ([75b57fb](https://github.com/Ronnasayd/AI-pair-programming/commit/75b57fb))

### **2026-03-20**

- **[♻️ Refactoring]** Add additional hook categories for improved tool management ([2efd186](https://github.com/Ronnasayd/AI-pair-programming/commit/2efd186))
- **[♻️ Refactoring]** Update workflow guidelines for significant code changes and improve clarity ([5112a9a](https://github.com/Ronnasayd/AI-pair-programming/commit/5112a9a))
- **[♻️ Refactoring]** Clean up comments and improve terminal auto-approve settings in settings.json ([922ebf4](https://github.com/Ronnasayd/AI-pair-programming/commit/922ebf4))
- **[🐛 Bug Fixes]** Correct typo in url for atlassian service in vscode.mcp.json ([3121a38](https://github.com/Ronnasayd/AI-pair-programming/commit/3121a38))
- **[🐛 Bug Fixes]** Update applyto pattern in code instructions for specific file types ([77cd63e](https://github.com/Ronnasayd/AI-pair-programming/commit/77cd63e))
- **[✨ Features]** Enhance protect_files script to extract file paths from cat commands and deny access to protected files ([99fa306](https://github.com/Ronnasayd/AI-pair-programming/commit/99fa306))
- **[✨ Features]** Add descriptions for log-tools-call and protect-files commands in hooks ([76a2993](https://github.com/Ronnasayd/AI-pair-programming/commit/76a2993))
- **[♻️ Refactoring]** Consolidate hook commands into a single hooks.json file ([fa3be2d](https://github.com/Ronnasayd/AI-pair-programming/commit/fa3be2d))
- **[🐛 Bug Fixes]** Clarify task retrieval tool reference in execute-task skill documentation ([01c45ae](https://github.com/Ronnasayd/AI-pair-programming/commit/01c45ae))
- **[🐛 Bug Fixes]** Improve task retrieval instructions and enhance task prompt formatting ([cc6f32d](https://github.com/Ronnasayd/AI-pair-programming/commit/cc6f32d))
- **[✨ Features]** Update task prompts in create-task and expand-task scripts to include spec_file references ([cb9f50c](https://github.com/Ronnasayd/AI-pair-programming/commit/cb9f50c))
- **[♻️ Refactoring]** Simplify argument parsing and update task prompts in taskmaster scripts ([e65b1c2](https://github.com/Ronnasayd/AI-pair-programming/commit/e65b1c2))
- **[📚 Documentation]** Enhance execute-task skill documentation with xp principles and detailed workflow steps ([141c596](https://github.com/Ronnasayd/AI-pair-programming/commit/141c596))
- **[✨ Features]** Add taskmaster-prd-generator skill for generating structured prds ([9e80ee4](https://github.com/Ronnasayd/AI-pair-programming/commit/9e80ee4))

### **2026-03-19**

- **[✨ Features]** Rename log-tools-call script to log_tools_call and update references ([2983c45](https://github.com/Ronnasayd/AI-pair-programming/commit/2983c45))
- **[🐛 Bug Fixes]** Update command paths in settings.json to use environment variable and improve output structure in protect_files.py ([11f0d0c](https://github.com/Ronnasayd/AI-pair-programming/commit/11f0d0c))
- **[✨ Features]** Add centralized hook configuration and scripts for logging tool calls and file protection ([5f6c7f0](https://github.com/Ronnasayd/AI-pair-programming/commit/5f6c7f0))
- **[✨ Features]** Update hook configuration and generator script for output directory support ([2d4336c](https://github.com/Ronnasayd/AI-pair-programming/commit/2d4336c))
- **[✨ Features]** Remove deprecated logging scripts and add centralized hook configuration ([1b29618](https://github.com/Ronnasayd/AI-pair-programming/commit/1b29618))
- **[✨ Features]** Add log-tools-call script for logging tool calls ([b9d2d98](https://github.com/Ronnasayd/AI-pair-programming/commit/b9d2d98))
- **[🐛 Bug Fixes]** Remove debug print statement from json loading in protect_files.py ([ee0d89b](https://github.com/Ronnasayd/AI-pair-programming/commit/ee0d89b))
- **[✨ Features]** Replace shell script with python script for file protection logic ([8b64954](https://github.com/Ronnasayd/AI-pair-programming/commit/8b64954))
- **[📚 Documentation]** Correct spacing in section header for mandatory rules in agent instructions ([1bfb84c](https://github.com/Ronnasayd/AI-pair-programming/commit/1bfb84c))
- **[🐛 Bug Fixes]** Update codex installation script to use agents.toml for configuration and manage prompts directory ([6ca5c40](https://github.com/Ronnasayd/AI-pair-programming/commit/6ca5c40))
- **[📚 Documentation]** Update mandatory agents list in skill.md for code review ([3c04be1](https://github.com/Ronnasayd/AI-pair-programming/commit/3c04be1))
- **[📚 Documentation]** Update agent instructions and skill.md for improved code review guidelines ([32a9765](https://github.com/Ronnasayd/AI-pair-programming/commit/32a9765))
- **[🐛 Bug Fixes]** Disable enableconseca option in security settings ([195f094](https://github.com/Ronnasayd/AI-pair-programming/commit/195f094))
- **[🐛 Bug Fixes]** Update commandregex patterns to remove unnecessary word boundaries and improve command matching ([7fe9630](https://github.com/Ronnasayd/AI-pair-programming/commit/7fe9630))
- **[✨ Features]** Add make-code-review prompt for comprehensive security and quality assessment ([05a0579](https://github.com/Ronnasayd/AI-pair-programming/commit/05a0579))
- **[✨ Features]** Add code review prompt for comprehensive security and quality assessment ([86c5ced](https://github.com/Ronnasayd/AI-pair-programming/commit/86c5ced))
- **[🐛 Bug Fixes]** Correct prompts directory handling in copilot installation script ([a49dd06](https://github.com/Ronnasayd/AI-pair-programming/commit/a49dd06))
- **[✨ Features]** Add save-session command documentation for session state management ([4641190](https://github.com/Ronnasayd/AI-pair-programming/commit/4641190))
- **[🧹 Chores]** Update gemini installation script to handle commands directory and improve symlink management ([121bcd9](https://github.com/Ronnasayd/AI-pair-programming/commit/121bcd9))
- **[✨ Features]** Remove obsolete prompt files and update installation scripts for new command structure ([9354d6b](https://github.com/Ronnasayd/AI-pair-programming/commit/9354d6b))
- **[🧹 Chores]** Refactor installation scripts to use default_folder variable for consistency ([9b15da5](https://github.com/Ronnasayd/AI-pair-programming/commit/9b15da5))
- **[✨ Features]** Restore sonarqube configuration in settings.json ([42bb271](https://github.com/Ronnasayd/AI-pair-programming/commit/42bb271))
- **[🧹 Chores]** Disable sonarqube configuration and update mcp-server settings ([d4b43e6](https://github.com/Ronnasayd/AI-pair-programming/commit/d4b43e6))
- **[✨ Features]** Add atlassian server configuration with http type and url ([8536c1e](https://github.com/Ronnasayd/AI-pair-programming/commit/8536c1e))
- **[✨ Features]** Add github server configuration with http type and url ([7606ef4](https://github.com/Ronnasayd/AI-pair-programming/commit/7606ef4))
- **[✨ Features]** Add exa server configuration with http type and url ([258a913](https://github.com/Ronnasayd/AI-pair-programming/commit/258a913))
- **[✨ Features]** Add exa server configuration with http type and url ([df73e21](https://github.com/Ronnasayd/AI-pair-programming/commit/df73e21))
- **[✨ Features]** Add comprehensive documentation for srs generation, including templates, workflows, and guidelines for requirements analysis and task decomposition ([03e986d](https://github.com/Ronnasayd/AI-pair-programming/commit/03e986d))
- **[🧹 Chores]** Comment out codex installation script in install.sh ([61f8edb](https://github.com/Ronnasayd/AI-pair-programming/commit/61f8edb))
- **[✨ Features]** Add new skills for python testing, regex vs llm structured text parsing, and tdd workflow ([422adbe](https://github.com/Ronnasayd/AI-pair-programming/commit/422adbe))
- **[✨ Features]** Add comprehensive coding standards for javascript, typescript, react, node.js, c++, and content-hash caching pattern ([10cfb82](https://github.com/Ronnasayd/AI-pair-programming/commit/10cfb82))
- **[✨ Features]** Add ai-regression-testing and api-design skill documentation ([3ce66b9](https://github.com/Ronnasayd/AI-pair-programming/commit/3ce66b9))
- **[✨ Features]** Add agent-harness-construction skill documentation and enable codex installation script ([afa1099](https://github.com/Ronnasayd/AI-pair-programming/commit/afa1099))

### **2026-03-18**

- **[✨ Features]** Add mcp server configuration for figma and taskmaster in config.toml ([5a6e5c8](https://github.com/Ronnasayd/AI-pair-programming/commit/5a6e5c8))
- **[🧹 Chores]** Update gitignore installation script permissions ([d2f294b](https://github.com/Ronnasayd/AI-pair-programming/commit/d2f294b))
- **[✨ Features]** Update taskmaster installation scripts and improve gitignore management ([4568792](https://github.com/Ronnasayd/AI-pair-programming/commit/4568792))
- **[🐛 Bug Fixes]** Correct logic for copying taskmaster configuration and state files ([503dc62](https://github.com/Ronnasayd/AI-pair-programming/commit/503dc62))
- **[✨ Features]** Add taskmaster tasks directory to documentation search context ([02947e8](https://github.com/Ronnasayd/AI-pair-programming/commit/02947e8))
- **[✨ Features]** Rename taskmaster skills for consistency and update usage instructions in skill.md files ([c65649a](https://github.com/Ronnasayd/AI-pair-programming/commit/c65649a))
- **[✨ Features]** Add new skills for task management including append, create, and expand functionalities ([0dcd3ec](https://github.com/Ronnasayd/AI-pair-programming/commit/0dcd3ec))
- **[✨ Features]** Enhance task conversion with per-tag markdown generation and metadata extraction ([5ab5eaa](https://github.com/Ronnasayd/AI-pair-programming/commit/5ab5eaa))
- **[✨ Features]** Enhance task specification skills with additional argument options and improved usage instructions ([496e67e](https://github.com/Ronnasayd/AI-pair-programming/commit/496e67e))
- **[✨ Features]** Consolidate command execution rules into auto-saved.toml and remove rules.toml ([9c95357](https://github.com/Ronnasayd/AI-pair-programming/commit/9c95357))
- **[✨ Features]** Add security settings for tool approval and policy defaults in settings.json; create initial policy for shell command execution ([b462647](https://github.com/Ronnasayd/AI-pair-programming/commit/b462647))
- **[✨ Features]** Add policies for command execution rules in rules.toml and update gemini.install.sh for policies symlink ([a8b9f02](https://github.com/Ronnasayd/AI-pair-programming/commit/a8b9f02))
- **[✨ Features]** Add semantic commit message generation skill based on staged changes ([90415fa](https://github.com/Ronnasayd/AI-pair-programming/commit/90415fa))
- **[🧹 Chores]** Remove unused terminal and remote extension settings from configuration ([21ca47c](https://github.com/Ronnasayd/AI-pair-programming/commit/21ca47c))
- **[✨ Features]** Implement ai-jail script for sandboxing ai coding agents with customizable mounts ([56c5743](https://github.com/Ronnasayd/AI-pair-programming/commit/56c5743))
- **[✨ Features]** Enhance expand-task script with task id and prompt parameters for complexity analysis ([1046707](https://github.com/Ronnasayd/AI-pair-programming/commit/1046707))

### **2026-03-17**

- **[🧹 Chores]** Remove redundant command for expanding tasks in append-tasks.sh ([a913baf](https://github.com/Ronnasayd/AI-pair-programming/commit/a913baf))
- **[✨ Features]** Add configuration file for gemini model settings and global parameters ([76c37b2](https://github.com/Ronnasayd/AI-pair-programming/commit/76c37b2))
- **[✨ Features]** Add task-retrospective skill for structured evaluation and rule generation after task completion ([619f210](https://github.com/Ronnasayd/AI-pair-programming/commit/619f210))
- **[✨ Features]** Add agent-creator skill with comprehensive guidelines for creating and improving specialist agents ([a98d6e9](https://github.com/Ronnasayd/AI-pair-programming/commit/a98d6e9))
- **[🧹 Chores]** Update project dependencies to latest versions ([a2912f9](https://github.com/Ronnasayd/AI-pair-programming/commit/a2912f9))
- **[✨ Features]** Add tailwind config conformance skill with validation and refactoring capabilities ([ae4b843](https://github.com/Ronnasayd/AI-pair-programming/commit/ae4b843))
- **[✨ Features]** Enhance execute-task skill with detailed workflow and delegation guidelines ([656f13a](https://github.com/Ronnasayd/AI-pair-programming/commit/656f13a))
- **[✨ Features]** Implement model configuration loading and validation for copilot ollama proxy ([864a96b](https://github.com/Ronnasayd/AI-pair-programming/commit/864a96b))
- **[✨ Features]** Add frontend-design skill with comprehensive guidelines for creating high-quality interfaces ([51cd993](https://github.com/Ronnasayd/AI-pair-programming/commit/51cd993))
- **[✨ Features]** Add python mcp server implementation guide and evaluation scripts ([35f1d76](https://github.com/Ronnasayd/AI-pair-programming/commit/35f1d76))
- **[✨ Features]** Add skill-creator documentation for creating and improving skills ([6d9a1f3](https://github.com/Ronnasayd/AI-pair-programming/commit/6d9a1f3))
- **[♻️ Refactoring]** Simplify plan-generator skill description and structure ([1cc2ed1](https://github.com/Ronnasayd/AI-pair-programming/commit/1cc2ed1))
- **[✨ Features]** Add technical decision maker skill with structured workflow and analysis guidelines ([ee62a0b](https://github.com/Ronnasayd/AI-pair-programming/commit/ee62a0b))

### **2026-03-16**

- **[🐛 Bug Fixes]** Update agents.md references to use correct paths for instructions ([7dc9fc8](https://github.com/Ronnasayd/AI-pair-programming/commit/7dc9fc8))
- **[✨ Features]** Add symbolic links for instruction files in agents.md and create instructions directory ([cf7905a](https://github.com/Ronnasayd/AI-pair-programming/commit/cf7905a))
- **[♻️ Refactoring]** Remove exec prefix from task-master commands in task scripts ([21e656c](https://github.com/Ronnasayd/AI-pair-programming/commit/21e656c))
- **[🧹 Chores]** Comment out codex installation script in install.sh ([5d06b07](https://github.com/Ronnasayd/AI-pair-programming/commit/5d06b07))
- **[✨ Features]** Update install scripts to manage agents.md and improve gitignore entries ([117b432](https://github.com/Ronnasayd/AI-pair-programming/commit/117b432))
- **[✨ Features]** Implement task expansion skill and update task scripts for improved execution ([afbf225](https://github.com/Ronnasayd/AI-pair-programming/commit/afbf225))
- **[✨ Features]** Enhance append-tasks and create-task scripts with extreme programming workflow and task tagging ([1978d52](https://github.com/Ronnasayd/AI-pair-programming/commit/1978d52))
- **[🧹 Chores]** Remove deprecated execute_task command configuration ([b1d90d5](https://github.com/Ronnasayd/AI-pair-programming/commit/b1d90d5))
- **[✨ Features]** Update argument placeholders in skill.md files for consistency and clarity ([bb8fd66](https://github.com/Ronnasayd/AI-pair-programming/commit/bb8fd66))
- **[📚 Documentation]** Update description and task instructions for generate-docs-init skill ([4e203c9](https://github.com/Ronnasayd/AI-pair-programming/commit/4e203c9))
- **[✨ Features]** Update append-tasks skill with command execution instructions and add new script for task processing ([b50d91e](https://github.com/Ronnasayd/AI-pair-programming/commit/b50d91e))
- **[✨ Features]** Update create-task skill documentation with command execution instructions ([434be62](https://github.com/Ronnasayd/AI-pair-programming/commit/434be62))
- **[✨ Features]** Add code block formatting to prompts in md2tasks and tasks2md for improved clarity ([27d1afd](https://github.com/Ronnasayd/AI-pair-programming/commit/27d1afd))
- **[✨ Features]** Update prompts in md2tasks and tasks2md for clearer command execution instructions ([11840ba](https://github.com/Ronnasayd/AI-pair-programming/commit/11840ba))
- **[🐛 Bug Fixes]** Update symlink paths in installation scripts for prompts and commands ([f8720ae](https://github.com/Ronnasayd/AI-pair-programming/commit/f8720ae))
- **[✨ Features]** Remove deprecated prompts and add new task management commands ([4965f48](https://github.com/Ronnasayd/AI-pair-programming/commit/4965f48))
- **[✨ Features]** Add plan-generator skill for structured task and project planning ([3856ed0](https://github.com/Ronnasayd/AI-pair-programming/commit/3856ed0))
- **[✨ Features]** Add new benchmark files for agent documentation retrieval, code compliance, and orchestration ([ff3b243](https://github.com/Ronnasayd/AI-pair-programming/commit/ff3b243))
- **[✨ Features]** Add new benchmark files for agent orchestration and code compliance tests ([4c60122](https://github.com/Ronnasayd/AI-pair-programming/commit/4c60122))
- **[🐛 Bug Fixes]** Update documentation references to include 'docs/' prefix for consistency ([9494584](https://github.com/Ronnasayd/AI-pair-programming/commit/9494584))
- **[✨ Features]** Update instruction files and remove deprecated ones for improved clarity and organization ([b746ec0](https://github.com/Ronnasayd/AI-pair-programming/commit/b746ec0))
- **[🐛 Bug Fixes]** Update plan directory path in settings.json and adjust formatting in vscode.mcp.json ([9b0d6ab](https://github.com/Ronnasayd/AI-pair-programming/commit/9b0d6ab))
- **[✨ Features]** Add directwebfetch option and update respectgitignore setting in settings.json ([c382233](https://github.com/Ronnasayd/AI-pair-programming/commit/c382233))
- **[🧹 Chores]** Add 'docs/agents/' to .gitignore if not present ([484ecad](https://github.com/Ronnasayd/AI-pair-programming/commit/484ecad))
- **[🐛 Bug Fixes]** Update file paths in documentation to use 'docs/agents/' directory ([25b179d](https://github.com/Ronnasayd/AI-pair-programming/commit/25b179d))
- **[🐛 Bug Fixes]** Update file paths in documentation and settings to use 'docs/' directory ([8599bbe](https://github.com/Ronnasayd/AI-pair-programming/commit/8599bbe))
- **[✨ Features]** Add plan configuration and billing strategy to settings.json ([5a40366](https://github.com/Ronnasayd/AI-pair-programming/commit/5a40366))

### **2026-03-15**

- **[✨ Features]** Add checkpointing configuration to settings.json ([d92bf08](https://github.com/Ronnasayd/AI-pair-programming/commit/d92bf08))
- **[✨ Features]** Implement large prompt handling with attachment conversion and cleanup functions ([3e2e45e](https://github.com/Ronnasayd/AI-pair-programming/commit/3e2e45e))
- **[✨ Features]** Add task creation script with detailed execution workflow ([c28b3ce](https://github.com/Ronnasayd/AI-pair-programming/commit/c28b3ce))
- **[🐛 Bug Fixes]** Remove redundant reference headers in gemini.md updates ([801c83a](https://github.com/Ronnasayd/AI-pair-programming/commit/801c83a))
- **[✨ Features]** Implement setup function for instruction file symlinks and restore lessons instructions ([6a14329](https://github.com/Ronnasayd/AI-pair-programming/commit/6a14329))
- **[📚 Documentation]** Add mandatory guidelines for avoiding common pitfalls and best practices ([2557023](https://github.com/Ronnasayd/AI-pair-programming/commit/2557023))
- **[✨ Features]** Add task orchestration specialist agent and orchestration skill documentation ([3a4c8f9](https://github.com/Ronnasayd/AI-pair-programming/commit/3a4c8f9))

### **2026-03-14**

- **[🐛 Bug Fixes]** Update documentation path for generated rules file ([cdfd0e0](https://github.com/Ronnasayd/AI-pair-programming/commit/cdfd0e0))

### **2026-03-13**

- **[🧹 Chores]** Comment out codex installation script in install.sh ([c4dcd41](https://github.com/Ronnasayd/AI-pair-programming/commit/c4dcd41))
- **[🐛 Bug Fixes]** Rename 'prompt' to 'developer_instructions' in agent toml files ([50b621c](https://github.com/Ronnasayd/AI-pair-programming/commit/50b621c))
- **[🐛 Bug Fixes]** Rename developer_instructions to prompt for consistency in toml generation ([9da9ada](https://github.com/Ronnasayd/AI-pair-programming/commit/9da9ada))
- **[🐛 Bug Fixes]** Update variable names for clarity and enhance codex configuration validation ([1ccf50b](https://github.com/Ronnasayd/AI-pair-programming/commit/1ccf50b))
- **[🐛 Bug Fixes]** Update codex installation paths to use home directory ([56d21e1](https://github.com/Ronnasayd/AI-pair-programming/commit/56d21e1))
- **[🧹 Chores]** Comment out codex installation script in install.sh ([06d8c6a](https://github.com/Ronnasayd/AI-pair-programming/commit/06d8c6a))
- **[🐛 Bug Fixes]** Update codex installation script to use home directory for skills path ([cf99dd9](https://github.com/Ronnasayd/AI-pair-programming/commit/cf99dd9))
- **[🐛 Bug Fixes]** Correct syntax for agent_id in codex configuration generation ([bf36fbf](https://github.com/Ronnasayd/AI-pair-programming/commit/bf36fbf))
- **[✨ Features]** Add codebase-rules-extractor-specialist agent and skill documentation for code analysis ([3036548](https://github.com/Ronnasayd/AI-pair-programming/commit/3036548))
- **[🧹 Chores]** Comment out codex installation script in install.sh ([ff7cc01](https://github.com/Ronnasayd/AI-pair-programming/commit/ff7cc01))
- **[✨ Features]** Enhance codex installation script and configuration generation ([7f90c3d](https://github.com/Ronnasayd/AI-pair-programming/commit/7f90c3d))
- **[✨ Features]** Add missing .agent/agents/ entry to .gitignore in codex.install.sh ([11bc4fe](https://github.com/Ronnasayd/AI-pair-programming/commit/11bc4fe))
- **[✨ Features]** Update install.sh to dynamically set source and local based on script location ([2edc1f3](https://github.com/Ronnasayd/AI-pair-programming/commit/2edc1f3))
- **[✨ Features]** Add md2toml.py for converting markdown files to toml format and update install scripts ([2a33350](https://github.com/Ronnasayd/AI-pair-programming/commit/2a33350))
- **[✨ Features]** Replace converter.py with toml2md.py for toml to markdown conversion ([6d93e69](https://github.com/Ronnasayd/AI-pair-programming/commit/6d93e69))

### **2026-03-12**

- **[✨ Features]** Enable respect for .gitignore in file filtering configuration ([1a5c481](https://github.com/Ronnasayd/AI-pair-programming/commit/1a5c481))
- **[✨ Features]** Add context configuration for file filtering in settings.json ([9fb9ba4](https://github.com/Ronnasayd/AI-pair-programming/commit/9fb9ba4))
- **[✨ Features]** Add chrome-devtools command to vscode.mcp.json and update installation script for mcp.json symlink ([0bab1d5](https://github.com/Ronnasayd/AI-pair-programming/commit/0bab1d5))
- **[✨ Features]** Add mcp-server-enablement.json and update installation script for server configuration ([4fb36b5](https://github.com/Ronnasayd/AI-pair-programming/commit/4fb36b5))
- **[✨ Features]** Add append-tasks-taskmaster skill for enhancing task specifications with new context and action plans ([7ae0d06](https://github.com/Ronnasayd/AI-pair-programming/commit/7ae0d06))
- **[✨ Features]** Add prd-reviewer-specialist and test-coverage-specialist agents with detailed analysis frameworks ([750ada8](https://github.com/Ronnasayd/AI-pair-programming/commit/750ada8))
- **[✨ Features]** Add create-task-taskmaster skill for generating structured task specifications ([72c64d3](https://github.com/Ronnasayd/AI-pair-programming/commit/72c64d3))
- **[✨ Features]** Create new skill for generating structured task specifications based on detailed analysis ([f0ff28b](https://github.com/Ronnasayd/AI-pair-programming/commit/f0ff28b))
- **[📚 Documentation]** Enhance skill.md with compact specification best practices and formatting guidelines ([50ac5d6](https://github.com/Ronnasayd/AI-pair-programming/commit/50ac5d6))
- **[🐛 Bug Fixes]** Correct task and impact sections in pr description template for clarity ([46e2fe0](https://github.com/Ronnasayd/AI-pair-programming/commit/46e2fe0))
- **[✨ Features]** Add generate-pr-description skill for automated pr description generation ([f1ae373](https://github.com/Ronnasayd/AI-pair-programming/commit/f1ae373))

### **2026-03-11**

- **[✨ Features]** Add orchestration instructions and update references in installation scripts ([9d85313](https://github.com/Ronnasayd/AI-pair-programming/commit/9d85313))
- **[✨ Features]** Add tdd guidelines and steps for writing tests in skill.md ([440f2ca](https://github.com/Ronnasayd/AI-pair-programming/commit/440f2ca))
- **[🐛 Bug Fixes]** Update tool references in create_task and execute_task prompts for consistency ([7aa649b](https://github.com/Ronnasayd/AI-pair-programming/commit/7aa649b))
- **[🐛 Bug Fixes]** Update tool references in create_task and execute_task prompts for consistency ([8d74dd1](https://github.com/Ronnasayd/AI-pair-programming/commit/8d74dd1))
- **[✨ Features]** Add new skills for task management and documentation generation ([830ed33](https://github.com/Ronnasayd/AI-pair-programming/commit/830ed33))
- **[📚 Documentation]** Update changelog for version 2026.03.11 with new features and chore updates ([0604fba](https://github.com/Ronnasayd/AI-pair-programming/commit/0604fba))
- **[🐛 Bug Fixes]** Correct file path key in protect-files script for consistency ([ca72d14](https://github.com/Ronnasayd/AI-pair-programming/commit/ca72d14))
- **[✨ Features]** Add protect-files hook and script to block access to sensitive files ([c82c55a](https://github.com/Ronnasayd/AI-pair-programming/commit/c82c55a))
- **[✨ Features]** Update documentation generation instructions to enforce agent usage ([cfc39d5](https://github.com/Ronnasayd/AI-pair-programming/commit/cfc39d5))
- **[✨ Features]** Update documentation generation tools to enforce agent usage and remove developer instructions ([85db3cd](https://github.com/Ronnasayd/AI-pair-programming/commit/85db3cd))
- **[✨ Features]** Remove my_mcp_generate_docs_update tool and add generate-docs-update skill for structured documentation updates ([8c03b9b](https://github.com/Ronnasayd/AI-pair-programming/commit/8c03b9b))
- **[🧹 Chores]** Update command execution instructions for code review skill to allow alternative diff-like outputs ([1fab49f](https://github.com/Ronnasayd/AI-pair-programming/commit/1fab49f))
- **[✨ Features]** Implement code review skill with structured analysis instructions ([dc93b30](https://github.com/Ronnasayd/AI-pair-programming/commit/dc93b30))

### **2026-03-10**

- **[🧹 Chores]** Remove my_mcp_run_command tool from the server implementation ([cd6d461](https://github.com/Ronnasayd/AI-pair-programming/commit/cd6d461))
- **[✨ Features]** Enhance task creation instructions with user confirmation for single or multiple tasks ([78a4f01](https://github.com/Ronnasayd/AI-pair-programming/commit/78a4f01))
- **[✨ Features]** Add codex installation script and update .gitignore for agent skills ([50957a5](https://github.com/Ronnasayd/AI-pair-programming/commit/50957a5))
- **[📚 Documentation]** Update changelog for version 2026.03.10 with new features and chore updates ([4b49fca](https://github.com/Ronnasayd/AI-pair-programming/commit/4b49fca))
- **[✨ Features]** Add comprehensive readme.md for ai pair programming workspace with project overview, key directories, and usage instructions ([f2f1f70](https://github.com/Ronnasayd/AI-pair-programming/commit/f2f1f70))
- **[✨ Features]** Consolidate gitignore updates into installation scripts and remove redundant gitignore.install.sh ([28b99d9](https://github.com/Ronnasayd/AI-pair-programming/commit/28b99d9))
- **[✨ Features]** Add installation scripts for github copilot, gemini, gitignore, and taskmaster ([1bda522](https://github.com/Ronnasayd/AI-pair-programming/commit/1bda522))
- **[✨ Features]** Add logging hooks for session start, end, and user prompt submission ([f11588d](https://github.com/Ronnasayd/AI-pair-programming/commit/f11588d))
- **[✨ Features]** Add comprehensive reactjs development standards and best practices documentation ([16e6542](https://github.com/Ronnasayd/AI-pair-programming/commit/16e6542))
- **[📚 Documentation]** Update changelog for version 2026.03.10 with new features and chore updates ([1fc4877](https://github.com/Ronnasayd/AI-pair-programming/commit/1fc4877))
- **[✨ Features]** Add reference check for github copilot instructions in gemini.md ([551aac7](https://github.com/Ronnasayd/AI-pair-programming/commit/551aac7))
- **[✨ Features]** Add context architect specialist and context map skills for multi-file change planning ([befedbe](https://github.com/Ronnasayd/AI-pair-programming/commit/befedbe))
- **[✨ Features]** Add figma design system to tailwind css conversion skill documentation ([0fc1067](https://github.com/Ronnasayd/AI-pair-programming/commit/0fc1067))
- **[🧹 Chores]** Update project dependencies to latest versions ([bec284b](https://github.com/Ronnasayd/AI-pair-programming/commit/bec284b))
- **[✨ Features]** Add tailwind css documentation and configuration resources ([5e84421](https://github.com/Ronnasayd/AI-pair-programming/commit/5e84421))

### **2026-03-09**

- **[🧹 Chores]** Update changelog for version 2026.03.09 with new features, bug fixes, and documentation improvements ([86fd8d3](https://github.com/Ronnasayd/AI-pair-programming/commit/86fd8d3))
- **[✨ Features]** Add environment preferences for javascript/typescript and python projects in instructions ([f21fbd0](https://github.com/Ronnasayd/AI-pair-programming/commit/f21fbd0))
- **[🐛 Bug Fixes]** Correct symlink creation for gemini settings.json in install script ([a1d83b9](https://github.com/Ronnasayd/AI-pair-programming/commit/a1d83b9))
- **[✨ Features]** Add symlink creation for gemini settings.json in install script ([903ff4f](https://github.com/Ronnasayd/AI-pair-programming/commit/903ff4f))
- **[✨ Features]** Add new settings configuration for mcp servers and ui preferences ([e96806f](https://github.com/Ronnasayd/AI-pair-programming/commit/e96806f))
- **[🧹 Chores]** Remove unused api key and token from context7 and sonarqube configurations ([58d850b](https://github.com/Ronnasayd/AI-pair-programming/commit/58d850b))
- **[✨ Features]** Add comprehensive git-guide skill with detailed commands and workflows ([79ded6c](https://github.com/Ronnasayd/AI-pair-programming/commit/79ded6c))
- **[✨ Features]** Add git-specialist agent with comprehensive git and devops guidance ([ac811ca](https://github.com/Ronnasayd/AI-pair-programming/commit/ac811ca))
- **[📚 Documentation]** Add comprehensive testing guidelines for typescript/node.js backend projects ([8b275d0](https://github.com/Ronnasayd/AI-pair-programming/commit/8b275d0))
- **[📚 Documentation]** Update description in execute_task prompt for clarity and add new figma mcp skill documentation ([1685c1b](https://github.com/Ronnasayd/AI-pair-programming/commit/1685c1b))
- **[📚 Documentation]** Improve description clarity in execute_task prompt ([e098d21](https://github.com/Ronnasayd/AI-pair-programming/commit/e098d21))
- **[📚 Documentation]** Add comprehensive guidelines for srs and testing in typescript/node.js backend projects ([8fc620a](https://github.com/Ronnasayd/AI-pair-programming/commit/8fc620a))
- **[✨ Features]** Add new prompts for creating react components and simulating roundtable discussions ([29c64ae](https://github.com/Ronnasayd/AI-pair-programming/commit/29c64ae))
- **[📚 Documentation]** Refine go style guide for clarity and conciseness ([551e02d](https://github.com/Ronnasayd/AI-pair-programming/commit/551e02d))
- **[✨ Features]** Enhance copilot instructions with delegation and skill usage guidelines ([86172fa](https://github.com/Ronnasayd/AI-pair-programming/commit/86172fa))
- **[📚 Documentation]** Update python style guide with modern conventions and best practices ([ed23c62](https://github.com/Ronnasayd/AI-pair-programming/commit/ed23c62))
- **[✨ Features]** Add file processing patterns, token estimation strategies, tools reference, and analysis scripts ([f4ff436](https://github.com/Ronnasayd/AI-pair-programming/commit/f4ff436))
- **[🧹 Chores]** Update .gitignore and gemini.md references in install script ([c2761ed](https://github.com/Ronnasayd/AI-pair-programming/commit/c2761ed))
- **[✨ Features]** Add taskmaster skill with project management workflows and command references ([3da8e4b](https://github.com/Ronnasayd/AI-pair-programming/commit/3da8e4b))
- **[♻️ Refactoring]** Enhance clarity and consistency in skill architect documentation ([ae4c190](https://github.com/Ronnasayd/AI-pair-programming/commit/ae4c190))
- **[✨ Features]** Add skill architect agent with comprehensive guidelines for designing and optimizing claude agent skills ([9633798](https://github.com/Ronnasayd/AI-pair-programming/commit/9633798))
- **[📚 Documentation]** Restructure and clarify code generation instructions in copilot guide ([59c592d](https://github.com/Ronnasayd/AI-pair-programming/commit/59c592d))

### **2026-03-07**

- **[✨ Features]** Add developer planning specialist agent with detailed instructions and responsibilities ([3c975fa](https://github.com/Ronnasayd/AI-pair-programming/commit/3c975fa))
- **[♻️ Refactoring]** Update task creation and execution prompts for clarity and consistency ([4969b5d](https://github.com/Ronnasayd/AI-pair-programming/commit/4969b5d))
- **[✨ Features]** Add comprehensive guidelines for srs generation and testing in typescript/node.js backend projects ([cfae9c5](https://github.com/Ronnasayd/AI-pair-programming/commit/cfae9c5))
- **[✨ Features]** Add new specialist agents for srs generation and frontend refactoring with detailed instructions ([1e07007](https://github.com/Ronnasayd/AI-pair-programming/commit/1e07007))
- **[♻️ Refactoring]** Remove unused tools section from prd and review-refactor specialist documentation chore: update install script to copy agents instead of creating symbolic links ([c10f990](https://github.com/Ronnasayd/AI-pair-programming/commit/c10f990))
- **[♻️ Refactoring]** Remove unused tools section from various specialist agent documentation ([586abba](https://github.com/Ronnasayd/AI-pair-programming/commit/586abba))
- **[✨ Features]** Add tools section to various specialist agents for enhanced functionality ([a0ab77a](https://github.com/Ronnasayd/AI-pair-programming/commit/a0ab77a))
- **[✨ Features]** Add new agent specialists for prd generation, review, srs generation, product ownership, and task reviewing ([8e7ff13](https://github.com/Ronnasayd/AI-pair-programming/commit/8e7ff13))
- **[✨ Features]** Add new specialist agents for documentation, usability, teaching, generative ai, and code review ([0e93ba6](https://github.com/Ronnasayd/AI-pair-programming/commit/0e93ba6))
- **[✨ Features]** Add database specialist and usability agent with detailed instructions ([427a93e](https://github.com/Ronnasayd/AI-pair-programming/commit/427a93e))
- **[✨ Features]** Add cybersecurity agent with detailed instructions and update .gitignore for new directories ([fd7ade7](https://github.com/Ronnasayd/AI-pair-programming/commit/fd7ade7))
- **[✨ Features]** Enhance task creation and execution prompts with detailed tool instructions ([1073a4c](https://github.com/Ronnasayd/AI-pair-programming/commit/1073a4c))
- **[✨ Features]** Update task prompts for mcp developer guidance and enhance documentation ([acc6b7e](https://github.com/Ronnasayd/AI-pair-programming/commit/acc6b7e))
- **[✨ Features]** Recreate and enhance task prompts for mcp developer guidance ([5ee3157](https://github.com/Ronnasayd/AI-pair-programming/commit/5ee3157))
- **[🧹 Chores]** Update .gitignore to include new directories for github and taskmaster ([0c589f9](https://github.com/Ronnasayd/AI-pair-programming/commit/0c589f9))
- **[✨ Features]** Add comprehensive testing guidelines for typescript/node.js backend projects ([9f09f67](https://github.com/Ronnasayd/AI-pair-programming/commit/9f09f67))
- **[✨ Features]** Add golang style guide documentation for readability and maintainability ([baf28c6](https://github.com/Ronnasayd/AI-pair-programming/commit/baf28c6))
- **[✨ Features]** Add python and typescript style guide documentation ([e714c2a](https://github.com/Ronnasayd/AI-pair-programming/commit/e714c2a))
- **[✨ Features]** Add gemini and github copilot sections to install.sh; implement taskmaster setup and state management ([c729894](https://github.com/Ronnasayd/AI-pair-programming/commit/c729894))
- **[🧹 Chores]** Reorganize install.sh script for better structure and clarity ([0a4558a](https://github.com/Ronnasayd/AI-pair-programming/commit/0a4558a))
- **[✨ Features]** Add prompts for creating and executing tasks for mcp developers ([2ac8cb3](https://github.com/Ronnasayd/AI-pair-programming/commit/2ac8cb3))
- **[🧹 Chores]** Restructure install.sh script and update typescript skill description for clarity ([f285248](https://github.com/Ronnasayd/AI-pair-programming/commit/f285248))
- **[✨ Features]** Update python skill description for clarity and conciseness ([217da13](https://github.com/Ronnasayd/AI-pair-programming/commit/217da13))

### **2026-03-06**

- **[🧹 Chores]** Remove task implementation steps from copilot instructions ([0913abb](https://github.com/Ronnasayd/AI-pair-programming/commit/0913abb))
- **[✨ Features]** Add python style guide for coding conventions and best practices ([094d9b1](https://github.com/Ronnasayd/AI-pair-programming/commit/094d9b1))
- **[✨ Features]** Add typescript style guide for coding conventions and best practices ([28d9e49](https://github.com/Ronnasayd/AI-pair-programming/commit/28d9e49))
- **[✨ Features]** Add install.sh script for symlinking task configuration files ([6d4e1ef](https://github.com/Ronnasayd/AI-pair-programming/commit/6d4e1ef))
- **[✨ Features]** Add create_task.toml for task creation instructions and tools ([0dcc07c](https://github.com/Ronnasayd/AI-pair-programming/commit/0dcc07c))

### **2026-03-05**

- **[✨ Features]** Add write_todos tool to execute_task.toml for task execution guidance ([416e46a](https://github.com/Ronnasayd/AI-pair-programming/commit/416e46a))
- **[✨ Features]** Add execute_task.toml for task execution instructions and tools ([79faf4d](https://github.com/Ronnasayd/AI-pair-programming/commit/79faf4d))
- **[🧹 Chores]** Update sensitive api keys in gemini.mcp.json and vscode.mcp.json to placeholders ([30fa397](https://github.com/Ronnasayd/AI-pair-programming/commit/30fa397))
- **[✨ Features]** Add new mcp.json and vscode.mcp.json configurations for server setup ([7dc7982](https://github.com/Ronnasayd/AI-pair-programming/commit/7dc7982))
- **[✨ Features]** Add mcp.json configuration for server setup and environment variables ([d0168ed](https://github.com/Ronnasayd/AI-pair-programming/commit/d0168ed))

### **2026-03-03**

- **[✨ Features]** Add comprehensive instructions for technical analysis and requirement assessment ([a9aea5e](https://github.com/Ronnasayd/AI-pair-programming/commit/a9aea5e))

### **2026-02-21**

- **[✨ Features]** Add comprehensive instructions for generative ai specialists to enhance workflow and problem-solving capabilities ([31e2e7a](https://github.com/Ronnasayd/AI-pair-programming/commit/31e2e7a))

### **2026-02-11**

- **[✨ Features]** Add context map section to task creation for improved documentation and clarity ([fdc84e0](https://github.com/Ronnasayd/AI-pair-programming/commit/fdc84e0))

### **2026-02-08**

- **[✨ Features]** Add optional filter parameter to documentation sync tool for targeted git diff ([71a3d69](https://github.com/Ronnasayd/AI-pair-programming/commit/71a3d69))
- **[✨ Features]** Add documentation synchronization tool to generate context from git diff ([0d5cb76](https://github.com/Ronnasayd/AI-pair-programming/commit/0d5cb76))

### **2026-02-05**

- **[✨ Features]** Add comprehensive testing guidelines for typescript/node.js backend projects ([345d9fb](https://github.com/Ronnasayd/AI-pair-programming/commit/345d9fb))
- **[✨ Features]** Enhance copilot instructions for clarity and structure in code generation tasks ([9074f69](https://github.com/Ronnasayd/AI-pair-programming/commit/9074f69))
- **[✨ Features]** Update code review output rules and structure for improved clarity and compliance ([2d1de4a](https://github.com/Ronnasayd/AI-pair-programming/commit/2d1de4a))
- **[✨ Features]** Enhance code review process with structured output rules and detailed task analysis instructions ([e71e500](https://github.com/Ronnasayd/AI-pair-programming/commit/e71e500))
- **[✨ Features]** Enhance task creation workflow with detailed phases for context discovery, specification generation, and user review ([1810109](https://github.com/Ronnasayd/AI-pair-programming/commit/1810109))
- **[🐛 Bug Fixes]** Clarify task implementation instructions and emphasize rule precedence ([c3d772f](https://github.com/Ronnasayd/AI-pair-programming/commit/c3d772f))
- **[🐛 Bug Fixes]** Correct task creation instructions and improve code comments for clarity ([63ac4fd](https://github.com/Ronnasayd/AI-pair-programming/commit/63ac4fd))
- **[🚧 Other Changes]** Format code for improved readability and consistency ([5bd5ef2](https://github.com/Ronnasayd/AI-pair-programming/commit/5bd5ef2))
- **[✨ Features]** Refactor instruction loading to use dedicated functions for improved readability and maintainability ([48a1c4a](https://github.com/Ronnasayd/AI-pair-programming/commit/48a1c4a))

### **2026-02-03**

- **[✨ Features]** Enhance code review instructions with detailed task creation workflow ([ca43a0a](https://github.com/Ronnasayd/AI-pair-programming/commit/ca43a0a))

### **2026-01-30**

- **[🐛 Bug Fixes]** Remove unnecessary comment from task creation function ([c84c735](https://github.com/Ronnasayd/AI-pair-programming/commit/c84c735))
- **[✨ Features]** Enhance task creation instructions to include web search for documentation ([d5eef0b](https://github.com/Ronnasayd/AI-pair-programming/commit/d5eef0b))
- **[✨ Features]** Update task creation instructions and modify model configuration for improved task description generation ([8218f39](https://github.com/Ronnasayd/AI-pair-programming/commit/8218f39))

### **2026-01-27**

- **[✨ Features]** Add comprehensive design conversion instructions for react components ([1f9425d](https://github.com/Ronnasayd/AI-pair-programming/commit/1f9425d))

### **2026-01-26**

- **[✨ Features]** Update task creation instructions to include dynamic filename for generated task specs ([69a812c](https://github.com/Ronnasayd/AI-pair-programming/commit/69a812c))
- **[✨ Features]** Update task creation instructions to include user review step before executing terminal commands ([cddc0ab](https://github.com/Ronnasayd/AI-pair-programming/commit/cddc0ab))
- **[✨ Features]** Add unchangeable text block to task creation workflow instructions ([112ef31](https://github.com/Ronnasayd/AI-pair-programming/commit/112ef31))
- **[✨ Features]** Add command to expand tasks in task creation instructions ([70bc58a](https://github.com/Ronnasayd/AI-pair-programming/commit/70bc58a))
- **[✨ Features]** Update task creation instructions to include terminal command execution ([5133494](https://github.com/Ronnasayd/AI-pair-programming/commit/5133494))
- **[✨ Features]** Refine task creation instructions for clarity and format adherence ([aef63b9](https://github.com/Ronnasayd/AI-pair-programming/commit/aef63b9))
- **[✨ Features]** Restore task reviewer instructions with detailed guidelines for task refinement and team interaction ([2f4fba9](https://github.com/Ronnasayd/AI-pair-programming/commit/2f4fba9))
- **[✨ Features]** Add task creation tool with detailed instructions for taskmaster integration ([beaae58](https://github.com/Ronnasayd/AI-pair-programming/commit/beaae58))
- **[✨ Features]** Enhance search functionality by adding top_n parameter for result ranking ([d7dfb00](https://github.com/Ronnasayd/AI-pair-programming/commit/d7dfb00))

### **2026-01-21**

- **[✨ Features]** Remove outdated run command instructions and add style guide references for code generation ([664fb74](https://github.com/Ronnasayd/AI-pair-programming/commit/664fb74))

### **2026-01-20**

- **[✨ Features]** Update copilot instructions and enhance task implementation guidelines for clarity and completeness ([a480ebd](https://github.com/Ronnasayd/AI-pair-programming/commit/a480ebd))

### **2025-12-21**

- **[✨ Features]** Translate and update instructions for srs and tasks generation to english, enhancing clarity and consistency ([d4ac57c](https://github.com/Ronnasayd/AI-pair-programming/commit/d4ac57c))

### **2025-12-19**

- **[✨ Features]** Restore and update guidelines for asking questions ([eab61c3](https://github.com/Ronnasayd/AI-pair-programming/commit/eab61c3))
- **[✨ Features]** Add guidelines for asking questions and integrate into mcp server ([ea40f06](https://github.com/Ronnasayd/AI-pair-programming/commit/ea40f06))
- **[🧹 Chores]** Translate to english ([80fef8e](https://github.com/Ronnasayd/AI-pair-programming/commit/80fef8e))
- **[🧹 Chores]** Translate to english ([634e525](https://github.com/Ronnasayd/AI-pair-programming/commit/634e525))

### **2025-12-16**

- **[📚 Documentation]** Translate instructions to english for consistency and clarity ([7bed78e](https://github.com/Ronnasayd/AI-pair-programming/commit/7bed78e))
- **[🐛 Bug Fixes]** Update error messages to english for consistency and clarity ([61a7ee2](https://github.com/Ronnasayd/AI-pair-programming/commit/61a7ee2))
- **[📚 Documentation]** Update developer instructions to improve clarity and consistency in software development guidelines ([439f1ad](https://github.com/Ronnasayd/AI-pair-programming/commit/439f1ad))
- **[✨ Features]** Add comprehensive guidelines for english language teaching and assessment ([a4cebe2](https://github.com/Ronnasayd/AI-pair-programming/commit/a4cebe2))

### **2025-12-15**

- **[✨ Features]** Enhance task markdown generation to include descriptions and additional fields ([f3a41a1](https://github.com/Ronnasayd/AI-pair-programming/commit/f3a41a1))
- **[📚 Documentation]** Add validation instructions for rules, avoidance, preview code, and action plan ([13ef62c](https://github.com/Ronnasayd/AI-pair-programming/commit/13ef62c))

### **2025-12-05**

- **[🐛 Bug Fixes]** Enhance attachment extraction logic to handle file paths and improve matching ([4e369d1](https://github.com/Ronnasayd/AI-pair-programming/commit/4e369d1))
- **[🐛 Bug Fixes]** Update version numbers in root and version endpoints to 0.6.4 ([a35d0cc](https://github.com/Ronnasayd/AI-pair-programming/commit/a35d0cc))

### **2025-12-04**

- **[📚 Documentation]** Add comprehensive usability documentation and workflow guidelines ([34e3c78](https://github.com/Ronnasayd/AI-pair-programming/commit/34e3c78))

### **2025-12-01**

- **[♻️ Refactoring]** Rename functions to include 'mcp' prefix for consistency ([0394b32](https://github.com/Ronnasayd/AI-pair-programming/commit/0394b32))

### **2025-11-27**

- **[📚 Documentation]** Add instruction to include relevant code snippets in markdown format ([25be9d4](https://github.com/Ronnasayd/AI-pair-programming/commit/25be9d4))
- **[🐛 Bug Fixes]** Improve attachment extraction logic to handle optional comments in file paths ([c8465c0](https://github.com/Ronnasayd/AI-pair-programming/commit/c8465c0))

### **2025-11-18**

- **[🧹 Chores]** Add new dependencies to requirements.txt ([f78bcfe](https://github.com/Ronnasayd/AI-pair-programming/commit/f78bcfe))

### **2025-11-14**

- **[📚 Documentation]** Enhance workflow instructions for task implementation with detailed checks and references ([dd5629b](https://github.com/Ronnasayd/AI-pair-programming/commit/dd5629b))

### **2025-10-30**

- **[📚 Documentation]** Add task_master section with detailed task workflow instructions ([a75ad3e](https://github.com/Ronnasayd/AI-pair-programming/commit/a75ad3e))

### **2025-10-29**

- **[📚 Documentation]** Add initial changelog entries for 2025‑10‑29 and update generate‑documentation instructions ([9e7f5c7](https://github.com/Ronnasayd/AI-pair-programming/commit/9e7f5c7))
- **[📚 Documentation]** Add initial changelog entries for 2025‑10‑29 with features, bug fixes, documentation updates, and refactoring details ([ef736d1](https://github.com/Ronnasayd/AI-pair-programming/commit/ef736d1))
- **[✨ Features]** Add initial changelog with features, bug fixes, documentation updates, and refactoring details ([b6a8eb6](https://github.com/Ronnasayd/AI-pair-programming/commit/b6a8eb6))
- **[📚 Documentation]** Update generate-documentation instructions with detailed file purpose and structure guidelines ([56e439b](https://github.com/Ronnasayd/AI-pair-programming/commit/56e439b))

### **2025-10-24**

- **[✨ Features]** Enable headless mode in get_cookies function for improved automation ([cfd3629](https://github.com/Ronnasayd/AI-pair-programming/commit/cfd3629))
- **[✨ Features]** Add comprehensive cybersecurity instructions for secure software development and operations ([bf17790](https://github.com/Ronnasayd/AI-pair-programming/commit/bf17790))
- **[✨ Features]** Add comprehensive coding guidelines and best practices to copilot.instructions.md ([759be39](https://github.com/Ronnasayd/AI-pair-programming/commit/759be39))

### **2025-10-21**

- **[✨ Features]** Enhance my_search_references function to support optional rootproject and globs parameters; add ag_search function for improved codebase searching ([d8749c2](https://github.com/Ronnasayd/AI-pair-programming/commit/d8749c2))

### **2025-10-20**

- **[✨ Features]** Implement search functionality in search_engine module; add my_search_references tool and update developer instructions ([96cc91b](https://github.com/Ronnasayd/AI-pair-programming/commit/96cc91b))

### **2025-10-13**

- **[✨ Features]** Add prd generation instructions and template handling in my_generate_prd function; update documentation workflow instructions ([a0e17ce](https://github.com/Ronnasayd/AI-pair-programming/commit/a0e17ce))

### **2025-10-10**

- **[✨ Features]** Add my_generate_docs_init function to return documentation generation instructions ([fbd9a35](https://github.com/Ronnasayd/AI-pair-programming/commit/fbd9a35))
- **[📚 Documentation]** Enhance documentation structure and provide detailed file descriptions in generate-documentation.instructions.md ([02d25a6](https://github.com/Ronnasayd/AI-pair-programming/commit/02d25a6))
- **[✨ Features]** Add documentation workflow instructions and enhance git diff handling in my_generate_docs_update function ([92a69c1](https://github.com/Ronnasayd/AI-pair-programming/commit/92a69c1))

### **2025-10-09**

- **[✨ Features]** Add input_text extraction from request body in generate_embeddings function ([9c945ad](https://github.com/Ronnasayd/AI-pair-programming/commit/9c945ad))
- **[🧹 Chores]** Update logging file path to /tmp for consistency across modules ([67c8582](https://github.com/Ronnasayd/AI-pair-programming/commit/67c8582))

### **2025-10-07**

- **[✨ Features]** Update my_get_context function to accept multiple parameters for context generation ([1475755](https://github.com/Ronnasayd/AI-pair-programming/commit/1475755))
- **[♻️ Refactoring]** Update my_run_command to use rootproject instead of cwd for directory execution ([56e1614](https://github.com/Ronnasayd/AI-pair-programming/commit/56e1614))

### **2025-10-03**

- **[✨ Features]** Add task implementation instructions and attachment references to prompt documentation ([b77f002](https://github.com/Ronnasayd/AI-pair-programming/commit/b77f002))

### **2025-10-02**

- **[♻️ Refactoring]** Clean up attachment extraction logic and improve prompt handling in chat function ([f3efc59](https://github.com/Ronnasayd/AI-pair-programming/commit/f3efc59))
- **[✨ Features]** Add attachment extraction function and integrate it into chat completion process ([fb9c7e0](https://github.com/Ronnasayd/AI-pair-programming/commit/fb9c7e0))
- **[♻️ Refactoring]** Enhance file exclusion logic and improve read_file function parameters ([da404ef](https://github.com/Ronnasayd/AI-pair-programming/commit/da404ef))

### **2025-10-01**

- **[✨ Features]** Add meta extraction and merging functions for tasks and subtasks in my_mcp_server ([19495cb](https://github.com/Ronnasayd/AI-pair-programming/commit/19495cb))
- **[✨ Features]** Add my_developer_workflow function to load and return developer workflow instructions ([fbaa6fc](https://github.com/Ronnasayd/AI-pair-programming/commit/fbaa6fc))
- **[♻️ Refactoring]** Improve path handling and enhance markdown generation in my_mcp_server ([023f36a](https://github.com/Ronnasayd/AI-pair-programming/commit/023f36a))
- **[✨ Features]** Add my_styleguide function to return style guide for specified programming language ([834ee34](https://github.com/Ronnasayd/AI-pair-programming/commit/834ee34))
- **[🧹 Chores]** Update .gitignore to include .github and remove teste.py file ([f89a084](https://github.com/Ronnasayd/AI-pair-programming/commit/f89a084))

### **2025-09-30**

- **[♻️ Refactoring]** Enhance logging in chat method and adjust response handling in call_copilot ([c6f009b](https://github.com/Ronnasayd/AI-pair-programming/commit/c6f009b))

### **2025-09-29**

- **[✨ Features]** Convert call_copilot function to asynchronous and update api calls accordingly ([00b5725](https://github.com/Ronnasayd/AI-pair-programming/commit/00b5725))
- **[✨ Features]** Refactor copilotapi methods to be asynchronous and update authentication flow ([3c3f31f](https://github.com/Ronnasayd/AI-pair-programming/commit/3c3f31f))

### **2025-09-27**

- **[♻️ Refactoring]** Update logging level to info and streamline logging configuration in copilotapi and ollama ([1ced442](https://github.com/Ronnasayd/AI-pair-programming/commit/1ced442))
- **[✨ Features]** Implement streaming response handling in call_copilot function and add test script for openai integration ([982354a](https://github.com/Ronnasayd/AI-pair-programming/commit/982354a))
- **[♻️ Refactoring]** Simplify chat response handling and remove unused chat_complete method ([00cd6b8](https://github.com/Ronnasayd/AI-pair-programming/commit/00cd6b8))
- **[♻️ Refactoring]** Update logging configuration to debug level and replace logging calls with logger instance in copilotapi ([bff3186](https://github.com/Ronnasayd/AI-pair-programming/commit/bff3186))
- **[✨ Features]** Refactor get_cookies function to be asynchronous and update related calls in copilotapi ([812750b](https://github.com/Ronnasayd/AI-pair-programming/commit/812750b))
- **[✨ Features]** Enhance logging in copilotapi chat methods for improved debugging ([5aa51fc](https://github.com/Ronnasayd/AI-pair-programming/commit/5aa51fc))
- **[✨ Features]** Add logging to copilotapi methods for better traceability ([17970a5](https://github.com/Ronnasayd/AI-pair-programming/commit/17970a5))
- **[✨ Features]** Add comprehensive developer instructions for software development and debugging processes ([0d22fd9](https://github.com/Ronnasayd/AI-pair-programming/commit/0d22fd9))

### **2025-09-25**

- **[♻️ Refactoring]** Update my_code_review and my_convert_markdown_to_tasks functions to use rootproject parameter instead of cwd ([6747bf6](https://github.com/Ronnasayd/AI-pair-programming/commit/6747bf6))
- **[✨ Features]** Refactor my_convert_markdown_to_tasks function to accept cwd and create tasks.json in specified directory ([815b9e3](https://github.com/Ronnasayd/AI-pair-programming/commit/815b9e3))
- **[✨ Features]** Implement markdown to tasks conversion and add test script for validation ([93a5128](https://github.com/Ronnasayd/AI-pair-programming/commit/93a5128))
- **[✨ Features]** Add main entry point to start mcp server and include example test calls ([951f152](https://github.com/Ronnasayd/AI-pair-programming/commit/951f152))
- **[✨ Features]** Enhance task conversion functions to support markdown format and improve validation ([431c5db](https://github.com/Ronnasayd/AI-pair-programming/commit/431c5db))

### **2025-09-24**

- **[🐛 Bug Fixes]** Update authorization handling in auth method to include github-bearer token for requests ([b2d1a1d](https://github.com/Ronnasayd/AI-pair-programming/commit/b2d1a1d))
- **[✨ Features]** Implement streaming response handling in copilotapi and update chat method to support streaming ([a5d8009](https://github.com/Ronnasayd/AI-pair-programming/commit/a5d8009))
- **[✨ Features]** Add tokenizer capabilities and additional parameters for model configuration ([1d971df](https://github.com/Ronnasayd/AI-pair-programming/commit/1d971df))
- **[🧹 Chores]** Update server port from 11435 to 11434 in copilot ollama api proxy ([0f88ed1](https://github.com/Ronnasayd/AI-pair-programming/commit/0f88ed1))
- **[🐛 Bug Fixes]** Update error handling to re-authenticate on 401 status code in copilotapi ([d985d03](https://github.com/Ronnasayd/AI-pair-programming/commit/d985d03))

### **2025-09-23**

- **[✨ Features]** Remove expand_task.json and update taskmaster.request.json with new prd processing logic; add tasksmaster-template.json for task schema validation ([e2394cc](https://github.com/Ronnasayd/AI-pair-programming/commit/e2394cc))
- **[🐛 Bug Fixes]** Handle 400 response by re-authenticating and refreshing token in copilotapi ([c7e7482](https://github.com/Ronnasayd/AI-pair-programming/commit/c7e7482))
- **[✨ Features]** Implement copilotapi and associated functionalities for github copilot integration; update requirements and add initial module files ([6a4635e](https://github.com/Ronnasayd/AI-pair-programming/commit/6a4635e))

### **2025-09-22**

- **[✨ Features]** Implement copilotapi class with chat and create_chat methods for github copilot integration ([920d9ba](https://github.com/Ronnasayd/AI-pair-programming/commit/920d9ba))
- **[✨ Features]** Add expand_task.json with task breakdown and subtasks generation logic ([b2a7e90](https://github.com/Ronnasayd/AI-pair-programming/commit/b2a7e90))

### **2025-09-20**

- **[🐛 Bug Fixes]** Update command arguments for my_run_command in my_mcp_client_stdio.py ([9c47634](https://github.com/Ronnasayd/AI-pair-programming/commit/9c47634))

### **2025-09-19**

- **[✨ Features]** Implement flexible model naming and enhance model validation in ollama api proxy server ([2fd7c2d](https://github.com/Ronnasayd/AI-pair-programming/commit/2fd7c2d))
- **[🐛 Bug Fixes]** Update remote ollama url and clear excluded paths in proxy server configuration ([ce02e42](https://github.com/Ronnasayd/AI-pair-programming/commit/ce02e42))
- **[✨ Features]** Enhance logging functionality in ollama api proxy server and add openai-compatible endpoints ([181d4dc](https://github.com/Ronnasayd/AI-pair-programming/commit/181d4dc))
- **[✨ Features]** Implement ollama api proxy server with request logging and model management endpoints ([cf12c63](https://github.com/Ronnasayd/AI-pair-programming/commit/cf12c63))

### **2025-09-18**

- **[✨ Features]** Add comprehensive guidelines for creating software requirements specification (srs) documents ([0446f1a](https://github.com/Ronnasayd/AI-pair-programming/commit/0446f1a))

### **2025-09-17**

- **[✨ Features]** Add new plan template for project and task management with detailed structure ([11954d1](https://github.com/Ronnasayd/AI-pair-programming/commit/11954d1))
- **[🐛 Bug Fixes]** Update documentation instructions to reflect changes in file naming conventions and structure. ([f785d11](https://github.com/Ronnasayd/AI-pair-programming/commit/f785d11))

### **2025-09-16**

- **[✨ Features]** Add 'design' category to tasks in tasks template for improved categorization ([ea151e1](https://github.com/Ronnasayd/AI-pair-programming/commit/ea151e1))
- **[✨ Features]** Remove summary and notes fields from requirements in srs and tasks templates for clarity ([f66bc18](https://github.com/Ronnasayd/AI-pair-programming/commit/f66bc18))
- **[✨ Features]** Enhance srs and tasks templates with detailed user stories and requirements structure ([f7cb744](https://github.com/Ronnasayd/AI-pair-programming/commit/f7cb744))
- **[✨ Features]** Remove epics, prioritization, and roadmap sections from tasks template for simplification ([0e2d557](https://github.com/Ronnasayd/AI-pair-programming/commit/0e2d557))
- **[✨ Features]** Update prd structure and add prompt template file ([311b201](https://github.com/Ronnasayd/AI-pair-programming/commit/311b201))

### **2025-09-12**

- **[✨ Features]** Add tasks template json structure for project management ([f18372e](https://github.com/Ronnasayd/AI-pair-programming/commit/f18372e))
- **[✨ Features]** Update prd and srs instructions to include structured input fields and optional parameters ([caf3f5a](https://github.com/Ronnasayd/AI-pair-programming/commit/caf3f5a))
- **[✨ Features]** Add general recommendations for srs generation process ([cddf0b8](https://github.com/Ronnasayd/AI-pair-programming/commit/cddf0b8))
- **[✨ Features]** Add prd and srs templates for structured documentation ([87fe8c1](https://github.com/Ronnasayd/AI-pair-programming/commit/87fe8c1))
- **[♻️ Refactoring]** Update file paths to reflect new project structure in my_mcp_server.py ([1def862](https://github.com/Ronnasayd/AI-pair-programming/commit/1def862))
- **[✨ Features]** Update output format to markdown template for task generation instructions ([828727c](https://github.com/Ronnasayd/AI-pair-programming/commit/828727c))
- **[✨ Features]** Add structured instructions for generating tasks from requirements across multiple methodologies ([01b8b81](https://github.com/Ronnasayd/AI-pair-programming/commit/01b8b81))
- **[✨ Features]** Add comprehensive instructions for generating prd and srs documents ([650681a](https://github.com/Ronnasayd/AI-pair-programming/commit/650681a))
- **[📚 Documentation]** Update srs structure formatting for consistency across instructions ([4cb7ff5](https://github.com/Ronnasayd/AI-pair-programming/commit/4cb7ff5))

### **2025-09-11**

- **[🧹 Chores]** Remove install script for generating context and coverage links ([fea8448](https://github.com/Ronnasayd/AI-pair-programming/commit/fea8448))
- **[🧹 Chores]** Update file permissions and relocate requirements file to src directory ([563d2db](https://github.com/Ronnasayd/AI-pair-programming/commit/563d2db))
- **[🧹 Chores]** Rename markdown and python files to appropriate directories for better organization ([73d7666](https://github.com/Ronnasayd/AI-pair-programming/commit/73d7666))
- **[🚧 Other Changes]** D83773e - first commit | 2025-09-11

---
Generated on 2026-03-30 19:57:46