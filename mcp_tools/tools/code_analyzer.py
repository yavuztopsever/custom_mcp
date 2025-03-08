import os
import json
from pathlib import Path
from typing import List, Dict, Any
import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import sqlite3
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_tools/logs/code_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CodeSummary(BaseModel):
    """Model for code summary output"""
    file_path: str = Field(description="Path to the analyzed file")
    functionality: str = Field(description="Summary of the file's functionality")
    dependencies: List[str] = Field(description="List of dependencies used in the file")
    complexity_score: int = Field(description="Estimated complexity score (1-10)")

class GroupedFunctionality(BaseModel):
    """Model for grouped functionality output"""
    group_name: str = Field(description="Name of the functionality group")
    files: List[str] = Field(description="List of files in this group")
    common_functionality: str = Field(description="Description of common functionality")
    consolidation_recommendation: str = Field(description="Recommendation for consolidation")

class CodeAnalyzer:
    def __init__(self):
        """Initialize the CodeAnalyzer with necessary configurations"""
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.2,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.db_path = "mcp_tools/data/code_analysis.db"
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for storing analysis results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_summaries (
                file_path TEXT PRIMARY KEY,
                functionality TEXT,
                dependencies TEXT,
                complexity_score INTEGER,
                analyzed_at TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS functionality_groups (
                group_name TEXT PRIMARY KEY,
                files TEXT,
                common_functionality TEXT,
                consolidation_recommendation TEXT,
                created_at TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    def collect_scripts(self, exclude_dirs: List[str] = None) -> List[str]:
        """Collect all script files in the project"""
        if exclude_dirs is None:
            exclude_dirs = ['.git', '.venv', '__pycache__', 'node_modules']
        
        script_files = []
        for root, dirs, files in os.walk('.', topdown=True):
            # Modify dirs in-place to prevent walking into excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith(('.py', '.sh', '.java', '.js', '.ts')):
                    full_path = os.path.join(root, file)
                    # Skip files in excluded directories
                    if not any(excluded in full_path.split(os.sep) for excluded in exclude_dirs):
                        script_files.append(full_path)
        
        return script_files

    def analyze_file(self, file_path: str) -> CodeSummary:
        """Analyze a single file using GPT-4"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a code analysis expert. Analyze the following code and provide a detailed summary."),
            ("user", "Code to analyze:\n{code}\n\nProvide a summary including main functionality, dependencies, and complexity score (1-10).")
        ])

        parser = PydanticOutputParser(pydantic_object=CodeSummary)
        chain = prompt | self.llm | parser

        response = chain.invoke({"code": content})
        if isinstance(response, CodeSummary):  # Handle mock response
            return response
        if hasattr(response, 'content'):  # Handle string response
            return parser.parse(response.content)
        return response

    def store_summary(self, summary: CodeSummary):
        """Store file analysis results in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO file_summaries
            (file_path, functionality, dependencies, complexity_score, analyzed_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            summary.file_path,
            summary.functionality,
            json.dumps(summary.dependencies),
            summary.complexity_score,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()

    def group_functionalities(self) -> GroupedFunctionality:
        """Group files with overlapping functionalities using GPT-4"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all summaries
        cursor.execute('SELECT file_path, functionality FROM file_summaries')
        summaries = cursor.fetchall()
        conn.close()

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a code organization expert. Group these files based on overlapping functionalities."),
            ("user", "File summaries:\n{summaries}\n\nGroup these files and provide consolidation recommendations.")
        ])

        parser = PydanticOutputParser(pydantic_object=GroupedFunctionality)
        chain = prompt | self.llm | parser

        summaries_text = "\n".join([f"{path}: {func}" for path, func in summaries])
        response = chain.invoke({"summaries": summaries_text})
        if isinstance(response, GroupedFunctionality):  # Handle mock response
            return response
        if hasattr(response, 'content'):  # Handle string response
            return parser.parse(response.content)
        return response

    def run_analysis(self):
        """Run the complete analysis pipeline"""
        logger.info("Starting code analysis...")
        
        # Collect all script files
        scripts = self.collect_scripts()
        logger.info(f"Found {len(scripts)} script files to analyze")
        
        # Analyze each file
        for script in scripts:
            try:
                logger.info(f"Analyzing {script}...")
                summary = self.analyze_file(script)
                self.store_summary(summary)
            except Exception as e:
                logger.error(f"Error analyzing {script}: {str(e)}")
        
        # Group functionalities
        logger.info("Grouping functionalities...")
        groups = self.group_functionalities()
        
        logger.info("Analysis complete. Check the database for results.")
        return groups

def main():
    """Main entry point for the code analyzer tool"""
    analyzer = CodeAnalyzer()
    groups = analyzer.run_analysis()
    
    # Print results
    print(f"\nGroup: {groups.group_name}")
    print("Files:")
    for file in groups.files:
        print(f"  - {file}")
    print(f"Common Functionality: {groups.common_functionality}")
    print(f"Consolidation Recommendation: {groups.consolidation_recommendation}")

if __name__ == "__main__":
    main() 