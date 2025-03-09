"""
Network utility functions for the Listening Learning App frontend
"""

import streamlit as st
import requests
import socket
import logging

# Configure logging
logger = logging.getLogger(__name__)

def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_backend_server():
    """
    Find the backend server by checking common ports.
    Returns the backend URL if found, otherwise None.
    """
    # Get backend port from config or use default
    backend_port = 8000  # Default

    # Check common backend ports
    possible_ports = [backend_port, 8080, 5000]
    backend_url = None

    for port in possible_ports:
        try:
            # Test if the backend is running on this port
            url = f"http://localhost:{port}/health"
            response = requests.get(url, timeout=1)
            
            if response.status_code == 200:
                # Found a valid backend
                backend_url = f"http://localhost:{port}"
                logger.info(f"Found backend server at: {backend_url}")
                break
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # Server not running on this port
            continue
        except Exception as e:
            logger.error(f"Error checking backend server on port {port}: {e}")
            continue

    if not backend_url:
        logger.warning("Could not find a running backend server")

    return backend_url 