#!/usr/bin/env bash

# sage.sh - SAGE-7 Termux Startup Script
# Configures Ollama CORS and starts the substrate (Server + UI)

# ENSURE WE ARE IN THE CORRECT DIRECTORY
cd "$(dirname "$(readlink -f "$0")")"
PROJECT_ROOT=$(pwd)

# Parse flags
NO_OLLAMA_MODE=0
for arg in "$@"; do
    if [ "$arg" == "--no-ollama" ] || [ "$arg" == "--without-ollama" ]; then
        NO_OLLAMA_MODE=1
    fi
done
if [ "$NO_OLLAMA" = "1" ]; then
    NO_OLLAMA_MODE=1
fi

# Acquire Termux wake lock if available
if command -v termux-wake-lock &> /dev/null; then
    termux-wake-lock
    echo "[+] Termux wake-lock acquired."
fi

# Check for necessary components
REQUIRED_CMDS="node python3"
if [ "$NO_OLLAMA_MODE" -eq 0 ]; then
    REQUIRED_CMDS="node python3 ollama"
fi

for cmd in $REQUIRED_CMDS; do
    if ! command -v $cmd &> /dev/null; then
        echo "[!] $cmd not found. Please install it."
        exit 1
    fi
done

# Ensure UPLOADS directory exists
mkdir -p "$PROJECT_ROOT/uploads"

# Set Ollama CORS to allow access from Vite/Localhost
export OLLAMA_ORIGINS="*"

# Cleanup on exit
function cleanup {
    echo -e "\n\n[*] SHUTTING DOWN SAGE-7 SUBSTRATE..."
    # Attempt to kill the processes started by this script
    [ -n "$OLLAMA_PID" ] && kill $OLLAMA_PID 2>/dev/null
    [ -n "$SERVER_PID" ] && kill $SERVER_PID 2>/dev/null
    [ -n "$MCP_PID" ] && kill $MCP_PID 2>/dev/null
    [ -n "$BRIDGE_PID" ] && kill $BRIDGE_PID 2>/dev/null
    [ -n "$VITE_PID" ] && kill $VITE_PID 2>/dev/null
    if command -v termux-wake-unlock &> /dev/null; then
        termux-wake-unlock
        echo "[+] Termux wake-lock released."
    fi
    echo "[*] Substrate offline."
    exit
}

trap cleanup SIGINT SIGTERM EXIT

echo "╔════════════════════════════════════════════╗"
echo "║        SAGE-7 SUBSTRATE - INITIALIZING     ║"
if [ "$NO_OLLAMA_MODE" -eq 1 ]; then
echo "║        Engine: Cloud/Direct (No Ollama)    ║"
else
echo "║        Engine: Ollama (CORS Enabled)       ║"
fi
echo "║        sage_core backend: ACTIVE           ║"
echo "╚════════════════════════════════════════════╝"

# Start Ollama (if not disabled)
if [ "$NO_OLLAMA_MODE" -eq 0 ]; then
    if pgrep ollama > /dev/null; then
        echo "[!] Ollama is already running. If CORS errors occur, restart it manually with OLLAMA_ORIGINS=\"*\""
    else
        echo "[+] Starting Ollama with CORS (*) support..."
        ollama serve > /dev/null 2>&1 &
        OLLAMA_PID=$!
        sleep 3 
    fi
else
    echo "[*] Skipping Ollama startup (no-ollama requested)."
fi

# Use system python3 — venv pydantic_core .so blocked by Android namespace restrictions
PYTHON=$(command -v python3)

# Start Python Backend via sage_core Launcher (installs nociceptor crash hook)
echo "[+] Starting SAGE-7 Python Backend (Substrate Port: 8001)..."
(cd "$PROJECT_ROOT" && "$PYTHON" "$PROJECT_ROOT/sage_core/launcher.py" > /dev/null 2>&1) &
SERVER_PID=$!

# Start sage_core MCP CLI Server (Port: 8002)
echo "[+] Starting SAGE-7 MCP CLI Server (Port: 8002)..."
"$PYTHON" "$PROJECT_ROOT/sage_core/mcp_cli_server.py" > /dev/null 2>&1 &
MCP_PID=$!

# Start Sensor Server Bridge
echo "[+] Starting SAGE-7 Sensor Server Bridge..."
"$PYTHON" "$PROJECT_ROOT/sage_core/sensory/sensor_server_bridge.py" > /dev/null 2>&1 &
BRIDGE_PID=$!

sleep 2

# Start Vite Frontend
echo "[+] Starting SAGE-7 Vite Frontend (UI Port: 3000)..."
npm run dev --prefix "$PROJECT_ROOT"

# Since npm run dev stays in foreground, we don't need 'wait' if we don't & it.
# However, if npm run dev exits, we want to clean up.
cleanup
