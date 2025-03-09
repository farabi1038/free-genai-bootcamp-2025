#!/usr/bin/env python
import os
import sys
import subprocess
import argparse
import time
import socket
import logging
import json
import importlib
import shutil
import gc
import platform
import signal
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Apply memory optimizations
def apply_memory_optimizations():
    """Apply memory optimizations to improve performance and reduce OOM errors"""
    # Set lower memory usage for Python processes
    import gc
    gc.collect()  # Force garbage collection
    
    # Set environment variables for child processes
    os.environ["PYTHONOPTIMIZE"] = "1"  # -O flag for Python
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"  # Disable stats
    
    # Reduce Ollama memory footprint by setting context size limit
    # This will be passed to ollama processes
    os.environ["OLLAMA_MAX_TOKENS"] = "1024"
    
    logger.info("Applied memory optimizations")

# Apply memory optimizations early
apply_memory_optimizations()

# Default settings
DEFAULT_FRONTEND_PORT = 8501  # Default Streamlit port
DEFAULT_BACKEND_PORT = 8000   # Default FastAPI port
DEFAULT_CONFIG_FILE = "config.json"

# Utility functions for managing ports and processes
def get_pid_using_port(port):
    """Get the process ID (PID) of any process using the specified port"""
    try:
        if platform.system() == "Windows":
            # Windows-specific command
            output = subprocess.check_output(
                f"netstat -ano | findstr :{port}", 
                shell=True, 
                stderr=subprocess.STDOUT,
                text=True
            )
            
            if output:
                # Extract the PID which is typically the last column
                pids = []
                for line in output.splitlines():
                    if f":{port}" in line:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            pids.append(parts[-1])
                
                # Return unique PIDs
                return list(set(pids))
            
        else:
            # Linux/Mac command
            try:
                output = subprocess.check_output(
                    ["lsof", "-ti", f":{port}"], 
                    stderr=subprocess.STDOUT,
                    text=True
                )
                
                if output:
                    return [pid.strip() for pid in output.splitlines()]
            except FileNotFoundError:
                # If lsof is not available, try with netstat
                output = subprocess.check_output(
                    ["netstat", "-tlnp"], 
                    stderr=subprocess.STDOUT,
                    text=True
                )
                
                pids = []
                for line in output.splitlines():
                    if f":{port}" in line:
                        # Extract PID from netstat output (format varies by platform)
                        pid_match = re.search(r'(\d+)/(.*)', line)
                        if pid_match:
                            pids.append(pid_match.group(1))
                
                return pids
                
    except subprocess.CalledProcessError:
        # No process using this port
        pass
    except Exception as e:
        logger.warning(f"Error checking processes on port {port}: {str(e)}")
    
    return []

def kill_process(pid):
    """Kill a process by its PID"""
    try:
        if platform.system() == "Windows":
            subprocess.check_call(["taskkill", "/F", "/PID", str(pid)])
            logger.info(f"Killed process {pid} on Windows")
        else:
            # Linux/Mac
            os.kill(int(pid), signal.SIGKILL)
            logger.info(f"Killed process {pid} on Unix")
        return True
    except Exception as e:
        logger.error(f"Failed to kill process {pid}: {str(e)}")
        return False

def free_port(port):
    """Free up a port by killing any processes using it"""
    pids = get_pid_using_port(port)
    
    if not pids:
        logger.info(f"Port {port} is already free")
        return True
    
    logger.info(f"Found processes using port {port}: {pids}")
    success = True
    
    for pid in pids:
        if not kill_process(pid):
            success = False
    
    # Verify port is now free
    if success:
        # Wait a moment for OS to release the port
        time.sleep(1)
        if is_port_in_use(port):
            logger.warning(f"Port {port} is still in use after killing processes")
            success = False
    
    return success

# Dependencies
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
    "transformers",
    "pydub",
    "pyttsx3",
    "gtts",
    "requests",
    "numpy",
    "pandas"
]

WHISPER_MODELS = ["tiny", "base", "small", "medium", "large"]

# ================ DEPENDENCY CHECKING FUNCTIONS ================

def check_python_packages():
    """Check if required Python packages are installed"""
    missing_packages = []
    for package in REQUIRED_PACKAGES:
        try:
            importlib.import_module(package)
        except ImportError:
            missing_packages.append(package)
    
    return {
        "success": len(missing_packages) == 0,
        "message": f"Missing Python packages: {', '.join(missing_packages)}" if missing_packages else "All required Python packages are installed.",
        "missing": missing_packages
    }

