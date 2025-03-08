from mcp.server.fastmcp import FastMCP
from mcp.server.websocket import WebsocketServerTransport
import os
import logging
from dotenv import load_dotenv
from .tools import CodeAnalyzerTool, CodeFormatterTool, CodeDocumenterTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create FastMCP application instance
app = FastMCP(
    name="Cursor MCP Server",
    instructions="A custom MCP server for Cursor with code analysis, formatting, and documentation tools."
)

# Register tools
@app.tool(name="analyze_code", description="Analyzes Python code for potential issues and improvements.")
def analyze_code(file_path: str) -> str:
    logger.info(f"Analyzing code file: {file_path}")
    analyzer = CodeAnalyzerTool()
    return analyzer.analyze(file_path)

@app.tool(name="format_code", description="Formats Python code using black and isort.")
def format_code(file_path: str, line_length: int = 88, use_black: bool = True, use_isort: bool = True) -> str:
    logger.info(f"Formatting code file: {file_path}")
    formatter = CodeFormatterTool()
    return formatter.format(file_path, line_length, use_black, use_isort)

@app.tool(name="document_code", description="Generates or updates Python code documentation.")
def document_code(file_path: str, doc_style: str = "google", update_existing: bool = False) -> str:
    logger.info(f"Documenting code file: {file_path}")
    documenter = CodeDocumenterTool()
    return documenter.document(file_path, doc_style, update_existing)

# Configure server settings
app.settings.host = os.getenv("HOST", "0.0.0.0")
app.settings.port = int(os.getenv("PORT", "8000"))
app.settings.log_level = os.getenv("LOG_LEVEL", "INFO")

def start_server():
    """Start the MCP server with WebSocket transport."""
    try:
        logger.info(f"Starting server on {app.settings.host}:{app.settings.port}")
        transport = WebsocketServerTransport(
            host=app.settings.host,
            port=app.settings.port,
            health_check_path="/health"
        )
        logger.info("WebSocket transport configured")
        app.run(transport=transport)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise

if __name__ == "__main__":
    start_server() 