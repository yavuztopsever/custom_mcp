#!/bin/bash

# Exit on error
set -e

# Load configuration
CONFIG_FILE="config/settings.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Configuration file not found at $CONFIG_FILE"
    exit 1
fi

# Function to read JSON values
get_json_value() {
    python3 -c "import json,sys;print(json.load(open('$CONFIG_FILE'))$1)" 2>/dev/null
}

# Setup variables from config
OUTPUT_DIR=$(get_json_value "['build']['output_dir']")
TEMP_DIR=$(get_json_value "['build']['temp_dir']")
CLEAN_BUILD=$(get_json_value "['build']['clean_build']")
JAVA_VERSION=$(get_json_value "['java_version']")

echo "=== MCP Build Script ==="
echo "Java Version: $JAVA_VERSION"
echo "Output Directory: $OUTPUT_DIR"
echo "Temporary Directory: $TEMP_DIR"

# Create necessary directories
mkdir -p "$OUTPUT_DIR" "$TEMP_DIR"

# Clean build if configured
if [ "$CLEAN_BUILD" = "true" ]; then
    echo "Cleaning build directories..."
    rm -rf "$OUTPUT_DIR"/* "$TEMP_DIR"/*
fi

# Run organization script
echo "Organizing project files..."
python3 scripts/organize.py

# Check if we're using Gradle
if [ -f "build.gradle" ]; then
    echo "Gradle project detected, using Gradle for build..."
    if [ -f "./gradlew" ]; then
        ./gradlew build
    else
        gradle build
    fi
else
    # Traditional MCP build process
    echo "Using traditional MCP build process..."
    
    # Compile Java files
    echo "Compiling Java files..."
    find src/main/java -name "*.java" > sources.txt
    javac -d "$OUTPUT_DIR" @sources.txt
    rm sources.txt
    
    # Copy resources
    echo "Copying resources..."
    if [ -d "src/main/resources" ]; then
        cp -r src/main/resources/* "$OUTPUT_DIR/"
    fi
fi

# Generate documentation if configured
if [ "$(get_json_value "['documentation']['generate_javadoc']")" = "true" ]; then
    echo "Generating Javadoc..."
    JAVADOC_DIR=$(get_json_value "['documentation']['output_dir']")
    mkdir -p "$JAVADOC_DIR"
    find src/main/java -name "*.java" > sources.txt
    javadoc -d "$JAVADOC_DIR" @sources.txt
    rm sources.txt
fi

echo "Build completed successfully!" 