import pytest
import os
from pathlib import Path
from src.tools.code_analyzer import CodeAnalyzerTool
from src.tools.code_formatter import CodeFormatterTool
from src.tools.code_documenter import CodeDocumenterTool

@pytest.fixture
def sample_code_file(tmp_path):
    code = """
def hello(name):
    print(f"Hello, {name}!")

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def greet(self):
        print(f"Hi, I'm {self.name}")
"""
    file_path = tmp_path / "test.py"
    with open(file_path, "w") as f:
        f.write(code)
    return file_path

@pytest.mark.asyncio
async def test_code_analyzer(sample_code_file):
    analyzer = CodeAnalyzerTool()
    result = await analyzer.execute({
        "file_path": str(sample_code_file),
        "analysis_type": "structure"
    })
    
    assert result["success"] is True
    assert len(result["classes"]) == 1
    assert len(result["functions"]) == 3
    assert result["classes"][0]["name"] == "Person"

@pytest.mark.asyncio
async def test_code_formatter(sample_code_file):
    formatter = CodeFormatterTool()
    result = await formatter.execute({
        "file_path": str(sample_code_file),
        "line_length": 88
    })
    
    assert result["success"] is True

@pytest.mark.asyncio
async def test_code_documenter(sample_code_file):
    documenter = CodeDocumenterTool()
    result = await documenter.execute({
        "file_path": str(sample_code_file),
        "doc_style": "google"
    })
    
    assert result["success"] is True
    assert len(result["functions_documented"]) > 0
    assert len(result["classes_documented"]) > 0 