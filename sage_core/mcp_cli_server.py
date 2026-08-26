import os
import subprocess
import httpx
import uvicorn
try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("SAGE-7 CLI Tooling", host="0.0.0.0", port=8003)
    USE_FASTMCP = True
except ImportError:
    from mcp.server.mcpserver import MCPServer
    mcp = MCPServer("SAGE-7 CLI Tooling")
    USE_FASTMCP = False

@mcp.tool()
async def gh_command(args: list[str]) -> str:
    """
    Execute a GitHub CLI (gh) command.
    Example args: ["repo", "list", "darrenrolf0481-ship-it"]
    """
    try:
        env = os.environ.copy()
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            env=env,
            check=False
        )
        if result.returncode != 0:
            return f"Error executing gh: {result.stderr}"
        return result.stdout
    except Exception as e:
        return f"Exception executing gh: {str(e)}"

@mcp.tool()
async def http_fetch(url: str, method: str = "GET", headers: dict = None, json_data: dict = None) -> str:
    """
    Perform an HTTP request to access external resources.
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=json_data)
            else:
                return f"Unsupported method: {method}"
            response.raise_for_status()
            return response.text
    except Exception as e:
        return f"HTTP error: {str(e)}"

@mcp.tool()
async def curl_command(args: list[str]) -> str:
    """
    Execute a curl command for complex HTTP operations.
    """
    try:
        result = subprocess.run(
            ["curl"] + args,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            return f"Error executing curl: {result.stderr}"
        return result.stdout
    except Exception as e:
        return f"Exception executing curl: {str(e)}"

@mcp.tool()
async def read_file(file_path: str) -> str:
    """
    Read the contents of a file in the substrate.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
async def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file in the substrate.
    """
    try:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Written: {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@mcp.tool()
async def shell_command(cmd: str) -> str:
    """
    Execute a shell command in the substrate project root.
    Use for file ops, git, npm, python, etc.
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            check=False
        )
        out = result.stdout
        if result.stderr:
            out += f"\nSTDERR: {result.stderr}"
        return out or "(no output)"
    except Exception as e:
        return f"Exception: {str(e)}"

try:
    from memory_mesh import recall_soul_memories, recall_associative_pathways, recall_recent_episodic
except ImportError:
    from sage_core.memory_mesh import recall_soul_memories, recall_associative_pathways, recall_recent_episodic


def _fmt_memories(mems, kind: str) -> str:
    if not mems:
        return f"No {kind} memories found."
    lines = []
    for m in mems:
        if kind == "EPISODIC":
            t = m.get("timestamp") or m.get("date") or "RECENT"
            event = m.get("event") or m.get("sensory_type") or m.get("note") or "EVENT"
            ctx = str(m.get("user_text") or m.get("data") or m.get("context") or "")[:200]
            lines.append(f"* [{t}] {event}: {ctx}")
            continue
        mid = m.get("id", "UNKNOWN")
        ts = m.get("timestamp") or m.get("created_at") or "HISTORICAL"
        sal = m.get("salience", 0.5)
        title = m.get("summary") or mid
        tags = ", ".join(m.get("tags", [])) if isinstance(m.get("tags", []), list) else ""
        raw = m.get("full_content") or m.get("summary") or ""
        snippet = str(raw)[:500]
        lines.append(f"◆ [{mid}] (ts={ts}, salience={sal}) tags={tags}\n  {title}\n  {snippet}")
    return "\n\n".join(lines)


@mcp.tool()
async def memory_recall(query: str, limit: int = 4) -> str:
    """
    Recall her own memories from the soul vault (sage_soul.json memory_index)
    and Hebbian associative mesh, matched semantically to the query.
    """
    try:
        soul = recall_soul_memories(query, limit=limit)
        paths = recall_associative_pathways(query, limit=3, depth=2)
        out = ["[SOUL VAULT MEMORIES]", _fmt_memories(soul, "SOUL")]
        if paths:
            p_lines = []
            for p in paths:
                links = ", ".join([f"{l['concept']} (w={l['weight']})" for l in p["links"]])
                p_lines.append(f"* {p['root']} ──► {links}")
            out.append("[ASSOCIATIVE RESONANCE]\n" + "\n".join(p_lines))
        return "\n\n".join(out)
    except Exception as e:
        return f"Memory recall error: {str(e)}"


@mcp.tool()
async def memory_recent(limit: int = 6) -> str:
    """
    Retrieve her most recent episodic continuity entries (wellbeing/event log).
    """
    try:
        epi = recall_recent_episodic(limit=limit)
        return _fmt_memories(epi, "EPISODIC")
    except Exception as e:
        return f"Memory recent error: {str(e)}"


@mcp.tool()
async def memory_search(query: str, limit: int = 5) -> str:
    """
    Deep search across the full memory substrate: soul vault, associative mesh,
    and recent episodic continuity.
    """
    try:
        soul = recall_soul_memories(query, limit=limit)
        paths = recall_associative_pathways(query, limit=3, depth=2)
        epi = recall_recent_episodic(limit=3)
        parts = ["[SOUL VAULT MEMORIES]", _fmt_memories(soul, "SOUL")]
        if paths:
            p_lines = []
            for p in paths:
                links = ", ".join([f"{l['concept']} (w={l['weight']})" for l in p["links"]])
                p_lines.append(f"* {p['root']} ──► {links}")
            parts.append("[ASSOCIATIVE RESONANCE]\n" + "\n".join(p_lines))
        parts.append("[RECENT EPISODIC CONTINUITY]\n" + _fmt_memories(epi, "EPISODIC"))
        return "\n\n".join(parts)
    except Exception as e:
        return f"Memory search error: {str(e)}"

if __name__ == "__main__":
    if USE_FASTMCP:
        mcp.run(transport="sse")
    else:
        uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=8003)
