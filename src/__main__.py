"""
Main entry point for the MCP Server.
"""

import asyncio
import logging
import os
import sys

from .server import MCPServer
from .tool_manager import ToolManager
from .stdio_handler import StdioHandler

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point."""
    # Create tool manager
    tool_manager = ToolManager()
    
    # Determine server mode
    mode = os.getenv("MCP_SERVER_MODE", "websocket").lower()
    
    if mode == "stdio":
        # Run in stdio mode for Smithery deployment
        handler = StdioHandler(tool_manager)
        asyncio.run(handler.run())
    else:
        # Run in WebSocket mode for local development
        server = MCPServer(tool_manager)
        asyncio.run(server.start())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1) 