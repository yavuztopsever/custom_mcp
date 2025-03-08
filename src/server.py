"""
MCP Server implementation with WebSocket support.
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional

import websockets
from websockets.server import WebSocketServerProtocol
from aiohttp import web

from .tool_manager import ToolManager

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class MCPServer:
    def __init__(self, tool_manager: Optional[ToolManager] = None):
        self.host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
        self.port = int(os.getenv("MCP_SERVER_PORT", "25565"))
        self.auth_token = os.getenv("MCP_AUTH_TOKEN")
        self.tool_manager = tool_manager or ToolManager()
        self.app = web.Application()
        self.app.router.add_get("/health", self.health_check)
        
    async def health_check(self, request):
        """Health check endpoint."""
        return web.Response(text="OK", status=200)
        
    async def handle_client(self, websocket: WebSocketServerProtocol):
        """Handle client connection and messages."""
        try:
            # Handle authentication
            auth_msg = await websocket.recv()
            auth_data = json.loads(auth_msg)
            
            if not self._authenticate(auth_data):
                await websocket.send(json.dumps({
                    "status": "error",
                    "message": "Authentication failed"
                }))
                return
                
            await websocket.send(json.dumps({
                "status": "success",
                "message": "Authentication successful"
            }))
            
            # Handle commands
            async for message in websocket:
                try:
                    data = json.loads(message)
                    response = await self._handle_command(data)
                    await websocket.send(json.dumps(response))
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "status": "error",
                        "message": "Invalid JSON format"
                    }))
                except Exception as e:
                    logger.error(f"Error handling command: {e}")
                    await websocket.send(json.dumps({
                        "status": "error",
                        "message": str(e)
                    }))
                    
        except Exception as e:
            logger.error(f"Connection error: {e}")
    
    def _authenticate(self, auth_data: Dict[str, Any]) -> bool:
        """Validate client authentication."""
        return (
            auth_data.get("type") == "auth" and
            auth_data.get("token") == self.auth_token
        )
    
    async def _handle_command(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming commands."""
        command_type = data.get("type")
        if command_type == "command":
            command = data.get("command")
            args = data.get("args", {})
            return await self.tool_manager.execute_command(command, args)
        elif command_type == "query":
            query = data.get("query")
            if query == "get_available_tools":
                return {
                    "status": "success",
                    "data": {
                        "tools": self.tool_manager.get_available_tools()
                    }
                }
        return {
            "status": "error",
            "message": f"Unknown command type: {command_type}"
        }
    
    async def start(self):
        """Start the WebSocket server and HTTP server."""
        logger.info(f"Starting MCP server on {self.host}:{self.port}")
        
        # Start HTTP server for health checks
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port + 1)  # Health check on port+1
        await site.start()
        logger.info(f"Health check endpoint available at http://{self.host}:{self.port + 1}/health")
        
        # Start WebSocket server
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # run forever

def main():
    """Main entry point."""
    server = MCPServer()
    asyncio.run(server.start()) 