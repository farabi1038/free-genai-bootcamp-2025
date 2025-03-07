#!/usr/bin/env python
"""
Starter script for the vocabulary importer.
This script handles common setup tasks and then launches the Streamlit app.
"""

import os
import sys
import logging
import subprocess
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Set up the environment for the application."""
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    logger.info("Created output directory")
    
    # Ensure we have a .env file with defaults if it doesn't exist
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("LLM_SERVICE_HOST=localhost\n")
            f.write("LLM_SERVICE_PORT=11434\n")
            f.write("LLM_MODEL_ID=llama2\n")
        logger.info("Created default .env file")
    
    # Check if we're running in WSL and fix DNS if needed
    if os.path.exists("/proc/version") and "microsoft" in open("/proc/version").read().lower():
        logger.info("Running in WSL environment, checking DNS configuration")
        try:
            # Check if we can resolve domain names
            try:
                subprocess.run(["ping", "-c", "1", "google.com"], 
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.DEVNULL, 
                              check=True, 
                              timeout=3)
                logger.info("DNS resolution is working")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                logger.warning("DNS resolution not working, attempting to fix")
                # Try to set Google DNS
                with open("/etc/resolv.conf", "r") as f:
                    resolv_conf = f.read()
                
                if "8.8.8.8" not in resolv_conf:
                    try:
                        subprocess.run(["sudo", "bash", "-c", 'echo "nameserver 8.8.8.8" > /etc/resolv.conf'], 
                                      stdout=subprocess.DEVNULL, 
                                      stderr=subprocess.DEVNULL, 
                                      check=True)
                        logger.info("Updated DNS configuration")
                    except Exception as e:
                        logger.warning(f"Failed to update DNS: {str(e)}")
                        print("\n⚠️  DNS resolution issues detected. If you have problems, try the following command:")
                        print('   sudo bash -c \'echo "nameserver 8.8.8.8" > /etc/resolv.conf\'')
        except Exception as e:
            logger.warning(f"Error checking/fixing WSL DNS: {str(e)}")

def start_streamlit():
    """Start the Streamlit application."""
    logger.info("Starting Streamlit application")
    try:
        # Start Streamlit
        subprocess.run(["streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.error(f"Error running Streamlit: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        print("\nTry running the application manually with: streamlit run app.py")
        sys.exit(1)

if __name__ == "__main__":
    print("\n📚 Language Learning Vocabulary Generator")
    print("=====================================\n")
    
    try:
        setup_environment()
        start_streamlit()
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1) 