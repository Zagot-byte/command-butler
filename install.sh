```bash
#!/usr/bin/env bash
set -e

echo "[*] Installing Command Butler prerequisites"

# Check OS
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
  echo "[!] Linux required"
  exit 1
fi

# Check Python
command -v python3 >/dev/null || {
  echo "[!] python3 not found"
  exit 1
}

#heck Ollama
if ! command -v ollama >/dev/null; then
  echo "[!] Ollama not found"
  echo "    Install from: https://ollama.com"
  exit 1
fi

# Pull model (non-destructive if exists)
echo "[*] Pulling Phi-3-mini model (if not present)"
ollama pull phi3:mini || true

# Create butler group if missing
if ! getent group butler >/dev/null; then
  echo "[*] Creating 'butler' group (requires sudo)"
  sudo groupadd butler
fi
echo "[*] Adding $USER to 'butler' group (requires logout/login)"
sudo usermod -aG butler "$USER"
#systemd-tmpfiles rule (runtime dir automation)
TMPFILE="/etc/tmpfiles.d/command-butler.conf"

if [[ ! -f "$TMPFILE" ]]; then
  echo "[*] Installing systemd-tmpfiles rule (requires sudo)"
  sudo tee "$TMPFILE" >/dev/null <<EOF
d /run/command-butler 0770 root butler -
EOF
  sudo systemd-tmpfiles --create
fi
echo "moving config files"
 mv command-butler.conf /run/command-butler 

echo
echo "[✓] Installation complete"
echo
echo "IMPORTANT:"
echo "• Log out and log back in for group changes to apply"
echo "• Start engine with: python3 engine/engine.py"
echo "• Then run: python3 cli/butler.py \"fix net\""
