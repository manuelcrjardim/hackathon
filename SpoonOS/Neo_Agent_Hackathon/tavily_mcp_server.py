from fastmcp import FastMCP
from pydantic import BaseModel, Field
from tavily import TavilyClient
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is not set in your .env file!")

# Create the MCP server
mcp = FastMCP("Tavily Search MCP Server")

# Input schema for the tool
class SearchInput(BaseModel):
    query: str = Field(..., description="Search query to execute")
    max_results: int = Field(default=5, description="Maximum number of results to return")

# Define the Tavily search tool
@mcp.tool()
def tavily_search(query: str, max_results: int = 5) -> str:
    """Search the web using Tavily API and return formatted results."""
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        # Tavily's search method is synchronous, not async
        result = client.search(query, max_results=max_results)
        
        # Check if we have results
        if not result or "results" not in result:
            return "No results found"
        
        # Format the results
        formatted_results = []
        for item in result["results"][:max_results]:
            title = item.get("title", "No title")
            url = item.get("url", "No URL")
            content = item.get("content", "")
            formatted_results.append(f"Title: {title}\nURL: {url}\nSummary: {content}\n")
        
        return "\n---\n".join(formatted_results) if formatted_results else "No results found"
    
    except Exception as e:
        return f"Error during search: {str(e)}"

if __name__ == "__main__":
    # Run the server using stdio transport (default for MCP)
    mcp.run()