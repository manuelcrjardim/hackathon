from spoon_ai.agents import ToolCallAgent
from spoon_ai.tools import ToolManager
from pydantic import Field
from fastmcp import Client
import asyncio
import sys
from pathlib import Path

class TavilySearchTool:
    """Wrapper to call the FastMCP Tavily search tool from SpoonAI agent."""
    
    name = "tavily_search"
    description = "Search the web using Tavily to find current information"
    
    def __init__(self, server_script_path: str = "./tavily_mcp_server.py"):
        """
        Initialize the tool with path to MCP server script.
        
        Args:
            server_script_path: Path to the MCP server Python script
        """
        self.server_script_path = server_script_path
        self.client = None
    
    async def _ensure_connected(self):
        """Ensure the MCP client is connected."""
        if self.client is None:
            # Get the full path to the server script
            server_path = Path(self.server_script_path).resolve()
            
            # Connect to MCP server - just pass the script path as a string
            self.client = Client(str(server_path))
            await self.client.__aenter__()
    
    async def execute(self, query: str, max_results: int = 5) -> str:
        """
        Execute a web search using Tavily.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            Formatted search results as a string
        """
        try:
            await self._ensure_connected()
            
            # Call the tavily_search tool on the MCP server
            result = await self.client.call_tool(
                "tavily_search",
                arguments={"query": query, "max_results": max_results}
            )
            
            # Extract the formatted text from the result
            # The CallToolResult object has a .data property with the formatted string
            if hasattr(result, 'data') and result.data:
                return result.data
            elif hasattr(result, 'content') and result.content:
                # Fallback: extract from content array
                return result.content[0].text if result.content else str(result)
            else:
                return str(result)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Error executing search: {str(e)}"
    
    async def cleanup(self):
        """Clean up the MCP client connection."""
        if self.client:
            try:
                await self.client.__aexit__(None, None, None)
            except:
                pass
            self.client = None

class SearchAgent(ToolCallAgent):
    name: str = "search_agent"
    description: str = "An agent that can search the web for information"
    system_prompt: str = """You are a helpful assistant with access to web search.
When asked questions that require current information, use the tavily_search tool to find relevant information.
Always provide clear, concise answers based on the search results."""
    max_steps: int = 5
    
    available_tools: ToolManager = Field(
        default_factory=lambda: ToolManager([
            TavilySearchTool(),
        ])
    )