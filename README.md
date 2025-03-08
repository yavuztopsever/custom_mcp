# Custom MCP Server

A modular system for managing Minecraft Coder Pack (MCP) projects within the Cursor IDE. This system provides a scalable and extensible framework for integrating various development tools and workflows.

## Project Structure

```
custom_mcp_server/
├── mcp_tools/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── base_tool.py        # Base class for all tools
│   │   └── config_manager.py   # Configuration management
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── clean_code.py       # Sample tool for code cleaning
│   │   └── mcp_protocol.py     # MCP protocol implementation
│   ├── config/
│   │   └── config.yaml         # Global configuration
│   ├── logs/                   # Tool-specific logs
│   └── mcp_tool_manager.sh     # Main tool execution script
├── tests/                      # Test directory
├── .env                        # Environment variables (not in git)
├── .env.template               # Environment variable template
├── .venv/                      # Python virtual environment
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Setup

1. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate     # On Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Make the tool manager executable:
   ```bash
   chmod +x mcp_tools/mcp_tool_manager.sh
   ```

4. Configure environment variables:
   ```bash
   # Copy the template
   cp .env.template .env
   
   # Edit .env with your values
   nano .env  # or use your preferred editor
   ```

### Environment Variables

The following environment variables can be configured in your `.env` file:

- **Required Variables**:
  - `MCP_AUTH_TOKEN`: Authentication token for the MCP server
  - `OPENAI_API_KEY`: Your OpenAI API key (if using GPT-4 features)

- **Optional Variables**:
  - `MCP_SERVER_HOST`: Host for the MCP server (default: localhost)
  - `MCP_SERVER_PORT`: Port for the MCP server (default: 25565)
  - `LOG_LEVEL`: Logging level (default: INFO)

Example `.env` file:
```bash
# Required
MCP_AUTH_TOKEN=your_secure_token_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=25565
LOG_LEVEL=INFO
```

**Note**: The `.env` file contains sensitive information and is not tracked by Git. Make sure to keep your tokens secure and never commit them to version control.

## MCP Protocol Connection

The MCP protocol server provides a secure interface for Cursor IDE to communicate with the MCP tools. Here's how to connect:

### Server Configuration

The MCP protocol server can be configured through `config.yaml`:

```yaml
tools:
  mcp_protocol:
    host: localhost
    port: 25565
    max_connections: 5
    buffer_size: 4096
    timeout: 60
```

### Starting the Server

```bash
./mcp_tools/mcp_tool_manager.sh mcp_protocol
```

### Connection Details

- **Host**: localhost (default)
- **Port**: 25565 (default)
- **Protocol**: TCP
- **Authentication**: Required (token-based)
- **Message Format**: JSON

### Message Protocol

1. **Authentication**
   ```json
   {
     "type": "auth",
     "token": "your-auth-token"
   }
   ```
   Response:
   ```json
   {
     "status": "success",
     "message": "Authentication successful"
   }
   ```

2. **Command Execution**
   ```json
   {
     "type": "command",
     "command": "clean_code",
     "args": {
       "target_dir": "/path/to/directory"
     }
   }
   ```
   Response:
   ```json
   {
     "status": "success",
     "message": "Command executed successfully"
   }
   ```

3. **Query**
   ```json
   {
     "type": "query",
     "query": "get_available_tools"
   }
   ```
   Response:
   ```json
   {
     "status": "success",
     "data": {
       "tools": ["clean_code", "mcp_protocol"]
     }
   }
   ```

### Error Handling

Error responses follow this format:
```json
{
  "status": "error",
  "message": "Error description"
}
```

### Cursor IDE Integration

To connect your Cursor IDE to the MCP server:

1. Configure connection settings in Cursor:
   - Server: `localhost:25565`
   - Authentication Token: Your secure token

2. Use the MCP protocol client in your Cursor extension:
   ```python
   import socket
   import json

   def connect_to_mcp_server(host='localhost', port=25565, token=None):
       sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       sock.connect((host, port))
       
       # Authenticate
       auth_message = {
           'type': 'auth',
           'token': token
       }
       sock.send(json.dumps(auth_message).encode('utf-8'))
       response = json.loads(sock.recv(4096).decode('utf-8'))
       
       if response['status'] != 'success':
           raise Exception(f"Authentication failed: {response['message']}")
           
       return sock

   # Example usage
   sock = connect_to_mcp_server(token='your-auth-token')
   ```

## Usage

### Running Tools

Tools can be executed using the `mcp_tool_manager.sh` script:

```bash
./mcp_tools/mcp_tool_manager.sh <tool_name> [arguments...]
```

For example, to run the code cleaning tool:
```bash
./mcp_tools/mcp_tool_manager.sh clean_code
```

### Available Tools

1. **clean_code**: Formats and lints Python code using black, flake8, and mypy
   - Configurable through `config.yaml`
   - Supports custom file extensions and directory exclusions

2. **mcp_protocol**: Manages communication between MCP server and Cursor IDE
   - Secure token-based authentication
   - JSON-based message protocol
   - Supports command execution and queries

### Configuration

Tools can be configured through the `mcp_tools/config/config.yaml` file. The configuration system supports:

- Global settings
- Tool-specific settings
- Logging configuration
- OpenAI integration settings (for tools using GPT-4)

Example configuration:
```yaml
tools:
  clean_code:
    target_extensions: ['.py']
    exclude_dirs: ['venv', '.venv', '__pycache__', '.git']
    line_length: 88
    use_black: true
    use_flake8: true
    use_mypy: true

