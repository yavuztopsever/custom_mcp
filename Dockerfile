FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p /app/mcp_tools /app/config /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV MCP_SERVER_HOST=0.0.0.0
ENV LOG_LEVEL=INFO

# Expose the WebSocket port
EXPOSE 25565

# Start the MCP server using the Python module
CMD ["python", "-m", "src"] 