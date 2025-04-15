"""
Configuration Module for the Automated Zoom Poll Generator.
Handles loading and saving of application configuration.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

# Configure logger
logger = logging.getLogger(__name__)

# Constants
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "zoom_client_type": "desktop",  # Force desktop client
    "transcript_interval": 10,  # minutes
    "poll_interval": 15,  # minutes
    "display_name": "Poll Generator",
    "auto_enable_captions": True,
    "auto_start": False,
    "chatgpt_integration_method": "browser",  # 'browser' or 'api'
    "check_interval": 30,  # seconds
    "save_transcripts": True,
    "transcripts_folder": "./transcripts",
    "poll_generation_prompt": """Based on the transcript below from a Zoom meeting, generate one engaging poll question with exactly four answer options. Format your response as a JSON object with "question" and "options" keys, where "options" is a list of four answer choices. The poll should be relevant to the content discussed in the transcript and encourage participation.

Transcript:
{transcript}

Response format:
{
  "question": "Your poll question here?",
  "options": [
    "Option A",
    "Option B",
    "Option C",
    "Option D"
  ]
}
""",
    "wait_times": {
        "zoom_launch": 8,       # seconds to wait for Zoom to launch
        "join_screen": 5,       # seconds to wait for join screen
        "meeting_load": 10,     # seconds to wait for meeting to load
        "ui_action": 2,         # seconds to wait between UI actions
    }
}

# Timing constants
WAIT_SHORT = 1  # 1 second
WAIT_MEDIUM = 5  # 5 seconds
WAIT_LONG = 10  # 10 seconds

def load_config() -> Dict[str, Any]:
    """
    Load configuration from config file.
    If the file doesn't exist, create it with default values.
    
    Returns:
        Dict containing configuration values
    """
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                logger.info("Configuration loaded from file")
                
                # Merge with defaults to ensure all required keys exist
                merged_config = DEFAULT_CONFIG.copy()
                merged_config.update(config)
                
                return merged_config
        else:
            # Create default config file
            save_config(DEFAULT_CONFIG)
            logger.info("Created default configuration file")
            return DEFAULT_CONFIG
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        logger.info("Using default configuration")
        return DEFAULT_CONFIG

def save_config(config: Dict[str, Any]) -> bool:
    """
    Save configuration to config file.
    
    Args:
        config: Dict containing configuration values
        
    Returns:
        Boolean indicating whether save was successful
    """
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
            logger.info("Configuration saved to file")
            return True
    except Exception as e:
        logger.error(f"Error saving configuration: {str(e)}")
        return False

def get_config_value(key: str, default: Any = None) -> Any:
    """
    Get a specific configuration value.
    
    Args:
        key: Configuration key to get
        default: Default value to return if key is not found
        
    Returns:
        Configuration value or default
    """
    config = load_config()
    return config.get(key, default)

def set_config_value(key: str, value: Any) -> bool:
    """
    Set a specific configuration value.
    
    Args:
        key: Configuration key to set
        value: Value to set
        
    Returns:
        Boolean indicating whether set was successful
    """
    try:
        config = load_config()
        config[key] = value
        return save_config(config)
    except Exception as e:
        logger.error(f"Error setting configuration value: {str(e)}")
        return False