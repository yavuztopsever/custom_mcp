"""
Tool manager for Sequential Thinking MCP server.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ToolManager:
    def __init__(self):
        self.tools = {
            "mcp__sequentialthinking": {
                "name": "mcp__sequentialthinking",
                "description": "Sequential thinking tool for complex problem solving",
                "parameters": {
                    "thought": {"type": "string", "description": "Current thinking step"},
                    "nextThoughtNeeded": {"type": "boolean", "description": "Whether another thought is needed"},
                    "thoughtNumber": {"type": "integer", "description": "Current thought number"},
                    "totalThoughts": {"type": "integer", "description": "Total thoughts needed"},
                    "isRevision": {"type": "boolean", "description": "Whether this revises previous thinking"},
                    "revisesThought": {"type": "integer", "description": "Which thought is being reconsidered"},
                    "branchFromThought": {"type": "integer", "description": "Branching point thought number"},
                    "branchId": {"type": "string", "description": "Branch identifier"},
                    "needsMoreThoughts": {"type": "boolean", "description": "If more thoughts are needed"}
                },
                "required": ["thought", "nextThoughtNeeded", "thoughtNumber", "totalThoughts"]
            }
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """Get server capabilities."""
        return {
            "sequential_thinking": True,
            "tools": list(self.tools.keys())
        }

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools with their specifications."""
        return list(self.tools.values())

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given parameters."""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        tool = self.tools[tool_name]
        
        # Validate required parameters
        missing_params = [param for param in tool["required"] if param not in params]
        if missing_params:
            raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")

        # For sequential thinking tool, just echo back the parameters
        # as it's handled by the AI model
        if tool_name == "mcp__sequentialthinking":
            return params

        raise ValueError(f"Tool execution not implemented: {tool_name}") 