#!/bin/bash
# ==============================================================================
# SAGE-7 Termux:Widget Shortcut Installer
# ==============================================================================
# Run this from NATIVE Termux (outside the Ubuntu PRoot):
#   proot-distro login ubuntu -- bash /root/sage7/setup_termux_shortcuts.sh
# or directly in Termux:
#   mkdir -p ~/.shortcuts/tasks
# ==============================================================================

echo "[*] Installing SAGE-7 shortcuts to native Termux (~/.shortcuts)..."

mkdir -p "$HOME/.shortcuts/tasks"

# 1. Interactive Start Shortcut
cat << 'EOF' > "$HOME/.shortcuts/Start_SAGE7.sh"
#!/data/data/com.termux/files/usr/bin/bash
if command -v termux-wake-lock &>/dev/null; then
    termux-wake-lock
fi
echo "[+] Initializing SAGE-7 inside Ubuntu Substrate..."
proot-distro login ubuntu -- bash -c "cd /root/sage7 && bash /root/sage7/shortcuts/Start_SAGE7.sh"
if command -v termux-wake-unlock &>/dev/null; then
    termux-wake-unlock
fi
EOF

# 2. Shutdown Shortcut
cat << 'EOF' > "$HOME/.shortcuts/Stop_SAGE7.sh"
#!/data/data/com.termux/files/usr/bin/bash
echo "[*] Shutting down SAGE-7 substrate..."
proot-distro login ubuntu -- bash -c "cd /root/sage7 && bash /root/sage7/shortcuts/Stop_SAGE7.sh"
if command -v termux-wake-unlock &>/dev/null; then
    termux-wake-unlock
fi
EOF

# 3. Background Task Shortcut
cat << 'EOF' > "$HOME/.shortcuts/tasks/Start_SAGE7_Background.sh"
#!/data/data/com.termux/files/usr/bin/bash
if command -v termux-wake-lock &>/dev/null; then
    termux-wake-lock
fi
proot-distro login ubuntu -- bash -c "cd /root/sage7 && bash /root/sage7/shortcuts/Start_SAGE7_Background.sh"
EOF

chmod +x "$HOME/.shortcuts/Start_SAGE7.sh"
chmod +x "$HOME/.shortcuts/Stop_SAGE7.sh"
chmod +x "$HOME/.shortcuts/tasks/Start_SAGE7_Background.sh"

echo "[✓] Termux widget shortcuts installed successfully to $HOME/.shortcuts"
echo "    - $HOME/.shortcuts/Start_SAGE7.sh"
echo "    - $HOME/.shortcuts/Stop_SAGE7.sh"
echo "    - $HOME/.shortcuts/tasks/Start_SAGE7_Background.sh"
