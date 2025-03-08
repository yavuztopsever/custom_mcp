import os
import pytest
from pathlib import Path

@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def test_data_dir(project_root):
    """Return the test data directory, creating it if it doesn't exist."""
    data_dir = project_root / "tests" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Setup test environment variables."""
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")
    monkeypatch.setenv("MCP_AUTH_TOKEN", "test_token")

@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path."""
    return tmp_path / "test.db"

@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    import logging
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    return logger 