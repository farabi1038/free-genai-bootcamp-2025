#!/bin/bash
# Script to run the Vocabulary Importer using Docker

# Set default model if not specified
export LLM_MODEL_ID=${LLM_MODEL_ID:-llama2:13b}
echo "Using LLM model: $LLM_MODEL_ID"

# Create output directory if it doesn't exist
mkdir -p output

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running or not installed"
    echo "Please start Docker and try again"
    exit 1
fi

# Pull model before starting (optional but recommended)
echo "Pre-pulling Ollama model $LLM_MODEL_ID..."
if docker run --rm -v ollama-data:/root/.ollama ollama/ollama pull $LLM_MODEL_ID; then
    echo "✅ Model pre-pulled successfully"
else
    echo "⚠️ Warning: Failed to pre-pull model. Container will attempt to pull on startup."
fi

# Start the Docker Compose stack
echo "Starting Vocabulary Importer stack with Docker Compose..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
for i in {1..10}; do
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        break
    fi
    echo "Waiting for Ollama to be ready... ($i/10)"
    sleep 3
done

# Provide user information
echo ""
echo "🚀 Vocabulary Importer is running!"
echo "📊 Access the application at: http://localhost:8501"
echo ""
echo "📝 To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "🛑 To stop the application:"
echo "  docker-compose down"
echo "" 