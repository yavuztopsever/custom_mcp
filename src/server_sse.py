import asyncio
import logging
import sys
import traceback
from fastapi import FastAPI, WebSocket
from mcp.server.fastmcp import FastMCP
from mcp.server.transport import Transport
import os
from dotenv import load_dotenv
from .tools import CodeAnalyzerTool, CodeFormatterTool, CodeDocumenterTool

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create FastAPI application
fastapi_app = FastAPI(
    title="Cursor MCP Server",
    description="Custom MCP server with code analysis, formatting, and documentation tools.",
    version="1.0.0"
)

# Create FastMCP application instance
mcp_app = FastMCP(
    name="Cursor MCP Server",
    instructions="A custom MCP server with code analysis, formatting, and documentation tools.",
    version="1.0.0"
)

class MCPWebSocketTransport(Transport):
    """Custom WebSocket transport implementation."""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.logger = logging.getLogger(__name__ + ".transport")
        self.logger.setLevel(logging.DEBUG)
        self.setup_routes()
    
    def setup_routes(self):
        """Set up FastAPI routes."""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy"}
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for MCP communication."""
            self.logger.info("New WebSocket connection request")
            try:
                await websocket.accept()
                self.logger.info("WebSocket connection accepted")
                
                while True:
                    try:
                        # Receive message
                        message = await websocket.receive_json()
                        self.logger.debug(f"Received message: {message}")
                        
                        # Process message through MCP
                        response = await mcp_app.handle_message(message)
                        self.logger.debug(f"Sending response: {response}")
                        
                        # Send response
                        await websocket.send_json(response)
                    except Exception as e:
                        self.logger.error(f"Error processing message: {str(e)}")
                        self.logger.error(traceback.format_exc())
                        await websocket.send_json({
                            "error": str(e),
                            "traceback": traceback.format_exc()
                        })
            except Exception as e:
                self.logger.error(f"WebSocket connection error: {str(e)}")
                self.logger.error(traceback.format_exc())
            finally:
                self.logger.info("WebSocket connection closed")
    
    async def start(self):
        """Start the transport (no-op as FastAPI handles this)."""
        self.logger.info("Transport ready")
    
    async def stop(self):
        """Stop the transport (no-op as FastAPI handles this)."""
        self.logger.info("Transport stopped")

# Register tools
@mcp_app.tool(name="analyze_code", description="Analyzes Python code for potential issues and improvements.")
async def analyze_code(file_path: str) -> str:
    logger.info(f"Analyzing code file: {file_path}")
    try:
        analyzer = CodeAnalyzerTool()
        return analyzer.analyze(file_path)
    except Exception as e:
        logger.error(f"Error analyzing code: {str(e)}")
        logger.error(traceback.format_exc())
        raise

@mcp_app.tool(name="format_code", description="Formats Python code using black and isort.")
async def format_code(file_path: str, line_length: int = 88, use_black: bool = True, use_isort: bool = True) -> str:
    logger.info(f"Formatting code file: {file_path}")
    try:
        formatter = CodeFormatterTool()
        return formatter.format(file_path, line_length, use_black, use_isort)
    except Exception as e:
        logger.error(f"Error formatting code: {str(e)}")
        logger.error(traceback.format_exc())
        raise

@mcp_app.tool(name="document_code", description="Generates or updates Python code documentation.")
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
    """Initialize the MCP server."""
    logger.info("Initializing MCP server...")
    try:
        await mcp_app.initialize()
        logger.info("MCP server initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MCP server: {str(e)}")
        logger.error(traceback.format_exc())
        raise

async def setup_server():
    """Set up the server with all components."""
    try:
        # Initialize MCP server
        await initialize_server()
        
        # Create and configure transport
        transport = MCPWebSocketTransport(fastapi_app)
        await transport.start()
        
        # Connect MCP app with transport
        await mcp_app.run(transport=transport)
        
        logger.info("Server setup completed successfully")
    except Exception as e:
        logger.error(f"Failed to set up server: {str(e)}")
        logger.error(traceback.format_exc())
        raise

# Startup event handler
@fastapi_app.on_event("startup")
async def startup_event():
    """Handle FastAPI startup."""
    logger.info("Starting server setup...")
    await setup_server()
    logger.info("Server started successfully")

# Make the FastAPI app available for uvicorn
app = fastapi_app 