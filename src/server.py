"""
Sequential Thinking MCP Server implementation with JSON-RPC and SSE support.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any, Optional

from .tool_manager import ToolManager

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class SequentialThinkingServer:
    def __init__(self, tool_manager: Optional[ToolManager] = None):
        self.tool_manager = tool_manager or ToolManager()
        self.protocol_version = "2024-11-05"
        self.server_info = {
            "name": "sequential-thinking-server",
            "version": "0.2.0"
        }

    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request."""
        return {
            "protocolVersion": self.protocol_version,
            "capabilities": {
                "tools": self.tool_manager.get_capabilities()
            },
            "serverInfo": self.server_info
        }

    async def handle_tools_list(self) -> Dict[str, Any]:
        """Handle tools/list request."""
        return {
            "tools": self.tool_manager.get_available_tools()
        }

    async def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle JSON-RPC request."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        if method == "initialize":
            result = await self.handle_initialize(params)
        elif method == "notifications/initialized":
            return None  # No response needed for notifications
        elif method == "tools/list":
            result = await self.handle_tools_list()
        else:
            result = {
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

        response = {"jsonrpc": "2.0"}
        if request_id is not None:
            response["id"] = request_id
        if "error" in result:
            response["error"] = result["error"]
        else:
            response["result"] = result

        return response

    async def process_stdio(self):
        """Process JSON-RPC messages via stdio."""
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break

                try:
                    request = json.loads(line)
                    response = await self.handle_request(request)
                    if response:
                        print(json.dumps(response), flush=True)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON received")
                    print(json.dumps({
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }), flush=True)

            except Exception as e:
                logger.error(f"Error processing request: {e}")
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": "Internal error"
                    }
                }), flush=True)

    def start(self):
        """Start the Sequential Thinking MCP Server."""
        logger.info("Sequential Thinking MCP Server running on stdio")
        asyncio.run(self.process_stdio())

def main():
    """Main entry point."""
    server = SequentialThinkingServer()
    server.start() 