def install_packages(packages):
    """Install missing Python packages"""
    if not packages:
        return True
    
    logger.info(f"Installing missing packages: {', '.join(packages)}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *packages])
        return True
    except subprocess.CalledProcessError:
        logger.error("Failed to install packages. Please install them manually.")
        return False

def check_system_dependencies():
    """Check if required system dependencies are installed"""
    dependencies = {
        "ffmpeg": shutil.which("ffmpeg") is not None
    }
    
    missing = [dep for dep, installed in dependencies.items() if not installed]
    
    return {
        "success": len(missing) == 0,
        "message": f"Missing system dependencies: {', '.join(missing)}" if missing else "All system dependencies are installed.",
        "missing": missing
    }

def check_ollama():
    """Check if Ollama is available and running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=1)  # Use a shorter timeout
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model.get("name") for model in models]
            
            if not model_names:
                return {
                    "success": False,
                    "message": "Ollama is running but no models are available. Please pull a model like 'llama3'.",
                    "models": []
                }
            
            return {
                "success": True,
                "message": f"Ollama is running with models: {', '.join(model_names)}",
                "models": model_names
            }
        else:
            return {
                "success": False,
                "message": "Ollama responded with an error. Continuing without Ollama.",
                "models": []
            }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "Ollama check timed out. Continuing without Ollama.",
            "models": []
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "Ollama is not running. Continuing without Ollama.",
            "models": []
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Could not connect to Ollama: {str(e)}. Continuing without Ollama.",
            "models": []
        }

def check_whisper_models():
    """Check if Whisper models are available"""
    try:
        import whisper
        # Check default model path
        models_dir = os.path.expanduser("~/.cache/whisper")
        
        if not os.path.exists(models_dir):
            return {
                "success": False,
                "message": f"Whisper models directory not found at: {models_dir}. Models will be downloaded on first use.",
                "models": []
            }
        
        available_models = []
        for model_name in WHISPER_MODELS:
            model_dir = os.path.join(models_dir, model_name + ".pt")
            if os.path.exists(model_dir):
                available_models.append(model_name)
        
        if not available_models:
            return {
                "success": False,
                "message": f"No Whisper models found. They will be downloaded on first use.",
                "models": []
            }
        
        return {
            "success": True,
            "message": f"Found Whisper models: {', '.join(available_models)}",
            "models": available_models
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error checking Whisper models: {str(e)}",
            "models": []
        }

def print_results(results):
    """Print dependency check results with colors"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    print(f"\n{BOLD}Dependency Check Results:{RESET}\n")
    
    all_success = True
    warnings = 0
    
    # Python packages
    if results["python_packages"]["success"]:
        print(f"{GREEN}✓ Python Packages:{RESET} All required packages installed")
    else:
        all_success = False
        print(f"{RED}✗ Python Packages:{RESET} {results['python_packages']['message']}")
    
    # System dependencies
    if results["system_dependencies"]["success"]:
        print(f"{GREEN}✓ System Dependencies:{RESET} All required dependencies installed")
    else:
        all_success = False
        print(f"{RED}✗ System Dependencies:{RESET} {results['system_dependencies']['message']}")
    
    # Ollama
    if results["ollama"]["success"]:
        print(f"{GREEN}✓ Ollama:{RESET} {results['ollama']['message']}")
    else:
        all_success = False
        print(f"{RED}✗ Ollama:{RESET} {results['ollama']['message']}")
    
    # Whisper
    if results["whisper"]["success"]:
        print(f"{GREEN}✓ Whisper:{RESET} {results['whisper']['message']}")
    else:
        warnings += 1
        print(f"{YELLOW}! Whisper:{RESET} {results['whisper']['message']}")
    
    # Summary
    print("\n" + "="*50 + "\n")
    if all_success and warnings == 0:
        print(f"{GREEN}{BOLD}All dependencies satisfied!{RESET}")
    elif all_success:
        print(f"{YELLOW}{BOLD}All critical dependencies satisfied, but there are warnings.{RESET}")
    else:
        print(f"{RED}{BOLD}Some dependencies are missing. Please install them before proceeding.{RESET}")
    
    return all_success

def check_all_dependencies(auto_install=False):
    """Check all dependencies and optionally install missing packages"""
    # Check Python packages first - these are essential
    pkg_check = check_python_packages()
    if not pkg_check["success"] and auto_install:
        logger.info("Attempting to install missing Python packages...")
        if install_packages(pkg_check["missing"]):
            pkg_check = check_python_packages()  # Re-check after installation
    
    # Check system dependencies
    sys_check = check_system_dependencies()
    
    # Check Ollama - this is optional and should never block startup
    try:
        logger.info("Checking Ollama status (will continue regardless)...")
        ollama_check = check_ollama()
    except Exception as e:
        logger.warning(f"Ollama check failed: {str(e)}. Continuing without Ollama.")
        ollama_check = {
            "success": False,
            "message": f"Ollama check failed: {str(e)}. Continuing without Ollama.",
            "models": []
        }
    
    # Check Whisper models - this is optional and should never block startup
    try:
        logger.info("Checking Whisper models (will continue regardless)...")
        whisper_check = check_whisper_models()
    except Exception as e:
        logger.warning(f"Whisper models check failed: {str(e)}. Continuing without Whisper.")
        whisper_check = {
            "success": False,
            "message": f"Whisper models check failed: {str(e)}. Continuing without Whisper.",
            "models": []
        }
    
    # Collect results
    results = {
        "python_packages": pkg_check,
        "system_dependencies": sys_check,
        "ollama": ollama_check,
        "whisper": whisper_check
    }
    
    # Print results
    success = print_results(results)
    
    # We continue even if some dependencies are missing - but we need to warn the user
    if not success:
        logger.warning("Some dependencies are missing. Some features may not work correctly.")
    
    # Return True to indicate we should continue with startup
    return True

# ================ ORIGINAL RUN.PY FUNCTIONS ================

def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port):
    """Find an available port starting from start_port"""
    port = start_port
    max_attempts = 100  # Limit the number of attempts to find an available port
    
    for _ in range(max_attempts):
        if not is_port_in_use(port):
            return port
        port += 1
    
    # If we couldn't find an available port, return the original port
    # and let the caller handle the error
    logger.warning(f"Could not find an available port after {max_attempts} attempts")
    return start_port

