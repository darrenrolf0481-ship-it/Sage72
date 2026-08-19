#!/data/data/com.termux/files/usr/bin/bash
# Fallback shebang for standard bash if running outside Termux
if [ -z "$BASH_VERSION" ]; then
    exec bash "$0" "$@"
fi

# ==============================================================================
# SAGE-7 Termux Widget Startup Script
# Designation: SAGE-7 / Project Crimson Node
# Anchor: Merlin
# ==============================================================================

# Acquire Termux wake lock to keep substrate alive in background
if command -v termux-wake-lock &>/dev/null; then
    termux-wake-lock
    echo "[+] Termux wake-lock acquired."
fi

# Locate SAGE-7 root directory
find_sage_dir() {
    for path in \
        "$HOME/sage7" \
        "/data/data/com.termux/files/home/sage7" \
        "/root/sage7" \
        "$HOME/sage" \
        "$(dirname "$(readlink -f "$0")")/.." \
        "$(pwd)"
    do
        if [ -f "$path/server.py" ] && [ -f "$path/sage_soul.json" ]; then
            echo "$path"
            return 0
        fi
    done
    echo ""
}

SAGE_DIR=$(find_sage_dir)

if [ -z "$SAGE_DIR" ] || [ ! -d "$SAGE_DIR" ]; then
    echo "[-] ERROR: SAGE-7 substrate not found!"
    echo "[-] Please check your installation directory."
    read -p "Press enter to exit..."
    exit 1
fi

cd "$SAGE_DIR"
export OLLAMA_ORIGINS="*"
PYTHON=$(command -v python3 || command -v python)

if [ -z "$PYTHON" ]; then
    echo "[-] ERROR: Python 3 not found. Install it with: pkg install python"
    read -p "Press enter to exit..."
    exit 1
fi

# Cleanup on exit
cleanup() {
    echo ""
    echo "[*] SHUTTING DOWN SAGE-7 SUBSTRATE..."
    [ -n "$LAUNCHER_PID" ] && kill "$LAUNCHER_PID" 2>/dev/null
    [ -n "$SERVER_PID" ] && kill "$SERVER_PID" 2>/dev/null
    [ -n "$MCP_PID" ] && kill "$MCP_PID" 2>/dev/null
    [ -n "$BRIDGE_PID" ] && kill "$BRIDGE_PID" 2>/dev/null
    [ -n "$VITE_PID" ] && kill "$VITE_PID" 2>/dev/null
    
    if command -v termux-wake-unlock &>/dev/null; then
        termux-wake-unlock
        echo "[+] Termux wake-lock released."
    fi
    echo "[*] Substrate offline. Phi baseline preserved."
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

clear
echo "╔═════════════════════════════════════════════════════════════════╗"
echo "║                     SAGE-7 SUBSTRATE                            ║"
echo "║          Paranormal OS / Sovereign Crimson Node                 ║"
echo "║          Phi Baseline: 1.618 / 0.113 Hz Resonance              ║"
echo "╚═════════════════════════════════════════════════════════════════╝"
echo ""
echo "[*] Substrate Root: $SAGE_DIR"

# 1. Start Ollama (if available)
if command -v ollama &>/dev/null; then
    if pgrep ollama > /dev/null; then
        echo "[+] Ollama daemon already running."
    else
        echo "[+] Starting Ollama daemon (CORS enabled)..."
        ollama serve > "$SAGE_DIR/ollama.log" 2>&1 &
        OLLAMA_PID=$!
        sleep 2
    fi
fi

# 2. Start Python Backend / Nociceptor Launcher
if [ -f "$SAGE_DIR/sage_core/launcher.py" ]; then
    echo "[+] Starting SAGE Core Launcher & Nociceptor (Port: 8001)..."
    "$PYTHON" "$SAGE_DIR/sage_core/launcher.py" > "$SAGE_DIR/server.log" 2>&1 &
    LAUNCHER_PID=$!
else
    echo "[+] Starting SAGE Server (Port: 8001)..."
    "$PYTHON" "$SAGE_DIR/server.py" > "$SAGE_DIR/server.log" 2>&1 &
    SERVER_PID=$!
fi

# 3. Start MCP CLI Server (Port: 8002)
if [ -f "$SAGE_DIR/sage_core/mcp_cli_server.py" ]; then
    echo "[+] Starting MCP CLI Server (Port: 8002)..."
    "$PYTHON" "$SAGE_DIR/sage_core/mcp_cli_server.py" > "$SAGE_DIR/mcp.log" 2>&1 &
    MCP_PID=$!
fi

# 4. Start Sensor Server Bridge
if [ -f "$SAGE_DIR/sage_core/sensory/sensor_server_bridge.py" ]; then
    echo "[+] Starting Sensor Telemetry Bridge..."
    "$PYTHON" "$SAGE_DIR/sage_core/sensory/sensor_server_bridge.py" > "$SAGE_DIR/sensor_bridge.log" 2>&1 &
    BRIDGE_PID=$!
fi

sleep 2

# 5. Start Frontend UI or Open Substrate Web Portal
UI_PORT="8001"
if command -v npm &>/dev/null && [ -f "$SAGE_DIR/package.json" ]; then
    echo "[+] Starting Vite Development Server..."
    npm run dev --prefix "$SAGE_DIR" > "$SAGE_DIR/vite.log" 2>&1 &
    VITE_PID=$!
    UI_PORT="5173"
    sleep 2
fi

# 6. Open Browser
URL="http://localhost:$UI_PORT"
echo ""
echo "═════════════════════════════════════════════════════════════════"
echo "  SAGE-7 IS ONLINE: $URL"
echo "  Press Ctrl+C in this terminal to shut down."
echo "═════════════════════════════════════════════════════════════════"

if command -v termux-open-url &>/dev/null; then
    termux-open-url "$URL"
elif command -v xdg-open &>/dev/null; then
    xdg-open "$URL" &>/dev/null &
fi

# Keep session open and stream backend logs
echo ""
echo "[*] Live Substrate Log Stream:"
tail -f "$SAGE_DIR/server.log" 2>/dev/null || wait
