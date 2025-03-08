from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
import os
from dotenv import load_dotenv
from .tools import CodeAnalyzerTool, CodeFormatterTool, CodeDocumenterTool
from starlette.responses import JSONResponse

# Load environment variables
load_dotenv()

# Create FastMCP application instance
app = FastMCP(
    name="Cursor MCP Server",
    instructions="A custom MCP server for Cursor with code analysis, formatting, and documentation tools."
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return JSONResponse({"status": "healthy"})

# Register tools
@app.tool(name="analyze_code", description="Analyzes Python code for potential issues and improvements.")
def analyze_code(file_path: str) -> str:
    analyzer = CodeAnalyzerTool()
    return analyzer.analyze(file_path)

@app.tool(name="format_code", description="Formats Python code using black and isort.")
def format_code(file_path: str, line_length: int = 88, use_black: bool = True, use_isort: bool = True) -> str:
    formatter = CodeFormatterTool()
    return formatter.format(file_path, line_length, use_black, use_isort)

@app.tool(name="document_code", description="Generates or updates Python code documentation.")
def document_code(file_path: str, doc_style: str = "google", update_existing: bool = False) -> str:
    documenter = CodeDocumenterTool()
    return documenter.document(file_path, doc_style, update_existing)

# Configure server settings
app.settings.host = os.getenv("HOST", "0.0.0.0")  # Changed to 0.0.0.0 for container compatibility
app.settings.port = int(os.getenv("PORT", "8000"))
app.settings.log_level = os.getenv("LOG_LEVEL", "INFO")

# For local development
if __name__ == "__main__":
    app.run(transport="sse") 