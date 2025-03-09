import os
import sys
import importlib
import subprocess
import platform
import shutil
import logging
import requests
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Required packages from requirements.txt
REQUIRED_PACKAGES = [
    "streamlit",
    "fastapi", 
    "uvicorn", 
    "pydantic",
    "sqlalchemy", 
    "yt_dlp", 
    "youtube_transcript_api",
    "whisper", 
    "ollama",
    "pydub",
    "pyttsx3",
    "gtts",
    "python-dotenv",
    "requests",
    "numpy",
    "pandas"
]

# External system dependencies
SYSTEM_DEPENDENCIES = {
    "ffmpeg": {
        "windows": "ffmpeg -version",
        "linux": "ffmpeg -version",
        "darwin": "ffmpeg -version",
    }
}

# Ollama configuration
OLLAMA_HOST = "127.0.0.1"
OLLAMA_PORT = 11434
DEFAULT_MODEL = "llama3"

def check_python_packages():
    """
    Check if required Python packages are installed
    
    Returns:
        tuple: (missing_packages, installed_packages)
    """
    missing_packages = []
    installed_packages = []
    
    for package in REQUIRED_PACKAGES:
        try:
            # Try to import the package
            importlib.import_module(package)
            installed_packages.append(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages, installed_packages

def install_packages(packages):
    """
    Install missing packages using pip
    
    Args:
        packages: List of packages to install
        
    Returns:
        bool: True if installation was successful
    """
    if not packages:
        return True
    
    logger.info(f"Installing missing packages: {', '.join(packages)}")
    
    try:
        # Create the pip install command
        cmd = [sys.executable, "-m", "pip", "install"] + packages
        
        # Run the command
        subprocess.check_call(cmd)
        
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing packages: {str(e)}")
        return False

def check_system_dependencies():
    """
    Check if required system dependencies are installed
    
    Returns:
        tuple: (missing_deps, installed_deps)
    """
    system = platform.system().lower()
    missing_deps = []
    installed_deps = []
    
    for dep, commands in SYSTEM_DEPENDENCIES.items():
        if system in commands:
            cmd = commands[system]
            
            try:
                # Try to run the command to check if it's installed
                subprocess.check_call(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                installed_deps.append(dep)
            except (subprocess.CalledProcessError, FileNotFoundError):
                missing_deps.append(dep)
    
    return missing_deps, installed_deps

def check_ollama():
    """
    Check if Ollama is installed and running
    
    Returns:
        tuple: (is_installed, is_running, available_models)
    """
    # Check if Ollama is installed
    ollama_path = shutil.which("ollama")
    is_installed = ollama_path is not None
    
    # Check if Ollama is running and what models are available
    is_running = False
    available_models = []
    
    if is_installed:
        try:
            response = requests.get(f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/tags", timeout=5)
            
            if response.status_code == 200:
                is_running = True
                models_data = response.json()
                if "models" in models_data:
                    available_models = [model["name"] for model in models_data["models"]]
        except:
            is_running = False
    
    return is_installed, is_running, available_models

def check_ffmpeg():
    """
    Check if ffmpeg is installed and available
    
    Returns:
        bool: True if ffmpeg is available
    """
    try:
        subprocess.check_call(
            "ffmpeg -version", 
            shell=True, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_whisper_models():
    """
    Check if Whisper models are available in the cache directory
    
    Returns:
        tuple: (is_available, info)
    """
    try:
        import whisper
        import whisper.utils
        
        # Get the current supported models
        available_models = whisper.available_models()
        
        # Try to load a base model to verify
        try:
            model = whisper.load_model('base')
            is_available = True
            info = f"Whisper models available: {', '.join(available_models)}"
        except Exception as e:
            is_available = False
            info = f"Error loading Whisper model: {str(e)}"
        
        return is_available, info
        
    except ImportError:
        return False, "Whisper package not installed"

def print_results(results):
    """Print a formatted report of dependency check results"""
    logger.info("=== Dependency Check Results ===")
    
    # Python packages
    logger.info("Python Packages:")
    if results["missing_packages"]:
        logger.warning(f"  Missing packages: {', '.join(results['missing_packages'])}")
    else:
        logger.info(f"  All required packages installed ({len(results['installed_packages'])})")
    
    # System dependencies
    logger.info("System Dependencies:")
    if results["missing_system_deps"]:
        logger.warning(f"  Missing dependencies: {', '.join(results['missing_system_deps'])}")
    else:
        logger.info(f"  All required system dependencies installed ({len(results['installed_system_deps'])})")
    
    # Ollama
    logger.info("Ollama:")
    if not results["ollama_installed"]:
        logger.warning("  Ollama is not installed")
    else:
        logger.info("  Ollama is installed")
        
        if not results["ollama_running"]:
            logger.warning("  Ollama is not running")
        else:
            logger.info("  Ollama is running")
            
            if DEFAULT_MODEL in results["ollama_models"]:
                logger.info(f"  Recommended model '{DEFAULT_MODEL}' is available")
            else:
                logger.warning(f"  Recommended model '{DEFAULT_MODEL}' is not available")
                if results["ollama_models"]:
                    logger.info(f"  Available models: {', '.join(results['ollama_models'])}")
                else:
                    logger.warning("  No models available")
    
    # Whisper
    logger.info("Whisper:")
    if results["whisper_available"]:
        logger.info(f"  {results['whisper_info']}")
    else:
        logger.warning(f"  {results['whisper_info']}")
    
    # FFmpeg
    logger.info("FFmpeg:")
    if results["ffmpeg_available"]:
        logger.info("  FFmpeg is installed and available")
    else:
        logger.warning("  FFmpeg is not installed or not available (required for audio processing)")
    
    # Overall status
    logger.info("Overall:")
    if results["all_requirements_met"]:
        logger.info("  All requirements met!")
    else:
        logger.warning("  Some requirements are not met. Please address the issues above.")

def check_all_dependencies(auto_install=False):
    """
    Check all dependencies and return results
    
    Args:
        auto_install: Whether to automatically install missing Python packages
        
    Returns:
        dict: Results of all dependency checks
    """
    # Check Python packages
    missing_packages, installed_packages = check_python_packages()
    
    # Auto-install missing packages if requested
    if auto_install and missing_packages:
        if install_packages(missing_packages):
            # Recheck after installation
            missing_packages, installed_packages = check_python_packages()
    
    # Check system dependencies
    missing_system_deps, installed_system_deps = check_system_dependencies()
    
    # Check Ollama
    ollama_installed, ollama_running, ollama_models = check_ollama()
    
    # Check FFmpeg
    ffmpeg_available = check_ffmpeg()
    
    # Check Whisper models
    whisper_available, whisper_info = check_whisper_models()
    
    # Determine if all requirements are met
    all_requirements_met = (
        not missing_packages and
        not missing_system_deps and
        ollama_installed and
        ollama_running and
        (DEFAULT_MODEL in ollama_models) and
        whisper_available and
        ffmpeg_available
    )
    
    # Collect results
    results = {
        "missing_packages": missing_packages,
        "installed_packages": installed_packages,
        "missing_system_deps": missing_system_deps,
        "installed_system_deps": installed_system_deps,
        "ollama_installed": ollama_installed,
        "ollama_running": ollama_running,
        "ollama_models": ollama_models,
        "whisper_available": whisper_available,
        "whisper_info": whisper_info,
        "ffmpeg_available": ffmpeg_available,
        "all_requirements_met": all_requirements_met
    }
    
    return results

def main():
    """Main function to run dependency checks"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Check dependencies for Listening Learning App")
    parser.add_argument("--auto-install", action="store_true", help="Automatically install missing Python packages")
    args = parser.parse_args()
    
    # Run all checks
    results = check_all_dependencies(auto_install=args.auto_install)
    
    # Print results
    print_results(results)
    
    # Return exit code
    return 0 if results["all_requirements_met"] else 1

if __name__ == "__main__":
    sys.exit(main()) 