"""FastMCP - A more ergonomic interface for MCP servers."""

from importlib.metadata import version, PackageNotFoundError

from .server import Context, FastMCP
from .utilities.types import Image

__version__ = "unknown"

__all__ = ["FastMCP", "Context", "Image"]
