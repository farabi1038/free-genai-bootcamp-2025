"""
Configuration utilities for the Listening Learning App frontend
"""

import json
import os
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

def load_config():
    """
    Load configuration from config file
    
    Returns:
        dict: Configuration dictionary
    """
    try:
        config_path = Path(__file__).parents[2] / "config.json"
        
        if not os.path.isfile(config_path):
            logger.warning(f"Config file not found: {config_path}")
            return {}
            
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {}

def save_config(config):
    """
    Save configuration to config file
    
    Parameters:
        config (dict): Configuration dictionary
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        config_path = Path(__file__).parents[2] / "config.json"
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
            
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False

def get_config_value(key, default=None):
    """
    Get a configuration value
    
    Parameters:
        key (str): Configuration key
        default: Default value if key not found
    
    Returns:
        The configuration value or default
    """
    config = load_config()
    return config.get(key, default)

def set_config_value(key, value):
    """
    Set a configuration value
    
    Parameters:
        key (str): Configuration key
        value: Configuration value
    
    Returns:
        bool: True if successful, False otherwise
    """
    config = load_config()
    config[key] = value
    return save_config(config) 