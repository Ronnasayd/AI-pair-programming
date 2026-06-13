alias cleanignore="rm .skillsignore && rm .agentsignore && rm .rulesignore" # Clean up all ignore files in the current directory: cleanignore
alias initai="/usr/local/bin/init-ai" # Execute a command with an AI-generated context based on the current directory's files: initai
alias mif="manage-ignore-files" # Manage .skillsignore and .agentsignore files based on the current directory's contents: manage-ignore
alias copilot-claude="npx copilot-api@latest start --claude-code" # Start a Copilot session with Claude code generation capabilities: copilot-claude
alias ai-memory-server="docker run -d --name ai-memory \
    --restart unless-stopped \
    -p 127.0.0.1:49374:49374 \
    -v ai-memory-data:/data \
    akitaonrails/ai-memory:latest"
