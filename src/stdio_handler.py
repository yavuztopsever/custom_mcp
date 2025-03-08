"""
Standard IO handler for the MCP server with JSON-RPC 2.0 support.
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any, TextIO, Optional, Union

from .tool_manager import ToolManager

logger = logging.getLogger(__name__)

class JsonRpcError(Exception):
    """JSON-RPC 2.0 Error"""
    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)

class StdioHandler:
    # JSON-RPC 2.0 error codes
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

    def __init__(self, tool_manager: ToolManager, input_stream: TextIO = sys.stdin, output_stream: TextIO = sys.stdout):
        self.tool_manager = tool_manager
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.initialized = False
        
    def _create_response(self, request_id: Optional[Union[str, int]], result: Any = None, error: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a JSON-RPC 2.0 response."""
        response = {
            "jsonrpc": "2.0",
            "id": request_id
        }
        if error is not None:
            response["error"] = error
        else:
            response["result"] = result
        return response

    def _create_error(self, code: int, message: str, data: Any = None) -> Dict[str, Any]:
        """Create a JSON-RPC 2.0 error object."""
        error = {
            "code": code,
            "message": message
        }
        if data is not None:
            error["data"] = data
        return error

    async def _read_message(self) -> Dict[str, Any]:
        """Read a JSON-RPC 2.0 message from stdin."""
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, self.input_stream.readline)
            if not line:
                raise EOFError("End of input stream")
            return json.loads(line)
        except json.JSONDecodeError as e:
            raise JsonRpcError(self.PARSE_ERROR, "Parse error", str(e))
            
    async def _write_message(self, message: Dict[str, Any]) -> None:
        """Write a JSON-RPC 2.0 message to stdout."""
        try:
            json_str = json.dumps(message)
            print(json_str, file=self.output_stream, flush=True)
        except Exception as e:
            logger.error(f"Error writing message: {e}")

    async def _handle_initialize(self, params: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """Handle the initialize request."""
        self.initialized = True
        capabilities = {
            "version": "1.0.0",
            "tools": self.tool_manager.get_available_tools()
        }
        return self._create_response(request_id, result=capabilities)

    async def _handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming JSON-RPC 2.0 messages."""
        # Validate JSON-RPC 2.0 message
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
            return self._create_response(None, error=self._create_error(
                self.INVALID_REQUEST, "Invalid Request: Not a valid JSON-RPC 2.0 request"
            ))

        request_id = message.get("id")
        method = message.get("method")
        params = message.get("params", {})

        try:
            # Handle initialization
            if method == "initialize":
                return await self._handle_initialize(params, request_id)

            # Check if initialized
            if not self.initialized and method != "initialize":
                return self._create_response(request_id, error=self._create_error(
                    self.INVALID_REQUEST, "Server not initialized"
                ))

            # Handle other methods
            if method == "execute":
                command = params.get("command")
                args = params.get("args", {})
                result = await self.tool_manager.execute_command(command, args)
                return self._create_response(request_id, result=result)
            elif method == "get_tools":
                tools = self.tool_manager.get_available_tools()
                return self._create_response(request_id, result={"tools": tools})
            else:
                return self._create_response(request_id, error=self._create_error(
                    self.METHOD_NOT_FOUND, f"Method not found: {method}"
                ))

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return self._create_response(request_id, error=self._create_error(
                self.INTERNAL_ERROR, "Internal error", str(e)
            ))
            
    async def run(self) -> None:
        """Run the stdio handler."""
        logger.info("Starting stdio handler with JSON-RPC 2.0 support")
        try:
            while True:
                try:
                    message = await self._read_message()
                    response = await self._handle_message(message)
                    await self._write_message(response)
                except JsonRpcError as e:
                    await self._write_message(self._create_response(
                        message.get("id") if isinstance(message, dict) else None,
                        error=self._create_error(e.code, e.message, e.data)
                    ))
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    await self._write_message(self._create_response(
                        message.get("id") if isinstance(message, dict) else None,
                        error=self._create_error(self.INTERNAL_ERROR, "Internal error", str(e))
                    ))
        except EOFError:
            logger.info("Input stream closed") 