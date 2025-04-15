"""
Logger Module for the Automated Zoom Poll Generator.
Provides consistent logging throughout the application.
"""

import os
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Optional

# Constants for logging
LOG_FOLDER = "logs"
LOG_FILE = "app.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = logging.DEBUG  # Default to DEBUG level
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
LOG_BACKUP_COUNT = 3  # Keep 3 backup logs

# Create logs directory if it doesn't exist
os.makedirs(LOG_FOLDER, exist_ok=True)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Optional name for the logger (defaults to root logger)
        
    Returns:
        Configured logger instance
    """
    # Get the logger
    logger = logging.getLogger(name)
    
    # Only configure the logger if it hasn't been configured yet
    if not logger.handlers:
        # Set the log level
        logger.setLevel(LOG_LEVEL)
        
        # Create a formatter
        formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
        
        # Create a rotating file handler
        log_path = os.path.join(LOG_FOLDER, LOG_FILE)
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=MAX_LOG_SIZE,
            backupCount=LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(LOG_LEVEL)
        
        # Create a console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)  # Console shows INFO and above
        
        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        logger.debug("Logger initialized")
    
    return logger

def export_logs(output_file: Optional[str] = None) -> str:
    """
    Export logs to a text file.
    
    Args:
        output_file: Optional file path for the exported logs
        
    Returns:
        Path to the exported log file
    """
    # Generate a default filename if not provided
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"exported_logs_{timestamp}.txt"
    
    # Get the log file path
    log_path = os.path.join(LOG_FOLDER, LOG_FILE)
    
    # Check if log file exists
    if not os.path.exists(log_path):
        get_logger().warning(f"Log file does not exist: {log_path}")
        return ""
    
    try:
        # Copy the log file to the output file
        with open(log_path, 'r', encoding='utf-8') as log_file:
            log_content = log_file.read()
        
        with open(output_file, 'w', encoding='utf-8') as output:
            output.write(log_content)
        
        get_logger().info(f"Logs exported to {output_file}")
        return output_file
        
    except Exception as e:
        get_logger().error(f"Failed to export logs: {str(e)}")
        return ""

def clear_logs() -> bool:
    """
    Clear the log file.
    
    Returns:
        Boolean indicating whether clearing was successful
    """
    log_path = os.path.join(LOG_FOLDER, LOG_FILE)
    
    try:
        # Truncate the log file
        with open(log_path, 'w') as f:
            f.write("")
        
        get_logger().info("Logs cleared")
        return True
        
    except Exception as e:
        get_logger().error(f"Failed to clear logs: {str(e)}")
        return False

# Configure basic logging for import time
logging.basicConfig(
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
    level=LOG_LEVEL
)