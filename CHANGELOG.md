# Changelog

## v2026.09.16 (Initial Release / Full History)

### **2026-09-16**

- **[♻️ Refactoring]** Update descriptions in skill.md and instructions files ([2366dfe](https://github.com/Ronnasayd/AI-pair-programming/commit/2366dfe))
- **[♻️ Refactoring]** Rewrite skill descriptions to english-only triggers and drop negative clauses ([5aac8e3](https://github.com/Ronnasayd/AI-pair-programming/commit/5aac8e3))
- **[♻️ Refactoring]** Update skill-description-generator to enforce english-only trigger phrases ([a4ebdc0](https://github.com/Ronnasayd/AI-pair-programming/commit/a4ebdc0))
- **[♻️ Refactoring]** Trim descriptions and drop non-english trigger phrases ([3abcbc5](https://github.com/Ronnasayd/AI-pair-programming/commit/3abcbc5))
- **[♻️ Refactoring]** Drop negative-trigger clauses from generated descriptions ([9deab34](https://github.com/Ronnasayd/AI-pair-programming/commit/9deab34))
- **[✨ Features]** Resolve /command prompts to body text for embedding ([73ab4f2](https://github.com/Ronnasayd/AI-pair-programming/commit/73ab4f2))
- **[♻️ Refactoring]** Separate dedup and referenced-skill skip logging ([4c82cf5](https://github.com/Ronnasayd/AI-pair-programming/commit/4c82cf5))

### **2026-09-15**

- **[♻️ Refactoring]** Update skills ([e221eea](https://github.com/Ronnasayd/AI-pair-programming/commit/e221eea))
- **[♻️ Refactoring]** Use sudo for package installations in install.sh ([0c3cc0e](https://github.com/Ronnasayd/AI-pair-programming/commit/0c3cc0e))
- **[♻️ Refactoring]** Move to installs directory and update source path ([50a3113](https://github.com/Ronnasayd/AI-pair-programming/commit/50a3113))
- **[♻️ Refactoring]** Update install and project dir references to project_dir ([bdd631d](https://github.com/Ronnasayd/AI-pair-programming/commit/bdd631d))
- **[♻️ Refactoring]** Add the-judge skill to manifest and index files ([589c908](https://github.com/Ronnasayd/AI-pair-programming/commit/589c908))
- **[♻️ Refactoring]** Update pr review skill and related tools ([1117173](https://github.com/Ronnasayd/AI-pair-programming/commit/1117173))
- **[✨ Features]** Add the judge skill ([30db8f3](https://github.com/Ronnasayd/AI-pair-programming/commit/30db8f3))

### **2026-09-14**

- **[🧹 Chores]** Sync tech-leads-club skills, add spec-driven-eval ([28d9e88](https://github.com/Ronnasayd/AI-pair-programming/commit/28d9e88))
- **[🐛 Bug Fixes]** Remove existing skill symlink/dir before recreating in claude.install.sh ([12a4447](https://github.com/Ronnasayd/AI-pair-programming/commit/12a4447))
- **[✨ Features]** Scan mcp tool_input string leaves for protected paths ([5b15529](https://github.com/Ronnasayd/AI-pair-programming/commit/5b15529))
- **[✨ Features]** Support pragma allowlist for secret scan false positives ([b9fc3f4](https://github.com/Ronnasayd/AI-pair-programming/commit/b9fc3f4))
- **[♻️ Refactoring]** Add tlc skills to .skillsignore and update skill_loader_mcp.py ([8481fbf](https://github.com/Ronnasayd/AI-pair-programming/commit/8481fbf))
- **[✨ Features]** Add download_remote_skill tool for bulk skill fetch add tool to download a skill (skill.md + all auxiliary files) from the remote repo in one call and save to <dest_dir>/<name>/, defaulting to .claude/skills. avoids per-file mcp round trips for skills with many auxiliary files. ([b170e0f](https://github.com/Ronnasayd/AI-pair-programming/commit/b170e0f))
- **[♻️ Refactoring]** Update skills and commands for new features ([da9ea0b](https://github.com/Ronnasayd/AI-pair-programming/commit/da9ea0b))
- **[✨ Features]** Add new tlc skills for confluence, harness eval, spec-driven eval, discover, implement, plan, and spec-lean ([415897d](https://github.com/Ronnasayd/AI-pair-programming/commit/415897d))
- **[✨ Features]** Add claude_install_skip_claude_md env var to skip claude.md write ([979fcc5](https://github.com/Ronnasayd/AI-pair-programming/commit/979fcc5))
- **[✨ Features]** Add claude_install_skip_auto_context env var and document env vars in readme ([e993fd0](https://github.com/Ronnasayd/AI-pair-programming/commit/e993fd0))
- **[♻️ Refactoring]** Update lefthook script paths to use absolute paths ([c6bf71b](https://github.com/Ronnasayd/AI-pair-programming/commit/c6bf71b))
- **[✨ Features]** Add commit-msg hook to reject emoji in commit messages ([457abd6](https://github.com/Ronnasayd/AI-pair-programming/commit/457abd6))
- **[♻️ Refactoring]** Remove leftover git-hooks references after lefthook migration ([32acc68](https://github.com/Ronnasayd/AI-pair-programming/commit/32acc68))
- **[♻️ Refactoring]** Migrate git-hooks scripts to lefthook ([ac6a6fc](https://github.com/Ronnasayd/AI-pair-programming/commit/ac6a6fc))
- **[✨ Features]** Inject agents.md content into sessionstart context ([1f495c0](https://github.com/Ronnasayd/AI-pair-programming/commit/1f495c0))
- **[📚 Documentation]** Trim agents.md/agent.instructions.md conventions, add skills table ([bf1819c](https://github.com/Ronnasayd/AI-pair-programming/commit/bf1819c))
- **[✨ Features]** Add skill-judge fetch and refactor tool downloader into functions ([3dab365](https://github.com/Ronnasayd/AI-pair-programming/commit/3dab365))
- **[♻️ Refactoring]** Update .mcp.json to include rag-rat and serena configurations ([22e267c](https://github.com/Ronnasayd/AI-pair-programming/commit/22e267c))

### **2026-09-12**

- **[📚 Documentation]** Add readme documenting active hook wiring ([010afbe](https://github.com/Ronnasayd/AI-pair-programming/commit/010afbe))
- **[♻️ Refactoring]** Move to correct location in spec-to-requirements-table skill ([ddaa7e9](https://github.com/Ronnasayd/AI-pair-programming/commit/ddaa7e9))
- **[✨ Features]** Add deterministic requirements table validator ([43c68f6](https://github.com/Ronnasayd/AI-pair-programming/commit/43c68f6))
- **[✨ Features]** Add deterministic pr description validator ([2bed1f3](https://github.com/Ronnasayd/AI-pair-programming/commit/2bed1f3))
- **[♻️ Refactoring]** Update external skills ([b5d1686](https://github.com/Ronnasayd/AI-pair-programming/commit/b5d1686))
- **[♻️ Refactoring]** Update .skillsignore to reorder and add new entries ([8d984e6](https://github.com/Ronnasayd/AI-pair-programming/commit/8d984e6))
- **[📚 Documentation]** Add mermaid execution flow diagram ([6be0d7f](https://github.com/Ronnasayd/AI-pair-programming/commit/6be0d7f))
- **[📚 Documentation]** Add mermaid flow diagram and refine web-search step ([fba5703](https://github.com/Ronnasayd/AI-pair-programming/commit/fba5703))

### **2026-09-11**

- **[✨ Features]** Add mcp server allowlist to protect_files hook ([f85a74e](https://github.com/Ronnasayd/AI-pair-programming/commit/f85a74e))

### **2026-09-10**

- **[♻️ Refactoring]** Replace cfie alias with function to open git exclude file in editor ([ab9083b](https://github.com/Ronnasayd/AI-pair-programming/commit/ab9083b))
- **[✨ Features]** Also emit **/-prefixed git exclude patterns for nested dirs ([4315669](https://github.com/Ronnasayd/AI-pair-programming/commit/4315669))
- **[♻️ Refactoring]** Centralize git exclude logic in shared helper ([ecfa577](https://github.com/Ronnasayd/AI-pair-programming/commit/ecfa577))
- **[♻️ Refactoring]** Tighten context7 search result filtering ([6ab9d8d](https://github.com/Ronnasayd/AI-pair-programming/commit/6ab9d8d))
- **[♻️ Refactoring]** Add session duration display to status line ([19434b0](https://github.com/Ronnasayd/AI-pair-programming/commit/19434b0))

### **2026-09-09**

- **[♻️ Refactoring]** Add ssh-mcp to disabled mcp servers list ([b0484e8](https://github.com/Ronnasayd/AI-pair-programming/commit/b0484e8))

### **2026-09-08**

- **[♻️ Refactoring]** Update permanent memory guidelines in start.md ([039596b](https://github.com/Ronnasayd/AI-pair-programming/commit/039596b))

### **2026-09-06**

- **[🧹 Chores]** Mount .serena rw and pass through context7/npm cache config ([39e99a6](https://github.com/Ronnasayd/AI-pair-programming/commit/39e99a6))
- **[♻️ Refactoring]** Rename dontask to bypasspermissions and centralize ask permissions ([8cf256a](https://github.com/Ronnasayd/AI-pair-programming/commit/8cf256a))
- **[♻️ Refactoring]** Update agent creation and task handling guidelines ([6a42fbf](https://github.com/Ronnasayd/AI-pair-programming/commit/6a42fbf))
- **[♻️ Refactoring]** Update agent creation and task handling guidelines ([8a7a4a3](https://github.com/Ronnasayd/AI-pair-programming/commit/8a7a4a3))
- **[♻️ Refactoring]** Update project_ports output formatting and command display ([4c9f920](https://github.com/Ronnasayd/AI-pair-programming/commit/4c9f920))
- **[✨ Features]** Report project apps listening on ports in start context ([204bbe4](https://github.com/Ronnasayd/AI-pair-programming/commit/204bbe4))

### **2026-09-05**

- **[♻️ Refactoring]** Add omniroute to disabled mcp servers list ([e65c6cd](https://github.com/Ronnasayd/AI-pair-programming/commit/e65c6cd))
- **[♻️ Refactoring]** Remove ignored entries from disabled mcp servers list ([13aaeca](https://github.com/Ronnasayd/AI-pair-programming/commit/13aaeca))
- **[♻️ Refactoring]** Apply disabled mcp servers to all projects ([1750c9c](https://github.com/Ronnasayd/AI-pair-programming/commit/1750c9c))
- **[🚧 Other Changes]** C148f11 - git add src/pyproject.toml src/uv.lock git commit -m "fix(mcp): pin fastmcp<3 to avoid broken v4.0.3 resolution" | 2026-09-05
- **[♻️ Refactoring]** Moved to mcp-manager ([70bf2d5](https://github.com/Ronnasayd/AI-pair-programming/commit/70bf2d5))
- **[✨ Features]** Add guide for generating images with omniroute ([b1ffcdf](https://github.com/Ronnasayd/AI-pair-programming/commit/b1ffcdf))

### **2026-09-04**

- **[🧹 Chores]** Add blender mcp server and swap session-memory command ([ebc840b](https://github.com/Ronnasayd/AI-pair-programming/commit/ebc840b))

### **2026-09-03**

- **[🐛 Bug Fixes]** Match durable memory pages by path with plural query forms ([135aea9](https://github.com/Ronnasayd/AI-pair-programming/commit/135aea9))
- **[🧹 Chores]** Gate ai-memory auto-improve behind manual approval ([583e175](https://github.com/Ronnasayd/AI-pair-programming/commit/583e175))
- **[📚 Documentation]** Add end-of-session permanent-memory step to sd-planning and sd-execute ([e703869](https://github.com/Ronnasayd/AI-pair-programming/commit/e703869))
- **[✨ Features]** Add hook authoring skill and conventions ([0fd8fcc](https://github.com/Ronnasayd/AI-pair-programming/commit/0fd8fcc))
- **[✨ Features]** Add sessionstart hook to surface durable ai-memory pages ([7840a95](https://github.com/Ronnasayd/AI-pair-programming/commit/7840a95))
- **[♻️ Refactoring]** Add ai_memory_project_strategy=repo-root to all hook commands and update aliases to include project strategy for consistent repo-root behavior. ([17302e2](https://github.com/Ronnasayd/AI-pair-programming/commit/17302e2))
- **[♻️ Refactoring]** Split ai-memory install into separate mcp and hooks aliases ([2c7bbd5](https://github.com/Ronnasayd/AI-pair-programming/commit/2c7bbd5))
- **[✨ Features]** Enforce interactive question tools on subagentstop ([bb3b29d](https://github.com/Ronnasayd/AI-pair-programming/commit/bb3b29d))
- **[🚧 Other Changes]** Add hooks for subagent start and stop commands ([c9c1ccf](https://github.com/Ronnasayd/AI-pair-programming/commit/c9c1ccf))

### **2026-09-02**

- **[♻️ Refactoring]** Move ai-memory install-skills to the end of the install process ([b225b69](https://github.com/Ronnasayd/AI-pair-programming/commit/b225b69))
- **[♻️ Refactoring]** Remove ai_memory_consolidate_on_session_end environment variable from aimsllm alias ([12fe04a](https://github.com/Ronnasayd/AI-pair-programming/commit/12fe04a))
- **[🧹 Chores]** Harden ai-memory setup and refresh agents.md docs ([9244c6d](https://github.com/Ronnasayd/AI-pair-programming/commit/9244c6d))
- **[♻️ Refactoring]** Update permission mode handling to use 'dontask' instead of 'bypasspermissions' ([23e6ce6](https://github.com/Ronnasayd/AI-pair-programming/commit/23e6ce6))
- **[♻️ Refactoring]** Update settings to limit concurrent subagents and disable explore plan agents ([2854b63](https://github.com/Ronnasayd/AI-pair-programming/commit/2854b63))

### **2026-09-01**

- **[♻️ Refactoring]** Update import path for fastmcp and change default model to sonnet ([d2b54b1](https://github.com/Ronnasayd/AI-pair-programming/commit/d2b54b1))
- **[♻️ Refactoring]** Update settings to enable auto-compaction and switch model to haiku ([1766b83](https://github.com/Ronnasayd/AI-pair-programming/commit/1766b83))
- **[✨ Features]** Truncate large lint outputs to /tmp with reference path ([d6ea863](https://github.com/Ronnasayd/AI-pair-programming/commit/d6ea863))

### **2026-08-31**

- **[✨ Features]** Surface disabled mcp servers in session context ([c6faf87](https://github.com/Ronnasayd/AI-pair-programming/commit/c6faf87))
- **[♻️ Refactoring]** Add language rule ([c8107cb](https://github.com/Ronnasayd/AI-pair-programming/commit/c8107cb))
- **[✨ Features]** Add generate-design-md skill ([2ce9f0b](https://github.com/Ronnasayd/AI-pair-programming/commit/2ce9f0b))

### **2026-08-30**

- **[✨ Features]** Promote ask to allow in bypasspermissions mode ([d645c7e](https://github.com/Ronnasayd/AI-pair-programming/commit/d645c7e))

### **2026-08-29**

- **[♻️ Refactoring]** Add label and status ([6e8f033](https://github.com/Ronnasayd/AI-pair-programming/commit/6e8f033))
- **[♻️ Refactoring]** Add log ([0088138](https://github.com/Ronnasayd/AI-pair-programming/commit/0088138))
- **[🐛 Bug Fixes]** Serialize concurrent jest coverage merges and show stale coverage ([65f1a0d](https://github.com/Ronnasayd/AI-pair-programming/commit/65f1a0d))
- **[✨ Features]** Add per-subagent status line ([cab9686](https://github.com/Ronnasayd/AI-pair-programming/commit/cab9686))
- **[🐛 Bug Fixes]** Resolve rag-rat.toml check against ai_project_dir ([47adcbe](https://github.com/Ronnasayd/AI-pair-programming/commit/47adcbe))
- **[🧹 Chores]** Block commit messages that mention ai code assistants ([1f8d41c](https://github.com/Ronnasayd/AI-pair-programming/commit/1f8d41c))
- **[♻️ Refactoring]** Compress specialist agent instruction files ([fd1cbb8](https://github.com/Ronnasayd/AI-pair-programming/commit/fd1cbb8))
- **[✨ Features]** Match rtk-proxied commands against plain permission patterns ([f9939ef](https://github.com/Ronnasayd/AI-pair-programming/commit/f9939ef))

### **2026-08-28**

- **[♻️ Refactoring]** Add block any claude info in commits ([4a3373f](https://github.com/Ronnasayd/AI-pair-programming/commit/4a3373f))
- **[♻️ Refactoring]** Remove subagent commit block ([bc7cb69](https://github.com/Ronnasayd/AI-pair-programming/commit/bc7cb69))
- **[🧹 Chores]** Mount mcp-manager dir read-only and add skip-permissions shortcut ([89e9785](https://github.com/Ronnasayd/AI-pair-programming/commit/89e9785))
- **[♻️ Refactoring]** Expand service labels and use colored dot indicators ([ac15523](https://github.com/Ronnasayd/AI-pair-programming/commit/ac15523))
- **[♻️ Refactoring]** Double context bar resolution to 5% per segment ([cd440d6](https://github.com/Ronnasayd/AI-pair-programming/commit/cd440d6))
- **[♻️ Refactoring]** Extract field separator into sep variable ([44f3891](https://github.com/Ronnasayd/AI-pair-programming/commit/44f3891))
- **[✨ Features]** Add osc 8 hyperlinks and catppuccin color vars ([132ef11](https://github.com/Ronnasayd/AI-pair-programming/commit/132ef11))
- **[♻️ Refactoring]** Use catppuccin color vars and k-format token counts ([e04b239](https://github.com/Ronnasayd/AI-pair-programming/commit/e04b239))
- **[✨ Features]** Add nerd font icons, catppuccin colors, and context bar ([3599c54](https://github.com/Ronnasayd/AI-pair-programming/commit/3599c54))
- **[🧹 Chores]** Retire md_json_lint hook and add requirements-table step to sd-planning ([afc518c](https://github.com/Ronnasayd/AI-pair-programming/commit/afc518c))
- **[♻️ Refactoring]** Add omniroute ([56d6338](https://github.com/Ronnasayd/AI-pair-programming/commit/56d6338))
- **[📚 Documentation]** Align spec-to-requirements-table output with example format ([e8fb58b](https://github.com/Ronnasayd/AI-pair-programming/commit/e8fb58b))
- **[✨ Features]** Add spec-to-requirements-table skill ([f8521ed](https://github.com/Ronnasayd/AI-pair-programming/commit/f8521ed))

### **2026-08-27**

- **[✨ Features]** Play alert sound on user questions and permission prompts ([3ffc1a5](https://github.com/Ronnasayd/AI-pair-programming/commit/3ffc1a5))
- **[🐛 Bug Fixes]** Reconstruct last assistant message from transcript in question enforcer ([7159bb0](https://github.com/Ronnasayd/AI-pair-programming/commit/7159bb0))
- **[🧹 Chores]** Move scripts unused by settings.json to unused/ ([86f3efb](https://github.com/Ronnasayd/AI-pair-programming/commit/86f3efb))
- **[♻️ Refactoring]** Rename tlc-* skills to sd-* naming scheme ([bec8fb5](https://github.com/Ronnasayd/AI-pair-programming/commit/bec8fb5))
- **[♻️ Refactoring]** Add new term for question tool enforce ([23b379f](https://github.com/Ronnasayd/AI-pair-programming/commit/23b379f))
- **[✨ Features]** Replace sessionend formatter with git pre-commit hook ([fba1cdc](https://github.com/Ronnasayd/AI-pair-programming/commit/fba1cdc))
- **[🐛 Bug Fixes]** Only report jscpd duplication above threshold ([95ea234](https://github.com/Ronnasayd/AI-pair-programming/commit/95ea234))
- **[🐛 Bug Fixes]** Only report jscpd duplication above threshold ([6fe24cc](https://github.com/Ronnasayd/AI-pair-programming/commit/6fe24cc))

### **2026-08-26**

- **[🐛 Bug Fixes]** Adjust script location ([fce4f87](https://github.com/Ronnasayd/AI-pair-programming/commit/fce4f87))
- **[✨ Features]** Warn agent to write markdown in english for docs/spec dirs ([397d1bc](https://github.com/Ronnasayd/AI-pair-programming/commit/397d1bc))
- **[✨ Features]** Add spacy stopword removal deps and model install ([5aa25b5](https://github.com/Ronnasayd/AI-pair-programming/commit/5aa25b5))

### **2026-08-25**

- **[📚 Documentation]** Update env var name in environments.md table ([8e18495](https://github.com/Ronnasayd/AI-pair-programming/commit/8e18495))
- **[♻️ Refactoring]** Rename claude_project_dir to ai_project_dir, allow memory md writes ([6bb3653](https://github.com/Ronnasayd/AI-pair-programming/commit/6bb3653))
- **[🐛 Bug Fixes]** Resolve tsconfig path aliases in jest related-files import scan ([2d78b96](https://github.com/Ronnasayd/AI-pair-programming/commit/2d78b96))
- **[✨ Features]** Add jest related-files report hook ([b44d057](https://github.com/Ronnasayd/AI-pair-programming/commit/b44d057))
- **[♻️ Refactoring]** Move jest coverage-summary build out of background merge ([5c4b405](https://github.com/Ronnasayd/AI-pair-programming/commit/5c4b405))
- **[🐛 Bug Fixes]** Write coverage json atomically to avoid partial reads ([2a95d8e](https://github.com/Ronnasayd/AI-pair-programming/commit/2a95d8e))
- **[♻️ Refactoring]** Write jest coverage-summary.json under coverage/summary/ ([9a82ccf](https://github.com/Ronnasayd/AI-pair-programming/commit/9a82ccf))
- **[🧹 Chores]** Sync dev tooling and hooks config ([dd6278c](https://github.com/Ronnasayd/AI-pair-programming/commit/dd6278c))

### **2026-08-24**

- **[✨ Features]** Surface uncovered line numbers in jest coverage report ([cdde920](https://github.com/Ronnasayd/AI-pair-programming/commit/cdde920))
- **[♻️ Refactoring]** Add position ([daeacf5](https://github.com/Ronnasayd/AI-pair-programming/commit/daeacf5))
- **[🐛 Bug Fixes]** Always append findrelatedtests and coverage flags in incremental jest run ([24cf666](https://github.com/Ronnasayd/AI-pair-programming/commit/24cf666))
- **[✨ Features]** Add custom jest coverage command overrides ([3a558de](https://github.com/Ronnasayd/AI-pair-programming/commit/3a558de))
- **[🐛 Bug Fixes]** Set node_env=test for jest coverage runs and wire session-end hook ([a9dcbf4](https://github.com/Ronnasayd/AI-pair-programming/commit/a9dcbf4))
- **[♻️ Refactoring]** Change to runinband ([2abba4f](https://github.com/Ronnasayd/AI-pair-programming/commit/2abba4f))
- **[🚧 Other Changes]** Cap jest workers at 25% in coverage hooks ([afddbd4](https://github.com/Ronnasayd/AI-pair-programming/commit/afddbd4))
- **[♻️ Refactoring]** Replace embedding daemon with rag-rat semantic_search in similar_code_ref ([bb7563a](https://github.com/Ronnasayd/AI-pair-programming/commit/bb7563a))
- **[♻️ Refactoring]** Replace regex symbol/import extraction with tree-sitter ast ([797fd1e](https://github.com/Ronnasayd/AI-pair-programming/commit/797fd1e))
- **[📚 Documentation]** Compress skill.md into scannable core ([73a5979](https://github.com/Ronnasayd/AI-pair-programming/commit/73a5979))
- **[✨ Features]** Add dynamic programming ([0e8abd3](https://github.com/Ronnasayd/AI-pair-programming/commit/0e8abd3))
- **[📚 Documentation]** Move adr template reference to local skill directory ([03a291d](https://github.com/Ronnasayd/AI-pair-programming/commit/03a291d))
- **[📚 Documentation]** Restructure step loop and sync checklist ([fa7f983](https://github.com/Ronnasayd/AI-pair-programming/commit/fa7f983))
- **[🚧 Other Changes]** Add eval cases for impact_surface_hint hook ([a9fc53c](https://github.com/Ronnasayd/AI-pair-programming/commit/a9fc53c))
- **[🐛 Bug Fixes]** Resolve symbol from post-edit file content, not stale old_string ([721e34a](https://github.com/Ronnasayd/AI-pair-programming/commit/721e34a))
- **[🐛 Bug Fixes]** Read changed symbols from payload instead of git diff hunks ([4ca302a](https://github.com/Ronnasayd/AI-pair-programming/commit/4ca302a))
- **[✨ Features]** Add impact_surface_hint posttooluse hook ([7038535](https://github.com/Ronnasayd/AI-pair-programming/commit/7038535))

### **2026-08-23**

- **[✨ Features]** Add taskmaster_next_task sessionstart hook ([ff93fe0](https://github.com/Ronnasayd/AI-pair-programming/commit/ff93fe0))

### **2026-08-22**

- **[🐛 Bug Fixes]** Correct ai_project_dir to ai_project_root_dir in hook paths ([8ebcf92](https://github.com/Ronnasayd/AI-pair-programming/commit/8ebcf92))

### **2026-08-21**

- **[🐛 Bug Fixes]** Python call ([7c5644f](https://github.com/Ronnasayd/AI-pair-programming/commit/7c5644f))
- **[🐛 Bug Fixes]** Add missing pyyaml dependency to pyproject.toml ([f5c5415](https://github.com/Ronnasayd/AI-pair-programming/commit/f5c5415))
- **[🧹 Chores]** Migrate src package from poetry to uv/setuptools ([8b411fd](https://github.com/Ronnasayd/AI-pair-programming/commit/8b411fd))
- **[🧹 Chores]** Install hook-script deps via uv sync ([3d58a35](https://github.com/Ronnasayd/AI-pair-programming/commit/3d58a35))
- **[🧹 Chores]** Run hook scripts through isolated uv venv ([5bd350b](https://github.com/Ronnasayd/AI-pair-programming/commit/5bd350b))
- **[🧹 Chores]** Lock hook-script dependencies (numpy, fastembed) ([1e34262](https://github.com/Ronnasayd/AI-pair-programming/commit/1e34262))
- **[🧹 Chores]** Add root pyproject.toml for hook-script deps ([fef41b3](https://github.com/Ronnasayd/AI-pair-programming/commit/fef41b3))
- **[🧹 Chores]** Update styles ([c9c2e44](https://github.com/Ronnasayd/AI-pair-programming/commit/c9c2e44))

### **2026-08-20**

- **[🚧 Other Changes]** Add eval cases for previously untested pretooluse hooks ([697ce42](https://github.com/Ronnasayd/AI-pair-programming/commit/697ce42))
- **[♻️ Refactoring]** Consolidate hook eval runners into a single generic script ([7729fcb](https://github.com/Ronnasayd/AI-pair-programming/commit/7729fcb))
- **[🧹 Chores]** Lower default model/effort and skip commits on protected branches ([7883eba](https://github.com/Ronnasayd/AI-pair-programming/commit/7883eba))
- **[🚧 Other Changes]** F46bf4a - git commit -m "refactor: dedupe split_on_operators/strip_heredocs across hook scripts | 2026-08-20
- **[♻️ Refactoring]** Remove rag-rat ([a470959](https://github.com/Ronnasayd/AI-pair-programming/commit/a470959))
- **[♻️ Refactoring]** Add .serena to exclude ([c802c5f](https://github.com/Ronnasayd/AI-pair-programming/commit/c802c5f))
- **[🧹 Chores]** Create backup ([a8a42a0](https://github.com/Ronnasayd/AI-pair-programming/commit/a8a42a0))
- **[♻️ Refactoring]** Fix python ([59b0efe](https://github.com/Ronnasayd/AI-pair-programming/commit/59b0efe))
- **[✨ Features]** Re-add claude.warmup.sh ([6bbebc5](https://github.com/Ronnasayd/AI-pair-programming/commit/6bbebc5))

### **2026-08-19**

- **[✨ Features]** Allow user-controlled allowed_patterns extension via env var ([4b8a35e](https://github.com/Ronnasayd/AI-pair-programming/commit/4b8a35e))
- **[🧹 Chores]** Remove rag-rat from settings ([dd990c7](https://github.com/Ronnasayd/AI-pair-programming/commit/dd990c7))
- **[📚 Documentation]** Require taskcreate/taskupdate tracking in grilling and taskmaster skills ([f4d2a0e](https://github.com/Ronnasayd/AI-pair-programming/commit/f4d2a0e))
- **[✨ Features]** Add protect_branches hook for main/master/develop/homolog ([42ba744](https://github.com/Ronnasayd/AI-pair-programming/commit/42ba744))

### **2026-08-18**

- **[✨ Features]** Add gghget_file for single-file github downloads ([060e25d](https://github.com/Ronnasayd/AI-pair-programming/commit/060e25d))
- **[🧹 Chores]** Update skills ([f245043](https://github.com/Ronnasayd/AI-pair-programming/commit/f245043))
- **[🐛 Bug Fixes]** Gate bm25 skill matches on cosine results ([dbaa9aa](https://github.com/Ronnasayd/AI-pair-programming/commit/dbaa9aa))
- **[✨ Features]** Add regex fallback secret scanner ([d2995c4](https://github.com/Ronnasayd/AI-pair-programming/commit/d2995c4))
- **[🐛 Bug Fixes]** Raise bm25 term overlap threshold to reduce false positives ([6a014c4](https://github.com/Ronnasayd/AI-pair-programming/commit/6a014c4))
- **[✨ Features]** Warn on markdown files created outside doc directories ([c54ef64](https://github.com/Ronnasayd/AI-pair-programming/commit/c54ef64))
- **[✨ Features]** Add tmux/screen guard for dev server commands ([036236d](https://github.com/Ronnasayd/AI-pair-programming/commit/036236d))
- **[♻️ Refactoring]** Harden protect_files splitter and add smart_approve hook ([b0eb058](https://github.com/Ronnasayd/AI-pair-programming/commit/b0eb058))
- **[🐛 Bug Fixes]** Mount ai_project_root_dir so hooks/skills symlinks resolve ([b95d0a0](https://github.com/Ronnasayd/AI-pair-programming/commit/b95d0a0))
- **[🐛 Bug Fixes]** Include scores in skill activation debug logs ([73aad98](https://github.com/Ronnasayd/AI-pair-programming/commit/73aad98))
- **[♻️ Refactoring]** Increase min score ([82c385e](https://github.com/Ronnasayd/AI-pair-programming/commit/82c385e))
- **[🐛 Bug Fixes]** Tighten bm25 skill matching to reduce false positives ([65910d4](https://github.com/Ronnasayd/AI-pair-programming/commit/65910d4))
- **[♻️ Refactoring]** Compress technical-decision-helper skill.md ([f6caf3a](https://github.com/Ronnasayd/AI-pair-programming/commit/f6caf3a))
- **[✨ Features]** Add bm25 lexical search fused with vector similarity for skill activation ([ac4a7c4](https://github.com/Ronnasayd/AI-pair-programming/commit/ac4a7c4))
- **[✨ Features]** Surface config files in start_context additionalcontext ([939f997](https://github.com/Ronnasayd/AI-pair-programming/commit/939f997))

### **2026-08-15**

- **[✨ Features]** Add rag-rat search hook for userpromptsubmit and askuserquestion ([ff8dae0](https://github.com/Ronnasayd/AI-pair-programming/commit/ff8dae0))
- **[♻️ Refactoring]** Remove headroom integration ([9a8a48e](https://github.com/Ronnasayd/AI-pair-programming/commit/9a8a48e))

### **2026-08-14**

- **[♻️ Refactoring]** Simplify lhwc alias and disable headroom mcp by default ([41c9e62](https://github.com/Ronnasayd/AI-pair-programming/commit/41c9e62))
- **[♻️ Refactoring]** Remove claude.warmup ([51d703b](https://github.com/Ronnasayd/AI-pair-programming/commit/51d703b))
- **[♻️ Refactoring]** Add tee logs ([67f3c94](https://github.com/Ronnasayd/AI-pair-programming/commit/67f3c94))
- **[✨ Features]** Inject live mcp-manager context via pretooluse hook ([3f71221](https://github.com/Ronnasayd/AI-pair-programming/commit/3f71221))
- **[🐛 Bug Fixes]** Add ~/.local/bin to path in warmup script ([669c2fe](https://github.com/Ronnasayd/AI-pair-programming/commit/669c2fe))
- **[♻️ Refactoring]** Persist current account on choose, drop timestamped backups ([8380cc4](https://github.com/Ronnasayd/AI-pair-programming/commit/8380cc4))

### **2026-08-13**

- **[✨ Features]** Add cron warmup script for multi-account session tracking ([2cf606f](https://github.com/Ronnasayd/AI-pair-programming/commit/2cf606f))
- **[🧹 Chores]** Disable tool search, add ponytail plugin, enable auto mode ([c02f035](https://github.com/Ronnasayd/AI-pair-programming/commit/c02f035))
- **[✨ Features]** Detect skill invocation via /skill-name prompts too ([64ce554](https://github.com/Ronnasayd/AI-pair-programming/commit/64ce554))
- **[🐛 Bug Fixes]** Run session-end formatters detached via nohup ([e853e68](https://github.com/Ronnasayd/AI-pair-programming/commit/e853e68))
- **[✨ Features]** Return golangci-lint, ruff, mypy, eslint output as json ([9f14f97](https://github.com/Ronnasayd/AI-pair-programming/commit/9f14f97))
- **[✨ Features]** Return jscpd output as structured json ([ceae4aa](https://github.com/Ronnasayd/AI-pair-programming/commit/ceae4aa))
- **[✨ Features]** Run skill/context7 search on askuserquestion answers ([735f3a4](https://github.com/Ronnasayd/AI-pair-programming/commit/735f3a4))
- **[✨ Features]** Log userpromptexpansion events ([164ffff](https://github.com/Ronnasayd/AI-pair-programming/commit/164ffff))
- **[🐛 Bug Fixes]** Only skip suggesting referenced skill when it exists locally ([635faec](https://github.com/Ronnasayd/AI-pair-programming/commit/635faec))
- **[✨ Features]** Detect referenced skill via /skill-name and skip suggesting it ([d7fd878](https://github.com/Ronnasayd/AI-pair-programming/commit/d7fd878))

### **2026-08-12**

- **[♻️ Refactoring]** Change percentage to 5 ([a794aab](https://github.com/Ronnasayd/AI-pair-programming/commit/a794aab))
- **[♻️ Refactoring]** Add cat-ca ([f254d29](https://github.com/Ronnasayd/AI-pair-programming/commit/f254d29))
- **[♻️ Refactoring]** Standardize debug log tag for additionalcontext output ([469e010](https://github.com/Ronnasayd/AI-pair-programming/commit/469e010))
- **[🧹 Chores]** Register tlc-semantic-grilling in manifest and ignore list ([6bdef70](https://github.com/Ronnasayd/AI-pair-programming/commit/6bdef70))
- **[♻️ Refactoring]** Migrate prompt content into skill ([ee07bd4](https://github.com/Ronnasayd/AI-pair-programming/commit/ee07bd4))
- **[📚 Documentation]** Restructure into numbered workflow steps ([0933d5b](https://github.com/Ronnasayd/AI-pair-programming/commit/0933d5b))
- **[🧹 Chores]** Enable auto permission mode and disable background tasks ([58ce54f](https://github.com/Ronnasayd/AI-pair-programming/commit/58ce54f))
- **[📚 Documentation]** Add sequentialthinking pre-step ([75bb524](https://github.com/Ronnasayd/AI-pair-programming/commit/75bb524))

### **2026-08-11**

- **[✨ Features]** Add claude account switcher script and aliases ([dac9555](https://github.com/Ronnasayd/AI-pair-programming/commit/dac9555))
- **[♻️ Refactoring]** Drop metadata.json generation ([d66a8ff](https://github.com/Ronnasayd/AI-pair-programming/commit/d66a8ff))
- **[♻️ Refactoring]** Extract bucket size constant in checklist_context_watch ([a348528](https://github.com/Ronnasayd/AI-pair-programming/commit/a348528))
- **[♻️ Refactoring]** Improve readability of skills_root assignment with multi-line formatting ([107bcff](https://github.com/Ronnasayd/AI-pair-programming/commit/107bcff))
- **[🐛 Bug Fixes]** Resolve skills root under .claude when ai_project_dir is set ([7b20cd2](https://github.com/Ronnasayd/AI-pair-programming/commit/7b20cd2))

### **2026-08-10**

- **[✨ Features]** Protect .claude-l directory from edits ([dc9f45a](https://github.com/Ronnasayd/AI-pair-programming/commit/dc9f45a))
- **[♻️ Refactoring]** Split quality_gate.py into check-only + session-end formatting ([f8ef934](https://github.com/Ronnasayd/AI-pair-programming/commit/f8ef934))
- **[♻️ Refactoring]** Change context usage bucket threshold to 5% ([212ca0a](https://github.com/Ronnasayd/AI-pair-programming/commit/212ca0a))
- **[🐛 Bug Fixes]** Correct skills root default and add debug logging ([042f4b4](https://github.com/Ronnasayd/AI-pair-programming/commit/042f4b4))
- **[✨ Features]** Resurface skill checklist.md on context growth ([6eaf5ef](https://github.com/Ronnasayd/AI-pair-programming/commit/6eaf5ef))
- **[🐛 Bug Fixes]** Write context debug log to ~/.claude/logs ([bf5a914](https://github.com/Ronnasayd/AI-pair-programming/commit/bf5a914))
- **[📚 Documentation]** Sync docs via generate-docs after execute ([f26ea0e](https://github.com/Ronnasayd/AI-pair-programming/commit/f26ea0e))
- **[✨ Features]** Add adr template and criteria for offering adrs ([ef5fb12](https://github.com/Ronnasayd/AI-pair-programming/commit/ef5fb12))

### **2026-08-08**

- **[🐛 Bug Fixes]** Bind systemd-resolved stub for dns resolution in sandbox ([27b0e67](https://github.com/Ronnasayd/AI-pair-programming/commit/27b0e67))
- **[♻️ Refactoring]** Move hook logs from /tmp to ~/.claude/logs ([3ac17d6](https://github.com/Ronnasayd/AI-pair-programming/commit/3ac17d6))
- **[🐛 Bug Fixes]** Bind real /tmp and passthrough env vars to fix claude auto-update in sandbox ([246ad2c](https://github.com/Ronnasayd/AI-pair-programming/commit/246ad2c))

### **2026-08-07**

- **[🧹 Chores]** Enable 1m context and auto tool-search for sonnet/opus ([9981ea5](https://github.com/Ronnasayd/AI-pair-programming/commit/9981ea5))
- **[✨ Features]** Add phase 3.5 test-file mining ([93611cd](https://github.com/Ronnasayd/AI-pair-programming/commit/93611cd))
- **[📚 Documentation]** Include grep and read as fallback search tools ([df2f3f7](https://github.com/Ronnasayd/AI-pair-programming/commit/df2f3f7))

### **2026-08-06**

- **[✨ Features]** Add pretooluse hook to surface dir-level context files ([c4c9d2e](https://github.com/Ronnasayd/AI-pair-programming/commit/c4c9d2e))
- **[✨ Features]** Accept broader change sources and add semantic search ([14c4863](https://github.com/Ronnasayd/AI-pair-programming/commit/14c4863))
- **[♻️ Refactoring]** Update skills manifest and index for generate-docs skill ([b0f1cb8](https://github.com/Ronnasayd/AI-pair-programming/commit/b0f1cb8))
- **[🧹 Chores]** Remove superseded generate-docs-init and generate-docs-update skills ([e5bb904](https://github.com/Ronnasayd/AI-pair-programming/commit/e5bb904))
- **[✨ Features]** Add dispatcher skill.md with auto-detect mode selection ([ace2016](https://github.com/Ronnasayd/AI-pair-programming/commit/ace2016))
- **[✨ Features]** Port templates for create mode ([87c3abb](https://github.com/Ronnasayd/AI-pair-programming/commit/87c3abb))
- **[✨ Features]** Add update mode reference ([6df7b06](https://github.com/Ronnasayd/AI-pair-programming/commit/6df7b06))
- **[✨ Features]** Add create mode reference ([0bf2592](https://github.com/Ronnasayd/AI-pair-programming/commit/0bf2592))
- **[✨ Features]** Add shared reference for writing standards and anti-patterns ([2b61b0d](https://github.com/Ronnasayd/AI-pair-programming/commit/2b61b0d))
- **[🚧 Other Changes]** 8752c81 - refactor `/tlc-semantic-grilling` prompt to include taskmaster registration option | 2026-08-06
- **[♻️ Refactoring]** Adjust name ([f6468d4](https://github.com/Ronnasayd/AI-pair-programming/commit/f6468d4))
- **[♻️ Refactoring]** Rename tlc-execute-tasks to tlc-spec-driven-taskmaster, drop adversarial variant ([292c4d9](https://github.com/Ronnasayd/AI-pair-programming/commit/292c4d9))
- **[♻️ Refactoring]** Fold tlc-execute-tasks-adversarial into tlc-execute-tasks as thin taskmaster wrapper ([8fb004e](https://github.com/Ronnasayd/AI-pair-programming/commit/8fb004e))
- **[🧹 Chores]** Tune similarity threshold and effort level, silence probe warning ([69ff3f5](https://github.com/Ronnasayd/AI-pair-programming/commit/69ff3f5))

### **2026-08-05**

- **[♻️ Refactoring]** Update skills ([19f4fba](https://github.com/Ronnasayd/AI-pair-programming/commit/19f4fba))
- **[✨ Features]** Strip stopwords/lemma via spacy before embedding ([d5e58ab](https://github.com/Ronnasayd/AI-pair-programming/commit/d5e58ab))
- **[♻️ Refactoring]** Replace oauth account switcher with config-dir cloning ([debfd5b](https://github.com/Ronnasayd/AI-pair-programming/commit/debfd5b))
- **[♻️ Refactoring]** Route tlc-execute-tasks through orchestrator context-map ([249bb53](https://github.com/Ronnasayd/AI-pair-programming/commit/249bb53))
- **[✨ Features]** Add jira-to-todo skill for exporting pending jira issues ([96b9508](https://github.com/Ronnasayd/AI-pair-programming/commit/96b9508))

### **2026-08-04**

- **[📚 Documentation]** Add descriptive comments to remaining aliases ([d2ed8be](https://github.com/Ronnasayd/AI-pair-programming/commit/d2ed8be))
- **[✨ Features]** Add agent-flow hooks to all lifecycle events ([2850cfd](https://github.com/Ronnasayd/AI-pair-programming/commit/2850cfd))
- **[🧹 Chores]** Add osd shortcut for opencode-supervisor dashboard ([eb58261](https://github.com/Ronnasayd/AI-pair-programming/commit/eb58261))
- **[🧹 Chores]** Rename create-commit prompt to .md and tweak aliases ([79110f0](https://github.com/Ronnasayd/AI-pair-programming/commit/79110f0))

### **2026-08-03**

- **[✨ Features]** Isolate task execution in worktrees with run-branch merge and post-merge verify ([f2f9540](https://github.com/Ronnasayd/AI-pair-programming/commit/f2f9540))

### **2026-07-31**

- **[♻️ Refactoring]** Use .git/info/exclude instead of .gitignore for local ignores ([5a3daeb](https://github.com/Ronnasayd/AI-pair-programming/commit/5a3daeb))
- **[📚 Documentation]** Add semantic-grilling prompt command ([da2ab3a](https://github.com/Ronnasayd/AI-pair-programming/commit/da2ab3a))

### **2026-07-30**

- **[📚 Documentation]** Fix run-branch naming and pending-task filter in tlc-execute-tasks-adversarial ([af8bf9c](https://github.com/Ronnasayd/AI-pair-programming/commit/af8bf9c))
- **[♻️ Refactoring]** Add log ([e16105e](https://github.com/Ronnasayd/AI-pair-programming/commit/e16105e))
- **[🐛 Bug Fixes]** Skip session-end jest coverage if already running ([1e79c6d](https://github.com/Ronnasayd/AI-pair-programming/commit/1e79c6d))
- **[♻️ Refactoring]** Trigger worktree init from enterworktree posttooluse ([6e4fc7c](https://github.com/Ronnasayd/AI-pair-programming/commit/6e4fc7c))
- **[🐛 Bug Fixes]** Prefer explicit worktree path fields over cwd ([5af686a](https://github.com/Ronnasayd/AI-pair-programming/commit/5af686a))
- **[🐛 Bug Fixes]** Echo worktree path from worktreecreate hook ([b1df04d](https://github.com/Ronnasayd/AI-pair-programming/commit/b1df04d))
- **[✨ Features]** Symlink node_modules into new worktrees ([41b2410](https://github.com/Ronnasayd/AI-pair-programming/commit/41b2410))
- **[📚 Documentation]** Add run-branch isolation and review-merge step ([2a6c7cc](https://github.com/Ronnasayd/AI-pair-programming/commit/2a6c7cc))
- **[♻️ Refactoring]** Pass full payload to rule match predicates ([5c3f838](https://github.com/Ronnasayd/AI-pair-programming/commit/5c3f838))
- **[♻️ Refactoring]** Rename context-rules hook to support posttooluse ([5a1c067](https://github.com/Ronnasayd/AI-pair-programming/commit/5a1c067))
- **[📚 Documentation]** Replace skill's requirements-doc structure with domain-table format ([8a2ee7d](https://github.com/Ronnasayd/AI-pair-programming/commit/8a2ee7d))
- **[🐛 Bug Fixes]** Raise context7 match thresholds, expand debug log fields ([376ffc8](https://github.com/Ronnasayd/AI-pair-programming/commit/376ffc8))
- **[✨ Features]** Inject package.json scripts into sessionstart context ([59d3f3e](https://github.com/Ronnasayd/AI-pair-programming/commit/59d3f3e))
- **[📚 Documentation]** Drop mcp suffix from tool names in start.md rules ([65323c7](https://github.com/Ronnasayd/AI-pair-programming/commit/65323c7))
- **[📚 Documentation]** Add mcp-manager tools table to start.md hook ([ce5ee2d](https://github.com/Ronnasayd/AI-pair-programming/commit/ce5ee2d))
- **[🐛 Bug Fixes]** Match tlc-execute-tasks-adversarial in context rule regex ([b5b663e](https://github.com/Ronnasayd/AI-pair-programming/commit/b5b663e))

### **2026-07-29**

- **[✨ Features]** Compress extract-software-requirements skill, add last-n extraction ([32f4280](https://github.com/Ronnasayd/AI-pair-programming/commit/32f4280))
- **[♻️ Refactoring]** Replace start prompt with sessionstart hook injecting rules ([836dce6](https://github.com/Ronnasayd/AI-pair-programming/commit/836dce6))
- **[♻️ Refactoring]** Replace start prompt with sessionstart hook injecting rules ([2be8c19](https://github.com/Ronnasayd/AI-pair-programming/commit/2be8c19))
- **[♻️ Refactoring]** Rebuild manifest ([bcf2c38](https://github.com/Ronnasayd/AI-pair-programming/commit/bcf2c38))
- **[♻️ Refactoring]** Rename simplified-technical-english skill to ste, add ste-pt ([2aaabbf](https://github.com/Ronnasayd/AI-pair-programming/commit/2aaabbf))
- **[🧹 Chores]** Change style ([e46836d](https://github.com/Ronnasayd/AI-pair-programming/commit/e46836d))
- **[♻️ Refactoring]** Derive ai_project_root_dir at install time instead of hardcoding ([55e9dfb](https://github.com/Ronnasayd/AI-pair-programming/commit/55e9dfb))
- **[♻️ Refactoring]** Verifi *rc files before insert ([a1a2da9](https://github.com/Ronnasayd/AI-pair-programming/commit/a1a2da9))
- **[♻️ Refactoring]** Adjust names ([cec376d](https://github.com/Ronnasayd/AI-pair-programming/commit/cec376d))
- **[♻️ Refactoring]** Auto install alias ([69a0d84](https://github.com/Ronnasayd/AI-pair-programming/commit/69a0d84))
- **[🐛 Bug Fixes]** Split commands ([9244a7d](https://github.com/Ronnasayd/AI-pair-programming/commit/9244a7d))
- **[🐛 Bug Fixes]** Adjust path ([fe521ff](https://github.com/Ronnasayd/AI-pair-programming/commit/fe521ff))
- **[✨ Features]** Add build.sh helper install script and reference it in install.sh ([0f53eb9](https://github.com/Ronnasayd/AI-pair-programming/commit/0f53eb9))
- **[🐛 Bug Fixes]** Adjust icon ([bbf050c](https://github.com/Ronnasayd/AI-pair-programming/commit/bbf050c))
- **[✨ Features]** Add serena status indicator to statusline and alias ([cb64bb7](https://github.com/Ronnasayd/AI-pair-programming/commit/cb64bb7))

### **2026-07-28**

- **[🐛 Bug Fixes]** Use $ai_project_root_dir in statusline command path ([b79d816](https://github.com/Ronnasayd/AI-pair-programming/commit/b79d816))
- **[♻️ Refactoring]** Rename ai_project_dir to ai_project_root_dir ([9b1eb3d](https://github.com/Ronnasayd/AI-pair-programming/commit/9b1eb3d))
- **[♻️ Refactoring]** Adjsut text ([f14f9ab](https://github.com/Ronnasayd/AI-pair-programming/commit/f14f9ab))
- **[🐛 Bug Fixes]** Add rtk install command ([3b4d3d7](https://github.com/Ronnasayd/AI-pair-programming/commit/3b4d3d7))
- **[🐛 Bug Fixes]** Add more verbose messages ([f1f92ef](https://github.com/Ronnasayd/AI-pair-programming/commit/f1f92ef))
- **[🐛 Bug Fixes]** Add install fastembed ([724ebb4](https://github.com/Ronnasayd/AI-pair-programming/commit/724ebb4))
- **[✨ Features]** Allow read-only mcp tools in permission allow list ([78a28d7](https://github.com/Ronnasayd/AI-pair-programming/commit/78a28d7))
- **[✨ Features]** Add per-file lockfile to jest coverage hooks to prevent races ([8a7777f](https://github.com/Ronnasayd/AI-pair-programming/commit/8a7777f))
- **[✨ Features]** Colorize account email in statusline output ([9484319](https://github.com/Ronnasayd/AI-pair-programming/commit/9484319))
- **[✨ Features]** Add debug logging and empty-data guard to embedding daemon ([211d955](https://github.com/Ronnasayd/AI-pair-programming/commit/211d955))

### **2026-07-27**

- **[✨ Features]** Add config path arg and account email to statusline/dmsl scripts ([8697487](https://github.com/Ronnasayd/AI-pair-programming/commit/8697487))
- **[✨ Features]** Add jest coverage reporting hook with additionalcontext ([533b4d8](https://github.com/Ronnasayd/AI-pair-programming/commit/533b4d8))
- **[✨ Features]** Add jest coverage session end hook and utilities ([d578652](https://github.com/Ronnasayd/AI-pair-programming/commit/d578652))
- **[✨ Features]** Improve html report file handling in coverage merge ([4780918](https://github.com/Ronnasayd/AI-pair-programming/commit/4780918))
- **[✨ Features]** Enhance coverage merging and reporting functionality ([4084487](https://github.com/Ronnasayd/AI-pair-programming/commit/4084487))
- **[✨ Features]** Implement coverage merging functionality ([e84cdbf](https://github.com/Ronnasayd/AI-pair-programming/commit/e84cdbf))
- **[🐛 Bug Fixes]** Correct coverage file handling in incremental hook ([cc302bd](https://github.com/Ronnasayd/AI-pair-programming/commit/cc302bd))
- **[✨ Features]** Enhance incremental coverage merging process ([d945fe4](https://github.com/Ronnasayd/AI-pair-programming/commit/d945fe4))
- **[✨ Features]** Add coverage report generation to incremental hook ([8d683c8](https://github.com/Ronnasayd/AI-pair-programming/commit/8d683c8))
- **[✨ Features]** Update jest command to use --findrelatedtests option ([a8be1d6](https://github.com/Ronnasayd/AI-pair-programming/commit/a8be1d6))
- **[✨ Features]** Add incremental jest coverage hook and update models ([8653591](https://github.com/Ronnasayd/AI-pair-programming/commit/8653591))

### **2026-07-25**

- **[✨ Features]** Add 9router-medium model and update environment variables ([d740fc4](https://github.com/Ronnasayd/AI-pair-programming/commit/d740fc4))
- **[✨ Features]** Add start_embedding_daemon.py script for pre-warming daemon ([ac8ebf4](https://github.com/Ronnasayd/AI-pair-programming/commit/ac8ebf4))
- **[✨ Features]** Add rag-rat status to status line output ([11dd71f](https://github.com/Ronnasayd/AI-pair-programming/commit/11dd71f))
- **[🧹 Chores]** Add debug logging to external hooks and rag-rat init alias ([8c344e2](https://github.com/Ronnasayd/AI-pair-programming/commit/8c344e2))
- **[🐛 Bug Fixes]** Update .gitignore and settings for rag-rat plugin ([532eae1](https://github.com/Ronnasayd/AI-pair-programming/commit/532eae1))
- **[🐛 Bug Fixes]** Disable tool search in headroom wrap command ([73da076](https://github.com/Ronnasayd/AI-pair-programming/commit/73da076))
- **[🐛 Bug Fixes]** Replace session_start.py with start_embedding_daemon.py ([e7be590](https://github.com/Ronnasayd/AI-pair-programming/commit/e7be590))

### **2026-07-24**

- **[🐛 Bug Fixes]** Update headroom alias and script for cleanup ([d390302](https://github.com/Ronnasayd/AI-pair-programming/commit/d390302))
- **[✨ Features]** Add headroom start script and new alias for it ([d606116](https://github.com/Ronnasayd/AI-pair-programming/commit/d606116))
- **[🐛 Bug Fixes]** Add completion message to install script ([1032f2a](https://github.com/Ronnasayd/AI-pair-programming/commit/1032f2a))
- **[🐛 Bug Fixes]** Update command usage in install script for clarity ([def522c](https://github.com/Ronnasayd/AI-pair-programming/commit/def522c))
- **[🐛 Bug Fixes]** Ensure context-refs.json symlink creation and add directory checks ([0e4639c](https://github.com/Ronnasayd/AI-pair-programming/commit/0e4639c))
- **[🐛 Bug Fixes]** Add github_pat_token check in update-external-tools.sh ([b0b7fb8](https://github.com/Ronnasayd/AI-pair-programming/commit/b0b7fb8))
- **[📚 Documentation]** Update readme.md for clarity and structure improvements ([7a54c79](https://github.com/Ronnasayd/AI-pair-programming/commit/7a54c79))
- **[📚 Documentation]** Remove outdated sections from readme.md for clarity ([3dd8f14](https://github.com/Ronnasayd/AI-pair-programming/commit/3dd8f14))
- **[🐛 Bug Fixes]** Update alias for ai context generator to 'iai' ([b42d108](https://github.com/Ronnasayd/AI-pair-programming/commit/b42d108))
- **[🐛 Bug Fixes]** Add support for 'path' in file access checks ([fadc6f2](https://github.com/Ronnasayd/AI-pair-programming/commit/fadc6f2))
- **[✨ Features]** Enhance scoring mechanism in topresults function ([cf38cd8](https://github.com/Ronnasayd/AI-pair-programming/commit/cf38cd8))
- **[🐛 Bug Fixes]** Remove context from debug messages in hooks scripts ([7138458](https://github.com/Ronnasayd/AI-pair-programming/commit/7138458))
- **[✨ Features]** Enhance context7 search with daemon integration ([8b113ae](https://github.com/Ronnasayd/AI-pair-programming/commit/8b113ae))
- **[🐛 Bug Fixes]** Prevent execution if stop hook is active added a check to exit early if the 'stop_hook_active' key is present in the payload, ensuring that the script does not proceed when the hook is disabled. ([e78ae57](https://github.com/Ronnasayd/AI-pair-programming/commit/e78ae57))
- **[🐛 Bug Fixes]** Remove 'context7' from disabled mcp servers list ([22fee25](https://github.com/Ronnasayd/AI-pair-programming/commit/22fee25))
- **[✨ Features]** Add context7 search command and script ([e57e6e6](https://github.com/Ronnasayd/AI-pair-programming/commit/e57e6e6))
- **[🐛 Bug Fixes]** Add debug logging for output in hooks scripts ([b84b5bb](https://github.com/Ronnasayd/AI-pair-programming/commit/b84b5bb))
- **[✨ Features]** Add hooks for subagent guidelines and question tool enforcement ([7524ef9](https://github.com/Ronnasayd/AI-pair-programming/commit/7524ef9))
- **[🐛 Bug Fixes]** Improve instructions for file editing rules updated the instructions to clarify the process of finding and following rules for matching file types before editing or creating files. this enhances user understanding and compliance with file handling protocols. ([1561cf4](https://github.com/Ronnasayd/AI-pair-programming/commit/1561cf4))
- **[🐛 Bug Fixes]** Update ref path to use /tmp for non-absolute paths ([4a75189](https://github.com/Ronnasayd/AI-pair-programming/commit/4a75189))
- **[✨ Features]** Add command to remove orphaned containers in env script ([a08c442](https://github.com/Ronnasayd/AI-pair-programming/commit/a08c442))

### **2026-07-23**

- **[✨ Features]** Configure 9router models as defaults in env script ([2aa436e](https://github.com/Ronnasayd/AI-pair-programming/commit/2aa436e))
- **[✨ Features]** Add 9router models and update environment setup ([29ff34a](https://github.com/Ronnasayd/AI-pair-programming/commit/29ff34a))

### **2026-07-22**

- **[✨ Features]** Restructure figma capture skills and templates ([63961ce](https://github.com/Ronnasayd/AI-pair-programming/commit/63961ce))
- **[✨ Features]** Add large file read warning hook ([c86db52](https://github.com/Ronnasayd/AI-pair-programming/commit/c86db52))
- **[🐛 Bug Fixes]** Reduce refresh interval from 20 to 10 seconds ([2c849dc](https://github.com/Ronnasayd/AI-pair-programming/commit/2c849dc))
- **[✨ Features]** Enhance context refs hook for file editing ([a9292d6](https://github.com/Ronnasayd/AI-pair-programming/commit/a9292d6))
- **[✨ Features]** Enhance description extraction from ref files ([93558cc](https://github.com/Ronnasayd/AI-pair-programming/commit/93558cc))
- **[✨ Features]** Update context refs hook to point to file locations ([a3a2618](https://github.com/Ronnasayd/AI-pair-programming/commit/a3a2618))
- **[✨ Features]** Add scripts for checking and extracting ste dictionary ([5cbe653](https://github.com/Ronnasayd/AI-pair-programming/commit/5cbe653))

### **2026-07-21**

- **[✨ Features]** Add instructions loaded hook for log processing ([8458b09](https://github.com/Ronnasayd/AI-pair-programming/commit/8458b09))
- **[✨ Features]** Update scripts and add disable-mcps-default.py ([0f24545](https://github.com/Ronnasayd/AI-pair-programming/commit/0f24545))
- **[✨ Features]** Update execution steps and tracking instructions ([d5f533c](https://github.com/Ronnasayd/AI-pair-programming/commit/d5f533c))

### **2026-07-20**

- **[✨ Features]** Update task execution description and wave dispatch logic ([4fd60fd](https://github.com/Ronnasayd/AI-pair-programming/commit/4fd60fd))
- **[✨ Features]** Add mutation-testing instructions for stryker analysis ([fb1602a](https://github.com/Ronnasayd/AI-pair-programming/commit/fb1602a))
- **[✨ Features]** Update headroom proxy status icons in status line script ([ed9db31](https://github.com/Ronnasayd/AI-pair-programming/commit/ed9db31))
- **[✨ Features]** Add headroom proxy status to status line script ([4b0186f](https://github.com/Ronnasayd/AI-pair-programming/commit/4b0186f))
- **[✨ Features]** Add mutation-survivor-triage skill for stryker analysis ([2547270](https://github.com/Ronnasayd/AI-pair-programming/commit/2547270))
- **[✨ Features]** Add coverage-gap-audit skill for jest test coverage analysis ([9442238](https://github.com/Ronnasayd/AI-pair-programming/commit/9442238))
- **[✨ Features]** Add litellm docker setup and configuration files ([b2fc929](https://github.com/Ronnasayd/AI-pair-programming/commit/b2fc929))
- **[✨ Features]** Add new aliases for headroom and token saving ([4b7932a](https://github.com/Ronnasayd/AI-pair-programming/commit/4b7932a))
- **[✨ Features]** Add usage instructions for task tracking in skill.md added instructions on using taskcreate, taskget, tasklist, and taskupdate to track wave/task progress alongside taskmaster mcp updates. ([d154a07](https://github.com/Ronnasayd/AI-pair-programming/commit/d154a07))

### **2026-07-18**

- **[✨ Features]** Update image-mockup-recreator skill and add overlay diff script ([b22811f](https://github.com/Ronnasayd/AI-pair-programming/commit/b22811f))
- **[✨ Features]** Add color comparison script and update ssim thresholds ([51bebb9](https://github.com/Ronnasayd/AI-pair-programming/commit/51bebb9))

### **2026-07-17**

- **[✨ Features]** Enhance logging for hooks with customizable log file ([96ecfcc](https://github.com/Ronnasayd/AI-pair-programming/commit/96ecfcc))
- **[✨ Features]** Update pr review skill documentation and add examples ([0dc888d](https://github.com/Ronnasayd/AI-pair-programming/commit/0dc888d))
- **[✨ Features]** Add guidelines for creating subagents in start.prompt.md ([ebc3ef9](https://github.com/Ronnasayd/AI-pair-programming/commit/ebc3ef9))

### **2026-07-16**

- **[✨ Features]** Update figma-capture skill to version 1.5.0 ([3606c02](https://github.com/Ronnasayd/AI-pair-programming/commit/3606c02))
- **[✨ Features]** Update figma-capture skill version to 1.4.0 ([8c59472](https://github.com/Ronnasayd/AI-pair-programming/commit/8c59472))
- **[✨ Features]** Update figma-capture skill and add new scripts ([c6124e1](https://github.com/Ronnasayd/AI-pair-programming/commit/c6124e1))
- **[✨ Features]** Update image-mockup-recreator skill and add examples ([7f42784](https://github.com/Ronnasayd/AI-pair-programming/commit/7f42784))
- **[✨ Features]** Update figma-capture skill documentation and examples ([e7cf68a](https://github.com/Ronnasayd/AI-pair-programming/commit/e7cf68a))
- **[✨ Features]** Update skill documentation and examples ([748bab2](https://github.com/Ronnasayd/AI-pair-programming/commit/748bab2))
- **[📚 Documentation]** Update test and vue coding standards ([acd22ff](https://github.com/Ronnasayd/AI-pair-programming/commit/acd22ff))

### **2026-07-15**

- **[✨ Features]** Improve instructions for file creation ([c5e4670](https://github.com/Ronnasayd/AI-pair-programming/commit/c5e4670))
- **[✨ Features]** Enhance skill with references and examples ([8d4179a](https://github.com/Ronnasayd/AI-pair-programming/commit/8d4179a))
- **[✨ Features]** Add compress-skill and update related documentation ([91b7b9b](https://github.com/Ronnasayd/AI-pair-programming/commit/91b7b9b))
- **[🧹 Chores]** Remove obsolete rules document ([c059fe3](https://github.com/Ronnasayd/AI-pair-programming/commit/c059fe3))
- **[✨ Features]** Add rules for editing and large sessions ([75ec5c9](https://github.com/Ronnasayd/AI-pair-programming/commit/75ec5c9))
- **[🐛 Bug Fixes]** Remove redundant traceability footer section ([beb1740](https://github.com/Ronnasayd/AI-pair-programming/commit/beb1740))
- **[✨ Features]** Add extract-automation-candidates skill ([9a8eeaa](https://github.com/Ronnasayd/AI-pair-programming/commit/9a8eeaa))
- **[✨ Features]** Add skill and scripts for automation extraction ([047b12b](https://github.com/Ronnasayd/AI-pair-programming/commit/047b12b))
- **[🐛 Bug Fixes]** Update applyto pattern for markdown files ([494a3d6](https://github.com/Ronnasayd/AI-pair-programming/commit/494a3d6))
- **[🐛 Bug Fixes]** Correct awk condition in extract_body function ([5249496](https://github.com/Ronnasayd/AI-pair-programming/commit/5249496))
- **[🐛 Bug Fixes]** Update model to haiku in settings.json ([f7b2dbd](https://github.com/Ronnasayd/AI-pair-programming/commit/f7b2dbd))
- **[✨ Features]** Enhance instruction and skill linking for agents ([0efe982](https://github.com/Ronnasayd/AI-pair-programming/commit/0efe982))

### **2026-07-14**

- **[✨ Features]** Enhance context usage reporting in status line script ([405b16e](https://github.com/Ronnasayd/AI-pair-programming/commit/405b16e))
- **[🧹 Chores]** Remove disabled mcp servers from settings.json ([0793f17](https://github.com/Ronnasayd/AI-pair-programming/commit/0793f17))
- **[✨ Features]** Enable auto compact and ensure always thinking is disabled ([29f48de](https://github.com/Ronnasayd/AI-pair-programming/commit/29f48de))
- **[✨ Features]** Update lintfix alias to use uv run with claude-agent-sdk feat(mcp): change mcp-manager command to use uvx with git source chore(uv.lock): add uv.lock file with version and python requirements ([7c7e5c4](https://github.com/Ronnasayd/AI-pair-programming/commit/7c7e5c4))
- **[🐛 Bug Fixes]** Update model from haiku to sonnet in settings.json docs(skill): refine description for tlc-execute-tasks-adversarial skill ([0900d22](https://github.com/Ronnasayd/AI-pair-programming/commit/0900d22))
- **[✨ Features]** Add additional allowed file patterns for image files ([be3d4f9](https://github.com/Ronnasayd/AI-pair-programming/commit/be3d4f9))
- **[✨ Features]** Add tlc-execute-tasks-adversarial skill and update manifest ([9513cd5](https://github.com/Ronnasayd/AI-pair-programming/commit/9513cd5))
- **[✨ Features]** Remove old tlc-execute-tasks references and add adversarial execution skill ([b837980](https://github.com/Ronnasayd/AI-pair-programming/commit/b837980))
- **[✨ Features]** Add environment variable expansion for command targets ([2a2106a](https://github.com/Ronnasayd/AI-pair-programming/commit/2a2106a))
- **[♻️ Refactoring]** Enhance path normalization and pattern matching for security ([3d76dce](https://github.com/Ronnasayd/AI-pair-programming/commit/3d76dce))
- **[✨ Features]** Add content-based secret scanning functionality ([1ea4bd0](https://github.com/Ronnasayd/AI-pair-programming/commit/1ea4bd0))

### **2026-07-13**

- **[♻️ Refactoring]** Bound token cost and disable subagent commits in adversarial-dev/tlc-execute-tasks ([7588bc4](https://github.com/Ronnasayd/AI-pair-programming/commit/7588bc4))
- **[♻️ Refactoring]** Reorder cross-source precedence to commits > specs > transcripts ([f042e13](https://github.com/Ronnasayd/AI-pair-programming/commit/f042e13))
- **[✨ Features]** Add extract-software-requirements skill ([da988e0](https://github.com/Ronnasayd/AI-pair-programming/commit/da988e0))
- **[♻️ Refactoring]** Add home_dir ([820b5b3](https://github.com/Ronnasayd/AI-pair-programming/commit/820b5b3))
- **[✨ Features]** Add per-task executor model selection to tlc-execute-tasks ([6969919](https://github.com/Ronnasayd/AI-pair-programming/commit/6969919))
- **[♻️ Refactoring]** Route tlc-execute-tasks execution through adversarial-dev ([8cb500e](https://github.com/Ronnasayd/AI-pair-programming/commit/8cb500e))
- **[✨ Features]** Add adversarial-dev skill ([dc88a47](https://github.com/Ronnasayd/AI-pair-programming/commit/dc88a47))
- **[✨ Features]** Add adversarial-dev skill for dual-agent generator/evaluator loops ([bcb74c7](https://github.com/Ronnasayd/AI-pair-programming/commit/bcb74c7))

### **2026-07-12**

- **[🧹 Chores]** Register index and manifest ([1ec7e36](https://github.com/Ronnasayd/AI-pair-programming/commit/1ec7e36))
- **[✨ Features]** Add image mockup recreator skill ([a6dceca](https://github.com/Ronnasayd/AI-pair-programming/commit/a6dceca))
- **[✨ Features]** Add script to overlay pixel grid on images ([d837c93](https://github.com/Ronnasayd/AI-pair-programming/commit/d837c93))

### **2026-07-11**

- **[♻️ Refactoring]** Add sync agents summary ([fe5bef9](https://github.com/Ronnasayd/AI-pair-programming/commit/fe5bef9))
- **[♻️ Refactoring]** Update skills ([e966ce4](https://github.com/Ronnasayd/AI-pair-programming/commit/e966ce4))
- **[♻️ Refactoring]** Change names to avoid colision ([a5e965f](https://github.com/Ronnasayd/AI-pair-programming/commit/a5e965f))
- **[✨ Features]** Add relavant skills ([c31b02d](https://github.com/Ronnasayd/AI-pair-programming/commit/c31b02d))
- **[♻️ Refactoring]** Update skills ignore ([8dedcff](https://github.com/Ronnasayd/AI-pair-programming/commit/8dedcff))
- **[✨ Features]** Add new skills ([9ed703e](https://github.com/Ronnasayd/AI-pair-programming/commit/9ed703e))
- **[🚧 Other Changes]** C58bde4 - feat:add new skills | 2026-07-11
- **[🐛 Bug Fixes]** Resolve skills.db path via ai_project_dir env var ([19b1a95](https://github.com/Ronnasayd/AI-pair-programming/commit/19b1a95))
- **[🐛 Bug Fixes]** Use absolute $ai_project_dir path for hook scripts ([27859e5](https://github.com/Ronnasayd/AI-pair-programming/commit/27859e5))
- **[🐛 Bug Fixes]** Handle manifest entries as plain path strings ([22dc23e](https://github.com/Ronnasayd/AI-pair-programming/commit/22dc23e))
- **[✨ Features]** Support fetching adjacent skill files ([1f11dce](https://github.com/Ronnasayd/AI-pair-programming/commit/1f11dce))
- **[♻️ Refactoring]** Drop stale .agents skills path and prune index entries ([4c8c56c](https://github.com/Ronnasayd/AI-pair-programming/commit/4c8c56c))

### **2026-07-10**

- **[♻️ Refactoring]** Sync external skills and improve tool script error handling ([f863500](https://github.com/Ronnasayd/AI-pair-programming/commit/f863500))
- **[♻️ Refactoring]** Update external skills ([068dcd3](https://github.com/Ronnasayd/AI-pair-programming/commit/068dcd3))
- **[🐛 Bug Fixes]** Use relative hook paths instead of $claude_project_dir ([f5bc43f](https://github.com/Ronnasayd/AI-pair-programming/commit/f5bc43f))
- **[🐛 Bug Fixes]** Scope rtk permission rules by subcommand ([01a3092](https://github.com/Ronnasayd/AI-pair-programming/commit/01a3092))
- **[🐛 Bug Fixes]** Use project root as cwd for lint-fix subagents so hooks resolve ([6816d86](https://github.com/Ronnasayd/AI-pair-programming/commit/6816d86))
- **[🐛 Bug Fixes]** Use $claude_project_dir for hook script paths ([a529141](https://github.com/Ronnasayd/AI-pair-programming/commit/a529141))
- **[✨ Features]** Load global claude settings for lint-fix subagents ([c4ca229](https://github.com/Ronnasayd/AI-pair-programming/commit/c4ca229))
- **[✨ Features]** Add concurrent eslint auto-fix agent script ([02e09ea](https://github.com/Ronnasayd/AI-pair-programming/commit/02e09ea))

### **2026-07-08**

- **[✨ Features]** Add context7 mcp server config ([e3ad190](https://github.com/Ronnasayd/AI-pair-programming/commit/e3ad190))
- **[✨ Features]** Fall back to git mirror for missing context refs ([ae87bcf](https://github.com/Ronnasayd/AI-pair-programming/commit/ae87bcf))
- **[♻️ Refactoring]** Move colorize_json to utils, drop regex-based coloring ([4331a67](https://github.com/Ronnasayd/AI-pair-programming/commit/4331a67))
- **[📚 Documentation]** Rewrite frontmatter descriptions for all instruction files ([e41764d](https://github.com/Ronnasayd/AI-pair-programming/commit/e41764d))

### **2026-07-07**

- **[🐛 Bug Fixes]** Scope viewer css to avoid class/tag collisions ([24003b3](https://github.com/Ronnasayd/AI-pair-programming/commit/24003b3))
- **[✨ Features]** Add html viewer for captured figma nodes ([2890b0b](https://github.com/Ronnasayd/AI-pair-programming/commit/2890b0b))
- **[🚧 Other Changes]** Add similar_code_ref eval suite ([6581816](https://github.com/Ronnasayd/AI-pair-programming/commit/6581816))
- **[🚧 Other Changes]** Add context_refs eval suite ([867e264](https://github.com/Ronnasayd/AI-pair-programming/commit/867e264))
- **[✨ Features]** Add ai-memory hooks instalation ([067ef4a](https://github.com/Ronnasayd/AI-pair-programming/commit/067ef4a))
- **[🧹 Chores]** Update model preference and secure secret handling ([8c05efb](https://github.com/Ronnasayd/AI-pair-programming/commit/8c05efb))
- **[🐛 Bug Fixes]** Harden protect_files exec/getfacl handling, tune permissions, add skill_activation evals ([568a5e5](https://github.com/Ronnasayd/AI-pair-programming/commit/568a5e5))

### **2026-07-06**

- **[🧹 Chores]** Add eval and xargs to ask list for interactive confirmation ([d77573d](https://github.com/Ronnasayd/AI-pair-programming/commit/d77573d))
- **[🧹 Chores]** Add curl and wget to ask permissions ([ee4bf40](https://github.com/Ronnasayd/AI-pair-programming/commit/ee4bf40))
- **[🐛 Bug Fixes]** Harden protect_files with process-substitution detection ([bb7d093](https://github.com/Ronnasayd/AI-pair-programming/commit/bb7d093))
- **[🐛 Bug Fixes]** Harden protect_files and deny with missing checks ([0af4489](https://github.com/Ronnasayd/AI-pair-programming/commit/0af4489))
- **[✨ Features]** Add command classification and opaque-command detection ([0db42d0](https://github.com/Ronnasayd/AI-pair-programming/commit/0db42d0))
- **[✨ Features]** Harden protect_files with exfil detection and interpreter sandboxing ([b2913ac](https://github.com/Ronnasayd/AI-pair-programming/commit/b2913ac))
- **[✨ Features]** Harden protect_files with chaining, substitution, and exfil detection ([9e2f02e](https://github.com/Ronnasayd/AI-pair-programming/commit/9e2f02e))
- **[✨ Features]** Add qa-specialist agent for functional testing and release qa ([b5f0f63](https://github.com/Ronnasayd/AI-pair-programming/commit/b5f0f63))
- **[🧹 Chores]** Simplify hook log aliases from tail -f to cat ([6ee0980](https://github.com/Ronnasayd/AI-pair-programming/commit/6ee0980))
- **[🧹 Chores]** Disable unused mcp servers and add hook debug aliases ([ff9dfff](https://github.com/Ronnasayd/AI-pair-programming/commit/ff9dfff))
- **[🧹 Chores]** Remove mcp-manager instructions from agent guide ([29b9680](https://github.com/Ronnasayd/AI-pair-programming/commit/29b9680))
- **[✨ Features]** Add golang lint hook ([a07ccb7](https://github.com/Ronnasayd/AI-pair-programming/commit/a07ccb7))

### **2026-07-05**

- **[🧹 Chores]** Increase context-refs refresh interval to 20 ([4854a90](https://github.com/Ronnasayd/AI-pair-programming/commit/4854a90))
- **[📚 Documentation]** Add python docstring instructions ([7315da2](https://github.com/Ronnasayd/AI-pair-programming/commit/7315da2))
- **[🐛 Bug Fixes]** Add go support and improve multi-import extraction in similar-code-ref ([db193c0](https://github.com/Ronnasayd/AI-pair-programming/commit/db193c0))
- **[🧹 Chores]** Add comprehensive debug logging to similar-code-ref hook ([ca222a3](https://github.com/Ronnasayd/AI-pair-programming/commit/ca222a3))
- **[✨ Features]** Add similar-code-ref pretooluse hook ([b6d48fc](https://github.com/Ronnasayd/AI-pair-programming/commit/b6d48fc))

### **2026-07-04**

- **[🧹 Chores]** Remove docker run, exec, stop from deny list ([9d3f4e1](https://github.com/Ronnasayd/AI-pair-programming/commit/9d3f4e1))
- **[📚 Documentation]** Add mcp-manager documentation to agents.md and clarify prompt instructions ([c6ce3da](https://github.com/Ronnasayd/AI-pair-programming/commit/c6ce3da))
- **[🧹 Chores]** Negative ([df4b400](https://github.com/Ronnasayd/AI-pair-programming/commit/df4b400))
- **[📚 Documentation]** Add mcp-manager documentation and update code examples ([2bebe73](https://github.com/Ronnasayd/AI-pair-programming/commit/2bebe73))
- **[🐛 Bug Fixes]** Use fixed-string grep and add missing mcp.json gitignore entry ([0ef9256](https://github.com/Ronnasayd/AI-pair-programming/commit/0ef9256))
- **[🧹 Chores]** Add json colorization to logging and enable remote control startup ([f675b36](https://github.com/Ronnasayd/AI-pair-programming/commit/f675b36))

### **2026-07-03**

- **[♻️ Refactoring]** Split skill doc into references ([288a863](https://github.com/Ronnasayd/AI-pair-programming/commit/288a863))
- **[🧹 Chores]** Change default model to haiku and add notification settings ([8cd8240](https://github.com/Ronnasayd/AI-pair-programming/commit/8cd8240))
- **[✨ Features]** Add python code standards guide ([97647cd](https://github.com/Ronnasayd/AI-pair-programming/commit/97647cd))
- **[♻️ Refactoring]** Consolidate lint hook logic into shared utils ([7f8028b](https://github.com/Ronnasayd/AI-pair-programming/commit/7f8028b))
- **[🐛 Bug Fixes]** Enable exit code signaling for jscpd duplicate detection ([2e0ac33](https://github.com/Ronnasayd/AI-pair-programming/commit/2e0ac33))
- **[✨ Features]** Add jscpd duplicate code detection to lint hooks ([c1218d8](https://github.com/Ronnasayd/AI-pair-programming/commit/c1218d8))
- **[✨ Features]** Add remote skill-loader mcp and manifest for cross-project skill activation ([40a7bae](https://github.com/Ronnasayd/AI-pair-programming/commit/40a7bae))
- **[🧹 Chores]** Add scan-codebase-rules-ai-memory skill and ai memory service setup ([5f071c9](https://github.com/Ronnasayd/AI-pair-programming/commit/5f071c9))
- **[📚 Documentation]** Regenerate full history through 2026-07-03 ([c28a178](https://github.com/Ronnasayd/AI-pair-programming/commit/c28a178))
- **[🧹 Chores]** Pin model per prompt file ([14feb2f](https://github.com/Ronnasayd/AI-pair-programming/commit/14feb2f))
- **[🐛 Bug Fixes]** Switch database mcp servers to git-hosted uvx packages ([a3b4b94](https://github.com/Ronnasayd/AI-pair-programming/commit/a3b4b94))
- **[🐛 Bug Fixes]** Fix keycloak spelling and add admin credential env vars ([f231dd7](https://github.com/Ronnasayd/AI-pair-programming/commit/f231dd7))
- **[🧹 Chores]** Reorganize ignore rules and add claude.md pointer ([ff7c6fc](https://github.com/Ronnasayd/AI-pair-programming/commit/ff7c6fc))
- **[🐛 Bug Fixes]** Switch keycloak server to git-hosted uvx package, add gcloud server ([37ed36b](https://github.com/Ronnasayd/AI-pair-programming/commit/37ed36b))

### **2026-07-01**

- **[🐛 Bug Fixes]** Resolve embedding daemon socket never created on cold start ([9b48848](https://github.com/Ronnasayd/AI-pair-programming/commit/9b48848))
- **[🧹 Chores]** Update skillsignore entries and protect skill/instruction dirs ([abeb198](https://github.com/Ronnasayd/AI-pair-programming/commit/abeb198))
- **[🐛 Bug Fixes]** Emit structured json suggestions instead of joined string ([b60896f](https://github.com/Ronnasayd/AI-pair-programming/commit/b60896f))
- **[🐛 Bug Fixes]** Preserve non-ascii chars in json output ([f837fef](https://github.com/Ronnasayd/AI-pair-programming/commit/f837fef))
- **[♻️ Refactoring]** Use full description as hint, activate skill-description-generator ([a4ac5cb](https://github.com/Ronnasayd/AI-pair-programming/commit/a4ac5cb))
- **[📚 Documentation]** Require task* tools for multi-step progress feedback ([1315de4](https://github.com/Ronnasayd/AI-pair-programming/commit/1315de4))
- **[📚 Documentation]** Require task* tools for multi-step progress feedback ([0180c16](https://github.com/Ronnasayd/AI-pair-programming/commit/0180c16))
- **[✨ Features]** Copy kanban board viewer to .taskmaster on generation ([0c55d7e](https://github.com/Ronnasayd/AI-pair-programming/commit/0c55d7e))
- **[✨ Features]** Add standalone kanban board viewer for tasks.json ([26fdcb2](https://github.com/Ronnasayd/AI-pair-programming/commit/26fdcb2))
- **[🧹 Chores]** Activate general-use skills in .skillsignore ([55e84ff](https://github.com/Ronnasayd/AI-pair-programming/commit/55e84ff))
- **[🐛 Bug Fixes]** Preserve unicode in generated skill/agent index.yaml files ([cc87be9](https://github.com/Ronnasayd/AI-pair-programming/commit/cc87be9))
- **[🐛 Bug Fixes]** Tune skill suggestion threshold and strengthen prompt ([8694930](https://github.com/Ronnasayd/AI-pair-programming/commit/8694930))

### **2026-06-30**

- **[✨ Features]** Add keycloak mcp server config and revert default model to sonnet ([ed98d4b](https://github.com/Ronnasayd/AI-pair-programming/commit/ed98d4b))
- **[♻️ Refactoring]** Emphasize agents.md instructions and clean up whitespace ([d458a87](https://github.com/Ronnasayd/AI-pair-programming/commit/d458a87))
- **[🧹 Chores]** Switch default model to haiku and begin ai-memory consolidation ([7704607](https://github.com/Ronnasayd/AI-pair-programming/commit/7704607))
- **[♻️ Refactoring]** Use agents.md for instructions in install scripts ([f1655b4](https://github.com/Ronnasayd/AI-pair-programming/commit/f1655b4))
- **[♻️ Refactoring]** Change shebangs to use /usr/bin/python3 for consistency across scripts ([dc59c6c](https://github.com/Ronnasayd/AI-pair-programming/commit/dc59c6c))

### **2026-06-29**

- **[🧹 Chores]** Add debug logging to skill scoring and remove unused permission setting ([8d77c8d](https://github.com/Ronnasayd/AI-pair-programming/commit/8d77c8d))
- **[🐛 Bug Fixes]** Ensure embeddings use float32 dtype and set default model to haiku ([7df467a](https://github.com/Ronnasayd/AI-pair-programming/commit/7df467a))
- **[♻️ Refactoring]** Replace sentence_transformers with fastembed ([f1a7146](https://github.com/Ronnasayd/AI-pair-programming/commit/f1a7146))

### **2026-06-27**

- **[🐛 Bug Fixes]** Update session start script path in settings.json ([68bac32](https://github.com/Ronnasayd/AI-pair-programming/commit/68bac32))
- **[🧹 Chores]** Switch default model to haiku and adjust skill similarity threshold ([d7021bc](https://github.com/Ronnasayd/AI-pair-programming/commit/d7021bc))
- **[♻️ Refactoring]** Split agent and docs conventions into separate files ([dbb5422](https://github.com/Ronnasayd/AI-pair-programming/commit/dbb5422))

### **2026-06-26**

- **[✨ Features]** Enable parallel execution within waves via orchestrate skill ([9d59936](https://github.com/Ronnasayd/AI-pair-programming/commit/9d59936))
- **[✨ Features]** Switch to multilingual sentence transformer model ([917c27c](https://github.com/Ronnasayd/AI-pair-programming/commit/917c27c))
- **[✨ Features]** Introduce daemon for persistent model serving ([d246402](https://github.com/Ronnasayd/AI-pair-programming/commit/d246402))
- **[🐛 Bug Fixes]** Tighten similarity threshold and fix gitignore path ([f25f42c](https://github.com/Ronnasayd/AI-pair-programming/commit/f25f42c))
- **[✨ Features]** Expand debug logging for vector search pipeline ([9a91de5](https://github.com/Ronnasayd/AI-pair-programming/commit/9a91de5))
- **[✨ Features]** Expand debug logging for vector search pipeline ([5797fbb](https://github.com/Ronnasayd/AI-pair-programming/commit/5797fbb))
- **[✨ Features]** Replace keyword/regex matching with vector search ([5aeb3ef](https://github.com/Ronnasayd/AI-pair-programming/commit/5aeb3ef))

### **2026-06-25**

- **[♻️ Refactoring]** Complete hint descriptions and simplify sync script ([732f353](https://github.com/Ronnasayd/AI-pair-programming/commit/732f353))
- **[🧹 Chores]** Refine keywords and intent patterns for precision ([785c640](https://github.com/Ronnasayd/AI-pair-programming/commit/785c640))
- **[✨ Features]** Add sync script to map index.yaml to skill-rules ([45217fa](https://github.com/Ronnasayd/AI-pair-programming/commit/45217fa))
- **[🐛 Bug Fixes]** Ensure hooks.log exists before tailing in lgh alias ([d4a93ed](https://github.com/Ronnasayd/AI-pair-programming/commit/d4a93ed))
- **[✨ Features]** Enhance skill activation observability ([78f858a](https://github.com/Ronnasayd/AI-pair-programming/commit/78f858a))
- **[✨ Features]** Add skill activation hook to suggest relevant skills ([48663e1](https://github.com/Ronnasayd/AI-pair-programming/commit/48663e1))
- **[🐛 Bug Fixes]** Date command compatibility and display formatting ([6fb9263](https://github.com/Ronnasayd/AI-pair-programming/commit/6fb9263))

### **2026-06-24**

- **[🚧 Other Changes]** Simplify statusline display with nerd font icons and cleaner formatting ([8a02db7](https://github.com/Ronnasayd/AI-pair-programming/commit/8a02db7))
- **[🐛 Bug Fixes]** Adjust context-refs.json symlink check to handle existing files ([1b39a34](https://github.com/Ronnasayd/AI-pair-programming/commit/1b39a34))
- **[✨ Features]** Add codebase-linguistic-analysis skill and extend context references for test and vue files ([42a2989](https://github.com/Ronnasayd/AI-pair-programming/commit/42a2989))
- **[✨ Features]** Add type-specific context references for js, openapi, react, and test files ([ff78056](https://github.com/Ronnasayd/AI-pair-programming/commit/ff78056))
- **[♻️ Refactoring]** Adjust context-refs.json and update install script to symlink it ([caf93dd](https://github.com/Ronnasayd/AI-pair-programming/commit/caf93dd))
- **[♻️ Refactoring]** Update .gitignore and context-refs.json for new rules ([f39b951](https://github.com/Ronnasayd/AI-pair-programming/commit/f39b951))
- **[✨ Features]** Add support for multiple glob patterns in context_refs.py ([bb9d251](https://github.com/Ronnasayd/AI-pair-programming/commit/bb9d251))
- **[♻️ Refactoring]** Simplify glob matching in context_refs.py ([f63fe31](https://github.com/Ronnasayd/AI-pair-programming/commit/f63fe31))
- **[✨ Features]** Add context-refs hook and reorganize skills ([ca142f7](https://github.com/Ronnasayd/AI-pair-programming/commit/ca142f7))
- **[✨ Features]** Add mattpocock engineering skills for diagnosing-bugs and domain-modeling ([6245eb9](https://github.com/Ronnasayd/AI-pair-programming/commit/6245eb9))
- **[✨ Features]** Add grilling skill for stress-testing plans ([25e4f9a](https://github.com/Ronnasayd/AI-pair-programming/commit/25e4f9a))
- **[♻️ Refactoring]** Add mattpocock skills and remove ignored skills ([93fbb21](https://github.com/Ronnasayd/AI-pair-programming/commit/93fbb21))

### **2026-06-23**

- **[✨ Features]** Add analyze-comfyui-workflow-json skill ([c59722d](https://github.com/Ronnasayd/AI-pair-programming/commit/c59722d))
- **[♻️ Refactoring]** Update prompts ([79c083c](https://github.com/Ronnasayd/AI-pair-programming/commit/79c083c))
- **[♻️ Refactoring]** Update skill descriptions to use single quotes for consistency and escape apostrophes. ([bc1fb8e](https://github.com/Ronnasayd/AI-pair-programming/commit/bc1fb8e))

### **2026-06-22**

- **[♻️ Refactoring]** Test coverage review skill and update settings ([50cbb60](https://github.com/Ronnasayd/AI-pair-programming/commit/50cbb60))
- **[✨ Features]** Add permissions for git merge and git commit commands ([b79449f](https://github.com/Ronnasayd/AI-pair-programming/commit/b79449f))
- **[♻️ Refactoring]** Adjust type hints and handle missing file_path in lint scripts ([9c649da](https://github.com/Ronnasayd/AI-pair-programming/commit/9c649da))
- **[♻️ Refactoring]** Add logs for mypy and ruff execution results in python_lint.py ([e76940d](https://github.com/Ronnasayd/AI-pair-programming/commit/e76940d))
- **[✨ Features]** Add python linting hook with mypy and ruff support ([483589d](https://github.com/Ronnasayd/AI-pair-programming/commit/483589d))
- **[♻️ Refactoring]** Update typescript linting to use tsc-files for better performance and support for project references ([71368cc](https://github.com/Ronnasayd/AI-pair-programming/commit/71368cc))

### **2026-06-21**

- **[♻️ Refactoring]** Use local tsc and eslint binaries in typescript lint hook ([6619b61](https://github.com/Ronnasayd/AI-pair-programming/commit/6619b61))
- **[♻️ Refactoring]** Add --quiet flag to eslint command and simplify output data construction ([0502284](https://github.com/Ronnasayd/AI-pair-programming/commit/0502284))
- **[♻️ Refactoring]** Remove .js and .jsx from linting extensions ([6624c65](https://github.com/Ronnasayd/AI-pair-programming/commit/6624c65))
- **[♻️ Refactoring]** Enhance typescript and eslint hooks with detailed results and logging ([f0eab9d](https://github.com/Ronnasayd/AI-pair-programming/commit/f0eab9d))
- **[♻️ Refactoring]** Update post-tool-use hooks and matchers in settings.json ([b7c1980](https://github.com/Ronnasayd/AI-pair-programming/commit/b7c1980))
- **[🧹 Chores]** Updates ([e0ee088](https://github.com/Ronnasayd/AI-pair-programming/commit/e0ee088))
- **[✨ Features]** Allow .claude directory access in protect_files hook ([58d92b4](https://github.com/Ronnasayd/AI-pair-programming/commit/58d92b4))
- **[♻️ Refactoring]** Update quality gate to remove 'strict' mode and related logging ([b09f595](https://github.com/Ronnasayd/AI-pair-programming/commit/b09f595))
- **[♻️ Refactoring]** Add logging hooks for subagent events ([a7ca09f](https://github.com/Ronnasayd/AI-pair-programming/commit/a7ca09f))
- **[✨ Features]** Add logging hook for all hooks to debug and monitor their payloads ([53e589d](https://github.com/Ronnasayd/AI-pair-programming/commit/53e589d))

### **2026-06-19**

- **[✨ Features]** Add prd-get-implicit-requirements skill for analyzing prds and identifying gaps ([ace202f](https://github.com/Ronnasayd/AI-pair-programming/commit/ace202f))
- **[✨ Features]** Add clc alias for conventional commit message generation ([9525788](https://github.com/Ronnasayd/AI-pair-programming/commit/9525788))
- **[♻️ Refactoring]** Improve alias comment clarity and conciseness in .ai.alias.zshrc ([b0ea061](https://github.com/Ronnasayd/AI-pair-programming/commit/b0ea061))
- **[♻️ Refactoring]** Improve ignore file management and ai memory container handling in .ai.alias.zshrc ([16ef461](https://github.com/Ronnasayd/AI-pair-programming/commit/16ef461))
- **[♻️ Refactoring]** Shorten alias names for better usability ([8c98685](https://github.com/Ronnasayd/AI-pair-programming/commit/8c98685))
- **[✨ Features]** Add pr-review skill for systematic github pr analysis and feedback generation ([175ed01](https://github.com/Ronnasayd/AI-pair-programming/commit/175ed01))

### **2026-06-18**

- **[♻️ Refactoring]** Update mcp environment variable defaults and model setting ([b068925](https://github.com/Ronnasayd/AI-pair-programming/commit/b068925))

### **2026-06-17**

- **[🐛 Bug Fixes]** Handle large get_diff output in pr-review skill ([18ddec4](https://github.com/Ronnasayd/AI-pair-programming/commit/18ddec4))
- **[✨ Features]** Add pr-review skill for systematic github pr evaluation ([d86aa31](https://github.com/Ronnasayd/AI-pair-programming/commit/d86aa31))
- **[♻️ Refactoring]** Remove claude.md and .mcp.json from .gitignore in installation script ([ce8d6e6](https://github.com/Ronnasayd/AI-pair-programming/commit/ce8d6e6))
- **[🐛 Bug Fixes]** Update taskmaster mcp calls to use set_task_status with tag parameter ([f092f23](https://github.com/Ronnasayd/AI-pair-programming/commit/f092f23))

### **2026-06-16**

- **[🧹 Chores]** Update claude ([751e681](https://github.com/Ronnasayd/AI-pair-programming/commit/751e681))
- **[🧹 Chores]** Add .mcp.json configuration for multiple mcp servers ([346cd42](https://github.com/Ronnasayd/AI-pair-programming/commit/346cd42))
- **[✨ Features]** Add git command restrictions to settings.json ([e0fa0dd](https://github.com/Ronnasayd/AI-pair-programming/commit/e0fa0dd))
- **[🧹 Chores]** Add attribution fields to settings.json ([e45ebeb](https://github.com/Ronnasayd/AI-pair-programming/commit/e45ebeb))
- **[🧹 Chores]** Update .skillsignore to exclude tlc-execute-tasks skill ([b99f110](https://github.com/Ronnasayd/AI-pair-programming/commit/b99f110))
- **[✨ Features]** Add tlc-execute-tasks skill with tag validation and task execution flow ([7e9232f](https://github.com/Ronnasayd/AI-pair-programming/commit/7e9232f))
- **[✨ Features]** Add active skills, rules, and agents aliases ([4b0f528](https://github.com/Ronnasayd/AI-pair-programming/commit/4b0f528))
- **[♻️ Refactoring]** Update agent context search order and formatting in docs/agent.instructions.md ([0d19f32](https://github.com/Ronnasayd/AI-pair-programming/commit/0d19f32))
- **[♻️ Refactoring]** Format cost to three decimal places in status line ([020970d](https://github.com/Ronnasayd/AI-pair-programming/commit/020970d))
- **[✨ Features]** Add total session cost to status line ([7b5717c](https://github.com/Ronnasayd/AI-pair-programming/commit/7b5717c))
- **[✨ Features]** Add sort when saving ([affb675](https://github.com/Ronnasayd/AI-pair-programming/commit/affb675))
- **[✨ Features]** Add search filter to ignore file manager ui ([7011a3a](https://github.com/Ronnasayd/AI-pair-programming/commit/7011a3a))
- **[✨ Features]** Update taskmaster conversion scripts and tests ([73d4856](https://github.com/Ronnasayd/AI-pair-programming/commit/73d4856))

### **2026-06-15**

- **[🧹 Chores]** Refactor gemini installation ([af24b72](https://github.com/Ronnasayd/AI-pair-programming/commit/af24b72))
- **[🧹 Chores]** Add script to list mcp manager servers and update instructions ([e02a565](https://github.com/Ronnasayd/AI-pair-programming/commit/e02a565))
- **[🧹 Chores]** Adjust mkdir claude instructions to avoid potential issues with symlinks and directories ([f99d8d7](https://github.com/Ronnasayd/AI-pair-programming/commit/f99d8d7))
- **[🧹 Chores]** Update generation claude.md and gemini.md to support context-specific rules ([5b0fe0a](https://github.com/Ronnasayd/AI-pair-programming/commit/5b0fe0a))
- **[✨ Features]** Process all frontmatter fields in converters ([a77433b](https://github.com/Ronnasayd/AI-pair-programming/commit/a77433b))
- **[🧹 Chores]** Update agent instructions and node.js/typescript guidelines ([99e2736](https://github.com/Ronnasayd/AI-pair-programming/commit/99e2736))
- **[🧹 Chores]** Add alias for claude with code execution capabilities ([ff11175](https://github.com/Ronnasayd/AI-pair-programming/commit/ff11175))
- **[🧹 Chores]** Add plansdirectory setting to settings.json ([12affc4](https://github.com/Ronnasayd/AI-pair-programming/commit/12affc4))
- **[✨ Features]** Add caveman mode status to status line ([a318bdc](https://github.com/Ronnasayd/AI-pair-programming/commit/a318bdc))
- **[🧹 Chores]** Update status line script location in settings.json ([d8b7867](https://github.com/Ronnasayd/AI-pair-programming/commit/d8b7867))
- **[✨ Features]** Add skill-description-generator skill with description and frontmatter, update tlc-tasks-to-taskmaster description for better trigger accuracy, and add skill-description-generator to index.yaml and .skillsignore. ([907654b](https://github.com/Ronnasayd/AI-pair-programming/commit/907654b))
- **[✨ Features]** Add tlc-tasks-to-taskmaster skill for converting tasks.md to taskmaster format with execution metadata ([e847f9d](https://github.com/Ronnasayd/AI-pair-programming/commit/e847f9d))
- **[🧹 Chores]** Update status line script with enhanced context and rate limit info ([03ac03c](https://github.com/Ronnasayd/AI-pair-programming/commit/03ac03c))

### **2026-06-13**

- **[🧹 Chores]** Update .skillsignore to include prd-generator ([a8aed2c](https://github.com/Ronnasayd/AI-pair-programming/commit/a8aed2c))
- **[✨ Features]** Add prd generator skill with 5-battery framework and project type patterns reference guide ([54fefef](https://github.com/Ronnasayd/AI-pair-programming/commit/54fefef))
- **[🧹 Chores]** Update settings.json ([d9ada15](https://github.com/Ronnasayd/AI-pair-programming/commit/d9ada15))
- **[🧹 Chores]** Update claude.install.sh ([31ede09](https://github.com/Ronnasayd/AI-pair-programming/commit/31ede09))
- **[🧹 Chores]** Add ai-memory ([5f82b23](https://github.com/Ronnasayd/AI-pair-programming/commit/5f82b23))
- **[🧹 Chores]** Add status line command script for model and context display ([687db0d](https://github.com/Ronnasayd/AI-pair-programming/commit/687db0d))
- **[🧹 Chores]** Add status line command script and update settings ([6ae86bb](https://github.com/Ronnasayd/AI-pair-programming/commit/6ae86bb))

### **2026-06-12**

- **[✨ Features]** Update claude settings and installation script ([c95c8cc](https://github.com/Ronnasayd/AI-pair-programming/commit/c95c8cc))

### **2026-06-11**

- **[🧹 Chores]** Remove skills-lock.json during clean mode execution ([280fa37](https://github.com/Ronnasayd/AI-pair-programming/commit/280fa37))
- **[✨ Features]** Update installation scripts to use npx for adding skills instead of curl ([51d6b7b](https://github.com/Ronnasayd/AI-pair-programming/commit/51d6b7b))
- **[🧹 Chores]** Update .gitignore entries for caveman and cavecrew, add skills-lock.json and .agents/skills/* feat: add activate-caveman command documentation ([6cb3d25](https://github.com/Ronnasayd/AI-pair-programming/commit/6cb3d25))
- **[📚 Documentation]** Clarify instructions for creating files in create-tlc-files prompt ([6bdd72a](https://github.com/Ronnasayd/AI-pair-programming/commit/6bdd72a))
- **[✨ Features]** Add create-tlc-files command documentation ([46012f5](https://github.com/Ronnasayd/AI-pair-programming/commit/46012f5))
- **[✨ Features]** Add task conversion script and restore orchestrate taskmaster prompt ([d570fcb](https://github.com/Ronnasayd/AI-pair-programming/commit/d570fcb))

### **2026-06-10**

- **[✨ Features]** Add mcp_config.json and update installation script to manage mcp configuration ([1c99cf9](https://github.com/Ronnasayd/AI-pair-programming/commit/1c99cf9))
- **[✨ Features]** Add antigravity backend support and clean scripts ([d049f63](https://github.com/Ronnasayd/AI-pair-programming/commit/d049f63))
- **[📚 Documentation]** Add response style guidelines for agent interactions ([eee3b46](https://github.com/Ronnasayd/AI-pair-programming/commit/eee3b46))
- **[🧹 Chores]** Add .sessions/* to .gitignore if not already present ([890f111](https://github.com/Ronnasayd/AI-pair-programming/commit/890f111))

### **2026-06-09**

- **[🐛 Bug Fixes]** Correct condition checks for existing copilot configuration files ([8209bba](https://github.com/Ronnasayd/AI-pair-programming/commit/8209bba))

### **2026-06-06**

- **[🧹 Chores]** Update ignore scripts to ensure all ignore files are added to .gitignore ([fb35e7f](https://github.com/Ronnasayd/AI-pair-programming/commit/fb35e7f))
- **[🚧 Other Changes]** Uncomment test.instructions.md for clarity ([bcf4eff](https://github.com/Ronnasayd/AI-pair-programming/commit/bcf4eff))
- **[📚 Documentation]** Update mcp-manager instructions for clarity and consistency ([f11da00](https://github.com/Ronnasayd/AI-pair-programming/commit/f11da00))

### **2026-06-05**

- **[✨ Features]** Enable additional services in mcp-server-enablement.json configuration ([e5f1c00](https://github.com/Ronnasayd/AI-pair-programming/commit/e5f1c00))
- **[✨ Features]** Implement replace_between function and update claude.md and gemini.md with dynamic instructions ([ecad982](https://github.com/Ronnasayd/AI-pair-programming/commit/ecad982))
- **[🚧 Other Changes]** Comment out specific entries in ignore files for clarity ([8ce37af](https://github.com/Ronnasayd/AI-pair-programming/commit/8ce37af))

### **2026-06-03**

- **[✨ Features]** Set asdf_nodejs_version in install script for environment configuration ([c2d1f5c](https://github.com/Ronnasayd/AI-pair-programming/commit/c2d1f5c))

### **2026-06-02**

- **[✨ Features]** Update installation scripts to check for skills-lock.json before executing installation and updating .gitignore ([6783f10](https://github.com/Ronnasayd/AI-pair-programming/commit/6783f10))
- **[✨ Features]** Add caveman installation and update .gitignore for new patterns ([f5cde45](https://github.com/Ronnasayd/AI-pair-programming/commit/f5cde45))
- **[✨ Features]** Add new prompt files for memory management and task conversion functionalities ([d8e8300](https://github.com/Ronnasayd/AI-pair-programming/commit/d8e8300))
- **[✨ Features]** Update ignore files to enable specified agents and rules for improved functionality ([0bf0acf](https://github.com/Ronnasayd/AI-pair-programming/commit/0bf0acf))

### **2026-05-29**

- **[✨ Features]** Add transcript path handling in session header for improved session continuity ([0b76cbc](https://github.com/Ronnasayd/AI-pair-programming/commit/0b76cbc))
- **[✨ Features]** Update configuration file copying to append missing entries instead of overwriting ([5898c38](https://github.com/Ronnasayd/AI-pair-programming/commit/5898c38))
- **[✨ Features]** Add new skills and update agent descriptions for improved task orchestration and execution ([8185632](https://github.com/Ronnasayd/AI-pair-programming/commit/8185632))

### **2026-05-28**

- **[✨ Features]** Add tcl-execute-tasks-by-orchestrate-taskmaster command prompt documentation ([e21f0c1](https://github.com/Ronnasayd/AI-pair-programming/commit/e21f0c1))
- **[✨ Features]** Add new commands for task orchestration and memory management ([18b2eb2](https://github.com/Ronnasayd/AI-pair-programming/commit/18b2eb2))
- **[✨ Features]** Add mcp-manager instructions for tool usage and examples ([c3b323d](https://github.com/Ronnasayd/AI-pair-programming/commit/c3b323d))
- **[🧹 Chores]** Remove outdated command documentation and add new prompts for task management and ai setup audit ([10fe122](https://github.com/Ronnasayd/AI-pair-programming/commit/10fe122))
- **[✨ Features]** Add new command prompts for task conversion and simulation ([3740fcd](https://github.com/Ronnasayd/AI-pair-programming/commit/3740fcd))

### **2026-05-26**

- **[🐛 Bug Fixes]** Update .skillsignore and skill.md for task delegation clarity ([f3a8733](https://github.com/Ronnasayd/AI-pair-programming/commit/f3a8733))
- **[✨ Features]** Add orchestrate to skills ignore list ([b72a9f0](https://github.com/Ronnasayd/AI-pair-programming/commit/b72a9f0))
- **[✨ Features]** Add orchestrate skill documentation for task coordination and execution strategy ([84842b4](https://github.com/Ronnasayd/AI-pair-programming/commit/84842b4))
- **[🐛 Bug Fixes]** Update .gitignore entries to include wildcard patterns for skills, commands, instructions, agents, and hooks ([cdf2033](https://github.com/Ronnasayd/AI-pair-programming/commit/cdf2033))
- **[✨ Features]** Add orchestrate command documentation for task coordination and execution strategy ([0574089](https://github.com/Ronnasayd/AI-pair-programming/commit/0574089))
- **[🐛 Bug Fixes]** Correct skill-architect entry to skill-specialist in .agentsignore ([a0e0a73](https://github.com/Ronnasayd/AI-pair-programming/commit/a0e0a73))
- **[🐛 Bug Fixes]** Update agent description and instructions for clarity and accuracy ([c27836d](https://github.com/Ronnasayd/AI-pair-programming/commit/c27836d))
- **[✨ Features]** Add openapi instructions for creating *.openapi.ts files ([46c242b](https://github.com/Ronnasayd/AI-pair-programming/commit/46c242b))
- **[✨ Features]** Add comprehensive documentation for claude code hooks ([64d6287](https://github.com/Ronnasayd/AI-pair-programming/commit/64d6287))
- **[🚧 Other Changes]** Fix formatting by removing trailing commas in function parameters and object literals ([2ec286b](https://github.com/Ronnasayd/AI-pair-programming/commit/2ec286b))

### **2026-05-25**

- **[🐛 Bug Fixes]** Update cleanignore alias to remove all ignore files and refine jsdoc applyto patterns ([707751e](https://github.com/Ronnasayd/AI-pair-programming/commit/707751e))
- **[🚧 Other Changes]** Fix formatting by adding missing commas in function parameters and object literals ([eb33774](https://github.com/Ronnasayd/AI-pair-programming/commit/eb33774))
- **[✨ Features]** Add jsdocs instructions and update task documentation for clarity ([74dadb7](https://github.com/Ronnasayd/AI-pair-programming/commit/74dadb7))

### **2026-05-22**

- **[✨ Features]** Add output tag resolution step to tlc-tasks-to-taskmaster skill documentation ([70ca366](https://github.com/Ronnasayd/AI-pair-programming/commit/70ca366))
- **[✨ Features]** Add tasks-md-to-taskmaster-json skill for converting tasks.md to taskmaster format ([9890511](https://github.com/Ronnasayd/AI-pair-programming/commit/9890511))
- **[✨ Features]** Add tlc-tasks-to-taskmaster skill and update related documentation ([ea73f71](https://github.com/Ronnasayd/AI-pair-programming/commit/ea73f71))
- **[🧹 Chores]** Remove unused aliases for ignore and ai context cleanup ([e16f008](https://github.com/Ronnasayd/AI-pair-programming/commit/e16f008))
- **[🧹 Chores]** Update file permissions for clean scripts to executable ([d59238a](https://github.com/Ronnasayd/AI-pair-programming/commit/d59238a))
- **[✨ Features]** Add clean functionality for install scripts to remove symlinks ([d614468](https://github.com/Ronnasayd/AI-pair-programming/commit/d614468))

### **2026-05-21**

- **[🧹 Chores]** Update .skillsignore to reorganize skills and remove commented entries ([a5e91e3](https://github.com/Ronnasayd/AI-pair-programming/commit/a5e91e3))
- **[✨ Features]** Add figma-capture skill to capture screenshots and jsx from figma nodes ([5757859](https://github.com/Ronnasayd/AI-pair-programming/commit/5757859))
- **[♻️ Refactoring]** Streamline symlink management for skills, commands, hooks, and agents in installation scripts ([6c2d2b2](https://github.com/Ronnasayd/AI-pair-programming/commit/6c2d2b2))
- **[🧹 Chores]** Update symlink management for skills, prompts, hooks, agents, and instructions in copilot installation script ([37b45fe](https://github.com/Ronnasayd/AI-pair-programming/commit/37b45fe))
- **[✨ Features]** Enable modular-monolith-decomposer in skills ignore list ([3e45331](https://github.com/Ronnasayd/AI-pair-programming/commit/3e45331))
- **[✨ Features]** Add modular monolith decomposer skill and folder structure rules documentation ([a96b7f8](https://github.com/Ronnasayd/AI-pair-programming/commit/a96b7f8))
- **[📚 Documentation]** Improve formatting and clarity in documentation sections for srs and task generation steps ([96139e9](https://github.com/Ronnasayd/AI-pair-programming/commit/96139e9))

### **2026-05-20**

- **[📚 Documentation]** Remove context section from code instructions to clarify scope of rules ([0240cc5](https://github.com/Ronnasayd/AI-pair-programming/commit/0240cc5))
- **[📚 Documentation]** Update agent behavior documentation; simplify descriptions and enhance clarity on interactive question tools ([4b64db5](https://github.com/Ronnasayd/AI-pair-programming/commit/4b64db5))
- **[✨ Features]** Update documentation for agent behavior, http api, node.js/typescript, react, and vue standards; remove outdated reactjs instructions ([184fc40](https://github.com/Ronnasayd/AI-pair-programming/commit/184fc40))
- **[✨ Features]** Add rules management to ignore file manager ([913acc5](https://github.com/Ronnasayd/AI-pair-programming/commit/913acc5))
- **[✨ Features]** Add .rulesignore file and update scripts to handle rules ignoring ([40bcde6](https://github.com/Ronnasayd/AI-pair-programming/commit/40bcde6))
- **[✨ Features]** Add vuejs 3 development instructions and best practices documentation ([1ad30a4](https://github.com/Ronnasayd/AI-pair-programming/commit/1ad30a4))
- **[✨ Features]** Add additional rules for vue code standards and split complex computed properties into simpler ones ([66f4e88](https://github.com/Ronnasayd/AI-pair-programming/commit/66f4e88))
- **[✨ Features]** Add rules for code standards in vue_rules_prompt.md ([695208f](https://github.com/Ronnasayd/AI-pair-programming/commit/695208f))
- **[✨ Features]** Add initial rules for code standards in react_rules_prompt.md ([d2a3b90](https://github.com/Ronnasayd/AI-pair-programming/commit/d2a3b90))

### **2026-05-19**

- **[✨ Features]** Remove command for protecting sensitive files from hooks ([a7387fc](https://github.com/Ronnasayd/AI-pair-programming/commit/a7387fc))
- **[📚 Documentation]** Refine documentation on context search directories for clarity and order ([dacb70e](https://github.com/Ronnasayd/AI-pair-programming/commit/dacb70e))
- **[✨ Features]** Update documentation skill version and refine documentation file references ([31d2e4f](https://github.com/Ronnasayd/AI-pair-programming/commit/31d2e4f))
- **[✨ Features]** Enhance documentation templates with new sections for models and endpoints ([d93ef63](https://github.com/Ronnasayd/AI-pair-programming/commit/d93ef63))
- **[✨ Features]** Update module context documentation template and enhance versioning ([7b61c67](https://github.com/Ronnasayd/AI-pair-programming/commit/7b61c67))
- **[✨ Features]** Add documentation templates for project structure and guidelines ([8bd4253](https://github.com/Ronnasayd/AI-pair-programming/commit/8bd4253))
- **[📚 Documentation]** Update code standards with comprehensive guidelines for naming conventions, function structure, and readability ([8907bce](https://github.com/Ronnasayd/AI-pair-programming/commit/8907bce))
- **[✨ Features]** Add new command to protect sensitive files and enhance code modification guidelines ([e234251](https://github.com/Ronnasayd/AI-pair-programming/commit/e234251))
- **[📚 Documentation]** Add typescript coding guidelines and best practices ([81af574](https://github.com/Ronnasayd/AI-pair-programming/commit/81af574))
- **[📚 Documentation]** Add comprehensive guidelines for code standards, http api standards, react standards, and testing practices ([f940fea](https://github.com/Ronnasayd/AI-pair-programming/commit/f940fea))
- **[♻️ Refactoring]** Rename technical-decision-maker to technical-decision-helper across documentation and skills ([f142703](https://github.com/Ronnasayd/AI-pair-programming/commit/f142703))
- **[🧹 Chores]** Add cleanignore alias to remove ignore files ([c41fe35](https://github.com/Ronnasayd/AI-pair-programming/commit/c41fe35))
- **[📚 Documentation]** Enhance interaction rules for using interactive question tools ([95d5651](https://github.com/Ronnasayd/AI-pair-programming/commit/95d5651))
- **[📚 Documentation]** Enhance interaction rules for technical decision-making process ([ad13010](https://github.com/Ronnasayd/AI-pair-programming/commit/ad13010))

### **2026-05-18**

- **[♻️ Refactoring]** Consolidate figma server entries in configuration files ([62534aa](https://github.com/Ronnasayd/AI-pair-programming/commit/62534aa))
- **[♻️ Refactoring]** Consolidate atlassian server entries in configuration files ([8f09553](https://github.com/Ronnasayd/AI-pair-programming/commit/8f09553))
- **[📚 Documentation]** Update wording for clarity in skills discovery documentation ([0507f91](https://github.com/Ronnasayd/AI-pair-programming/commit/0507f91))
- **[✨ Features]** Add skills-discovery skill with detailed description and update .skillsignore ([03af585](https://github.com/Ronnasayd/AI-pair-programming/commit/03af585))
- **[🧹 Chores]** Remove empty code change entries from the changes log ([480150d](https://github.com/Ronnasayd/AI-pair-programming/commit/480150d))
- **[✨ Features]** Add seo and subagent creator skills with comprehensive guidelines and best practices ([dabe565](https://github.com/Ronnasayd/AI-pair-programming/commit/dabe565))
- **[✨ Features]** Update .agentsignore and .skillsignore to include and reorganize agent and skill entries ([aa04014](https://github.com/Ronnasayd/AI-pair-programming/commit/aa04014))
- **[✨ Features]** Update .agentsignore to include file extensions for agent specifications ([7d11159](https://github.com/Ronnasayd/AI-pair-programming/commit/7d11159))
- **[✨ Features]** Reorganize .agentsignore and .skillsignore files, add new skills, and remove obsolete entries ([e7bb67d](https://github.com/Ronnasayd/AI-pair-programming/commit/e7bb67d))
- **[✨ Features]** Enable plan in settings and add agents overrides section ([56cd64c](https://github.com/Ronnasayd/AI-pair-programming/commit/56cd64c))
- **[✨ Features]** Update mcp server configurations to include new figma and github entries with distinct labels ([b3a0e73](https://github.com/Ronnasayd/AI-pair-programming/commit/b3a0e73))
- **[✨ Features]** Add metadata section to multiple skill.md files and remove prompt-optimizer skill ([7dd7308](https://github.com/Ronnasayd/AI-pair-programming/commit/7dd7308))
- **[✨ Features]** Add rendering and validation scripts for mermaid diagrams ([4a9f1b4](https://github.com/Ronnasayd/AI-pair-programming/commit/4a9f1b4))
- **[🚧 Other Changes]** Update .skillsignore to uncomment tlc-spec-driven entry ([bcc9beb](https://github.com/Ronnasayd/AI-pair-programming/commit/bcc9beb))
- **[✨ Features]** Add detailed methodologies for research and plan phases, including migration patterns and testing strategies ([1fba652](https://github.com/Ronnasayd/AI-pair-programming/commit/1fba652))
- **[✨ Features]** Enhance gghget script with sha1 comparison and improved error handling for github api calls ([293052b](https://github.com/Ronnasayd/AI-pair-programming/commit/293052b))
- **[✨ Features]** Add project initialization, quick mode, roadmap creation, session handoff, specification, state management, task breakdown, and validation processes ([653ca2a](https://github.com/Ronnasayd/AI-pair-programming/commit/653ca2a))

### **2026-05-17**

- **[✨ Features]** Add comprehensive documentation for database migrations, deployment patterns, docker best practices, and regex vs llm structured text parsing ([21c6153](https://github.com/Ronnasayd/AI-pair-programming/commit/21c6153))
- **[✨ Features]** Add comprehensive documentation for database migrations, deployment patterns, docker patterns, and regex vs llm structured text parsing ([a7710fb](https://github.com/Ronnasayd/AI-pair-programming/commit/a7710fb))
- **[✨ Features]** Add api design patterns and guidelines, including resource naming, status codes, pagination, filtering, error responses, versioning, and rate limiting for production apis; introduce agent harness construction and ai regression testing strategies ([2791f11](https://github.com/Ronnasayd/AI-pair-programming/commit/2791f11))
- **[✨ Features]** Add python mcp server implementation guide and evaluation scripts ([6687a2c](https://github.com/Ronnasayd/AI-pair-programming/commit/6687a2c))
- **[✨ Features]** Add skill evaluation and improvement scripts ([439b565](https://github.com/Ronnasayd/AI-pair-programming/commit/439b565))
- **[🧹 Chores]** Update vendoring instructions for skill.md to reflect correct file path ([fde3903](https://github.com/Ronnasayd/AI-pair-programming/commit/fde3903))
- **[✨ Features]** Add tdd and test coverage review skills for enhanced testing practices ([20886ff](https://github.com/Ronnasayd/AI-pair-programming/commit/20886ff))
- **[✨ Features]** Implement structured framework for resolving git merge conflicts ([0e998cd](https://github.com/Ronnasayd/AI-pair-programming/commit/0e998cd))
- **[✨ Features]** Rename deep-research skill to deep-research-web and update .skillsignore ([8a45878](https://github.com/Ronnasayd/AI-pair-programming/commit/8a45878))
- **[🧹 Chores]** Update .skillsignore to include git-guide for improved skill management ([2fbcffa](https://github.com/Ronnasayd/AI-pair-programming/commit/2fbcffa))
- **[✨ Features]** Add new taskmaster skills for task management and validation ([f4a79f8](https://github.com/Ronnasayd/AI-pair-programming/commit/f4a79f8))
- **[✨ Features]** Add figma-to-code agentic skill for automated design-to-development handoff ([4b4399e](https://github.com/Ronnasayd/AI-pair-programming/commit/4b4399e))
- **[✨ Features]** Add skill architecture references and validation scripts ([22e094f](https://github.com/Ronnasayd/AI-pair-programming/commit/22e094f))
- **[✨ Features]** Add skill-architect to .skillsignore for improved skill management ([fe9d277](https://github.com/Ronnasayd/AI-pair-programming/commit/fe9d277))
- **[✨ Features]** Add skill-architect to .skillsignore and update external tools script for skill management ([67f0ba5](https://github.com/Ronnasayd/AI-pair-programming/commit/67f0ba5))
- **[✨ Features]** Add skill architecture references and validation scripts ([65df366](https://github.com/Ronnasayd/AI-pair-programming/commit/65df366))

### **2026-05-16**

- **[✨ Features]** Add prd-from-codebase to .skillsignore for improved skill management ([034d127](https://github.com/Ronnasayd/AI-pair-programming/commit/034d127))
- **[✨ Features]** Add prd generation skill and stack hints reference for improved documentation ([702ea61](https://github.com/Ronnasayd/AI-pair-programming/commit/702ea61))
- **[♻️ Refactoring]** Update script paths in skill.md and handle-deleted-modified.sh for consistency ([f127316](https://github.com/Ronnasayd/AI-pair-programming/commit/f127316))
- **[♻️ Refactoring]** Uncomment specialists in .agentsignore for improved visibility ([bb2414f](https://github.com/Ronnasayd/AI-pair-programming/commit/bb2414f))
- **[♻️ Refactoring]** Update exit menu option from '0' to 'q' for consistency ([883e4df](https://github.com/Ronnasayd/AI-pair-programming/commit/883e4df))
- **[♻️ Refactoring]** Uncomment skills in .skillsignore for better visibility ([ebb5fe8](https://github.com/Ronnasayd/AI-pair-programming/commit/ebb5fe8))
- **[♻️ Refactoring]** Comment out echo statements for removed skills and agents in ignores.sh ([cce6f76](https://github.com/Ronnasayd/AI-pair-programming/commit/cce6f76))
- **[♻️ Refactoring]** Reorganize .skillsignore entries and update comments in manage-ignore-files.py for clarity ([7b01942](https://github.com/Ronnasayd/AI-pair-programming/commit/7b01942))
- **[♻️ Refactoring]** Update .skillsignore to toggle comments for better organization ([3bb6b3c](https://github.com/Ronnasayd/AI-pair-programming/commit/3bb6b3c))
- **[♻️ Refactoring]** Clarify comments and logic in ignore file processing ([17ded6a](https://github.com/Ronnasayd/AI-pair-programming/commit/17ded6a))
- **[✨ Features]** Update .skillsignore to enable specific skills and remove comments ([85f360f](https://github.com/Ronnasayd/AI-pair-programming/commit/85f360f))
- **[✨ Features]** Add alias for managing ignore files in .ai.alias.zshrc ([331bb65](https://github.com/Ronnasayd/AI-pair-programming/commit/331bb65))
- **[✨ Features]** Add symlink for manage-ignore-files script in install.sh and update workspace root resolution in manage-ignore-files.py ([d34f4bb](https://github.com/Ronnasayd/AI-pair-programming/commit/d34f4bb))
- **[✨ Features]** Add interactive script for managing .skillsignore and .agentsignore files ([b86fe0e](https://github.com/Ronnasayd/AI-pair-programming/commit/b86fe0e))

### **2026-05-13**

- **[✨ Features]** Add skill-advisor documentation and update .skillsignore ([37bcd07](https://github.com/Ronnasayd/AI-pair-programming/commit/37bcd07))
- **[🧹 Chores]** Remove evals.json files for document summarizer, requirements screen mapper, figma to code agentic, and tailwind config conformance skills ([38b03a3](https://github.com/Ronnasayd/AI-pair-programming/commit/38b03a3))
- **[✨ Features]** Add event-storming skill documentation and ignore file entry ([b4a3520](https://github.com/Ronnasayd/AI-pair-programming/commit/b4a3520))
- **[✨ Features]** Enhance install script with argument parsing and help display ([2b62492](https://github.com/Ronnasayd/AI-pair-programming/commit/2b62492))
- **[♻️ Refactoring]** Improve cleanai alias for better readability and maintainability ([dda1f8c](https://github.com/Ronnasayd/AI-pair-programming/commit/dda1f8c))
- **[✨ Features]** Enable claude installation script in the setup process ([da88546](https://github.com/Ronnasayd/AI-pair-programming/commit/da88546))

### **2026-05-12**

- **[✨ Features]** Enhance figma requirements conformance skill with detailed design context and reporting structure ([72c2856](https://github.com/Ronnasayd/AI-pair-programming/commit/72c2856))
- **[🧹 Chores]** Update changelog for version 2026.05.12 with recent features and fixes ([186d83f](https://github.com/Ronnasayd/AI-pair-programming/commit/186d83f))
- **[✨ Features]** Add figma requirements screen mapper skill and evaluation prompts ([2615c71](https://github.com/Ronnasayd/AI-pair-programming/commit/2615c71))
- **[✨ Features]** Add figma requirements conformance skill and evaluation prompts ([6fe3725](https://github.com/Ronnasayd/AI-pair-programming/commit/6fe3725))
- **[✨ Features]** Add dynamic programming analysis skill for structured problem-solving ([c0783ca](https://github.com/Ronnasayd/AI-pair-programming/commit/c0783ca))

### **2026-05-08**

- **[✨ Features]** Add cleanai alias for removing all ai contexts and configurations ([e6f6b1b](https://github.com/Ronnasayd/AI-pair-programming/commit/e6f6b1b))
- **[✨ Features]** Update initai alias to use absolute path and add symlink creation in install script ([3f5d5f0](https://github.com/Ronnasayd/AI-pair-programming/commit/3f5d5f0))
- **[✨ Features]** Update session file naming to include time for better uniqueness ([5d6c9ec](https://github.com/Ronnasayd/AI-pair-programming/commit/5d6c9ec))
- **[🐛 Bug Fixes]** Update .skillsignore to include apk in ignored skills ([1e49218](https://github.com/Ronnasayd/AI-pair-programming/commit/1e49218))
- **[✨ Features]** Add apk reverse engineering skill and analysis script with detailed reporting ([e5ac46a](https://github.com/Ronnasayd/AI-pair-programming/commit/e5ac46a))

### **2026-05-07**

- **[🐛 Bug Fixes]** Correct markdown syntax in documentation for clarity and consistency ([c0fb529](https://github.com/Ronnasayd/AI-pair-programming/commit/c0fb529))

### **2026-05-05**

- **[✨ Features]** Add integration-testing to .skillsignore ([93199a5](https://github.com/Ronnasayd/AI-pair-programming/commit/93199a5))
- **[✨ Features]** Add integration testing skill with comprehensive guidance and approaches ([f2d32a9](https://github.com/Ronnasayd/AI-pair-programming/commit/f2d32a9))
- **[✨ Features]** Add initai alias for executing ai-generated context commands ([937e3c3](https://github.com/Ronnasayd/AI-pair-programming/commit/937e3c3))
- **[✨ Features]** Update alias to reloadignore for removing .skillsignore and .agentsignore files ([f2586e9](https://github.com/Ronnasayd/AI-pair-programming/commit/f2586e9))
- **[✨ Features]** Add alias for removing .skillsignore and .agentsignore files ([332cade](https://github.com/Ronnasayd/AI-pair-programming/commit/332cade))
- **[✨ Features]** Add mermaid class diagram and erd skills for visualizing relationships ([2498fcf](https://github.com/Ronnasayd/AI-pair-programming/commit/2498fcf))

### **2026-05-04**

- **[🧹 Chores]** Update model version in linter_solver to claude-haiku-4.5 ([ff9cf74](https://github.com/Ronnasayd/AI-pair-programming/commit/ff9cf74))

### **2026-05-03**

- **[✨ Features]** Add opencv skill for image and video processing reference ([af6afe4](https://github.com/Ronnasayd/AI-pair-programming/commit/af6afe4))

### **2026-04-29**

- **[✨ Features]** Add leet-code patterns skill for coding interview preparation ([695321a](https://github.com/Ronnasayd/AI-pair-programming/commit/695321a))

### **2026-04-28**

- **[🚧 Other Changes]** Enhance output formatting with color for linter messages ([f70b81f](https://github.com/Ronnasayd/AI-pair-programming/commit/f70b81f))
- **[🐛 Bug Fixes]** Improve directory and file handling in main function of linter_solver ([cbfa156](https://github.com/Ronnasayd/AI-pair-programming/commit/cbfa156))
- **[🐛 Bug Fixes]** Add linter command output logging in run_linter function ([273c09b](https://github.com/Ronnasayd/AI-pair-programming/commit/273c09b))
- **[🐛 Bug Fixes]** Enhance linter error fixing process by including command verification in fix_linter_errors ([311c83e](https://github.com/Ronnasayd/AI-pair-programming/commit/311c83e))
- **[🐛 Bug Fixes]** Simplify linter error fix prompt and remove unnecessary file write ([d79f7dd](https://github.com/Ronnasayd/AI-pair-programming/commit/d79f7dd))
- **[✨ Features]** Enhance context bar display and improve event handling in linter session ([9a176e3](https://github.com/Ronnasayd/AI-pair-programming/commit/9a176e3))
- **[🐛 Bug Fixes]** Correct event subscription handling in fix_linter_errors function ([d8ea94f](https://github.com/Ronnasayd/AI-pair-programming/commit/d8ea94f))
- **[🚧 Other Changes]** Fix formatting and variable assignment in linter_solver.py fix: update key names in config.json for consistency ([d59e9e1](https://github.com/Ronnasayd/AI-pair-programming/commit/d59e9e1))
- **[✨ Features]** Add linter auto-fix script using github copilot python sdk ([9dd2678](https://github.com/Ronnasayd/AI-pair-programming/commit/9dd2678))
- **[✨ Features]** Add copilot-sdk to .skillsignore for improved skill management ([7140f9c](https://github.com/Ronnasayd/AI-pair-programming/commit/7140f9c))
- **[✨ Features]** Add copilot-sdk skill documentation for python applications using github copilot ([54efa95](https://github.com/Ronnasayd/AI-pair-programming/commit/54efa95))
- **[✨ Features]** Add python sdk skill documentation for github copilot integration and update .skillsignore ([8b3d86e](https://github.com/Ronnasayd/AI-pair-programming/commit/8b3d86e))

### **2026-04-20**

- **[🐛 Bug Fixes]** Update tool reference for fetching task definition in execute-task skill ([4e3f305](https://github.com/Ronnasayd/AI-pair-programming/commit/4e3f305))
- **[✨ Features]** Add taskmaster-mapper skill to enrich tasks with suggested skills and agents ([efdb8ca](https://github.com/Ronnasayd/AI-pair-programming/commit/efdb8ca))

### **2026-04-17**

- **[✨ Features]** Update config.json keys for consistency and add github-copilot-sdk to requirements ([43f37e6](https://github.com/Ronnasayd/AI-pair-programming/commit/43f37e6))
- **[✨ Features]** Add config.json for github copilot configuration and update installation script ([5bc46a8](https://github.com/Ronnasayd/AI-pair-programming/commit/5bc46a8))
- **[🧹 Chores]** Remove input prompts and update environment variable references in mcp-config.json ([b1df2e3](https://github.com/Ronnasayd/AI-pair-programming/commit/b1df2e3))
- **[✨ Features]** Add mcp-config.json for github copilot configuration ([4c58fdd](https://github.com/Ronnasayd/AI-pair-programming/commit/4c58fdd))
- **[✨ Features]** Enhance taskmaster-prd-generator skill description and usage scenarios ([22aa094](https://github.com/Ronnasayd/AI-pair-programming/commit/22aa094))
- **[✨ Features]** Add srs-generator skill for generating software requirements specification documents ([72a5d5e](https://github.com/Ronnasayd/AI-pair-programming/commit/72a5d5e))
- **[🧹 Chores]** Update date format in documentation and skills to yyyy-mm-dd ([96845c1](https://github.com/Ronnasayd/AI-pair-programming/commit/96845c1))

### **2026-04-16**

- **[✨ Features]** Add design-image-diff skill for comparing design and implementation visuals ([04c2220](https://github.com/Ronnasayd/AI-pair-programming/commit/04c2220))

### **2026-04-14**

- **[🧹 Chores]** Remove unused burp server configuration from vscode.mcp.json ([f0617ce](https://github.com/Ronnasayd/AI-pair-programming/commit/f0617ce))
- **[🧹 Chores]** Add keycloack to skillsignore for improved skill management ([2082dfd](https://github.com/Ronnasayd/AI-pair-programming/commit/2082dfd))
- **[✨ Features]** Add keycloak documentation index skill for structured navigation and reference ([ca5ab30](https://github.com/Ronnasayd/AI-pair-programming/commit/ca5ab30))

### **2026-04-10**

- **[🧹 Chores]** Add safe-refactor skill for structured code refactoring guidance ([bd295ca](https://github.com/Ronnasayd/AI-pair-programming/commit/bd295ca))
- **[♻️ Refactoring]** Update command execution for mcp-manager and database types to use uvx ([1f2a4a1](https://github.com/Ronnasayd/AI-pair-programming/commit/1f2a4a1))
- **[♻️ Refactoring]** Update command execution for postgresql, mysql, and sqlite to use uvx ([2e229a2](https://github.com/Ronnasayd/AI-pair-programming/commit/2e229a2))
- **[🧹 Chores]** Update project structure and remove unused code ([36bc23d](https://github.com/Ronnasayd/AI-pair-programming/commit/36bc23d))
- **[🧹 Chores]** Remove psycopg2 dependency from pyproject.toml ([dc467e8](https://github.com/Ronnasayd/AI-pair-programming/commit/dc467e8))
- **[🧹 Chores]** Add mysql-connector-python and psycopg2 dependencies in pyproject.toml ([152ce6b](https://github.com/Ronnasayd/AI-pair-programming/commit/152ce6b))
- **[✨ Features]** Update mongodb command and refactor main execution in mcp scripts ([89bcfaf](https://github.com/Ronnasayd/AI-pair-programming/commit/89bcfaf))
- **[♻️ Refactoring]** Encapsulate main execution logic in a separate function ([8cd0d09](https://github.com/Ronnasayd/AI-pair-programming/commit/8cd0d09))
- **[🧹 Chores]** Uncomment dependencies in pyproject.toml for clarity and consistency ([7d6d2cb](https://github.com/Ronnasayd/AI-pair-programming/commit/7d6d2cb))
- **[🐛 Bug Fixes]** Remove unnecessary 'from' attribute in package configuration for clarity ([046d63a](https://github.com/Ronnasayd/AI-pair-programming/commit/046d63a))
- **[🧹 Chores]** Comment out dependencies in pyproject.toml for clarity and consistency ([27c6faf](https://github.com/Ronnasayd/AI-pair-programming/commit/27c6faf))
- **[🧹 Chores]** Uncomment dependencies in pyproject.toml for clarity and consistency ([ebadf50](https://github.com/Ronnasayd/AI-pair-programming/commit/ebadf50))
- **[🧹 Chores]** Comment out unused dependencies in pyproject.toml for clarity ([9101038](https://github.com/Ronnasayd/AI-pair-programming/commit/9101038))
- **[✨ Features]** Update package configuration in pyproject.toml for correct module inclusion ([1ba8e0a](https://github.com/Ronnasayd/AI-pair-programming/commit/1ba8e0a))
- **[✨ Features]** Update mcp-manager command to use uvx and add git source configuration ([21b50ca](https://github.com/Ronnasayd/AI-pair-programming/commit/21b50ca))
- **[✨ Features]** Replace protect_files.py with strategic compact suggester for improved tool usage management ([62b1367](https://github.com/Ronnasayd/AI-pair-programming/commit/62b1367))
- **[✨ Features]** Add session cleanup functionality to main process for better resource management ([6d71d38](https://github.com/Ronnasayd/AI-pair-programming/commit/6d71d38))
- **[✨ Features]** Enhance protect_files.py with improved pattern matching and project boundary checks ([1152790](https://github.com/Ronnasayd/AI-pair-programming/commit/1152790))

### **2026-04-09**

- **[✨ Features]** Add new html files for agent and skill mapping documentation ([9f84044](https://github.com/Ronnasayd/AI-pair-programming/commit/9f84044))
- **[✨ Features]** Add script to list agent and skill names and descriptions from markdown files ([035121d](https://github.com/Ronnasayd/AI-pair-programming/commit/035121d))
- **[🧹 Chores]** Add task verification guidelines to agent instructions for improved task management ([563eff8](https://github.com/Ronnasayd/AI-pair-programming/commit/563eff8))
- **[🧹 Chores]** Comment out unused skills in .skillsignore for better organization ([d9a3bf6](https://github.com/Ronnasayd/AI-pair-programming/commit/d9a3bf6))
- **[🧹 Chores]** Reorganize and enhance .agentsignore and .skillsignore for improved structure and clarity ([78e10ca](https://github.com/Ronnasayd/AI-pair-programming/commit/78e10ca))
- **[🧹 Chores]** Reorganize .skillsignore for better structure and clarity ([c9bfa13](https://github.com/Ronnasayd/AI-pair-programming/commit/c9bfa13))
- **[🧹 Chores]** Update .skillsignore to include taskmaster, tdd, generate-docs, and resolve-conflicts ([2cc0172](https://github.com/Ronnasayd/AI-pair-programming/commit/2cc0172))
- **[📚 Documentation]** Enhance skill.md by clarifying question types and improving structure for prd generation ([233794a](https://github.com/Ronnasayd/AI-pair-programming/commit/233794a))
- **[📚 Documentation]** Update default num_tasks from 5 to 10 in skill.md ([f2fe083](https://github.com/Ronnasayd/AI-pair-programming/commit/f2fe083))
- **[🧹 Chores]** Update .gitignore and .skillsignore, remove deprecated taskmaster scripts, and enhance skill.md documentation ([0304d94](https://github.com/Ronnasayd/AI-pair-programming/commit/0304d94))

### **2026-04-08**

- **[🐛 Bug Fixes]** Ensure .agentsignore and .skillsignore are added to .gitignore if not present ([03f75ca](https://github.com/Ronnasayd/AI-pair-programming/commit/03f75ca))

### **2026-04-07**

- **[🐛 Bug Fixes]** Lower ssim threshold from 0.95 to 0.9 across documentation and scripts ([f49e713](https://github.com/Ronnasayd/AI-pair-programming/commit/f49e713))
- **[🐛 Bug Fixes]** Ensure correct data types for ssim_score and is_match in comparisonresult ([8a4132d](https://github.com/Ronnasayd/AI-pair-programming/commit/8a4132d))
- **[🚧 Other Changes]** Format code for improved readability and consistency ([f378b12](https://github.com/Ronnasayd/AI-pair-programming/commit/f378b12))
- **[✨ Features]** Enhance agentic loop with session management and logging capabilities ([1178eec](https://github.com/Ronnasayd/AI-pair-programming/commit/1178eec))
- **[🐛 Bug Fixes]** Ensure .skillsignore is copied only if it doesn't exist ([7ce907e](https://github.com/Ronnasayd/AI-pair-programming/commit/7ce907e))
- **[🐛 Bug Fixes]** Ensure .agentsignore is copied only if it doesn't exist ([77e3a21](https://github.com/Ronnasayd/AI-pair-programming/commit/77e3a21))
- **[✨ Features]** Add figma-to-code-agentic skill with quick start guide, readme, and evaluation scripts ([d0722bd](https://github.com/Ronnasayd/AI-pair-programming/commit/d0722bd))

### **2026-04-02**

- **[🐛 Bug Fixes]** Update log size limit to prevent log flooding ([266259e](https://github.com/Ronnasayd/AI-pair-programming/commit/266259e))

### **2026-04-01**

- **[✨ Features]** Add conflict resolution skills and supporting scripts for handling merge conflicts ([f643da2](https://github.com/Ronnasayd/AI-pair-programming/commit/f643da2))
- **[🐛 Bug Fixes]** Increase log size limit to prevent log flooding ([cfac938](https://github.com/Ronnasayd/AI-pair-programming/commit/cfac938))
- **[🐛 Bug Fixes]** Increase log size limit and update regex for attachment parsing ([56aca66](https://github.com/Ronnasayd/AI-pair-programming/commit/56aca66))
- **[🐛 Bug Fixes]** Limit logged request and response body sizes to improve performance and prevent excessive logging ([92d6cbf](https://github.com/Ronnasayd/AI-pair-programming/commit/92d6cbf))
- **[🧹 Chores]** Remove commented-out rtk instructions from claude.install.sh ([6cb21dd](https://github.com/Ronnasayd/AI-pair-programming/commit/6cb21dd))
- **[🧹 Chores]** Comment out rtk instructions generation in claude.install.sh ([ac867b3](https://github.com/Ronnasayd/AI-pair-programming/commit/ac867b3))
- **[✨ Features]** Update .gitignore and installation script to include commands directory and streamline hooks configuration ([8832596](https://github.com/Ronnasayd/AI-pair-programming/commit/8832596))
- **[🐛 Bug Fixes]** Update instruction paths in claude.install.sh to correct directory references ([3c48a48](https://github.com/Ronnasayd/AI-pair-programming/commit/3c48a48))
- **[✨ Features]** Add settings.local.json for configuration and update installation script to link it ([4cb165b](https://github.com/Ronnasayd/AI-pair-programming/commit/4cb165b))
- **[✨ Features]** Update .gitignore to include claude.md and enhance installation scripts for claude ([e7ffca7](https://github.com/Ronnasayd/AI-pair-programming/commit/e7ffca7))
- **[✨ Features]** Add .mcp.json to .gitignore and update installation scripts for claude ([83022fd](https://github.com/Ronnasayd/AI-pair-programming/commit/83022fd))
- **[✨ Features]** Add claude installation script and update .gitignore for new directories ([6b13827](https://github.com/Ronnasayd/AI-pair-programming/commit/6b13827))
- **[✨ Features]** Improve code formatting and add anthropic-compatible messages endpoint ([ac6d8be](https://github.com/Ronnasayd/AI-pair-programming/commit/ac6d8be))

### **2026-03-31**

- **[✨ Features]** Enhance model response structure to include tools capability in json output ([4984166](https://github.com/Ronnasayd/AI-pair-programming/commit/4984166))

### **2026-03-30**

- **[📚 Documentation]** Update descriptions in skill.md files for clarity and precision ([eef5f17](https://github.com/Ronnasayd/AI-pair-programming/commit/eef5f17))
- **[🚧 Other Changes]** Update echo statements in ignores.sh to include folder context for removed skills and agents ([93fc623](https://github.com/Ronnasayd/AI-pair-programming/commit/93fc623))
- **[🧹 Chores]** Update changelog for version 2026.03.30 with recent changes and enhancements ([ffe6197](https://github.com/Ronnasayd/AI-pair-programming/commit/ffe6197))
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

Generated on 2026-09-16 01:45:51
