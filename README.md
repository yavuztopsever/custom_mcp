# Custom MCP Server

A Python implementation of the Model Context Protocol (MCP) server with custom tools and functionalities. This server provides a standardized way for AI models to interact with external tools, resources, and prompts through a WebSocket or SSE (Server-Sent Events) interface.

## Overview

The Custom MCP Server implements the Model Context Protocol, which defines a standard way for AI models to:
- Access and manipulate resources
- Execute custom tools
- Manage prompts and templates
- Handle real-time notifications
- Support logging and progress tracking
- Manage model sampling preferences

## Features

- **WebSocket and SSE Support**: Supports both WebSocket and Server-Sent Events for real-time communication
- **Resource Management**: 
  - List and read resources
  - Subscribe to resource updates
  - Support for resource templates
- **Tool Management**:
  - Dynamic tool registration
  - Tool execution with progress tracking
  - Custom tool implementation support
- **Prompt Management**:
  - Template-based prompts
  - Dynamic prompt arguments
  - Prompt completion support
- **Model Sampling**:
  - Configurable model preferences
  - Support for different LLM providers
  - Temperature and token control
- **Logging and Progress**:
  - Configurable logging levels
  - Real-time progress notifications
  - Error handling and reporting

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

## Dependencies

- Python 3.7+
- anyio>=3.0.0
- pydantic>=2.0.0
- sse-starlette>=0.8.4
- httpx>=0.23.0
- uvicorn>=0.18.0
- pydantic-settings>=1.0.1

## Usage

### Starting the Server

1. Start the SSE server:
```bash
python src/server_sse.py
```

2. The server will start and listen for incoming connections.

### Server Configuration

The server can be configured through environment variables or a `.env` file:

```env
HOST=localhost
PORT=8000
LOG_LEVEL=INFO
```

### Protocol Implementation

The server implements the Model Context Protocol (MCP) with the following key components:

1. **Initialization**
   - Protocol version negotiation
   - Capability exchange
   - Server information sharing

2. **Resource Operations**
   ```python
   # List available resources
   GET /resources
   
   # Read a specific resource
   GET /resources/{resource_id}
   
   # Subscribe to resource updates
   POST /resources/subscribe
   ```

3. **Tool Operations**
   ```python
   # List available tools
   GET /tools
   
   # Execute a tool
   POST /tools/call
   ```

4. **Prompt Operations**
   ```python
   # List available prompts
   GET /prompts
   
   # Get a specific prompt
   GET /prompts/{prompt_name}
   ```

### Custom Tool Development

To create a custom tool:

1. Create a new tool class:
```python
from mcp.types import Tool, CallToolResult

class MyCustomTool(Tool):
    name = "my_custom_tool"
    description = "Description of what the tool does"
    
    async def execute(self, arguments: dict) -> CallToolResult:
        # Tool implementation
        pass
```

2. Register the tool with the server:
```python
server.register_tool(MyCustomTool())
```

## API Documentation

### Server Endpoints

- `GET /`: Server status and information
- `GET /resources`: List available resources
- `GET /resources/{id}`: Get specific resource
- `POST /resources/subscribe`: Subscribe to resource updates
- `GET /tools`: List available tools
- `POST /tools/call`: Execute a tool
- `GET /prompts`: List available prompts
- `GET /prompts/{name}`: Get specific prompt

### WebSocket API

The WebSocket API follows the JSON-RPC 2.0 specification with MCP extensions:

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {}
  },
  "id": 1
}
```

## Error Handling

The server implements standardized error handling:

- HTTP Status Codes for REST endpoints
- JSON-RPC error objects for WebSocket communication
- Detailed error messages and stack traces in development mode

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the terms specified in the LICENSE file.

## Security

Please report security vulnerabilities to the project maintainers. See SECURITY.md for details.

## Support

For support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue if needed

## Acknowledgments

This project implements the Model Context Protocol (MCP) specification.
