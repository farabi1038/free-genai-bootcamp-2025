#!/bin/bash

# Check if Ollama is running
echo "Checking if Ollama is running..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama is running!"
else
    echo "⚠️ Warning: Ollama is not running or not accessible at http://localhost:11434"
    echo "Please start Ollama before running the application."
    echo "If Ollama is already running on a different host or port, configure with environment variables."
fi

# Create output directory
mkdir -p output

# Run the Streamlit application
echo "Starting Streamlit application..."
streamlit run app.py 