"""
Base tool class for MCP tools.
All tools should inherit from this class and implement its interface.
"""

import abc
import logging
from typing import Any, Dict, Optional
from pathlib import Path

from .config_manager import ConfigManager

class BaseTool(abc.ABC):
    def __init__(self, name: str, config_manager: Optional[ConfigManager] = None):
        self.name = name
        self.config_manager = config_manager or ConfigManager()
        self.logger = self._setup_logger()
        self.tool_config = self.config_manager.get_tool_config(self.name)

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the tool."""
        logger = logging.getLogger(f'mcp_tools.{self.name}')
        log_config = self.config_manager.logging_config
        
        # Create logs directory if it doesn't exist
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Get log format with fallback
        log_format = '%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)'
        if isinstance(log_config, dict) and isinstance(log_config.get('format'), str):
            log_format = log_config['format']
        
        # Set up file handler
        file_handler = logging.FileHandler(log_dir / f'{self.name}.log')
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)
        
        # Set up console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(console_handler)
        
        # Set log level
        log_level = 'INFO'
        if isinstance(log_config, dict) and isinstance(log_config.get('level'), str):
            log_level = log_config['level']
        logger.setLevel(log_level)
        
        return logger

    @abc.abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """
        Run the tool with the given arguments.
        
        Args:
            *args: Positional arguments for the tool
            **kwargs: Keyword arguments for the tool
            
        Returns:
            Any: The result of running the tool
        """
        pass

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a tool-specific configuration value."""
        return self.tool_config.get(key, default)

    def set_config(self, key: str, value: Any) -> None:
        """Set a tool-specific configuration value."""
        self.tool_config[key] = value
        self.config_manager.set_tool_config(self.name, self.tool_config)

    def validate_config(self) -> bool:
        """
        Validate the tool's configuration.
        Override this method to implement tool-specific validation.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        return True 