# Custom MCP Server for Cursor

A custom MCP (Model Control Protocol) server for the Cursor app, providing code analysis, formatting, and documentation tools.

## Features

- **Code Analyzer**: Analyzes Python code for potential issues and improvements
- **Code Formatter**: Formats Python code using black and isort
- **Code Documenter**: Generates and updates Python code documentation in various styles (Google, NumPy, Sphinx)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/custom_mcp_server.git
   cd custom_mcp_server
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `.env` file in the project root (optional):
   ```env
   HOST=127.0.0.1
   PORT=8000
   LOG_LEVEL=INFO
   ```

2. Configure Cursor to use the MCP server by creating or updating `cursor.json`:
   ```json
   {
       "mcp": {
           "type": "sse",
           "url": "http://127.0.0.1:8000/sse",
           "tools": [
               {
                   "name": "analyze_code",
                   "description": "Analyzes Python code for potential issues and improvements.",
                   "parameters": {
                       "file_path": {
                           "type": "string",
                           "description": "Path to the Python file to analyze"
                       }
                   }
               },
               {
                   "name": "format_code",
                   "description": "Formats Python code using black and isort.",
                   "parameters": {
                       "file_path": {
                           "type": "string",
                           "description": "Path to the Python file to format"
                       },
                       "line_length": {
                           "type": "integer",
                           "description": "Maximum line length",
                           "default": 88
                       },
                       "use_black": {
                           "type": "boolean",
                           "description": "Whether to use black formatter",
                           "default": true
                       },
                       "use_isort": {
                           "type": "boolean",
                           "description": "Whether to use isort for import sorting",
                           "default": true
                       }
                   }
               },
               {
                   "name": "document_code",
                   "description": "Generates or updates Python code documentation.",
                   "parameters": {
                       "file_path": {
                           "type": "string",
                           "description": "Path to the Python file to document"
                       },
                       "doc_style": {
                           "type": "string",
                           "description": "Documentation style to use (google, numpy, or sphinx)",
                           "enum": ["google", "numpy", "sphinx"],
                           "default": "google"
                       },
                       "update_existing": {
                           "type": "boolean",
                           "description": "Whether to update existing docstrings",
                           "default": false
                       }
                   }
               }
           ]
       }
   }
   ```

## Usage

1. Start the MCP server:
   ```bash
   python -m src.server_sse
   ```

2. The server will start at `http://127.0.0.1:8000` (or the configured host/port).

3. Use the tools in Cursor:
   - **Code Analysis**: Analyze Python code for potential issues
   - **Code Formatting**: Format Python code using black and isort
   - **Code Documentation**: Generate or update Python code documentation

## Development

### Project Structure

```
custom_mcp_server/
├── .env                    # Environment variables
├── .venv/                  # Virtual environment
├── cursor.json            # Cursor configuration
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
└── src/                  # Source code
    ├── __init__.py
    ├── server_sse.py     # SSE server implementation
    └── tools/            # Tool implementations
        ├── __init__.py
        ├── code_analyzer.py
        ├── code_formatter.py
        └── code_documenter.py
```

### Adding New Tools

1. Create a new tool class in `src/tools/`:
   ```python
   class NewTool:
       def execute(self, **parameters) -> str:
           # Implement tool functionality
           pass
   ```

2. Register the tool in `src/server_sse.py`:
   ```python
   @app.tool(name="new_tool", description="Description of the new tool")
   def new_tool(**parameters) -> str:
       tool = NewTool()
       return tool.execute(**parameters)
   ```

3. Add tool configuration to `cursor.json`.

### Testing

Run tests using pytest:
```bash
pytest
```

## Troubleshooting

### Common Issues

1. **Server won't start**:
   - Check if the port is already in use
   - Verify virtual environment is activated
   - Check Python version (3.8+ required)

2. **Tool not found in Cursor**:
   - Verify `cursor.json` configuration
   - Check server logs for registration errors
   - Restart Cursor app

3. **Tool execution fails**:
   - Check server logs for error messages
   - Verify file paths are correct
   - Check tool-specific requirements

## License

MIT License. See [LICENSE](LICENSE) for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions:
- Open a GitHub issue
- Contact the maintainers 