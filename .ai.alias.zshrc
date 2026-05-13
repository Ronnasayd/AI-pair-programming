alias reloadignore="rm .skillsignore && rm .agentsignore && initai"
alias initai="/usr/local/bin/init-ai" # Execute a command with an AI-generated context based on the current directory's files: initai
alias cleanai="rm -rf .gemini \
&& rm -rf .sessions \
&& rm -rf .copilot \
&& rm -rf .claude \
&& rm -rf .codex \
&& rm -rf .taskmaster \
&& rm -rf .github/agents \
&& rm -rf .github/hooks \
&& rm -rf .github/instructions \
&& rm -rf .github/prompts \
&& rm -rf .github/skills" # Clean up all AI contexts and configurations: cleanai
alias copilot-claude="npx copilot-api@latest start --claude-code" # Start a Copilot session with Claude code generation capabilities: copilot-claude