def load_config():
    """Load configuration from config.json if it exists"""
    config_path = Path(__file__).parent / DEFAULT_CONFIG_FILE
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
    
    # Default configuration
    return {
        "frontend_port": DEFAULT_FRONTEND_PORT,
        "backend_port": DEFAULT_BACKEND_PORT,
        "ollama_model": "llama3.2:1b",
        "whisper_model": "base",
        "log_level": "INFO"
    }

def save_config(config):
    """Save configuration to config.json"""
    config_path = Path(__file__).parent / DEFAULT_CONFIG_FILE
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Saved configuration to {config_path}")
    except Exception as e:
        logger.error(f"Error saving configuration: {str(e)}")

def start_backend(port, ollama_model, whisper_model):
    """Start the backend server with dynamic port selection"""
    # Always find an available port to avoid conflicts
    if is_port_in_use(port):
        logger.info(f"Port {port} is in use. Finding an available port...")
        original_port = port
        port = find_available_port(port)
        if port != original_port:
            logger.info(f"Using alternative port: {port}")
    
    backend_path = Path(__file__).parent / "backend" / "main.py"
    
    # Set environment variables for configuration
    env = os.environ.copy()
    env["PORT"] = str(port)
    env["OLLAMA_MODEL"] = ollama_model
    env["WHISPER_MODEL"] = whisper_model
    env["ENABLE_RELOAD"] = "false"  # Disable auto-reload to prevent memory issues
    
    # Start the backend process
    logger.info(f"Starting backend server on port {port}...")
    
    try:
        # Don't capture stdout/stderr to allow uvicorn logs to show up
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", str(port)],
            env=env,
            cwd=str(Path(__file__).parent)  # Set working directory to project root
        )
        
        # Wait a bit for the server to start without immediately checking the port
        # The port might not be bound yet even though the process started
        time.sleep(3)
        
        # IMPORTANT: Don't check the port yet - assume the backend is starting since there's no error
        
        # Update config with the new port
        config = load_config()
        if config["backend_port"] != port:
            config["backend_port"] = port
            save_config(config)
            logger.info(f"Updated configuration with new backend port: {port}")
        
        logger.info(f"Backend server started. Uvicorn is initializing on port {port}...")
        logger.info(f"Uvicorn logs will appear in the terminal directly.")
        
        # Return the process without checking if it's ready
        return process
        
    except Exception as e:
        logger.error(f"Error starting backend: {str(e)}")
        logger.error(f"Failed to start backend server")
        return None

