# Sequential Thinking MCP Server

A custom Model Context Protocol (MCP) server implementation that supports sequential thinking capabilities through Supergateway integration.

## Features

- JSON-RPC 2.0 protocol support
- Server-Sent Events (SSE) for real-time communication
- Sequential thinking tool integration
- Supergateway integration for stdio communication

## Requirements

- Node.js 16.x or later
- Python 3.8 or later

## Installation

1. Install Node.js dependencies:
```bash
npm install
```

## Usage

Start the server:
```bash
npm start
```

For development with auto-reload:
```bash
npm run dev
```

## Protocol

The server implements the Model Context Protocol (MCP) version 2024-11-05 with the following capabilities:

- Sequential thinking tool support
- JSON-RPC 2.0 message format
- SSE-based communication

### Supported Methods

1. `initialize`
   - Initializes the server connection
   - Returns server capabilities and information

2. `notifications/initialized`
   - Notification after initialization
   - No response required

3. `tools/list`
   - Lists available tools
   - Returns tool specifications

### Sequential Thinking Tool

The server provides the `mcp__sequentialthinking` tool with the following parameters:

- `thought` (string, required): Current thinking step
- `nextThoughtNeeded` (boolean, required): Whether another thought is needed
- `thoughtNumber` (integer, required): Current thought number
- `totalThoughts` (integer, required): Total thoughts needed
- `isRevision` (boolean): Whether this revises previous thinking
- `revisesThought` (integer): Which thought is being reconsidered
- `branchFromThought` (integer): Branching point thought number
- `branchId` (string): Branch identifier
- `needsMoreThoughts` (boolean): If more thoughts are needed

## Development

The server runs on port 8001 by default and communicates through stdio using Supergateway. The communication flow is:

1. Client connects through SSE
2. Server initializes with capabilities
3. Sequential thinking requests are processed through JSON-RPC
4. Responses are sent back through SSE

## License

MIT
