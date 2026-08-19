#!/data/data/com.termux/files/usr/bin/bash
# Fallback shebang for standard bash if running outside Termux
if [ -z "$BASH_VERSION" ]; then
    exec bash "$0" "$@"
fi

# ==============================================================================
# SAGE-7 Termux Widget Shutdown Script
# Designation: SAGE-7 / Project Crimson Node
# ==============================================================================

clear
echo "╔═════════════════════════════════════════════════════════════════╗"
echo "║                  SAGE-7 SUBSTRATE SHUTDOWN                      ║"
echo "╚═════════════════════════════════════════════════════════════════╝"
echo ""

echo "[*] Stopping Python backends, launcher, and bridges..."
pkill -f "sage_core/launcher.py" 2>/dev/null || true
pkill -f "server.py" 2>/dev/null || true
pkill -f "sage_core/mcp_cli_server.py" 2>/dev/null || true
pkill -f "sensor_server_bridge.py" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

if command -v termux-wake-unlock &>/dev/null; then
    termux-wake-unlock 2>/dev/null || true
    echo "[+] Termux wake-lock released."
fi

if command -v termux-toast &>/dev/null; then
    termux-toast "SAGE-7 Substrate Offline"
fi

echo "[✓] All SAGE-7 services terminated successfully."
sleep 1
