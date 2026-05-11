import os
import subprocess
import httpx
from mcp.server.fastmcp import FastMCP

# Port in constructor, not run()
mcp = FastMCP("SAGE-7 CLI Tooling", host="0.0.0.0", port=8002)

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

if __name__ == "__main__":
    mcp.run(transport="sse")