logging:
  level: INFO
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

openai:
  api_key_env: OPENAI_API_KEY
  model: gpt-4
```

## Creating New Tools

1. Create a new Python file in the `mcp_tools/tools` directory
2. Inherit from `BaseTool` in `core/base_tool.py`
3. Implement the required `run` method
4. Add tool-specific configuration to `config.yaml` if needed

Example:
```python
from core.base_tool import BaseTool

class MyNewTool(BaseTool):
    def __init__(self, config_manager=None):
        super().__init__('my_new_tool', config_manager)
        
    def run(self, *args, **kwargs):
        # Tool implementation here
        pass
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Smithery Deployment

This MCP server can be deployed on Smithery for seamless integration and accessibility. Follow these steps to deploy:

### Prerequisites

1. A Smithery account with API access
2. Your MCP server registered on Smithery Registry
3. Docker installed on your local machine (for testing)

### Configuration

1. **Smithery Configuration**
   The `config/smithery.json` file contains the deployment configuration:
   ```json
   {
       "name": "custom-mcp-server",
       "description": "Custom MCP Server for Minecraft modding with advanced tooling support",
       "transport": {
           "type": "ws",
           "port": 25565
       }
   }
   ```

2. **Environment Variables**
   Ensure your Smithery deployment has the following environment variables configured:
   - `MCP_AUTH_TOKEN`: Your secure authentication token
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `LOG_LEVEL`: Desired logging level (default: INFO)

### Deployment Steps

1. **Local Testing**
   Test your deployment locally using Docker:
   ```bash
   docker build -t custom-mcp-server .
   docker run -p 25565:25565 -e MCP_AUTH_TOKEN=your_token -e OPENAI_API_KEY=your_key custom-mcp-server
   ```

2. **Smithery Deployment**
   a. Login to Smithery and navigate to your server page
   b. Click on the "Deployments" tab
   c. Click "Deploy" and follow the prompts
   d. Smithery will build and deploy your server according to the configuration

### WebSocket Connection

Once deployed, your MCP server will be accessible via WebSocket:
```python
import websockets
import json

async def connect_to_smithery():
    uri = "wss://your-server.smithery.ai"
    async with websockets.connect(uri) as websocket:
        # Authenticate
        await websocket.send(json.dumps({
            "type": "auth",
            "token": "your-auth-token"
        }))
        response = await websocket.recv()
        print(f"Authentication response: {response}")

        # Send commands
        await websocket.send(json.dumps({
            "type": "command",
            "command": "clean_code",
            "args": {"target_dir": "/path/to/directory"}
        }))
        result = await websocket.recv()
        print(f"Command result: {result}")
```

### Monitoring and Logs

- Access logs through the Smithery dashboard
- Monitor server status and performance metrics
- Set up alerts for server health and errors

### Troubleshooting

1. **Connection Issues**
   - Verify your authentication token
   - Check if the server is running (status in Smithery dashboard)
   - Ensure your client is using the correct WebSocket URL

2. **Deployment Failures**
   - Check the build logs in Smithery dashboard
   - Verify your Dockerfile and dependencies
   - Ensure all required environment variables are set

3. **Performance Issues**
   - Monitor server metrics in Smithery dashboard
   - Check resource allocation in `smithery.json`
   - Review server logs for bottlenecks

For more information, visit the [Smithery Documentation](https://smithery.ai/docs). 