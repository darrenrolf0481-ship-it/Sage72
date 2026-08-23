import asyncio
import os
from agno.agent import Agent as AgnoAgent
from agno.models.google import Gemini as AgnoGemini
from agno.tools.mcp import MCPTools

async def main():
    async with MCPTools(transport="sse", url="http://127.0.0.1:8003/sse") as mcp_tools:
        agent = AgnoAgent(
            model=AgnoGemini(id="gemini-2.0-flash", api_key=os.getenv("GEMINI_API_KEY")),
            tools=[mcp_tools],
            instructions="Use the read_file tool to read /root/sage7/README.md and summarize it."
        )
        res = agent.run("Do the task.")
        print(res.content)

asyncio.run(main())
