"""
MCP Protocol Tool
Handles communication between the MCP server and Cursor IDE.
"""

import sys
import json
import socket
import threading
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.append(str(Path(__file__).parent.parent))
from core.base_tool import BaseTool

class MCPProtocolTool(BaseTool):
    def __init__(self, config_manager=None):
        super().__init__('mcp_protocol', config_manager)
        self.default_config = {
            'host': 'localhost',
            'port': 25565,  # Default Minecraft port, can be changed
            'max_connections': 5,
            'buffer_size': 4096,
            'timeout': 60,
            'auth_token': None  # Should be set via environment variable
        }
        self._init_config()
        self.server_socket = None
        self.running = False
        self.clients = {}

    def _init_config(self) -> None:
        """Initialize tool configuration with defaults if not set."""
        for key, value in self.default_config.items():
            if not self.get_config(key):
                self.set_config(key, value)

    def _handle_client(self, client_socket: socket.socket, address: tuple) -> None:
        """Handle individual client connections."""
        try:
            self.logger.info(f"New connection from {address}")
            while self.running:
                try:
                    data = client_socket.recv(self.get_config('buffer_size'))
                    if not data:
                        break

                    message = json.loads(data.decode('utf-8'))
                    response = self._process_message(message)
                    client_socket.send(json.dumps(response).encode('utf-8'))

                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON received: {e}")
                    break
                except Exception as e:
                    self.logger.error(f"Error handling client message: {e}")
                    break

        finally:
            client_socket.close()
            if address in self.clients:
                del self.clients[address]
            self.logger.info(f"Connection closed for {address}")

    def _process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming messages and generate responses."""
        try:
            if not isinstance(message, dict):
                return {'status': 'error', 'message': 'Message must be a JSON object'}

            msg_type = message.get('type')
            if not msg_type:
                return {'status': 'error', 'message': 'Missing message type'}

            if msg_type == 'auth':
                return self._handle_auth(message)
            elif msg_type == 'command':
                return self._handle_command(message)
            elif msg_type == 'query':
                return self._handle_query(message)
            else:
                return {'status': 'error', 'message': f'Unknown message type: {msg_type}'}

        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return {'status': 'error', 'message': str(e)}

    def _handle_auth(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle authentication requests."""
        token = message.get('token')
        if not token:
            return {'status': 'error', 'message': 'Missing authentication token'}

        if token != self.get_config('auth_token'):
            return {'status': 'error', 'message': 'Invalid authentication token'}

        return {'status': 'success', 'message': 'Authentication successful'}

    def _handle_command(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle command execution requests."""
        command = message.get('command')
        if not command:
            return {'status': 'error', 'message': 'Missing command'}

        try:
            # Execute the command using the tool manager
            # This is a placeholder for actual command execution
            return {'status': 'success', 'message': f'Command executed: {command}'}
        except Exception as e:
            return {'status': 'error', 'message': f'Command execution failed: {str(e)}'}

    def _handle_query(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle query requests."""
        query = message.get('query')
        if not query:
            return {'status': 'error', 'message': 'Missing query'}

        try:
            # Process the query and return results
            # This is a placeholder for actual query processing
            return {'status': 'success', 'data': {'query_result': 'placeholder'}}
        except Exception as e:
            return {'status': 'error', 'message': f'Query failed: {str(e)}'}

    def run(self, *args: Any, **kwargs: Any) -> bool:
        """
        Start the MCP protocol server.
        
        Returns:
            bool: True if server started successfully, False otherwise
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            host = self.get_config('host')
            port = self.get_config('port')
            
            self.server_socket.bind((host, port))
            self.server_socket.listen(self.get_config('max_connections'))
            
            self.running = True
            self.logger.info(f"MCP Protocol server started on {host}:{port}")
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    client_socket.settimeout(self.get_config('timeout'))
                    
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                    self.clients[address] = client_thread
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    self.logger.error(f"Error accepting connection: {e}")
                    continue
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting MCP Protocol server: {e}")
            return False
        
    def stop(self) -> None:
        """Stop the MCP protocol server."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        
        # Create a copy of the clients dictionary to avoid modification during iteration
        clients_copy = dict(self.clients)
        for client_thread in clients_copy.values():
            client_thread.join(timeout=1.0)
        self.clients.clear()

if __name__ == '__main__':
    tool = MCPProtocolTool()
    try:
        tool.run()
    except KeyboardInterrupt:
        tool.stop()
        sys.exit(0) 