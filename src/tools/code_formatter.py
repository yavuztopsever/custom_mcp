from typing import Dict, Any, Optional
from pathlib import Path
import black
import isort

class CodeFormatterTool:
    """Tool for formatting Python code."""

    def format(self, file_path: str, line_length: int = 88, use_black: bool = True, use_isort: bool = True) -> str:
        """Format Python code using black and isort.

        Args:
            file_path: Path to the Python file to format.
            line_length: Maximum line length for formatting.
            use_black: Whether to use black for code formatting.
            use_isort: Whether to use isort for import sorting.

        Returns:
            A string containing the formatted code.
        """
        try:
            with open(file_path, 'r') as f:
                code = f.read()

            formatted_code = code
            changes_made = []

            if use_black:
                try:
                    mode = black.Mode(line_length=line_length)
                    formatted_code = black.format_str(formatted_code, mode=mode)
                    changes_made.append("Applied black formatting")
                except Exception as e:
                    changes_made.append(f"Error applying black: {str(e)}")

            if use_isort:
                try:
                    isort_config = isort.Config(line_length=line_length)
                    formatted_code = isort.code(formatted_code, config=isort_config)
                    changes_made.append("Applied isort formatting")
                except Exception as e:
                    changes_made.append(f"Error applying isort: {str(e)}")

            # Write the formatted code back to the file
            with open(file_path, 'w') as f:
                f.write(formatted_code)

            return "\n".join([
                "Code Formatting Report:",
                "",
                "Changes Made:",
                *[f"- {change}" for change in changes_made]
            ])

        except Exception as e:
            return f"Error formatting code: {str(e)}" 