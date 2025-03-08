from typing import Dict, Any, Optional
import ast
from pathlib import Path

class CodeAnalyzerTool:
    """Tool for analyzing Python code."""

    def analyze(self, file_path: str) -> str:
        """Analyze Python code for potential issues and improvements.

        Args:
            file_path: Path to the Python file to analyze.

        Returns:
            A string containing the analysis results.
        """
        try:
            with open(file_path, 'r') as f:
                code = f.read()

            tree = ast.parse(code)
            analyzer = CodeAnalyzer()
            analyzer.visit(tree)

            return analyzer.get_report()
        except Exception as e:
            return f"Error analyzing code: {str(e)}"

class CodeAnalyzer(ast.NodeVisitor):
    """AST visitor for code analysis."""

    def __init__(self):
        self.issues = []
        self.stats = {
            'functions': 0,
            'classes': 0,
            'imports': 0,
            'lines': 0
        }

    def visit_FunctionDef(self, node):
        self.stats['functions'] += 1
        if not ast.get_docstring(node):
            self.issues.append(f"Function '{node.name}' is missing a docstring")
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.stats['classes'] += 1
        if not ast.get_docstring(node):
            self.issues.append(f"Class '{node.name}' is missing a docstring")
        self.generic_visit(node)

    def visit_Import(self, node):
        self.stats['imports'] += 1
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self.stats['imports'] += 1
        self.generic_visit(node)

    def get_report(self) -> str:
        """Generate a report of the analysis results."""
        report = ["Code Analysis Report:", ""]
        
        # Add statistics
        report.append("Statistics:")
        for key, value in self.stats.items():
            report.append(f"- {key.capitalize()}: {value}")
        report.append("")
        
        # Add issues
        if self.issues:
            report.append("Issues Found:")
            for issue in self.issues:
                report.append(f"- {issue}")
        else:
            report.append("No issues found.")
        
        return "\n".join(report) 