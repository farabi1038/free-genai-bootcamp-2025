import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
env_path = Path('.') / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# LLM Provider Configuration
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "ollama").lower()  # 'openai' or 'ollama'

# OpenAI Configuration
OPENAI_API_ENDPOINT = os.environ.get("OPENAI_API_ENDPOINT", "https://api.openai.com/v1/chat/completions")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

# Ollama Configuration
OLLAMA_API_ENDPOINT = os.environ.get("OLLAMA_API_ENDPOINT", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")

# Application Settings
DEBUG = os.environ.get("DEBUG", "True").lower() in ("true", "1", "t")  # Default to True for better troubleshooting
VOCABULARY_API_URL = os.environ.get("VOCABULARY_API_URL", "http://localhost:5000/api/groups/1/raw")

# Default vocabulary for testing when API is not available
DEFAULT_VOCABULARY = [
    {"japanese": "りんご", "english": "apple"},
    {"japanese": "ねこ", "english": "cat"},
    {"japanese": "いぬ", "english": "dog"},
    {"japanese": "ほん", "english": "book"},
    {"japanese": "みず", "english": "water"},
    {"japanese": "あさ", "english": "morning"},
    {"japanese": "よる", "english": "night"},
    {"japanese": "たべる", "english": "eat"},
    {"japanese": "のむ", "english": "drink"},
    {"japanese": "がっこう", "english": "school"}
]