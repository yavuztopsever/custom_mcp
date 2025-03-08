"""
Standard IO handler for the MCP server.
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any, TextIO

from .tool_manager import ToolManager

logger = logging.getLogger(__name__)

class StdioHandler:
    def __init__(self, tool_manager: ToolManager, input_stream: TextIO = sys.stdin, output_stream: TextIO = sys.stdout):
        self.tool_manager = tool_manager
        self.input_stream = input_stream
        self.output_stream = output_stream
        
    async def _read_message(self) -> Dict[str, Any]:
        """Read a JSON message from stdin."""
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, self.input_stream.readline)
            if not line:
                raise EOFError("End of input stream")
            return json.loads(line)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON message: {e}")
            return {"type": "error", "message": "Invalid JSON format"}
            
    async def _write_message(self, message: Dict[str, Any]) -> None:
        """Write a JSON message to stdout."""
        try:
            json_str = json.dumps(message)
            print(json_str, file=self.output_stream, flush=True)
        except Exception as e:
            logger.error(f"Error writing message: {e}")
            
    async def _handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming messages."""
        message_type = message.get("type")
        
        if message_type == "command":
            command = message.get("command")
            args = message.get("args", {})
            return await self.tool_manager.execute_command(command, args)
        elif message_type == "query":
            query = message.get("query")
            if query == "get_available_tools":
                return {
                    "status": "success",
                    "data": {
                        "tools": self.tool_manager.get_available_tools()
                    }
                }
        
        return {
            "status": "error",
            "message": f"Unknown message type: {message_type}"
        }
            
    async def run(self) -> None:
        """Run the stdio handler."""
        logger.info("Starting stdio handler")
        try:
            while True:
                message = await self._read_message()
                response = await self._handle_message(message)
                await self._write_message(response)
        except EOFError:
            logger.info("Input stream closed")
        except Exception as e:
            logger.error(f"Error in stdio handler: {e}")
            await self._write_message({
                "status": "error",
                "message": str(e)
            }) 