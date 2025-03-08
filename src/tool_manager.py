"""
Tool manager for integrating MCP tools with the WebSocket server.
"""

import importlib
import inspect
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Type

from mcp_tools.core.base_tool import BaseTool
from mcp_tools.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class ToolManager:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.tools: Dict[str, BaseTool] = {}
        self._load_tools()

    def _load_tools(self) -> None:
        """Load all available tools from the mcp_tools/tools directory."""
        tools_dir = Path(__file__).parent.parent / "mcp_tools" / "tools"
        if not tools_dir.exists():
            logger.warning(f"Tools directory not found: {tools_dir}")
            return

        for file in tools_dir.glob("*.py"):
            if file.name.startswith("__"):
                continue

            try:
                # Import the module
                module_path = f"mcp_tools.tools.{file.stem}"
                module = importlib.import_module(module_path)

                # Find tool classes (subclasses of BaseTool)
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, BaseTool) and 
                        obj != BaseTool):
                        tool = obj(config_manager=self.config_manager)
                        self.tools[tool.name] = tool
                        logger.info(f"Loaded tool: {tool.name}")

            except Exception as e:
                logger.error(f"Error loading tool from {file}: {e}")

    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return list(self.tools.keys())

    async def execute_command(self, command: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool command."""
        if command not in self.tools:
            return {
                "status": "error",
                "message": f"Unknown tool: {command}"
            }

        try:
            tool = self.tools[command]
            result = tool.run(**args)
            return {
                "status": "success",
                "data": result
            }
        except Exception as e:
            logger.error(f"Error executing tool {command}: {e}")
            return {
                "status": "error",
                "message": str(e)
            } 