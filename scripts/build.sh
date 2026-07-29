if [ -f ~/.bashrc ] && ! grep -q "export PATH=$HOME/.local/bin:$PATH" ~/.bashrc; then
  echo "export PATH=$HOME/.local/bin:$PATH" >> ~/.bashrc
fi
if [ -f ~/.zshrc ] && ! grep -q "export PATH=$HOME/.local/bin:$PATH" ~/.zshrc; then
  echo "export PATH=$HOME/.local/bin:$PATH" >> ~/.zshrc
fi
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
mkdir -p ~/.local/bin
curl -fsSL https://raw.githubusercontent.com/akitaonrails/ai-memory/main/bin/ai-memory \
    -o ~/.local/bin/ai-memory
chmod +x ~/.local/bin/ai-memory
echo "ai-memory installation ok"


# Install rtk
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh  && echo "rtk installation ok"
rtk init -g
