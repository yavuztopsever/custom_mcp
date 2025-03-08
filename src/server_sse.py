import asyncio
import logging
import sys
import traceback
from mcp.server.fastmcp import FastMCP
from mcp.server.websocket import WebsocketServerTransport
from mcp.server.transport import Transport
import os
from dotenv import load_dotenv
from .tools import CodeAnalyzerTool, CodeFormatterTool, CodeDocumenterTool

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more verbose output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout  # Ensure logs go to stdout
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class CustomWebsocketTransport(WebsocketServerTransport):
    """Custom WebSocket transport with additional logging."""
    
    def __init__(self, host: str, port: int, health_check_path: str = "/health"):
        super().__init__(host=host, port=port, health_check_path=health_check_path)
        self.logger = logging.getLogger(__name__ + ".transport")
        self.logger.setLevel(logging.DEBUG)
    
    async def start(self) -> None:
        """Start the WebSocket server with additional logging."""
        self.logger.info("Starting WebSocket transport...")
        try:
            await super().start()
            self.logger.info("WebSocket transport started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start WebSocket transport: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    async def handle_connection(self, websocket) -> None:
        """Handle WebSocket connection with additional logging."""
        self.logger.info("New WebSocket connection established")
        try:
            await super().handle_connection(websocket)
        except Exception as e:
            self.logger.error(f"Error handling WebSocket connection: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise
        finally:
            self.logger.info("WebSocket connection closed")

# Create FastMCP application instance
app = FastMCP(
    name="Cursor MCP Server",
    instructions="A custom MCP server for Cursor with code analysis, formatting, and documentation tools.",
    version="1.0.0"
)

# Register tools
@app.tool(name="analyze_code", description="Analyzes Python code for potential issues and improvements.")
async def analyze_code(file_path: str) -> str:
    logger.info(f"Analyzing code file: {file_path}")
    try:
        analyzer = CodeAnalyzerTool()
        return analyzer.analyze(file_path)
    except Exception as e:
        logger.error(f"Error analyzing code: {str(e)}")
        logger.error(traceback.format_exc())
        raise

@app.tool(name="format_code", description="Formats Python code using black and isort.")
async def format_code(file_path: str, line_length: int = 88, use_black: bool = True, use_isort: bool = True) -> str:
    logger.info(f"Formatting code file: {file_path}")
    try:
        formatter = CodeFormatterTool()
        return formatter.format(file_path, line_length, use_black, use_isort)
    except Exception as e:
        logger.error(f"Error formatting code: {str(e)}")
        logger.error(traceback.format_exc())
        raise

@app.tool(name="document_code", description="Generates or updates Python code documentation.")
async def document_code(file_path: str, doc_style: str = "google", update_existing: bool = False) -> str:
    logger.info(f"Documenting code file: {file_path}")
    try:
        documenter = CodeDocumenterTool()
        return documenter.document(file_path, doc_style, update_existing)
    except Exception as e:
        logger.error(f"Error documenting code: {str(e)}")
        logger.error(traceback.format_exc())
        raise

async def initialize_server() -> None:
    """Initialize the MCP server with detailed logging."""
    logger.info("Initializing server...")
    try:
        await app.initialize()
        logger.info("Server initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize server: {str(e)}")
        logger.error(traceback.format_exc())
        raise

async def create_transport() -> Transport:
    """Create and configure the WebSocket transport."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Creating WebSocket transport on {host}:{port}")
    
    try:
        transport = CustomWebsocketTransport(
            host=host,
            port=port,
            health_check_path="/health"
        )
        logger.info("WebSocket transport created successfully")
        return transport
    except Exception as e:
        logger.error(f"Failed to create transport: {str(e)}")
        logger.error(traceback.format_exc())
        raise

async def start_server():
    """Start the MCP server with detailed error handling and logging."""
    try:
        # Initialize server first
        await initialize_server()
        
        # Create and configure transport
        transport = await create_transport()
        
        # Start the server
        logger.info("Starting server...")
        await app.run(transport=transport)
        logger.info("Server started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def main():
    """Main entry point with comprehensive error handling."""
    try:
        logger.info("Starting MCP server process...")
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal server error: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 