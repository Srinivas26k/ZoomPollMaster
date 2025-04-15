"""
Logging module for the Automated Zoom Poll Generator.
Handles detailed logging of all application operations with timestamp support.
"""

import logging
import os
import datetime
from pathlib import Path
from config import LOG_FOLDER, LOG_FORMAT, LOG_LEVEL


class ApplicationLogger:
    """
    Handles application-wide logging with file output and timestamp support.
    """
    
    def __init__(self):
        """Initialize the logger with default configuration."""
        self.logger = logging.getLogger("zoom_poll_generator")
        self.logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # Create log directory if it doesn't exist
        if not os.path.exists(LOG_FOLDER):
            os.makedirs(LOG_FOLDER)
        
        # Generate log filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(LOG_FOLDER, f"poll_generator_{timestamp}.log")
        
        # Configure file handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(getattr(logging, LOG_LEVEL))
        
        # Configure console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, LOG_LEVEL))
        
        # Create formatter and add to handlers
        formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info(f"Logger initialized. Log file: {self.log_file}")
    
    def get_logger(self):
        """Return the configured logger instance."""
        return self.logger
    
    def get_log_file_path(self):
        """Return the path to the current log file."""
        return self.log_file
    
    def export_log(self, export_path=None):
        """
        Export the current log file to a specified location or return its current path.
        
        Args:
            export_path (str, optional): Path to export the log file to.
                                        If None, returns the current log file path.
        
        Returns:
            str: Path to the exported log file or current log file.
        """
        if not export_path:
            return self.log_file
        
        # Create directory if it doesn't exist
        export_dir = os.path.dirname(export_path)
        if export_dir and not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        # Copy log file to export location
        with open(self.log_file, 'r') as source:
            with open(export_path, 'w') as dest:
                dest.write(source.read())
        
        self.logger.info(f"Log exported to: {export_path}")
        return export_path


# Create global logger instance
app_logger = ApplicationLogger()
logger = app_logger.get_logger()


def get_logger():
    """Access function to get the configured logger."""
    return logger


def export_log_file(export_path=None):
    """Export the log file to a specified path or return current path."""
    return app_logger.export_log(export_path)
