"""
Launcher script for the Listening Learning App

This script sets up the Python path correctly and launches both 
the frontend and backend components of the application.
"""

import os
import sys
import subprocess
import time
import socket
import logging
import json
from pathlib import Path
import signal
import threading
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# Store processes
processes = []

# Default ports
DEFAULT_BACKEND_PORT = 8040
DEFAULT_FRONTEND_PORT = 8506

# Function to check if a port is in use
def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Function to find a free port starting from a given port
def find_free_port(start_port):
    """Find a free port starting from start_port"""
    port = start_port
    while is_port_in_use(port):
        port += 1
    return port

# Function to get process IDs using a specific port
def get_processes_using_port(port):
    """Get the process IDs using a specific port"""
    try:
        # Check which OS we're on
        if os.name == 'nt':  # Windows
            # Windows: use netstat
            output = subprocess.check_output(f'netstat -ano | findstr :{port}', shell=True).decode()
            if not output:
                return []
            
            # Extract PIDs from the output
            pids = set()
            for line in output.split('\n'):
                if f":{port}" in line:
                    parts = line.strip().split()
                    if len(parts) > 4:
                        pids.add(parts[4])
            
            return list(pids)
        else:  # Unix/Linux/Mac
            # Unix: use lsof
            try:
                output = subprocess.check_output(f'lsof -i :{port} -t', shell=True).decode()
                return [pid.strip() for pid in output.split('\n') if pid.strip()]
            except subprocess.CalledProcessError:
                return []
    except Exception as e:
        logger.error(f"Error getting processes using port {port}: {e}")
        return []

# Function to free a port by killing processes using it
def free_port(port):
    """Free a port by killing processes using it"""
    try:
        pids = get_processes_using_port(port)
        if pids:
            logger.info(f"Found processes using port {port}: {pids}")
            for pid in pids:
                if pid:
                    try:
                        if os.name == 'nt':  # Windows
                            subprocess.run(f'taskkill /F /PID {pid}', shell=True)
                            logger.info(f"Killed process {pid} on Windows")
                        else:  # Unix/Linux/Mac
                            subprocess.run(f'kill -9 {pid}', shell=True)
                            logger.info(f"Killed process {pid} on Unix")
                    except Exception as e:
                        logger.error(f"Error killing process {pid}: {e}")
            return True
        else:
            logger.info(f"No processes found using port {port}")
            return False
    except Exception as e:
        logger.error(f"Error freeing port {port}: {e}")
        return False

# Function to load configuration
def load_config():
    """Load configuration from config file"""
    config_path = current_dir / "config.json"
    config = {
        "backend_port": DEFAULT_BACKEND_PORT,
        "frontend_port": DEFAULT_FRONTEND_PORT
    }
    
    # Create config file if it doesn't exist
    if not config_path.exists():
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info(f"Loaded configuration from defaults")
        return config
    
    # Load existing config
    try:
        with open(config_path, 'r') as f:
            loaded_config = json.load(f)
            config.update(loaded_config)
        logger.info(f"Loaded configuration from {config_path}")
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
    
    return config

# Function to save configuration
def save_config(config):
    """Save configuration to config file"""
    config_path = current_dir / "config.json"
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info(f"Saved configuration to {config_path}")
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")

# Function to start the backend
def start_backend(port):
    """Start the backend server"""
    logger.info(f"Starting backend on port {port}...")
    
    # Check if backend port is in use and try to free it
    if is_port_in_use(port):
        logger.info(f"Backend port {port} is in use. Attempting to free it...")
        free_port(port)
        time.sleep(1)  # Wait for the port to be freed
    
    # Set environment variables
    env = os.environ.copy()
    env["PORT"] = str(port)
    
    # Start the backend
    try:
        backend_path = current_dir / "backend" / "main.py"
        if os.name == 'nt':  # Windows
            backend_process = subprocess.Popen(
                ["python", str(backend_path)],
                env=env,
                cwd=str(current_dir)
            )
        else:  # Unix/Linux/Mac
            backend_process = subprocess.Popen(
                ["python", str(backend_path)],
                env=env,
                cwd=str(current_dir)
            )
        
        processes.append(backend_process)
        logger.info(f"Backend server started. Process ID: {backend_process.pid}")
        
        # Give the backend a moment to start
        time.sleep(2)
        
        return backend_process
    except Exception as e:
        logger.error(f"Error starting backend: {e}")
        return None

