#!/usr/bin/env python3
"""
Run script for the Kana Writing Practice application.
This script provides a convenient way to start the application
with proper environment setup.
"""

import os
import sys
import subprocess
import webbrowser
import platform
import signal
import socket
import time
from pathlib import Path

def is_wsl():
    """Check if running in Windows Subsystem for Linux"""
    if os.path.exists('/proc/version'):
        with open('/proc/version', 'r') as f:
            if "microsoft" in f.read().lower():
                return True
    return False

def check_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_process_using_port(port):
    """Find the process ID using the specified port"""
    try:
        if platform.system() == "Windows":
            output = subprocess.check_output(['netstat', '-ano'], text=True)
            for line in output.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    return line.strip().split()[-1]
        else:
            output = subprocess.check_output(['lsof', '-i', f':{port}'], text=True)
            if output:
                lines = output.splitlines()
                if len(lines) > 1:  # Has at least one entry after header
                    return lines[1].split()[1]
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
        pass
    return None

def kill_process_on_port(port, max_attempts=3):
    """Kill the process using the specified port with multiple attempts"""
    for attempt in range(max_attempts):
        pid = find_process_using_port(port)
        if not pid:
            # No process found, port must be free
            return True
            
        try:
            print(f"Attempt {attempt+1}/{max_attempts}: Killing process {pid} on port {port}...")
            
            if platform.system() == "Windows":
                subprocess.run(['taskkill', '/F', '/PID', pid], check=False)
            else:
                # Try SIGTERM first
                os.kill(int(pid), signal.SIGTERM)
                time.sleep(1)
                
                # If process still exists, try SIGKILL
                if find_process_using_port(port) == pid:
                    os.kill(int(pid), signal.SIGKILL)
            
            # Wait for port to be freed
            time.sleep(2)
            
            # Check if port is now free
            if not check_port_in_use(port):
                print(f"Successfully freed port {port}")
                return True
                
        except (subprocess.CalledProcessError, ProcessLookupError) as e:
            print(f"Attempt {attempt+1} failed: {e}")
        
        # Wait before trying again
        time.sleep(1)
    
    return False

def ensure_port_available(port):
    """Ensure the specified port is available before proceeding"""
    # First check if port is in use
    if not check_port_in_use(port):
        print(f"Port {port} is free.")
        return True
        
    print(f"Port {port} is in use. Attempting to free it...")
    success = kill_process_on_port(port)
    
    if not success:
        print(f"ERROR: Could not free port {port} after multiple attempts.")
        print("Please manually kill the process using this port before continuing.")
        print(f"You can try: lsof -i :{port} | grep LISTEN")
        print(f"And then: kill -9 <PID>")
        return False
        
    return True

def check_environment():
    """Check if the environment is properly set up"""
    # Check if .env file exists
    if not Path('.env').exists():
        print("Warning: .env file not found. Creating from .env.example...")
        if Path('.env.example').exists():
            with open('.env.example', 'r') as example_file:
                content = example_file.read()
            
            with open('.env', 'w') as env_file:
                env_file.write(content)
            
            print("Created .env file. Please edit it to add your API keys before proceeding.")
        else:
            print("Error: .env.example not found. Please create a .env file manually.")
            return False
    
    # Get LLM provider from .env file
    llm_provider = "openai"  # Default
    with open('.env', 'r') as env_file:
        for line in env_file:
            if line.strip().startswith('LLM_PROVIDER='):
                llm_provider = line.strip().split('=', 1)[1].strip().lower()
                break
    
    # If using Ollama, check if it's properly configured
    if llm_provider == "ollama":
        print("Checking Ollama configuration...")
        try:
            # Run check_ollama.py
            result = subprocess.run(
                [sys.executable, "check_ollama.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode != 0:
                print("\nOllama configuration check failed. Please fix the issues and try again.")
                print("You can run 'python check_ollama.py' manually to troubleshoot.")
                return False
        except Exception as e:
            print(f"Error checking Ollama configuration: {e}")
            print("Continuing anyway, but the application may not work properly.")
    
    # Check MangaOCR configuration
    print("\nChecking MangaOCR configuration...")
    try:
        # First, check if the models are already downloaded
        import importlib.util
        manga_ocr_installed = importlib.util.find_spec("manga_ocr") is not None
        
        if manga_ocr_installed:
            import manga_ocr
            try:
                # Test initialization without downloading models
                mocr = manga_ocr.MangaOcr(pretrained_model_name_or_path=None)
                print("✅ MangaOCR is already configured.")
            except:
                # If initialization fails, the models probably aren't downloaded
                print("MangaOCR needs to download models for offline use.")
                check_manga_ocr()
        else:
            print("MangaOCR is not installed. Running setup...")
            check_manga_ocr()
    except Exception as e:
        print(f"Error checking MangaOCR configuration: {e}")
        print("MangaOCR may not be available. The app will use a fallback method.")
    
    return True

def check_manga_ocr():
    """Run the MangaOCR setup script"""
    try:
        result = subprocess.run(
            [sys.executable, "check_manga_ocr.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            print("\nMangaOCR setup failed. The app will use a fallback method.")
            print("You can run 'python check_manga_ocr.py' manually to troubleshoot.")
    except Exception as e:
        print(f"Error running MangaOCR setup: {e}")

def main():
    """Main function to run the application"""
    # Change to the script directory
    os.chdir(Path(__file__).parent)
    
    # Default port for Streamlit
    port = 8501
    
    print("=" * 50)
    print("KANA WRITING PRACTICE APP LAUNCHER")
    print("=" * 50)
    
    # FIRST: Make sure the port is available before doing anything else
    print("\n----- PORT CHECK -----")
    if not ensure_port_available(port):
        print("Exiting due to port issues.")
        sys.exit(1)
    
    # Now check the environment
    print("\n----- ENVIRONMENT CHECK -----")
    if not check_environment():
        sys.exit(1)
    
    # Start the Streamlit app
    print("\n----- LAUNCHING APP -----")
    print(f"Starting Kana Writing Practice app on port {port}...")
    url = f"http://localhost:{port}"
    
    # Check if we're running in WSL
    running_in_wsl = is_wsl()
    
    # Open browser based on environment
    if running_in_wsl:
        print("\nRunning in WSL (Windows Subsystem for Linux)")
        print("Please open your browser manually and navigate to:")
        print(f"  {url}")
        print("\nIf you're using WSL, you can open a browser in Windows and enter the URL.")
    else:
        # Try to open browser automatically in non-WSL environments
        def open_browser():
            """Open the browser after a delay"""
            import time
            time.sleep(2)
            try:
                webbrowser.open(url)
            except Exception as e:
                print(f"\nCouldn't open browser automatically: {e}")
                print(f"Please open {url} manually in your browser.")
        
        # Start browser in a separate thread
        import threading
        threading.Thread(target=open_browser).start()
    
    # Run the Streamlit app
    subprocess.run([
        "streamlit", "run", "app.py", 
        "--server.port", str(port),
        "--server.address", "localhost"
    ])

if __name__ == "__main__":
    main() 