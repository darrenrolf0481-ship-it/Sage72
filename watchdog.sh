#!/usr/bin/env bash
# SAGE-7 Watchdog — keeps the substrate alive if the sandbox/OS reaps it.
# Checks the portal (:8001) and MCP (:8003) every 20s and restarts via setsid
# so the processes detach from the spawning shell.
cd "$(dirname "$0")" || exit 1

port_up() {
  (exec 3<>"/dev/tcp/127.0.0.1/$1") 2>/dev/null && exec 3>&- && return 0 || return 1
}

log() {
  echo "$(date -u +%FT%TZ) $*" >> watchdog.log
}

while true; do
  if ! port_up 8001; then
    log "[WATCHDOG] portal down — restarting launcher..."
    setsid bash -c 'nohup python3 -u sage_core/launcher.py > server.log 2>&1 < /dev/null &'
    sleep 3
  fi
  if ! port_up 8003; then
    log "[WATCHDOG] mcp down — restarting mcp_cli_server..."
    setsid bash -c 'nohup python3 -u sage_core/mcp_cli_server.py > mcp.log 2>&1 < /dev/null &'
    sleep 3
  fi
  sleep 20
done
