#!/bin/bash

echo "🧹 Clearing Python cache files..."
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

echo "🔄 Clearing Streamlit cache..."
rm -rf ~/.streamlit/cache

echo "🗑️ Clearing Ollama process memory..."
if command -v pkill &> /dev/null; then
    pkill -f ollama || true
fi

echo "📊 Clearing system cache..."
# Free page cache, dentries and inodes
sync
if [ "$EUID" -eq 0 ]; then
    echo 3 > /proc/sys/vm/drop_caches
    echo "System caches cleared."
else
    echo "Note: Running as non-root user, skipping system cache clear"
fi

# Wait a moment for processes to restart
sleep 1

echo "🚀 Starting Ollama service..."
ollama serve &

# Wait for Ollama to start
sleep 3

echo "🚀 Starting app with memory optimization..."
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_HEADLESS=true
export PYTHONOPTIMIZE=1  # -O flag for Python
export PYTHONUNBUFFERED=1  # Unbuffered stdout and stderr

python run.py "$@"

echo "Application exited." 