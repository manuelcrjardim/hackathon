# tavily_mcp_tool.py
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from tavily import TavilyClient

# Create the FastMCP server
mcp = FastMCP("Tavily Search MCP Server")

# Input schema for the tool
class SearchInput(BaseModel):
    query: str = Field(..., description="Search query")

# Define the Tavily search tool
@mcp.tool
async def tavily_search(input: SearchInput) -> str:
    client = TavilyClient(api_key="YOUR_TAVILY_API_KEY")
    result = await client.search(input.query)
    return "\n".join([f"{item['title']}: {item['link']}" for item in result["items"]])

if __name__ == "__main__":
    mcp.run()
