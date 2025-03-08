"""
Test client for the MCP WebSocket server.
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any

import websockets
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_server(
    uri: str = os.getenv("MCP_SERVER_URL", "ws://localhost:25565"),
    auth_token: str = os.getenv("MCP_AUTH_TOKEN", "1234")
):
    """Test the MCP server functionality."""
    logger.info(f"Connecting to server at {uri}")
    
    async with websockets.connect(uri) as websocket:
        # Test authentication
        logger.info("Testing authentication...")
        auth_message = {
            "type": "auth",
            "token": auth_token
        }
        await websocket.send(json.dumps(auth_message))
        response = await websocket.recv()
        logger.info(f"Auth response: {response}")

        # Test getting available tools
        logger.info("\nTesting tool listing...")
        tools_message = {
            "type": "query",
            "query": "get_available_tools"
        }
        await websocket.send(json.dumps(tools_message))
        response = await websocket.recv()
        logger.info(f"Tools response: {response}")

        # Test clean_code tool
        logger.info("\nTesting clean_code tool...")
        clean_message = {
            "type": "command",
            "command": "clean_code",
            "args": {
                "target_dir": "src"
            }
        }
        await websocket.send(json.dumps(clean_message))
        response = await websocket.recv()
        logger.info(f"Clean code response: {response}")

if __name__ == "__main__":
    asyncio.run(test_server()) 