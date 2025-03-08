import pytest
import socket
import json
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from mcp_tools.tools.mcp_protocol import MCPProtocolTool

@pytest.fixture
def mock_config_manager():
    """Create a mock configuration manager"""
    config = {
        'host': 'localhost',
        'port': 12345,
        'max_connections': 5,
        'buffer_size': 4096,
        'timeout': 1,
        'auth_token': 'test_token',
        'logging_config': {
            'format': '%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)',
            'level': 'INFO',
            'file': 'mcp_tools/logs/mcp_protocol.log'
        }
    }
    
    mock_manager = Mock()
    mock_manager.get_config = lambda key: config.get(key)
    mock_manager.get_tool_config = lambda tool_name: config
    mock_manager.set_tool_config = lambda tool_name, config: None
    mock_manager.logging_config = config['logging_config']
    mock_manager.set_config = lambda key, value: config.update({key: value})
    return mock_manager

@pytest.fixture
def mcp_server(mock_config_manager):
    """Create an MCP server instance with mock config"""
    server = MCPProtocolTool(config_manager=mock_config_manager)
    server._init_config()  # Ensure config is initialized
    yield server
    server.stop()

@pytest.fixture
def client_socket():
    """Create a client socket for testing"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    yield sock
    sock.close()

def test_init_config(mcp_server):
    """Test server initialization with config"""
    assert mcp_server.get_config('host') == 'localhost'
    assert mcp_server.get_config('port') == 12345
    assert mcp_server.get_config('max_connections') == 5
    assert mcp_server.get_config('auth_token') == 'test_token'

def test_server_start_stop(mcp_server):
    """Test server start and stop functionality"""
    # Start server in a separate thread
    server_thread = threading.Thread(target=mcp_server.run)
    server_thread.daemon = True
    server_thread.start()
    
    # Give server time to start
    time.sleep(0.1)
    
    assert mcp_server.running == True
    assert mcp_server.server_socket is not None
    
    # Stop server
    mcp_server.stop()
    server_thread.join(timeout=1.0)
    
    assert mcp_server.running == False
    assert len(mcp_server.clients) == 0

def test_client_connection(mcp_server, client_socket):
    """Test client connection handling"""
    # Start server
    server_thread = threading.Thread(target=mcp_server.run)
    server_thread.daemon = True
    server_thread.start()
    time.sleep(0.1)
    
    # Connect client
    client_socket.connect(('localhost', 12345))
    time.sleep(0.1)
    
    assert len(mcp_server.clients) == 1
    
    # Cleanup
    mcp_server.stop()
    server_thread.join(timeout=1.0)

def test_auth_message_handling(mcp_server):
    """Test authentication message handling"""
    # Test valid auth
    auth_message = {
        'type': 'auth',
        'token': 'test_token'
    }
    response = mcp_server._process_message(auth_message)
    assert response['status'] == 'success'
    
    # Test invalid auth
    auth_message['token'] = 'wrong_token'
    response = mcp_server._process_message(auth_message)
    assert response['status'] == 'error'
    
    # Test missing token
    auth_message.pop('token')
    response = mcp_server._process_message(auth_message)
    assert response['status'] == 'error'

def test_command_message_handling(mcp_server):
    """Test command message handling"""
    # Test valid command
    command_message = {
        'type': 'command',
        'command': 'test_command'
    }
    response = mcp_server._process_message(command_message)
    assert response['status'] == 'success'
    
    # Test missing command
    command_message.pop('command')
    response = mcp_server._process_message(command_message)
    assert response['status'] == 'error'

def test_query_message_handling(mcp_server):
    """Test query message handling"""
    # Test valid query
    query_message = {
        'type': 'query',
        'query': 'test_query'
    }
    response = mcp_server._process_message(query_message)
    assert response['status'] == 'success'
    assert 'data' in response
    
    # Test missing query
    query_message.pop('query')
    response = mcp_server._process_message(query_message)
    assert response['status'] == 'error'

def test_invalid_message_handling(mcp_server):
    """Test handling of invalid messages"""
    # Test missing type
    message = {'data': 'test'}
    response = mcp_server._process_message(message)
    assert response['status'] == 'error'
    
    # Test unknown type
    message = {'type': 'unknown'}
    response = mcp_server._process_message(message)
    assert response['status'] == 'error'

@pytest.mark.integration
def test_full_client_server_communication(mcp_server, client_socket):
    """Test full communication cycle between client and server"""
    # Start server
    server_thread = threading.Thread(target=mcp_server.run)
    server_thread.daemon = True
    server_thread.start()
    time.sleep(0.1)
    
    # Connect client
    client_socket.connect(('localhost', 12345))
    
    # Send auth message
    auth_message = {
        'type': 'auth',
        'token': 'test_token'
    }
    client_socket.send(json.dumps(auth_message).encode('utf-8'))
    
    # Receive response
    response = json.loads(client_socket.recv(4096).decode('utf-8'))
    assert response['status'] == 'success'
    
    # Send command
    command_message = {
        'type': 'command',
        'command': 'test_command'
    }
    client_socket.send(json.dumps(command_message).encode('utf-8'))
    
    # Receive response
    response = json.loads(client_socket.recv(4096).decode('utf-8'))
    assert response['status'] == 'success'
    
    # Cleanup
    mcp_server.stop()
    server_thread.join(timeout=1.0)

def test_error_handling(mcp_server, client_socket):
    """Test error handling in various scenarios"""
    # Test invalid JSON
    mock_socket = MagicMock()
    mock_socket.recv.return_value = b'invalid json'
    
    mcp_server._handle_client(mock_socket, ('localhost', 12345))
    
    # Verify that the socket was closed
    mock_socket.close.assert_called_once()
    
    # Test connection timeout
    with patch.object(socket.socket, 'accept') as mock_accept:
        mock_accept.side_effect = socket.timeout
        
        # Should not raise exception
        mcp_server.run()
    
    # Test general exception in message processing
    with patch.object(mcp_server, '_process_message') as mock_process:
        mock_process.side_effect = Exception('Test error')
        
        response = mcp_server._handle_client(MagicMock(), ('localhost', 12345))
        assert response is None  # Client handler should exit gracefully 