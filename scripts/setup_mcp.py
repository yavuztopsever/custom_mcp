#!/usr/bin/env python3

import os
import shutil
import json
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MCPSetup:
    def __init__(self, config_path="config/settings.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.mcp_version = self.config.get("mcp_version", "1.12.2")
        self.java_version = self.config.get("java_version", "1.8")
        self.source_dir = Path(self.config.get("source_dir", "src/main/java"))
        self.temp_dir = Path(self.config.get("build", {}).get("temp_dir", "temp"))
        self.mcp_dir = self.temp_dir / f"mcp_{self.mcp_version}"

    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found at {self.config_path}. Using defaults.")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in config file {self.config_path}")
            return {}

    def setup_directories(self):
        """Create necessary directories"""
        directories = [
            self.source_dir,
            self.temp_dir,
            self.mcp_dir
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")

    def extract_mcp(self, mcp_zip_path):
        """Extract MCP files from zip"""
        if not os.path.exists(mcp_zip_path):
            logger.error(f"MCP zip file not found at: {mcp_zip_path}")
            return False

        try:
            # Extract MCP
            logger.info(f"Extracting MCP from {mcp_zip_path} to {self.mcp_dir}")
            shutil.unpack_archive(mcp_zip_path, self.mcp_dir)
            
            # Make decompile script executable
            decompile_script = self.mcp_dir / ("decompile.sh" if os.name != 'nt' else "decompile.bat")
            if decompile_script.exists():
                decompile_script.chmod(0o755)
            
            return True
        except Exception as e:
            logger.error(f"Error extracting MCP: {str(e)}")
            return False

    def run_decompile(self):
        """Run MCP decompile script"""
        decompile_script = "decompile.sh" if os.name != 'nt' else "decompile.bat"
        script_path = self.mcp_dir / decompile_script

        if not script_path.exists():
            logger.error(f"Decompile script not found at: {script_path}")
            return False

        try:
            logger.info("Running decompile script...")
            process = subprocess.run(
                [str(script_path)],
                cwd=str(self.mcp_dir),
                check=True,
                text=True,
                capture_output=True
            )
            logger.info("Decompile completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running decompile script: {e.output}")
            return False

    def copy_source_files(self):
        """Copy decompiled source files to project structure"""
        mcp_src = self.mcp_dir / "src" / "minecraft"
        if not mcp_src.exists():
            logger.error(f"MCP source directory not found at: {mcp_src}")
            return False

        try:
            # Copy source files
            logger.info(f"Copying source files from {mcp_src} to {self.source_dir}")
            shutil.copytree(mcp_src, self.source_dir, dirs_exist_ok=True)
            
            # Run the organization script
            logger.info("Running organization script...")
            subprocess.run(["python3", "scripts/organize.py"], check=True)
            
            return True
        except Exception as e:
            logger.error(f"Error copying source files: {str(e)}")
            return False

def main():
    setup = MCPSetup()
    
    # Get MCP zip path from user
    mcp_zip = input("Please enter the path to your MCP zip file: ").strip()
    if not mcp_zip:
        logger.error("No MCP zip file specified")
        return

    # Setup process
    setup.setup_directories()
    
    if setup.extract_mcp(mcp_zip):
        if setup.run_decompile():
            if setup.copy_source_files():
                logger.info("MCP setup completed successfully!")
                logger.info("\nNext steps:")
                logger.info("1. Review the extracted files in src/main/java")
                logger.info("2. Run './scripts/build.sh' to test the build")
                logger.info("3. Start developing!")
            else:
                logger.error("Failed to copy source files")
        else:
            logger.error("Failed to run decompile script")
    else:
        logger.error("Failed to extract MCP")

if __name__ == "__main__":
    main() 