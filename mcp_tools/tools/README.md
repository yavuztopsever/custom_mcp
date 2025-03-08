# MCP Code Analyzer Tool

A powerful code analysis tool that uses GPT-4 to analyze, summarize, and suggest consolidation of code across your MCP project.

## Features

- Scans all script files in the project directory
- Analyzes each file's functionality using GPT-4
- Groups files with overlapping functionality
- Provides consolidation recommendations
- Stores analysis results in a SQLite database

## Prerequisites

- Python 3.8+
- OpenAI API key (set in `.env` file)
- Required Python packages (specified in requirements.txt)

## Installation

The tool is automatically installed as part of the MCP tools package. Make sure you have all dependencies installed:

```bash
pip install -r requirements.txt
```

## Usage

1. Make sure your OpenAI API key is set in the `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

2. Run the tool from the project root:
```bash
python mcp_tools/tools/code_analyzer.py
```

## Output

The tool will:
1. Log progress to `mcp_tools/logs/code_analyzer.log`
2. Store results in `mcp_tools/data/code_analysis.db`
3. Print a summary of grouped functionalities to the console

## Database Schema

### File Summaries Table
- file_path (TEXT): Path to the analyzed file
- functionality (TEXT): Summary of the file's functionality
- dependencies (TEXT): JSON list of dependencies
- complexity_score (INTEGER): Estimated complexity (1-10)
- analyzed_at (TIMESTAMP): Analysis timestamp

### Functionality Groups Table
- group_name (TEXT): Name of the functionality group
- files (TEXT): JSON list of files in the group
- common_functionality (TEXT): Description of shared functionality
- consolidation_recommendation (TEXT): Suggestions for consolidation
- created_at (TIMESTAMP): Group creation timestamp

## Example Output

```
Group: Data Processing
Files:
  - src/data/processor.py
  - src/utils/data_helper.py
Common Functionality: Both files handle data preprocessing and validation
Consolidation Recommendation: Merge data_helper.py functions into processor.py

Group: Configuration Management
Files:
  - src/config/loader.py
  - src/utils/config_utils.py
Common Functionality: Configuration file handling and validation
Consolidation Recommendation: Create a unified configuration module
``` 