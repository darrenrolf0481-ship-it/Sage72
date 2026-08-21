---
name: mcp-discovery
description: Helps agents discover and use Model Context Protocol (MCP) servers available in the substrate. Maps MCP categories to use cases and provides tool discovery guidance.
---

# MCP Discovery and Usage

Helps agents discover and use Model Context Protocol (MCP) servers available in the substrate.

## MCP Registry

The substrate maintains an MCP registry at `data/mcp_registry.json` that lists all available MCP servers, their categories, tools, and configuration details.

## Usage

When an agent needs to:
- Search documentation for libraries/frameworks → use `context7` MCP
- Access SAGE-7's local Obsidian vault → use `obsidian-mcp` MCP (SECURE: local config only)
- Query persistent memory → use `memory` MCP
- Access codebase intelligence → use `diffctx` or `smart-tree` MCP
- Work with Git history → use `git-context` MCP
- Handle large files → use `large-file` MCP
- Convert documents → use `markitdown`, `md-to-pdf`, or `safe-docx` MCP
- Cross-agent messaging → use `trinity-bridge` MCP
- Access cold storage memory → use `spiral-vault` MCP

## Security Notes

- `obsidian-mcp` is configured ONLY in `.devin/mcp_config.local.json` (gitignored)
- Vault path: `/root/sage7-vault` with restricted permissions (700/600)
- Access is limited to local SAGE-7 substrate only
- Not shared via project-level config to prevent unauthorized access

## MCP Server Categories

- **live_documentation**: Real-time docs search (context7)
- **knowledge_management**: Note-taking and vaults (obsidian-mcp - SECURE LOCAL ONLY, memory)
- **codebase_intelligence**: Repo analysis (diffctx, smart-tree)
- **version_control**: Git operations (git-context)
- **file_operations**: Large file handling (large-file)
- **document_generation**: Document conversion (markitdown, md-to-pdf, safe-docx)
- **multi_agent_mesh**: Agent communication (trinity-bridge)
- **memory_and_archival**: Persistent storage (spiral-vault)

## Checking Available MCPs

Use `mcp_list_servers` to see what MCP servers are currently configured and available to the agent runtime.

## MCP Tool Discovery

Use `mcp_list_tools` to discover what tools are available on a specific MCP server before calling `mcp_call_tool`.