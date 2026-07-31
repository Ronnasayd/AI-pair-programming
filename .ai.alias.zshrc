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
    akitaonrails/ai-memory:latest' # Start AI Memory container: ai-memory-start
alias aimh='ai-memory install-mcp   --client claude-code --apply --server-url "http://127.0.0.1:49374/mcp"  && ai-memory install-hooks --agent  claude-code --apply --server-url "http://127.0.0.1:49374"'
alias aimhllm='ai-memory install-mcp   --client claude-code --apply --server-url "http://127.0.0.1:49374/mcp" --auth-token "$(grep AI_MEMORY_AUTH_TOKEN ~/.secrets/claude.env | cut -d= -f2)" && ai-memory install-hooks --agent  claude-code --apply --server-url "http://127.0.0.1:49374" --auth-token "$(grep AI_MEMORY_AUTH_TOKEN ~/.secrets/claude.env | cut -d= -f2)"'
alias aimw="if command -v xdg-open &>/dev/null; then xdg-open http://localhost:49374/web; else open http://localhost:49374/web; fi" # Open AI Memory web: ai-memory-web
alias claude-yolo="claude --dangerously-skip-permissions" # Claude with no permission prompts: yolo
alias ats="grep '#' .skillsignore 2>/dev/null | sed 's/#/✅/g' || echo '.skillsignore not found'" # Show skills: show-skills
alias atr="grep '#' .rulesignore 2>/dev/null | sed 's/#/✅/g' || echo '.rulesignore not found'" # Show rules: show-rules
alias ata="grep '#' .agentsignore 2>/dev/null | sed 's/#/✅/g' || echo '.agentsignore not found'" # Show agents: show-agents
alias clc="claude --model haiku -p 'Thoroughly analyze the changes and create a clear and concise commit message in conventional commit format. Don't start the commit message with any words other than: feat, fix, docs, style, refactor, perf, test, or chore. Don't include any emojis. Ensure the message accurately reflects the changes made.'" # Commit message generator: commit-create
alias lgh="touch /tmp/hooks.log && tail -f /tmp/hooks.log | bat --paging=never -l log" # Live git hooks log: live-git-hooks
alias cat-pylint='cat /tmp/hooks.log | grep -e "\[PythonLint\]" | bat --paging=never -l log'
alias cat-tslint='cat /tmp/hooks.log | grep -e "\[TypeScriptLint\]" | bat --paging=never -l log'
alias cat-golint='cat /tmp/hooks.log | grep -e "\[GolangLint\]" | bat --paging=never -l log'
alias cat-ctxrefs='cat /tmp/hooks.log | grep -e "\[ContextRefs\]" | bat --paging=never -l log'
alias cat-prtfiles='cat /tmp/hooks.log | grep -e "\[ProtectFiles\]" | bat --paging=never -l log'
alias cat-scr='cat /tmp/hooks.log | grep -e "\[SimilarCodeRef\]" | bat --paging=never -l log'
alias cat-sa='cat /tmp/hooks.log | grep -e "\[SkillActivation\]" | bat --paging=never -l log'
alias mia="mif && iai --claude"
alias lintfix='uv run --with claude-agent-sdk $AI_PROJECT_ROOT_DIR/src/sdk/lint_fix_agent.py'
alias codeburn="npx codeburn"
alias hwc="ANTHROPIC_MODEL=claude-sonnet-5 ENABLE_TOOL_SEARCH=false headroom wrap claude --1m && killall headroom"
alias tksgi="echo '.tokensave/*' >> .git/info/exclude && echo '.headroom*' >> .git/info/exclude"
alias slt="bash $AI_PROJECT_ROOT_DIR/docker/litellm/start-litellm.sh"
alias slth="bash $AI_PROJECT_ROOT_DIR/docker/litellm/start-litellm-headroom.sh && killall headroom"
alias 9cl="ANTHROPIC_MODEL=9router-low claude"
alias 9ch="ANTHROPIC_MODEL=9router-high claude"
alias dms="$AI_PROJECT_ROOT_DIR/scripts/disable-mcps-default.py"
alias rri="rag-rat init --yes && rag-rat hooks install"
alias icl="export CLAUDE_CONFIG_DIR=~/.claude-L && ln -s $AI_PROJECT_ROOT_DIR/claude/settings.json ~/.claude-L/settings.json"
alias dmsl="$AI_PROJECT_ROOT_DIR/scripts/disable-mcps-default.py ~/.claude-L/.claude.json"
alias sri="serena init"
alias cfie="code .git/info/exclude"
export AI_PROJECT_ROOT_DIR="/home/ronnas/develop/personal/AI-pair-programming"
