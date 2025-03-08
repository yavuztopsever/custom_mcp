"""
Clean code tool for formatting and linting Python code.
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Any

from ..core.base_tool import BaseTool

class CleanCodeTool(BaseTool):
    def __init__(self, config_manager=None):
        super().__init__("clean_code", config_manager)
        self.default_config = {
            "target_extensions": [".py"],
            "exclude_dirs": ["venv", ".venv", "__pycache__", ".git"],
            "line_length": 88,
            "use_black": True,
            "use_flake8": True,
            "use_mypy": True
        }
        
    def run(self, target_dir: str = ".", **kwargs: Any) -> Dict[str, Any]:
        """
        Run code cleaning tools on the target directory.
        
        Args:
            target_dir: Directory to clean (default: current directory)
            **kwargs: Additional arguments
            
        Returns:
            Dict containing the results of each tool
        """
        target_path = Path(target_dir)
        if not target_path.exists():
            raise ValueError(f"Directory not found: {target_dir}")
            
        results = {
            "black": None,
            "flake8": None,
            "mypy": None
        }
        
        # Get configuration
        config = self.default_config.copy()
        config.update(self.tool_config)
        
        try:
            # Run black
            if config["use_black"]:
                self.logger.info("Running black formatter...")
                cmd = [
                    "black",
                    "--line-length", str(config["line_length"]),
                    str(target_path)
                ]
                process = subprocess.run(cmd, capture_output=True, text=True)
                results["black"] = {
                    "success": process.returncode == 0,
                    "output": process.stdout,
                    "error": process.stderr
                }
                
            # Run flake8
            if config["use_flake8"]:
                self.logger.info("Running flake8 linter...")
                cmd = [
                    "flake8",
                    "--max-line-length", str(config["line_length"]),
                    str(target_path)
                ]
                process = subprocess.run(cmd, capture_output=True, text=True)
                results["flake8"] = {
                    "success": process.returncode == 0,
                    "output": process.stdout,
                    "error": process.stderr
                }
                
            # Run mypy
            if config["use_mypy"]:
                self.logger.info("Running mypy type checker...")
                cmd = ["mypy", str(target_path)]
                process = subprocess.run(cmd, capture_output=True, text=True)
                results["mypy"] = {
                    "success": process.returncode == 0,
                    "output": process.stdout,
                    "error": process.stderr
                }
                
        except Exception as e:
            self.logger.error(f"Error running clean code tools: {e}")
            raise
            
        return results 