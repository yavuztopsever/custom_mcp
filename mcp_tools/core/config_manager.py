"""
Configuration manager for MCP tools.
Handles loading and managing tool and project configurations.
"""

import os
import yaml
from typing import Any, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

class ConfigManager:
    def __init__(self, config_dir: Optional[str] = None):
        # Load environment variables from .env file
        env_path = Path(__file__).parent.parent.parent / '.env'
        load_dotenv(env_path)
        
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent.parent / 'config'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.default_config = {
            'tools': {},
            'logging': {
                'level': os.getenv('LOG_LEVEL', 'INFO'),
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'model': 'gpt-4o-mini'
            }
        }
        self._config: Dict[str, Any] = {}
        self.load_config()
        self._apply_env_overrides()

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to configuration."""
        # MCP Protocol configuration overrides
        mcp_protocol_config = self.get_tool_config('mcp_protocol')
        mcp_protocol_config.update({
            'host': os.getenv('MCP_SERVER_HOST', mcp_protocol_config.get('host', 'localhost')),
            'port': int(os.getenv('MCP_SERVER_PORT', mcp_protocol_config.get('port', 25565))),
            'auth_token': os.getenv('MCP_AUTH_TOKEN', mcp_protocol_config.get('auth_token'))
        })
        self.set_tool_config('mcp_protocol', mcp_protocol_config)

    def load_config(self) -> None:
        """Load configuration from the config file."""
        config_file = self.config_dir / 'config.yaml'
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                self._config = yaml.safe_load(f)
        else:
            self._config = self.default_config.copy()
            self.save_config()

    def save_config(self) -> None:
        """Save current configuration to the config file."""
        config_file = self.config_dir / 'config.yaml'
        
        # Create a copy of the config without sensitive data
        safe_config = self._config.copy()
        if 'tools' in safe_config and 'mcp_protocol' in safe_config['tools']:
            safe_config['tools']['mcp_protocol'] = {
                k: v for k, v in safe_config['tools']['mcp_protocol'].items()
                if k not in ['auth_token']
            }
        if 'openai' in safe_config:
            safe_config['openai'] = {
                k: v for k, v in safe_config['openai'].items()
                if k not in ['api_key']
            }
        
        with open(config_file, 'w') as f:
            yaml.dump(safe_config, f, default_flow_style=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        config[keys[-1]] = value
        self.save_config()

    def get_tool_config(self, tool_name: str) -> Dict[str, Any]:
        """Get configuration for a specific tool."""
        return self.get(f'tools.{tool_name}', {})

    def set_tool_config(self, tool_name: str, config: Dict[str, Any]) -> None:
        """Set configuration for a specific tool."""
        self.set(f'tools.{tool_name}', config)

    @property
    def logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.get('logging', self.default_config['logging'])

    @property
    def openai_config(self) -> Dict[str, Any]:
        """Get OpenAI configuration."""
        return self.get('openai', self.default_config['openai']) 