# Function to start the frontend
def start_frontend(port):
    """Start the frontend server"""
    logger.info(f"Starting frontend on port {port}")
    
    # Check if frontend port is in use and try to free it
    if is_port_in_use(port):
        logger.info(f"Frontend port {port} is in use. Attempting to free it...")
        free_port(port)
        time.sleep(1)  # Wait for the port to be freed
    
    # Set environment variables
    env = os.environ.copy()
    env["STREAMLIT_SERVER_PORT"] = str(port)
    
    # Start the frontend
    try:
        frontend_module = "frontend.main"
        if os.name == 'nt':  # Windows
            frontend_process = subprocess.Popen(
                ["streamlit", "run", frontend_module],
                env=env,
                cwd=str(current_dir)
            )
        else:  # Unix/Linux/Mac
            frontend_process = subprocess.Popen(
                ["streamlit", "run", frontend_module],
                env=env,
                cwd=str(current_dir)
            )
        
        processes.append(frontend_process)
        logger.info(f"Frontend started on port {port}")
        
        return frontend_process
    except Exception as e:
        logger.error(f"Error starting frontend: {e}")
        return None

# Function to stop all processes
def stop_all():
    """Stop all processes"""
    logger.info("Stopping all processes...")
    
    for process in processes:
        try:
            # First try to terminate gracefully
            process.terminate()
            # Wait a bit for graceful termination
            process.wait(timeout=2)
        except Exception:
            # If termination fails, kill the process
            try:
                process.kill()
            except Exception as e:
                logger.error(f"Error killing process {process.pid}: {e}")
    
    # Clear processes list
    processes.clear()

# Handle Ctrl+C
def signal_handler(sig, frame):
    """Handle Ctrl+C signal"""
    logger.info("Received interrupt signal. Shutting down...")
    stop_all()
    sys.exit(0)

# Main function
def main():
    """Main function"""
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Load configuration
    config = load_config()
    backend_port = config.get("backend_port", DEFAULT_BACKEND_PORT)
    frontend_port = config.get("frontend_port", DEFAULT_FRONTEND_PORT)
    
    # Start backend
    backend_process = start_backend(backend_port)
    if not backend_process:
        logger.error("Failed to start backend server.")
        return
    
    # Update configuration if backend port changed
    if backend_port != config.get("backend_port"):
        config["backend_port"] = backend_port
        logger.info(f"Updated configuration with new backend port: {backend_port}")
        save_config(config)
    
    # Start frontend
    frontend_process = start_frontend(frontend_port)
    if not frontend_process:
        logger.error("Failed to start frontend. Stopping backend...")
        backend_process.terminate()
        return
    
    # Update configuration if frontend port changed
    if frontend_port != config.get("frontend_port"):
        config["frontend_port"] = frontend_port
        logger.info(f"Updated configuration with new frontend port: {frontend_port}")
        save_config(config)
    
    # Display success message
    print("\n============================================================")
    print("Application running. Press Ctrl+C to exit.")
    print("Backend server is running - YouTube features should work")
    print(f"You can access the frontend at: http://localhost:{frontend_port}")
    print("============================================================\n")
    
    # Keep the main thread alive
    try:
        while True:
            # Check if processes are still running
            if backend_process.poll() is not None:
                logger.error("Backend process has stopped unexpectedly. Restarting...")
                backend_process = start_backend(backend_port)
            
            if frontend_process.poll() is not None:
                logger.error("Frontend process has stopped unexpectedly. Restarting...")
                frontend_process = start_frontend(frontend_port)
            
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt. Shutting down...")
        stop_all()

# Run the main function
if __name__ == "__main__":
    main() 