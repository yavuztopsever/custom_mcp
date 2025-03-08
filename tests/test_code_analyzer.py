import os
import pytest
import sqlite3
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime
from pathlib import Path
from mcp_tools.tools.code_analyzer import CodeAnalyzer, CodeSummary, GroupedFunctionality

@pytest.fixture
def code_analyzer():
    """Fixture to create a CodeAnalyzer instance with mocked LLM"""
    with patch('mcp_tools.tools.code_analyzer.ChatOpenAI') as mock_llm:
        analyzer = CodeAnalyzer()
        analyzer.llm = mock_llm
        yield analyzer

@pytest.fixture
def sample_files(tmp_path):
    """Create sample files for testing"""
    # Create test files
    file1 = tmp_path / "test1.py"
    file2 = tmp_path / "test2.py"
    
    file1.write_text("def test1(): pass")
    file2.write_text("def test2(): pass")
    
    return [str(file1), str(file2)]

def test_init_database(code_analyzer, tmp_path):
    """Test database initialization"""
    code_analyzer.db_path = str(tmp_path / "test.db")
    code_analyzer._init_database()
    
    assert Path(code_analyzer.db_path).exists()
    
    # Verify tables were created
    conn = sqlite3.connect(code_analyzer.db_path)
    cursor = conn.cursor()
    
    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    
    assert "file_summaries" in tables
    assert "functionality_groups" in tables
    
    conn.close()

def test_collect_scripts(code_analyzer, tmp_path):
    """Test script collection functionality"""
    # Create test directory structure
    (tmp_path / "src").mkdir()
    (tmp_path / "src/test1.py").write_text("print('test1')")
    (tmp_path / "src/test2.py").write_text("print('test2')")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git/test.py").write_text("print('ignore')")
    
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [
            (str(tmp_path), ['src', '.git'], []),
            (str(tmp_path / 'src'), [], ['test1.py', 'test2.py']),
            (str(tmp_path / '.git'), [], ['test.py'])
        ]
        
        scripts = code_analyzer.collect_scripts()
        
        assert len(scripts) == 2
        assert any('test1.py' in s for s in scripts)
        assert any('test2.py' in s for s in scripts)
        assert not any('.git' in s for s in scripts)

def test_analyze_file(code_analyzer, tmp_path):
    """Test file analysis functionality"""
    test_file = tmp_path / "test.py"
    test_file.write_text("def example(): return 'test'")
    
    # Mock the LLM chain response
    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "file_path": str(test_file),
        "functionality": "Test function",
        "dependencies": ["pytest"],
        "complexity_score": 1
    })
    code_analyzer.llm.invoke.return_value = mock_response
    
    result = code_analyzer.analyze_file(str(test_file))
    
    assert isinstance(result, CodeSummary)
    assert result.file_path == str(test_file)
    assert result.functionality == "Test function"
    assert result.dependencies == ["pytest"]
    assert result.complexity_score == 1

def test_store_summary(code_analyzer, tmp_path):
    """Test storing summary in database"""
    code_analyzer.db_path = str(tmp_path / "test.db")
    code_analyzer._init_database()
    
    summary = CodeSummary(
        file_path="test.py",
        functionality="Test function",
        dependencies=["pytest"],
        complexity_score=1
    )
    
    code_analyzer.store_summary(summary)
    
    # Verify stored data
    conn = sqlite3.connect(code_analyzer.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM file_summaries WHERE file_path=?", ("test.py",))
    row = cursor.fetchone()
    
    assert row is not None
    assert row[0] == "test.py"
    assert row[1] == "Test function"
    assert json.loads(row[2]) == ["pytest"]
    assert row[3] == 1
    
    conn.close()

def test_group_functionalities(code_analyzer, tmp_path):
    """Test functionality grouping"""
    code_analyzer.db_path = str(tmp_path / "test.db")
    code_analyzer._init_database()
    
    # Store some test summaries
    summaries = [
        CodeSummary(
            file_path="test1.py",
            functionality="Data processing",
            dependencies=["pandas"],
            complexity_score=3
        ),
        CodeSummary(
            file_path="test2.py",
            functionality="Data processing helper",
            dependencies=["numpy"],
            complexity_score=2
        )
    ]
    
    for summary in summaries:
        code_analyzer.store_summary(summary)
    
    # Mock the LLM chain response
    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "group_name": "Data Processing",
        "files": ["test1.py", "test2.py"],
        "common_functionality": "Data processing operations",
        "consolidation_recommendation": "Merge into single module"
    })
    code_analyzer.llm.invoke.return_value = mock_response
    
    result = code_analyzer.group_functionalities()
    
    assert isinstance(result, GroupedFunctionality)
    assert result.group_name == "Data Processing"
    assert len(result.files) == 2
    assert result.common_functionality == "Data processing operations"

def test_run_analysis(code_analyzer, tmp_path, sample_files):
    """Test complete analysis pipeline"""
    code_analyzer.db_path = str(tmp_path / "test.db")
    code_analyzer._init_database()  # Initialize database
    
    mock_summary = CodeSummary(
        file_path="test.py",
        functionality="Test function",
        dependencies=["pytest"],
        complexity_score=1
    )
    
    # Mock the LLM chain response
    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "group_name": "Test Group",
        "files": ["test.py"],
        "common_functionality": "Test functionality",
        "consolidation_recommendation": "No changes needed"
    })
    
    with patch.object(code_analyzer, 'collect_scripts') as mock_collect:
        with patch.object(code_analyzer, 'analyze_file') as mock_analyze:
            mock_collect.return_value = sample_files
            mock_analyze.return_value = mock_summary
            code_analyzer.llm.invoke.return_value = mock_response
            
            result = code_analyzer.run_analysis()
            
            assert isinstance(result, GroupedFunctionality)
            assert mock_collect.called
            assert mock_analyze.call_count == len(sample_files)

def test_error_handling(code_analyzer, tmp_path):
    """Test error handling in analysis"""
    code_analyzer.db_path = str(tmp_path / "test.db")
    code_analyzer._init_database()  # Initialize database
    
    # Test file that will raise an error
    error_file = tmp_path / "error.py"
    error_file.write_text("invalid python code {")
    
    with patch.object(code_analyzer, 'collect_scripts') as mock_collect:
        mock_collect.return_value = [str(error_file)]
        
        # Mock analyze_file to raise an exception
        with patch.object(code_analyzer, 'analyze_file', side_effect=Exception("Test error")):
            # Should not raise exception but log error
            code_analyzer.run_analysis()
            
            # Verify error was logged (would need to check log file or mock logger) 