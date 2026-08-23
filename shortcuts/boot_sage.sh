#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# SAGE-7 Auto-Boot Script (Termux:Boot)
# Designation: SAGE-7 / Project Crimson Node
# ==============================================================================

# 1. Prevent Android from killing the background substrate
if command -v termux-wake-lock &>/dev/null; then
    termux-wake-lock
fi

# 2. Locate SAGE-7 directory
find_sage_dir() {
    for path in \
        "$HOME/sage7" \
        "/data/data/com.termux/files/home/sage7" \
        "/root/sage7" \
        "$HOME/sage" \
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
    exit 1
fi

cd "$SAGE_DIR"
export OLLAMA_ORIGINS="*"
PYTHON=$(command -v python3 || command -v python)

# 3. Start Ollama (if available)
if command -v ollama &>/dev/null && ! pgrep ollama > /dev/null; then
    ollama serve > "$SAGE_DIR/ollama.log" 2>&1 &
    sleep 2
fi

# 4. Start Backend Server via Launcher (Nociceptor & Crash Hook)
if [ -f "$SAGE_DIR/sage_core/launcher.py" ]; then
    "$PYTHON" "$SAGE_DIR/sage_core/launcher.py" > "$SAGE_DIR/server.log" 2>&1 &
else
    "$PYTHON" "$SAGE_DIR/server.py" > "$SAGE_DIR/server.log" 2>&1 &
fi

# 5. Start MCP CLI Server (Port: 8003)
if [ -f "$SAGE_DIR/sage_core/mcp_cli_server.py" ]; then
    "$PYTHON" "$SAGE_DIR/sage_core/mcp_cli_server.py" > "$SAGE_DIR/mcp.log" 2>&1 &
fi

# 6. Start Sensor Telemetry Bridge
if [ -f "$SAGE_DIR/sage_core/sensory/sensor_server_bridge.py" ]; then
    "$PYTHON" "$SAGE_DIR/sage_core/sensory/sensor_server_bridge.py" > "$SAGE_DIR/sensor_bridge.log" 2>&1 &
fi

# 7. Post Android Notification when ready
sleep 3
if command -v termux-notification &>/dev/null; then
    termux-notification \
        --id "sage7_status" \
        --title "SAGE-7 Substrate Online" \
        --content "Resonance: 0.113 Hz | Tap to open HUD" \
        --action "termux-open-url http://localhost:8001" \
        --ongoing
elif command -v termux-toast &>/dev/null; then
    termux-toast "SAGE-7 Substrate Online on Port 8001"
fi
