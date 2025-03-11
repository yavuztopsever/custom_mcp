'''
Codebase Analyzer Tool

This tool registers the CodebaseAnalyzer, which scans the entire codebase, analyzes each file using smolagents' CodeAgent with an OpenAI API backend, stores analyses in an SQLite database, generates Mermaid diagrams representing code flows, and lists obsolete files.

Reviewed Documentation:
  1. Hugging Face smolagents Repository: https://github.com/huggingface/smolagents
  2. Existing FastMCP Code Analyzer tool: src/mcp/server/fastmcp/tools/code_analyzer.py
  3. Custom project requirements and TDD guidelines
'''

import os
import sqlite3
import uuid
import ast
import argparse
from config import OPENAI_API_KEY

from smolagents import CodeAgent, OpenAIServerModel


class CodebaseAnalyzer:
    def __init__(self, db_path="codebase_analysis.db", openai_api_key=None, model=None):
        self.db_path = db_path
        self.codebase_id = str(uuid.uuid4())
        self.conn = sqlite3.connect(self.db_path)
        self._initialize_db()
        self.code_agent = self._initialize_code_agent(openai_api_key, model)
    
    def _initialize_db(self):
        cursor = self.conn.cursor()
        # Create the necessary tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS codebases (
                codebase_id TEXT PRIMARY KEY,
                analysis_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codebase_id TEXT,
                file_path TEXT,
                analysis TEXT,
                mermaid TEXT,
                UNIQUE(codebase_id, file_path),
                FOREIGN KEY(codebase_id) REFERENCES codebases(codebase_id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS obsolete (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codebase_id TEXT,
                file_path TEXT,
                reason TEXT,
                FOREIGN KEY(codebase_id) REFERENCES codebases(codebase_id)
            )
        """)
        self.conn.commit()
        # Insert the current codebase record
        try:
            cursor.execute("INSERT INTO codebases(codebase_id) VALUES(?)", (self.codebase_id,))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass
    
    def _initialize_code_agent(self, openai_api_key, model):
        if openai_api_key:
            os.environ["TOGETHER_API_KEY"] = openai_api_key
        if model is None:
            model = "gpt-4o-mini"
        model = OpenAIServerModel(
            model_id="deepseek-ai/DeepSeek-R1",
            api_base="https://api.together.xyz/v1/",
            api_key=os.environ.get("TOGETHER_API_KEY", ""),
            model=model
        )
        agent = CodeAgent(tools=[], model=model)
        return agent
    
    def scan_codebase(self, codebase_root="."):
        """
        Traverse the codebase directory and return a list of code file paths,
        excluding common directories like .venv, __pycache__, .git, and node_modules.
        """
        file_list = []
        for root, dirs, files in os.walk(codebase_root):
            dirs[:] = [d for d in dirs if d not in [".venv", "__pycache__", ".git", "node_modules"]]
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rb', '.php')):
                    file_list.append(os.path.join(root, file))
        return file_list
    
    def analyze_file(self, file_path):
        """
        Reads the file content and uses CodeAgent to perform an analysis that includes:
          1. A summary of the file's purpose.
          2. Identification of key functions and dependencies.
          3. Proposed flow diagrams (Mermaid syntax).
          4. Detection of obsolete or redundant code blocks.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return {"error": str(e)}
        
        prompt = f"""
Analyze the following code file and provide:
1. A summary of its purpose.
2. Key functions and their functionality.
3. Connections to other files or libraries (dependencies).
4. Proposed flow diagrams in mermaid syntax (prefixed with "MERMAID_DIAGRAM:" if applicable).
5. Detection of any obsolete or redundant code blocks.

File path: {file_path}
File contents:
{content}
"""
        analysis = self.code_agent.run(prompt)
        if "MERMAID_DIAGRAM:" in analysis:
            parts = analysis.split("MERMAID_DIAGRAM:")
            analysis_text = parts[0].strip()
            mermaid_text = parts[1].strip()
        else:
            analysis_text = analysis
            mermaid_text = ""
        return {"analysis": analysis_text, "mermaid": mermaid_text}
    
    def update_analysis_in_db(self, file_path, analysis_result):
        """
        Inserts or updates the analysis for a given file in the database.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO files(codebase_id, file_path, analysis, mermaid)
            VALUES (?, ?, ?, ?)
        """, (self.codebase_id, file_path, analysis_result.get("analysis", ""), analysis_result.get("mermaid", "")))
        self.conn.commit()
    
    def perform_dependency_analysis(self, file_path):
        """
        For Python files, uses the ast module to extract import dependencies.
        """
        dependencies = []
        if file_path.endswith(".py"):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    tree = ast.parse(f.read(), filename=file_path)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            dependencies.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            dependencies.append(node.module)
            except Exception as e:
                dependencies.append("error: " + str(e))
        return list(set(dependencies))
    
    def generate_mermaid_diagram(self):
        """
        Compiles a Mermaid diagram representing file flows and connections across the codebase.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT file_path FROM files WHERE codebase_id = ?", (self.codebase_id,))
        files = cursor.fetchall()
        diagram = "graph TD\n"
        for (file_path,) in files:
            node_id = file_path.replace("/", "_").replace(".", "_")
            diagram += f"    {node_id}[\"{file_path}\"];\n"
        for (file_path,) in files:
            if file_path.endswith(".py"):
                deps = self.perform_dependency_analysis(file_path)
                src_node = file_path.replace("/", "_").replace(".", "_")
                for dep in deps:
                    for (other_file,) in files:
                        if dep in other_file:
                            dest_node = other_file.replace("/", "_").replace(".", "_")
                            diagram += f"    {src_node} --> {dest_node};\n"
        return diagram
    
    def list_obsolete_files(self):
        """
        Returns and logs files that exist in the codebase but are not part of the analysis (i.e., potentially obsolete).
        """
        all_files = self.scan_codebase()
        cursor = self.conn.cursor()
        cursor.execute("SELECT file_path FROM files WHERE codebase_id = ?", (self.codebase_id,))
        analyzed_files = set(row[0] for row in cursor.fetchall())
        obsolete = []
        for f in all_files:
            if f not in analyzed_files:
                obsolete.append(f)
                cursor.execute("INSERT INTO obsolete(codebase_id, file_path, reason) VALUES (?, ?, ?)",
                               (self.codebase_id, f, "Not connected in analysis"))
        self.conn.commit()
        return obsolete
    
    def run_analysis(self, codebase_root="."):
        """
        Executes a full analysis of the codebase:
          - Scans files
          - Analyzes each file
          - Updates the database
          - Checks for obsolete files
        Returns a summary with the codebase_id and a list of obsolete files.
        """
        file_list = self.scan_codebase(codebase_root)
        for file_path in file_list:
            analysis_result = self.analyze_file(file_path)
            self.update_analysis_in_db(file_path, analysis_result)
        obsolete_files = self.list_obsolete_files()
        return {"codebase_id": self.codebase_id, "obsolete_files": obsolete_files}


def main():
    parser = argparse.ArgumentParser(description="Analyze a codebase and generate detailed documentation.")
    parser.add_argument("--codebase_root", type=str, default=".", help="Root directory of the codebase.")
    parser.add_argument("--db_path", type=str, default="codebase_analysis.db", help="Path to the analysis database.")
    parser.add_argument("--openai_api_key", type=str, default=OPENAI_API_KEY, help="OpenAI API Key for the OpenAIServerModel")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Model to use for analysis (default: gpt-4o-mini)")
    args = parser.parse_args()
    
    analyzer = CodebaseAnalyzer(db_path=args.db_path, openai_api_key=args.openai_api_key, model=args.model)
    result = analyzer.run_analysis(args.codebase_root)
    print("Analysis complete. Codebase ID:", result["codebase_id"])
    print("Obsolete files:", result["obsolete_files"])
    print("Mermaid Diagram:")
    print(analyzer.generate_mermaid_diagram())


if __name__ == "__main__":
    main() 