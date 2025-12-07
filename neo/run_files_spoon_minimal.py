"""
LLM-free SpoonOS agent runner that executes a specific Python file
inside an allowlisted directory.

Goal:
- Run mainTest.py located in:
  /home/islaspabl/Documents/Hackathons/Agentic_Hackathon_with_SpoonOS_and_Neo/SpoonOSAgent/neofs-dev-env

This uses SpoonOS:
- Custom BaseTool (RunPythonFileTool)
- ToolManager
- SimpleSpoonAgent

This does NOT use any API keys or LLM providers.
"""

import asyncio
import os

from run_python_tool_spoon import RunPythonFileTool
from simple_spoon_agent import SimpleSpoonAgent


async def main():
    # ---------------------------------------------------------------------
    # 1) Allowlist the exact directory that contains mainTest.py
    # ---------------------------------------------------------------------
    allowed_root = "/home/islaspabl/Documents/Hackathons/Agentic_Hackathon_with_SpoonOS_and_Neo/SpoonOSAgent/neofs-dev-env"

    # Optional sanity check so failures are obvious during demos
    if not os.path.isdir(allowed_root):
        raise RuntimeError(f"Allowed root directory not found: {allowed_root}")

    # ---------------------------------------------------------------------
    # 2) Instantiate the SpoonOS tool with this allowlisted root
    # ---------------------------------------------------------------------
    run_tool = RunPythonFileTool(allowed_root=allowed_root)

    # ---------------------------------------------------------------------
    # 3) Create the LLM-free agent that uses SpoonOS ToolManager
    # ---------------------------------------------------------------------
    agent = SimpleSpoonAgent(tools=[run_tool])

    # ---------------------------------------------------------------------
    # 4) Define a simple deterministic plan:
    #    run mainTest.py in that directory
    # ---------------------------------------------------------------------
    plan = [
        {
            "tool": "run_python_file",
            "args": {
                "relative_path": "MainTest.py",  # relative to allowed_root
                "args": [],                      # add CLI args here if needed
                "timeout_sec": 120,              # bump if your test spins up services
            },
        }
    ]

    # ---------------------------------------------------------------------
    # 5) Execute and print results
    # ---------------------------------------------------------------------
    results = await agent.run_plan(plan)
    for i, r in enumerate(results, start=1):
        print(f"\n--- Step {i} ---")
        print(r)


if __name__ == "__main__":
    asyncio.run(main())
