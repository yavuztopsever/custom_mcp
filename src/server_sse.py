from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
import os
from dotenv import load_dotenv
from .tools import CodeAnalyzerTool, CodeFormatterTool, CodeDocumenterTool

# Load environment variables
load_dotenv()

class CursorMCPSSEServer:
    def __init__(self):
        self.app = FastMCP(
            name="Cursor MCP Server",
            instructions="A custom MCP server for Cursor with code analysis, formatting, and documentation tools."
        )
        self._setup_tools()

    def _setup_tools(self):
        # Register tools using the FastMCP tool decorator
        @self.app.tool(name="analyze_code", description="Analyzes Python code for potential issues and improvements.")
        def analyze_code(file_path: str) -> str:
            analyzer = CodeAnalyzerTool()
            return analyzer.analyze(file_path)

        @self.app.tool(name="format_code", description="Formats Python code using black and isort.")
        def format_code(file_path: str, line_length: int = 88, use_black: bool = True, use_isort: bool = True) -> str:
            formatter = CodeFormatterTool()
            return formatter.format(file_path, line_length, use_black, use_isort)

        @self.app.tool(name="document_code", description="Generates or updates Python code documentation.")
        def document_code(file_path: str, doc_style: str = "google", update_existing: bool = False) -> str:
            documenter = CodeDocumenterTool()
            return documenter.document(file_path, doc_style, update_existing)

    def run(self, host: str = "127.0.0.1", port: int = 8000):
        """Run the SSE server."""
        host = os.getenv("HOST", host)
        port = int(os.getenv("PORT", port))
        
        print(f"Starting Cursor MCP Server at http://{host}:{port}")
        
        # Configure server settings
        self.app.settings.host = host
        self.app.settings.port = port
        self.app.settings.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Run the server with SSE transport
        self.app.run(transport="sse")

def main():
    server = CursorMCPSSEServer()
    server.run()

if __name__ == "__main__":
    main() 