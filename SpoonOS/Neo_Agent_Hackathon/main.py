import asyncio
from custom_agent import MyAgent
from spoon_ai.chat import ChatBot



async def main():
    agent = MyAgent(llm=ChatBot())
    response = await agent.ask_tool("Search for the date of Messi's 1000th goal", tool_name="tavily-search")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())