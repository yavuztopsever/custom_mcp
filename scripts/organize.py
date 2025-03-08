#!/usr/bin/env python3

import os
import shutil
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MCPProjectOrganizer:
    def __init__(self, config_path="config/settings.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.source_dir = self.config.get("source_dir", "src/main/java")
        self.resource_dir = self.config.get("resource_dir", "src/main/resources")
        self.backup_dir = self.config.get("backup_dir", "backup")

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

    def create_directory_structure(self):
        """Create necessary directory structure"""
        directories = [
            self.source_dir,
            self.resource_dir,
            "docs",
            "tests",
            self.backup_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")

    def backup_files(self):
        """Create backup of source files"""
        if os.path.exists(self.source_dir):
            backup_timestamp = Path(self.backup_dir) / f"backup_{int(time.time())}"
            shutil.copytree(self.source_dir, backup_timestamp, dirs_exist_ok=True)
            logger.info(f"Created backup at: {backup_timestamp}")

    def organize_java_files(self):
        """Organize Java source files"""
        if not os.path.exists(self.source_dir):
            logger.warning(f"Source directory {self.source_dir} does not exist")
            return

        for root, _, files in os.walk(self.source_dir):
            for file in files:
                if file.endswith(".java"):
                    self._process_java_file(root, file)

    def _process_java_file(self, root, file):
        """Process individual Java file"""
        file_path = Path(root) / file
        
        # Read the file to determine package
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                package_line = next((line for line in content.split('\n') 
                                   if line.strip().startswith('package ')), None)
                
                if package_line:
                    package = package_line.strip().replace('package ', '').replace(';', '')
                    target_dir = Path(self.source_dir) / package.replace('.', '/')
                    target_dir.mkdir(parents=True, exist_ok=True)
                    
                    target_path = target_dir / file
                    if file_path != target_path:
                        shutil.move(str(file_path), str(target_path))
                        logger.info(f"Moved {file} to {target_path}")
        except Exception as e:
            logger.error(f"Error processing file {file}: {str(e)}")

    def organize_resources(self):
        """Organize resource files"""
        if not os.path.exists(self.resource_dir):
            logger.warning(f"Resource directory {self.resource_dir} does not exist")
            return

        # Organize by file type
        for root, _, files in os.walk(self.resource_dir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext:
                    type_dir = Path(self.resource_dir) / ext[1:]  # Remove the dot
                    type_dir.mkdir(exist_ok=True)
                    
                    source = Path(root) / file
                    target = type_dir / file
                    if source != target:
                        shutil.move(str(source), str(target))
                        logger.info(f"Moved resource {file} to {target}")

def main():
    try:
        organizer = MCPProjectOrganizer()
        organizer.create_directory_structure()
        organizer.backup_files()
        organizer.organize_java_files()
        organizer.organize_resources()
        logger.info("Project organization completed successfully")
    except Exception as e:
        logger.error(f"Error during project organization: {str(e)}")
        raise

if __name__ == "__main__":
    main() 