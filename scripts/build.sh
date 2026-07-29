# Install uv/uvx
curl -LsSf https://astral.sh/uv/install.sh | sh && echo "uv installation ok"

# Install headroom
uv tool install "headroom-ai[all]" && echo "headroom installation ok"

# Install rag-rat
sudo apt install cargo  && echo "cargo installation ok"
cargo install rag-rat && echo "rag-rat installation ok"

# Install serena
uv tool install  serena-agent && echo "serena installation ok"
serena init

# Install ai-memory
curl -fsSL https://raw.githubusercontent.com/akitaonrails/ai-memory/main/bin/ai-memory \
    -o /usr/local/bin/ai-memory
chmod +x /usr/local/bin/ai-memory
ai-memory install-mcp   --client claude-code --apply
ai-memory install-hooks --agent  claude-code --apply
echo "ai-memory installation ok"


# Install rtk
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh  && echo "rtk installation ok"
rtk init -g
