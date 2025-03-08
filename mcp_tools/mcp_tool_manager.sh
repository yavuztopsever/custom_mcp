#!/bin/bash

# MCP Tool Manager
# This script manages and executes MCP tools

# Set script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment if it exists
if [ -d "$PROJECT_ROOT/.venv" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Function to display usage
show_usage() {
    echo "Usage: $0 <tool_name> [arguments...]"
    echo "Available tools:"
    ls "$SCRIPT_DIR/tools" | grep -E "\.py$|\.sh$" | sed 's/\.[^.]*$//' | sed 's/^/  - /'
}

# Check if a tool name is provided
if [ -z "$1" ]; then
    show_usage
    exit 1
fi

TOOL_NAME="$1"
shift  # Remove the tool name from the arguments

# Check for Python tool
if [ -f "$SCRIPT_DIR/tools/${TOOL_NAME}.py" ]; then
    python "$SCRIPT_DIR/tools/${TOOL_NAME}.py" "$@"
# Check for Shell tool
elif [ -f "$SCRIPT_DIR/tools/${TOOL_NAME}.sh" ]; then
    bash "$SCRIPT_DIR/tools/${TOOL_NAME}.sh" "$@"
else
    echo "Error: Tool '${TOOL_NAME}' not found"
    show_usage
    exit 1
fi 