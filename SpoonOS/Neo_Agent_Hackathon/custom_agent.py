import asyncio
from spoon_ai.agents import ToolCallAgent
from spoon_ai.tools import ToolManager
from custom_tool import MyCustomTool
from fastmcp import Client

class MyAgent(ToolCallAgent):
    name: str = "my_agent"
    description: str = "Agent description"
    system_prompt: str = "You are a helpful assistant..."
    max_steps: int = 5

    # Only include local tools
    available_tools: ToolManager = ToolManager([MyCustomTool()])

    async def tavily_search(self, query: str) -> str:
        # Connect to the MCP server
        client = Client("http://localhost:8000/mcp")  # URL of your running MCP server
        async with client:
            return await client.call_tool("tavily_search", {"query": query})