def start_frontend(port, backend_port):
    """Start the Streamlit frontend"""
    # Free up the port first
    if is_port_in_use(port):
        logger.info(f"Frontend port {port} is in use. Attempting to free it...")
        if not free_port(port):
            logger.warning(f"Could not free port {port}. Will try a different port.")
            port = find_available_port(port)
            logger.info(f"Using alternative frontend port: {port}")
    
    frontend_path = Path(__file__).parent / "frontend" / "main.py"
    
    # Set environment variables for configuration
    env = os.environ.copy()
    env["STREAMLIT_SERVER_PORT"] = str(port)
    env["BACKEND_PORT"] = str(backend_port)
    
    # Start the frontend process
    logger.info(f"Starting frontend on port {port}")
    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(frontend_path),
            "--server.port", str(port)
        ]
        
        # In a real implementation, you might want to redirect stdout/stderr
        process = subprocess.Popen(cmd, env=env)
        
        # Wait a bit to ensure the server starts up
        time.sleep(2)
        
        # Verify the server is running
        if not is_port_in_use(port):
            logger.warning(f"Frontend may have failed to start on port {port}")
            
        logger.info(f"Frontend started on port {port}")
        return process
    except Exception as e:
        logger.error(f"Error starting frontend: {str(e)}")
        return None

def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(description="Run the Japanese Listening Practice application")
    parser.add_argument("--check-only", action="store_true", help="Only check dependencies without starting the app")
    parser.add_argument("--auto-install", action="store_true", help="Automatically install missing dependencies")
    parser.add_argument("--frontend-port", type=int, help="Port for the frontend server")
    parser.add_argument("--backend-port", type=int, help="Port for the backend server")
    parser.add_argument("--ollama-model", type=str, help="Ollama model to use")
    parser.add_argument("--whisper-model", type=str, help="Whisper model to use")
    parser.add_argument("--skip-backend", action="store_true", help="Skip starting the backend server")
    args = parser.parse_args()
    
    # Check dependencies
    try:
        dependency_check = check_all_dependencies(auto_install=args.auto_install)
        if args.check_only:
            logger.info("Dependency check completed. Use --auto-install to install missing dependencies.")
            return
    except Exception as e:
        logger.error(f"Error during dependency check: {str(e)}")
        logger.warning("Continuing with startup despite dependency check errors.")
    
    # Load configuration
    config = load_config()
    
    # Override with command line arguments if provided
    if args.frontend_port:
        config["frontend_port"] = args.frontend_port
    if args.backend_port:
        config["backend_port"] = args.backend_port
    if args.ollama_model:
        config["ollama_model"] = args.ollama_model
    if args.whisper_model:
        config["whisper_model"] = args.whisper_model
    
    # Save updated configuration
    save_config(config)
    
    # Initialize database (but don't let failures stop us)
    try:
        # Import and initialize the database
        from backend.main import initialize_db
        initialize_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        logger.warning("Continuing with startup, but the application may not function correctly.")
    
    # Start backend server (unless skipped)
    backend_process = None
    if not args.skip_backend:
        try:
            backend_process = start_backend(
                config["backend_port"], 
                config["ollama_model"],
                config["whisper_model"]
            )
            
            if not backend_process:
                logger.warning("Failed to start backend server. YouTube features will not work.")
                logger.info("Starting frontend only...")
        except Exception as e:
            logger.error(f"Error starting backend: {str(e)}")
            logger.warning("Unable to start backend. YouTube features will not work.")
    else:
        logger.info("Skipping backend server as requested with --skip-backend flag.")
        logger.warning("YouTube features will not be available.")
    
    # Start frontend
    try:
        frontend_process = start_frontend(config["frontend_port"], config["backend_port"])
        
        if not frontend_process:
            logger.error("Failed to start frontend. Exiting.")
            # Kill backend process if frontend fails
            if backend_process and backend_process.poll() is None:
                backend_process.terminate()
            return 1
    except Exception as e:
        logger.error(f"Error starting frontend: {str(e)}")
        # Kill backend process if frontend fails
        if backend_process and backend_process.poll() is None:
            backend_process.terminate()
        return 1
    
    # Wait for processes to complete or be terminated
    try:
        print("\n" + "="*60)
        print("Application running. Press Ctrl+C to exit.")
        if backend_process:
            print("Backend server is running - YouTube features should work")
        else:
            print("NO BACKEND SERVER - YouTube features will NOT work")
        print("You can access the frontend at: http://localhost:8501")
        print("="*60 + "\n")
        
        while True:
            # If frontend process has exited, we should exit too
            if frontend_process.poll() is not None:
                logger.info(f"Frontend process exited with code {frontend_process.returncode}")
                break
                
            # If backend process was started but died, log it but continue running
            if backend_process and backend_process.poll() is not None:
                logger.warning(f"Backend process exited with code {backend_process.returncode}")
                logger.warning("YouTube features will no longer work")
                backend_process = None  # Clear the reference
                
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        # Clean up processes
        if backend_process and backend_process.poll() is None:
            logger.info("Terminating backend process...")
            backend_process.terminate()
            
        if frontend_process and frontend_process.poll() is None:
            logger.info("Terminating frontend process...")
            frontend_process.terminate()
            
        logger.info("Application shutdown complete")
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 