"""
A tiny LLM-free "agent" that still uses SpoonOS components.

We avoid ToolCallAgent and ChatBot entirely to prevent API key checks.

This agent:
- Receives a fixed "plan"
- Executes tools via SpoonOS ToolManager

This is the simplest keyless way to say:
"We used SpoonOS tools + orchestration."
"""

from typing import Any, Dict, List

from spoon_ai.tools.tool_manager import ToolManager


class SimpleSpoonAgent:
    """
    LLM-free, deterministic agent.

    It is "agentic" in the minimal sense:
    - it has a plan (list of steps)
    - it selects tools by name
    - it executes them and collects results
    """

    def __init__(self, tools: List[Any]):
        # ToolManager expects real tool objects with .name
        self.tools = ToolManager(tools)

    async def run_plan(self, plan: List[Dict[str, Any]]) -> List[str]:
        """
        Execute a list of tool calls.

        Each plan step looks like:
            {
              "tool": "run_python_file",
              "args": { "relative_path": "hello.py", "args": ["--name", "Neo"] }
            }
        """
        results: List[str] = []

        for step in plan:
            tool_name = step["tool"]
            tool_args = step.get("args", {})

            # Retrieve the tool instance from the manager's map
            tool = self.tools.tool_map.get(tool_name)
            if tool is None:
                results.append(f"Error: Tool not found: {tool_name}")
                continue

            # Execute the SpoonOS tool
            out = await tool.execute(**tool_args)
            results.append(out)

        return results
