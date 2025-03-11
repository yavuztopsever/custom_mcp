# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory to /app
WORKDIR /app

# Copy the project files into the container
COPY . /app

# Upgrade pip and install dependencies if a requirements.txt is present
RUN pip install --upgrade pip && \
    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Install the local mcp package in editable mode to ensure 'mcp' module is installed
RUN pip install -e .

# Explicitly install pydantic-settings to resolve missing module errors
RUN pip install --upgrade "pydantic-settings>=1.0.1"
RUN pip install smolagents

# Expose port 8000 (adjust if the server uses a different port)
EXPOSE 8000

# Run the MCP server; running in the foreground for Docker best practices
CMD ["python", "src/mcp/server/fastmcp/server.py"] 