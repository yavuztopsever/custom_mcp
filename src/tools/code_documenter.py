from typing import Dict, Any, Optional
from pathlib import Path
import ast
import libcst as cst

class CodeDocumenterTool:
    """Tool for generating and updating Python code documentation."""

    def document(self, file_path: str, doc_style: str = "google", update_existing: bool = False) -> str:
        """Generate or update Python code documentation.

        Args:
            file_path: Path to the Python file to document.
            doc_style: Documentation style to use (google, numpy, or sphinx).
            update_existing: Whether to update existing docstrings.

        Returns:
            A string containing the documentation results.
        """
        try:
            with open(file_path, 'r') as f:
                code = f.read()

            # Parse the code into an AST
            tree = ast.parse(code)
            documenter = CodeDocumenter(doc_style)
            documenter.visit(tree)

            # Generate documentation using libcst
            source = cst.parse_module(code)
            transformer = DocstringTransformer(documenter.docs, update_existing)
            modified_tree = source.visit(transformer)

            # Write the documented code back to the file
            with open(file_path, 'w') as f:
                f.write(modified_tree.code)

            return documenter.get_report()

        except Exception as e:
            return f"Error documenting code: {str(e)}"

class CodeDocumenter(ast.NodeVisitor):
    """AST visitor for collecting documentation information."""

    def __init__(self, doc_style: str):
        self.doc_style = doc_style
        self.docs = {}
        self.stats = {
            'functions_documented': 0,
            'classes_documented': 0,
            'missing_docs': 0
        }

    def visit_FunctionDef(self, node):
        """Visit a function definition node."""
        doc = self._generate_function_doc(node)
        self.docs[node.lineno] = doc
        if not ast.get_docstring(node):
            self.stats['missing_docs'] += 1
        else:
            self.stats['functions_documented'] += 1
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Visit a class definition node."""
        doc = self._generate_class_doc(node)
        self.docs[node.lineno] = doc
        if not ast.get_docstring(node):
            self.stats['missing_docs'] += 1
        else:
            self.stats['classes_documented'] += 1
        self.generic_visit(node)

    def _generate_function_doc(self, node: ast.FunctionDef) -> str:
        """Generate a docstring for a function."""
        args = [arg.arg for arg in node.args.args]
        returns = self._get_return_type(node)

        if self.doc_style == "google":
            doc = [f"{node.name} function.", ""]
            if args:
                doc.extend(["Args:", *[f"    {arg}: Description of {arg}." for arg in args], ""])
            if returns:
                doc.extend(["Returns:", f"    {returns}"])
        elif self.doc_style == "numpy":
            doc = [f"{node.name} function.", ""]
            if args:
                arg_docs = []
                for arg in args:
                    arg_docs.extend([f"{arg} : type", f"    Description of {arg}."])
                doc.extend(["Parameters", "----------", *arg_docs, ""])
            if returns:
                doc.extend(["Returns", "-------", returns])
        else:  # sphinx
            doc = [f"{node.name} function.", ""]
            if args:
                doc.extend([*[f":param {arg}: Description of {arg}." for arg in args], ""])
            if returns:
                doc.append(f":returns: {returns}")

        return "\n".join(doc)

    def _generate_class_doc(self, node: ast.ClassDef) -> str:
        """Generate a docstring for a class."""
        if self.doc_style == "google":
            return f"{node.name} class.\n\nAttributes:\n    Add class attributes here."
        elif self.doc_style == "numpy":
            return f"{node.name} class.\n\nAttributes\n----------\nAdd class attributes here."
        else:  # sphinx
            return f"{node.name} class.\n\n:ivar: Add class attributes here."

    def _get_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Get the return type from a function's return annotation."""
        if node.returns:
            return ast.unparse(node.returns)
        return None

    def get_report(self) -> str:
        """Generate a report of the documentation results."""
        report = ["Documentation Report:", ""]
        
        # Add statistics
        report.append("Statistics:")
        for key, value in self.stats.items():
            report.append(f"- {key.replace('_', ' ').capitalize()}: {value}")
        report.append("")
        
        # Add summary
        total_docs = self.stats['functions_documented'] + self.stats['classes_documented']
        if total_docs > 0:
            report.append(f"Successfully documented {total_docs} items using {self.doc_style} style.")
        if self.stats['missing_docs'] > 0:
            report.append(f"Added documentation to {self.stats['missing_docs']} items that were missing docstrings.")
        
        return "\n".join(report)

class DocstringTransformer(cst.CSTTransformer):
    """CST transformer for adding or updating docstrings."""

    def __init__(self, docs: Dict[int, str], update_existing: bool):
        self.docs = docs
        self.update_existing = update_existing

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        """Process a function definition node."""
        return self._maybe_add_docstring(original_node, updated_node)

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.ClassDef:
        """Process a class definition node."""
        return self._maybe_add_docstring(original_node, updated_node)

    def _maybe_add_docstring(
        self, original_node: cst.CSTNode, updated_node: cst.CSTNode
    ) -> cst.CSTNode:
        """Add or update a docstring if needed."""
        if not hasattr(original_node, "body"):
            return updated_node

        # Check if we have documentation for this node
        if original_node.lineno not in self.docs:
            return updated_node

        # Get the new docstring
        new_doc = self.docs[original_node.lineno]

        # Check if there's an existing docstring
        has_docstring = (
            isinstance(original_node.body.body[0], cst.SimpleStatementLine)
            and isinstance(original_node.body.body[0].body[0], cst.Expr)
            and isinstance(original_node.body.body[0].body[0].value, cst.SimpleString)
        )

        if has_docstring and not self.update_existing:
            return updated_node

        # Create the new docstring node
        docstring = cst.SimpleString(f'"""{new_doc}"""')
        docstring_stmt = cst.SimpleStatementLine([cst.Expr(docstring)])

        # Update the body
        if has_docstring:
            new_body = [docstring_stmt] + list(updated_node.body.body[1:])
        else:
            new_body = [docstring_stmt] + list(updated_node.body.body)

        return updated_node.with_changes(
            body=updated_node.body.with_changes(body=new_body)
        ) 