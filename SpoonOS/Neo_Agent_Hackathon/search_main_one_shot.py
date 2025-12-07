import os
import sys
import asyncio
import logging
from typing import Dict, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../spoon-toolkit')))

from spoon_ai.agents.spoon_react_mcp import SpoonReactMCP
from spoon_ai.tools.mcp_tool import MCPTool
from spoon_ai.tools.tool_manager import ToolManager
from spoon_ai.chat import ChatBot

logging.basicConfig(level=logging.INFO)

class SpoonResearchAssistantAgent(SpoonReactMCP):
    name: str = "SpoonResearchAssistantAgent"
    system_prompt: str = (
        "You are a research assistant helping a scientist design a survey "
        "about LLM usage among adults aged 60+. Ask clarifying questions and "
        "help shape the survey structure, demographic definitions, and question design."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.avaliable_tools = ToolManager([])

    async def initialize(self):
        logging.info("Initializing agent and loading tools...")
        tavily_key = os.getenv("TAVILY_API_KEY", "")

        if not tavily_key or "your-tavily-api-key-here" in tavily_key:
            raise ValueError("TAVILY_API_KEY is not set or is a placeholder.")

        tavily_tool = MCPTool(
            name="tavily-search",
            description="Performs a web search using the Tavily API.",
            mcp_config={
                "command": "npx",
                "args": ["--yes", "tavily-mcp"],
                "env": {"TAVILY_API_KEY": tavily_key}
            }
        )

        self.avaliable_tools = ToolManager([tavily_tool])
        logging.info(f"Available tools: {list(self.avaliable_tools.tool_map.keys())}")


# ---------------------------------------------------------
# One-shot conversation simulation
# ---------------------------------------------------------

async def simulate_conversation(agent: SpoonResearchAssistantAgent):

    conversation_prompt = """
The following is a simulated conversation. Generate BOTH the assistant turns and scientist turns.

Start:

🧑‍🔬 Scientist: Hello, I need your help defining a new research survey. We're studying how adults aged 60+ adopt and use modern AI systems like LLMs.

🤖 Assistant: (respond with clarifying questions about demographic scope, technology familiarity, and survey goals)

🧑‍🔬 Scientist: Great. I want the survey to understand motivations, barriers, and patterns of LLM use. What demographics should we capture?

🤖 Assistant: (provide specific demographic categories relevant to older adult technology adoption)

🧑‍🔬 Scientist: Good. Now help me draft 5–7 high-quality questions assessing usage behavior.

🤖 Assistant: (provide 5–7 well-designed survey questions tailored to adults 60+)
"""

    # 🔥 Only ONE LLM call here
    output = await agent.run(conversation_prompt)

    print("\n=== ONE-SHOT SIMULATED CONVERSATION ===\n")
    print(output)
    print("\n======================================\n")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

async def main():
    print("--- SpoonOS Research Assistant Agent Demo (One-Shot Mode) ---")
    agent = SpoonResearchAssistantAgent(llm=ChatBot(llm_provider="gemini"))
    print("Agent instance created.")
    await agent.initialize()

    await simulate_conversation(agent)


if __name__ == "__main__":
    asyncio.run(main())
