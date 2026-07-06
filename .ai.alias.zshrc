alias clign="rm -f .skillsignore .agentsignore .rulesignore 2>/dev/null && echo 'Cleaned ignore files'" # Clean ignore files: cleanignore
alias iai="/usr/local/bin/init-ai" # AI context generator: initai
alias mif="manage-ignore-files" # Manage ignore files: manage-ignore
alias aims="docker run -d --name ai-memory \
    --restart unless-stopped \
    -p 127.0.0.1:49374:49374 \
    -v ai-memory-data:/data \
    akitaonrails/ai-memory:latest" # Start AI Memory container: ai-memory-start
alias aimsllm="docker run -d --name ai-memory \
    --restart unless-stopped \
    -p 127.0.0.1:49374:49374 \
    -v ai-memory-data:/data \
    -e AI_MEMORY_LLM_MODEL=claude-haiku-4-5 \
    -e AI_MEMORY_LLM_PROVIDER=anthropic-oauth \
    -e AI_MEMORY_AUTH_TOKEN=$AI_MEMORY_AUTH_TOKEN \
    -e CLAUDE_CODE_OAUTH_TOKEN=$CLAUDE_CODE_OAUTH_TOKEN \
    akitaonrails/ai-memory:latest" # Start AI Memory container: ai-memory-start
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


