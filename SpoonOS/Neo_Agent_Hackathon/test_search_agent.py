import asyncio
from search_agent import SearchAgent, TavilySearchTool
from spoon_ai.chat import ChatBot

async def test_tool_directly():
    """Test the Tavily search tool directly."""
    print("=" * 80)
    print("Testing Tavily search tool directly...")
    print("=" * 80)
    
    tool = TavilySearchTool()
    try:
        result = await tool.execute("Lionel Messi career goals", max_results=3)
        print("\nSearch Results:")
        print("-" * 80)
        print(result)
        print("-" * 80)
    finally:
        await tool.cleanup()

async def test_with_agent():
    """Test using the agent with the search tool."""
    print("\n" + "=" * 80)
    print("Testing with SearchAgent...")
    print("=" * 80)
    
    agent = SearchAgent(llm=ChatBot())
    
    # Ask the agent a question that requires search
    response = await agent.run("When did Lionel Messi score his 1000th goal? Use the search tool to find this information.")
    print("\nAgent Response:")
    print("-" * 80)
    print(response)
    print("-" * 80)

async def main():
    # Test the tool directly first
    #await test_tool_directly()
    
    # Then test with the agent
    print("\n\nReady to test with agent? Uncomment the line below in the code.")
    await test_with_agent()

if __name__ == "__main__":
    asyncio.run(main())