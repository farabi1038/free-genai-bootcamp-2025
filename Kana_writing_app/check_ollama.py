#!/usr/bin/env python3
"""
Ollama Integration Helper for Kana Writing Practice

This script helps check if Ollama is properly installed and configured
for use with the Kana Writing Practice application.
"""

import os
import sys
import subprocess
import platform
import requests
import time
from pathlib import Path

# Get the config
sys.path.insert(0, str(Path(__file__).parent))
from config import OLLAMA_API_ENDPOINT, OLLAMA_MODEL

# Set the model name - ensure it matches the one in config.py
MODEL_NAME = "llama3.2:1b"

def check_ollama_installed():
    """Check if Ollama is installed on the system"""
    system = platform.system().lower()
    
    try:
        if system == "windows":
            # On Windows, check if the Ollama executable exists
            # Typical install locations
            windows_paths = [
                os.path.expanduser("~\\AppData\\Local\\Programs\\Ollama\\ollama.exe"),
                "C:\\Program Files\\Ollama\\ollama.exe",
                "C:\\Program Files (x86)\\Ollama\\ollama.exe"
            ]
            return any(os.path.exists(path) for path in windows_paths)
        else:
            # On Linux/macOS, try to run ollama command
            result = subprocess.run(
                ["which", "ollama"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            return result.returncode == 0
    except Exception as e:
        print(f"Error checking for Ollama installation: {e}")
        return False

def check_ollama_running():
    """Check if Ollama server is running"""
    try:
        # Extract base URL from the endpoint
        base_url = OLLAMA_API_ENDPOINT.rsplit("/api/", 1)[0]
        response = requests.get(f"{base_url}/api/tags")
        return response.status_code == 200
    except Exception:
        return False

def check_model_available(model_name):
    """Check if the specified model is available in Ollama"""
    try:
        base_url = OLLAMA_API_ENDPOINT.rsplit("/api/", 1)[0]
        response = requests.get(f"{base_url}/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return any(model.get("name") == model_name for model in models)
        return False
    except Exception:
        return False

def pull_model(model_name):
    """Pull the specified model using Ollama CLI"""
    try:
        print(f"Downloading model {model_name}...")
        result = subprocess.run(
            ["ollama", "pull", model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            print(f"Successfully pulled model {model_name}")
            return True
        else:
            print(f"Failed to pull model: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error pulling model: {e}")
        return False

def main():
    """Main function to check Ollama and model availability"""
    print("Checking Ollama integration for Kana Writing Practice...\n")
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        print("❌ Ollama is not installed on your system.")
        print("\nTo install Ollama, please visit: https://ollama.com/download")
        print("\nAfter installing, restart this application.")
        return 1
    
    print("✅ Ollama is installed on your system.")
    
    # Check if Ollama server is running
    if not check_ollama_running():
        print("\n❌ Ollama server is not running.")
        print("\nPlease start Ollama and try again.")
        print("- On Windows: Start Ollama from the Start menu")
        print("- On macOS: Open Ollama from Applications")
        print("- On Linux: Run 'ollama serve' in a terminal")
        return 2
    
    print("✅ Ollama server is running.")
    
    # Use the MODEL_NAME constant to ensure consistency
    model_to_check = MODEL_NAME
    
    # Check if model is available
    if not check_model_available(model_to_check):
        print(f"\n❌ Required model '{model_to_check}' is not available in Ollama.")
        print("\nWould you like to download it now? (y/n)")
        response = input("> ").strip().lower()
        
        if response in ["y", "yes"]:
            success = pull_model(model_to_check)
            if not success:
                print(f"\nFailed to download model '{model_to_check}'.")
                print(f"You can download it manually by running: ollama pull {model_to_check}")
                return 3
        else:
            print(f"\nPlease download the model manually with: ollama pull {model_to_check}")
            print("Or change the model in your .env file to one you already have.")
            return 3
    
    print(f"✅ Model '{model_to_check}' is available.")
    print("\n🎉 Your Ollama integration is properly configured!")
    print("You can now run the Kana Writing Practice application.")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 