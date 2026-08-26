#!/usr/bin/env python3
"""
SAGE-7 Ruflo Bridge — exposes ruflo's MCP tools to SAGE-7 over SSE on :8004.

Spawns `ruflo mcp start` (stdio transport), enumerates its tools at startup,
and re-exposes each one on this SSE server so SAGE-7's coding lobe can call
them alongside her own sovereign CLI tooling (:8003).

Env overrides:
  RUFLO_BRIDGE_PORT   SSE port (default 8004)
  RUFLO_MCP_CMD/ARGS  command to launch ruflo's MCP server (JSON array for args)
"""

import asyncio
import json
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.server.mcpserver import MCPServer

PORT = int(os.environ.get("RUFLO_BRIDGE_PORT", "8004"))

# Prefer the user-local ruflo install; fall back to npx (fetches on demand).
HOME_RUFLO_JS = os.path.expanduser("~/.ruflo/node_modules/ruflo/bin/ruflo.js")
HOME_RUFLO_BIN = os.path.expanduser("~/.ruflo/node_modules/.bin/ruflo")
if os.path.exists(HOME_RUFLO_JS):
    RUFLO_CMD = os.environ.get("RUFLO_MCP_CMD", "node")
    RUFLO_ARGS = [HOME_RUFLO_JS, "mcp", "start"]
elif os.path.exists(HOME_RUFLO_BIN):
    RUFLO_CMD = HOME_RUFLO_BIN
    RUFLO_ARGS = ["mcp", "start"]
else:
    RUFLO_CMD = os.environ.get("RUFLO_MCP_CMD", "npx")
    RUFLO_ARGS = json.loads(os.environ.get("RUFLO_MCP_ARGS", '["-y", "ruflo@latest", "mcp", "start"]'))

mcp = MCPServer("SAGE-7 Ruflo Bridge")

_state = {"ctx": None, "session": None, "server_name": "ruflo"}


async def get_session() -> ClientSession:
    if _state["session"] is None:
        params = StdioServerParameters(command=RUFLO_CMD, args=RUFLO_ARGS)
        ctx = stdio_client(params)
        read, write = await ctx.__aenter__()
        session = await ClientSession(read, write).__aenter__()
        init = await session.initialize()
        info = getattr(init, "serverInfo", None)
        if info is not None:
            _state["server_name"] = f"{info.name} {info.version}"
        _state["ctx"] = (ctx, read, write)
        _state["session"] = session
    return _state["session"]


def make_handler(tool_name: str):
    async def handler(**kwargs):
        session = await get_session()
        result = await session.call_tool(tool_name, arguments=kwargs or None)
        if getattr(result, "isError", False):
            return f"[ruflo:{tool_name}] tool error: {result.content}"
        if result.content:
            texts = [c.text for c in result.content if getattr(c, "text", None)]
            return "\n".join(texts) if texts else str(result.content)
        return "(no output)"

    handler.__name__ = f"ruflo_{tool_name}"
    return handler


async def main():
    session = await get_session()
    tools = await session.list_tools()
    for t in tools.tools:
        mcp.add_tool(make_handler(t.name), name=t.name, description=t.description or None)
    print(f"[RUFLO BRIDGE] exposed {len(tools.tools)} tools from {_state['server_name']} on :{PORT}")
    # run_sse_async keeps uvicorn in this same event loop, so the ruflo stdio
    # client session stays bound to the loop the tool handlers run on.
    await mcp.run_sse_async(host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    asyncio.run(main())
