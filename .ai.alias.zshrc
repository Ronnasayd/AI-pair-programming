alias clign="rm -f .skillsignore .agentsignore .rulesignore 2>/dev/null && echo 'Cleaned ignore files'" # Clean ignore files: cleanignore
alias aims="docker run -d --name ai-memory \
    --restart unless-stopped \
    -p 127.0.0.1:49374:49374 \
    -v ai-memory-data:/data \
    akitaonrails/ai-memory:latest" # Start AI Memory container: ai-memory-start
alias aimsllm='docker run -d --name ai-memory \
    --restart unless-stopped \
    -p 127.0.0.1:49374:49374 \
    -v ai-memory-data:/data \
    -e AI_MEMORY_LLM_MODEL=claude-haiku-4-5 \
    -e AI_MEMORY_LLM_PROVIDER=anthropic-oauth \
    -e AI_MEMORY_AUTH_TOKEN=$(grep AI_MEMORY_AUTH_TOKEN ~/.secrets/claude.env | cut -d= -f2) \
    -e CLAUDE_CODE_OAUTH_TOKEN=$(grep CLAUDE_CODE_OAUTH_TOKEN ~/.secrets/claude.env | cut -d= -f2) \
    akitaonrails/ai-memory:latest' # Start AI Memory container using LLM-backed mode: ai-memory-start-llm
