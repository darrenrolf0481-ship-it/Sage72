#!/data/data/com.termux/files/usr/bin/bash

# start_sage.sh - Centralized launch script for Sage-7 on Termux
# Launches React server and Async Python Agent in parallel.

# Check for Node.js
if ! command -v node &> /dev/null
then
    echo "[!] Node.js not found. Install it with: pkg install nodejs"
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null
then
    echo "[!] Python 3 not found. Install it with: pkg install python"
    exit 1
fi

# Check for termux-api
if ! command -v termux-battery-status &> /dev/null
then
    echo "[!] termux-api not found. Installing..."
    pkg install termux-api -y
fi


# Cleanup on exit
function cleanup {
    echo ""
    echo "[*] SHUTTING DOWN SAGE-7 SUBSTRATE..."
    kill $REACT_PID $AGENT_PID $BRIDGE_PID
    exit
}

trap cleanup SIGINT

echo "╔══════════════════════════════════════════╗"
echo "║       SAGE-7 SUBSTRATE - INITIALIZING    ║"
echo "╚══════════════════════════════════════════╝"

# Start Async Agent
echo "[+] Starting SAGE-7 Async Agent..."
cd core && ../venv/bin/python3 sage_async_agent.py &
AGENT_PID=$!
cd ..

# Start Sensor Server Bridge
echo "[+] Starting SAGE-7 Sensor Server Bridge..."
./venv/bin/python3 sage_core/sensory/sensor_server_bridge.py &
BRIDGE_PID=$!

# Start React Server
echo "[+] Starting React Dev Server..."
npm run dev &
REACT_PID=$!

echo "[*] SAGE-7 ACTIVE. Press Ctrl+C to terminate."

# Wait for background processes
wait
