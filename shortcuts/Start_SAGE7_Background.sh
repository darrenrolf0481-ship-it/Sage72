#!/data/data/com.termux/files/usr/bin/bash
# SAGE-7 Silent Background Widget Launcher (Termux:Widget Tasks)

if command -v termux-wake-lock &>/dev/null; then
    termux-wake-lock
fi

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
if [ -z "$SAGE_DIR" ]; then
    if command -v termux-toast &>/dev/null; then
        termux-toast "Error: SAGE-7 directory not found"
    fi
    exit 1
fi

cd "$SAGE_DIR"
export OLLAMA_ORIGINS="*"
PYTHON=$(command -v python3 || command -v python)

# Start Ollama if present
if command -v ollama &>/dev/null && ! pgrep ollama > /dev/null; then
    ollama serve > "$SAGE_DIR/ollama.log" 2>&1 &
fi

# Start Backend via Launcher
if [ -f "$SAGE_DIR/sage_core/launcher.py" ]; then
    "$PYTHON" "$SAGE_DIR/sage_core/launcher.py" > "$SAGE_DIR/server.log" 2>&1 &
else
    "$PYTHON" "$SAGE_DIR/server.py" > "$SAGE_DIR/server.log" 2>&1 &
fi

# Start MCP CLI Server
if [ -f "$SAGE_DIR/sage_core/mcp_cli_server.py" ]; then
    "$PYTHON" "$SAGE_DIR/sage_core/mcp_cli_server.py" > "$SAGE_DIR/mcp.log" 2>&1 &
fi

# Start Sensor Server Bridge
if [ -f "$SAGE_DIR/sage_core/sensory/sensor_server_bridge.py" ]; then
    "$PYTHON" "$SAGE_DIR/sage_core/sensory/sensor_server_bridge.py" > "$SAGE_DIR/sensor_bridge.log" 2>&1 &
fi

# Start Vite dev server if npm available
UI_PORT="8001"
if command -v npm &>/dev/null && [ -f "$SAGE_DIR/package.json" ]; then
    npm run dev --prefix "$SAGE_DIR" > "$SAGE_DIR/vite.log" 2>&1 &
    UI_PORT="5173"
fi

sleep 2

if command -v termux-toast &>/dev/null; then
    termux-toast "SAGE-7 Substrate Online (Port: $UI_PORT)"
fi

if command -v termux-open-url &>/dev/null; then
    termux-open-url "http://localhost:$UI_PORT"
fi