alias aimh='ai-memory install-mcp   --client claude-code --apply --server-url "http://127.0.0.1:49374/mcp"  && ai-memory install-hooks --agent  claude-code --apply --server-url "http://127.0.0.1:49374"' # Install AI Memory MCP + hooks into Claude Code: ai-memory-hooks
alias aimhllm='ai-memory install-mcp   --client claude-code --apply --server-url "http://127.0.0.1:49374/mcp" --auth-token "$(grep AI_MEMORY_AUTH_TOKEN ~/.secrets/claude.env | cut -d= -f2)" && ai-memory install-hooks --agent  claude-code --apply --server-url "http://127.0.0.1:49374" --auth-token "$(grep AI_MEMORY_AUTH_TOKEN ~/.secrets/claude.env | cut -d= -f2)"' # Install AI Memory MCP + hooks with auth token (LLM-backed mode): ai-memory-hooks-llm
alias aimw="if command -v xdg-open &>/dev/null; then xdg-open http://localhost:49374/web; else open http://localhost:49374/web; fi" # Open AI Memory web: ai-memory-web
alias claude-yolo="claude --dangerously-skip-permissions" # Claude with no permission prompts: yolo
alias ats="grep '#' .skillsignore 2>/dev/null | sed 's/#/✅/g' || echo '.skillsignore not found'" # Show skills: show-skills
alias atr="grep '#' .rulesignore 2>/dev/null | sed 's/#/✅/g' || echo '.rulesignore not found'" # Show rules: show-rules
alias ata="grep '#' .agentsignore 2>/dev/null | sed 's/#/✅/g' || echo '.agentsignore not found'" # Show agents: show-agents
alias clc="claude --model haiku -p 'Thoroughly analyze the changes and create a clear and concise commit message in conventional commit format. Don't start the commit message with any words other than: feat, fix, docs, style, refactor, perf, test, or chore. Don't include any emojis. Ensure the message accurately reflects the changes made.'" # Commit message generator: commit-create
alias lgh="touch $HOME/.claude/logs/hooks.log && tail -f $HOME/.claude/logs/hooks.log | bat --paging=never -l log" # Live git hooks log: live-git-hooks
alias lghe="touch $HOME/.claude/logs/external.log && tail -f $HOME/.claude/logs/external.log | bat --paging=never -l log" # Live git hooks log: live-git-hooks
alias cat-pylint='cat $HOME/.claude/logs/hooks.log | grep -e "\[PythonLint\]" | bat --paging=never -l log' # Show PythonLint hook log lines: cat-pylint
alias cat-tslint='cat $HOME/.claude/logs/hooks.log | grep -e "\[TypeScriptLint\]" | bat --paging=never -l log' # Show TypeScriptLint hook log lines: cat-tslint
alias cat-golint='cat $HOME/.claude/logs/hooks.log | grep -e "\[GolangLint\]" | bat --paging=never -l log' # Show GolangLint hook log lines: cat-golint
alias cat-ctxrefs='cat $HOME/.claude/logs/hooks.log | grep -e "\[ContextRefs\]" | bat --paging=never -l log' # Show ContextRefs hook log lines: cat-ctxrefs
alias cat-prtfiles='cat $HOME/.claude/logs/hooks.log | grep -e "\[ProtectFiles\]" | bat --paging=never -l log' # Show ProtectFiles hook log lines: cat-prtfiles
alias cat-scr='cat $HOME/.claude/logs/hooks.log | grep -e "\[SimilarCodeRef\]" | bat --paging=never -l log' # Show SimilarCodeRef hook log lines: cat-scr
alias cat-sa='cat $HOME/.claude/logs/hooks.log | grep -e "\[SkillActivation\]" | bat --paging=never -l log' # Show SkillActivation hook log lines: cat-sa
alias cat-cw='cat $HOME/.claude/logs/hooks.log | grep -e "\[ChecklistContextWatch\]" | bat --paging=never -l log' # Show ChecklistContextWatch hook log lines: cat-cw
alias cat-ac='cat $HOME/.claude/logs/hooks.log | grep -e "\[additionalContext\]" | bat --paging=never -l log' # Show additionalContext hook log lines: cat-ac
alias mia="mif && iai --claude" # Run mif then launch iai with Claude backend: mif-iai-claude
alias lintfix='uv run --with claude-agent-sdk $AI_PROJECT_ROOT_DIR/src/sdk/lint_fix_agent.py' # Run AI lint-fix agent script: lint-fix
alias codeburn="npx codeburn" # Run codeburn CLI via npx: codeburn
alias tksgi="echo '.tokensave/*' >> .git/info/exclude" # Ignore tokensave artifacts locally: tokensave-gitignore
alias slt="bash $AI_PROJECT_ROOT_DIR/docker/litellm/start-litellm.sh" # Start local LiteLLM proxy: start-litellm
alias 9cl="ANTHROPIC_MODEL=9router-low claude" # Run Claude via 9router low-cost model tier: 9router-claude-low
alias 9ch="ANTHROPIC_MODEL=9router-high claude" # Run Claude via 9router high-cost model tier: 9router-claude-high
alias dms="$AI_PROJECT_ROOT_DIR/scripts/disable-mcps-default.py" # Disable default MCP servers: disable-mcps
alias dmsl="$AI_PROJECT_ROOT_DIR/scripts/disable-mcps-default.py $HOME/.claude-L/.claude.json" # Disable default MCP servers: disable-mcps
alias rri="rag-rat init --yes && rag-rat hooks install" # Init rag-rat and install its hooks: rag-rat-init
alias sri="serena init" # Init serena in current project: serena-init
alias cfie="code .git/info/exclude" # Open git local exclude file in editor: code-info-exclude
alias osd="xdg-open http://localhost:24282/dashboard/" # Open opencode-supervisor dashboard: opencode-supervisor-dashboard
alias afa="npx agent-flow-app" # Run agent-flow-app via npx: agent-flow-app
alias aij="bash $AI_PROJECT_ROOT_DIR/scripts/ai-jail.sh" # Run ai-jail sandbox script: ai-jail
alias ca="bash $AI_PROJECT_ROOT_DIR/scripts/claude.accounts.sh"
alias cacs="bash $AI_PROJECT_ROOT_DIR/scripts/claude.accounts.sh choose"
alias lca="bash $AI_PROJECT_ROOT_DIR/scripts/ai-jail.sh claude" # Run ai-jail sandbox script with claude
alias omniroute="ASDF_NODEJS_VERSION=24.16.0 omniroute"
export AI_PROJECT_ROOT_DIR="/home/ronnas/develop/personal/AI-pair-programming"

