#!/usr/bin/env python3
"""
Helper script to update .env file with the latest configuration settings.
This will ensure your environment is using the llama3.2:1b model.
"""

import os
import sys
from pathlib import Path
import shutil

def main():
    """Update the .env file with the current .env.example"""
    script_dir = Path(__file__).parent
    env_example_path = script_dir / '.env.example'
    env_path = script_dir / '.env'
    
    if not env_example_path.exists():
        print("Error: .env.example file not found.")
        return 1
    
    # Check if .env exists and back it up if it does
    if env_path.exists():
        backup_path = env_path.with_suffix('.env.backup')
        print(f"Backing up existing .env to {backup_path}")
        shutil.copy2(env_path, backup_path)
    
    # Copy .env.example to .env
    print("Creating new .env file from .env.example...")
    shutil.copy2(env_example_path, env_path)
    print("✅ Updated .env file successfully!")
    
    print("\nYour application is now configured to use the llama3.2:1b model.")
    print("To verify your configuration, run:")
    print("  python check_ollama.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 