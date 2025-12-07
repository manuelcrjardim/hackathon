"""
A SpoonOS-native tool that runs Python files from an allowlisted directory.

This file DOES use SpoonOS:
- It subclasses BaseTool from spoon_ai
- It uses Pydantic-compatible private state

This file does NOT use any LLM or API keys.
"""

import os
import sys
import subprocess
from typing import List, Optional

# SpoonOS BaseTool is a Pydantic-based tool base.
# The import path below matches SpoonOS SDK examples and common repo layout.
from spoon_ai.tools.base import BaseTool
from pydantic import PrivateAttr


class RunPythonFileTool(BaseTool):
    """
    A minimal SpoonOS tool.

    The only "agentic" assumption:
    - The tool has a stable name/description/parameters
    - execute() does the real action
    """

    # Tool registry name
    name: str = "run_python_file"

    # Human-readable description for whatever orchestrates tools
    description: str = "Run a Python file from an allowlisted local directory."

    # Tool input schema (kept simple)
    parameters: dict = {
        "type": "object",
        "properties": {
            "relative_path": {
                "type": "string",
                "description": "Path to a .py file relative to the allowed root."
            },
            "args": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional command-line args for the script."
            },
            "timeout_sec": {
                "type": "integer",
                "default": 20,
                "description": "Max seconds to allow the script to run."
            },
        },
        "required": ["relative_path"],
    }

    # Pydantic private attribute: not part of the public schema
    _allowed_root: str = PrivateAttr()

    def __init__(self, allowed_root: str, **kwargs):
        # Let BaseTool/Pydantic initialize first
        super().__init__(**kwargs)

        # Store our internal safety boundary
        self._allowed_root = os.path.abspath(allowed_root)

    async def execute(
        self,
        relative_path: str,
        args: Optional[List[str]] = None,
        timeout_sec: int = 20,
    ) -> str:
        """
        Run a Python script safely and return a concise report.

        We keep this async to match SpoonOS tool conventions.
        """
        args = args or []

        # Resolve the target path inside the allowlisted root
        target_path = os.path.abspath(os.path.join(self._allowed_root, relative_path))

        # Block directory traversal attempts
        if not target_path.startswith(self._allowed_root + os.sep):
            return "Error: Path is outside the allowed scripts directory."

        # Only permit .py files
        if not target_path.endswith(".py"):
            return "Error: Only .py files are allowed."

        # Ensure file exists
        if not os.path.isfile(target_path):
            return f"Error: File not found: {relative_path}"

        # Use the current interpreter (your conda env)
        cmd = [sys.executable, target_path, *args]

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
            )
        except subprocess.TimeoutExpired:
            return f"Error: Script timed out after {timeout_sec} seconds."

        stdout = (proc.stdout or "").strip()
        stderr = (proc.stderr or "").strip()

        return "\n".join([
            f"Return code: {proc.returncode}",
            "STDOUT:",
            stdout if stdout else "(empty)",
            "STDERR:",
            stderr if stderr else "(empty)",
        ])
