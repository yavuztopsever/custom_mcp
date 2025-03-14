import pytest
<<<<<<< Updated upstream


@pytest.fixture
def anyio_backend():
    return "asyncio"
=======
import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Generator, AsyncGenerator

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@pytest.fixture(autouse=True)
def setup_test_env() -> Generator[None, None, None]:
    """
    Setup test environment before each test.
    
    This fixture runs automatically before each test and handles:
    1. Setting up any necessary environment variables
    2. Creating temporary directories if needed
    3. Any other test environment setup
    
    Yields:
        None
    """
    # Store original environment
    original_env = dict(os.environ)
    
    # Set test environment variables
    os.environ.update({
        'TESTING': 'true',
        'LOG_LEVEL': 'DEBUG'
    })
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture
def temp_workspace(tmp_path) -> Generator[str, None, None]:
    """
    Create a temporary workspace for tests.
    
    Args:
        tmp_path: Pytest fixture providing a temporary directory

    Yields:
        str: Path to the temporary workspace
    """
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    original_cwd = os.getcwd()
    os.chdir(workspace)
    
    yield str(workspace)
    
    os.chdir(original_cwd)

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def base_server() -> AsyncGenerator[FastMCP, None]:
    """Create a base server instance for testing."""
    config = ServerConfig(
        name="TestServer",
        host="localhost",
        port=8000,
        debug=True,
        log_level="DEBUG"
    )
    server = FastMCP(config=config)
    await server.startup()
    yield server
    await server.shutdown()

@pytest.fixture
async def base_client(base_server: FastMCP) -> AsyncGenerator[MCPClient, None]:
    """Create a base client instance for testing."""
    client = MCPClient("http://localhost:8000")
    yield client
    await client.close()

@pytest.fixture
def test_resources_dir() -> Path:
    """Return the path to test resources directory."""
    return Path(__file__).parent / "resources"

@pytest.fixture(autouse=True)
async def cleanup_after_test():
    """Clean up any resources after each test."""
    yield
    # Add cleanup logic here if needed
    pass 
>>>>>>> Stashed changes
