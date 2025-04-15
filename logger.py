"""
Logging module for the Automated Zoom Poll Generator.
Handles detailed logging of all application operations with timestamp support.
"""

import os
import sys
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path

# Import config or use default values if not available
try:
    from config import LOG_FOLDER, LOG_FORMAT, LOG_LEVEL
except ImportError:
    # Default values if config module is not available
    LOG_FOLDER = Path.home() / "ZoomPollGenerator_Logs"
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    LOG_LEVEL = "INFO"


class ApplicationLogger:
    """
    Handles application-wide logging with file output and timestamp support.
    """
    
    def __init__(self):
        """Initialize the logger with default configuration."""
        self.logger = logging.getLogger("ZoomPollGenerator")
        self.logger.setLevel(self._get_log_level(LOG_LEVEL))
        
        # Prevent duplicate logging
        if self.logger.handlers:
            return
            
        # Create logs directory if it doesn't exist
        try:
            os.makedirs(LOG_FOLDER, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create log directory: {e}")
            # Fallback to current directory
            log_dir = Path(".")
            
        # Set up log file path with timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        self.log_file = os.path.join(LOG_FOLDER, f"app_{timestamp}.log")
        
        # Create file handler for logging to file
        try:
            # Use rotating file handler to prevent huge log files
            file_handler = RotatingFileHandler(
                self.log_file, 
                maxBytes=1024*1024*5,  # 5MB max file size
                backupCount=5,         # Keep 5 backup files
                encoding="utf-8"
            )
            file_handler.setLevel(self._get_log_level(LOG_LEVEL))
            file_formatter = logging.Formatter(LOG_FORMAT)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not create log file: {e}")
        
        # Create console handler for logging to console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self._get_log_level(LOG_LEVEL))
        console_formatter = logging.Formatter(LOG_FORMAT)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        self.logger.info("Logger initialized")
    
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
            
        try:
            import shutil
            shutil.copy2(self.log_file, export_path)
            self.logger.info(f"Log exported to: {export_path}")
            return export_path
        except Exception as e:
            self.logger.error(f"Error exporting log: {str(e)}")
            return None
    
    def export_log_as_json(self, export_path=None):
        """
        Export the log as structured JSON data.
        
        Args:
            export_path (str, optional): Path to export the JSON file to.
                                        If None, generates a default path.
        
        Returns:
            str: Path to the exported JSON file.
        """
        if not export_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = os.path.join(LOG_FOLDER, f"log_export_{timestamp}.json")
            
        try:
            # Parse log file and convert to structured data
            log_entries = []
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    # Simple parsing of standard log format
                    try:
                        timestamp_str = line.split(' - ')[0]
                        level = line.split(' - ')[1]
                        message = ' - '.join(line.split(' - ')[2:]).strip()
                        
                        log_entries.append({
                            "timestamp": timestamp_str,
                            "level": level,
                            "message": message
                        })
                    except IndexError:
                        # Line doesn't match expected format, add as raw
                        log_entries.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3],
                            "level": "INFO",
                            "message": line.strip(),
                            "raw": True
                        })
            
            # Write to JSON file
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "application": "Zoom Poll Generator",
                    "export_time": datetime.now().isoformat(),
                    "log_entries": log_entries
                }, f, indent=2)
                
            self.logger.info(f"Log exported as JSON to: {export_path}")
            return export_path
            
        except Exception as e:
            self.logger.error(f"Error exporting log as JSON: {str(e)}")
            return None
    
    def _get_log_level(self, level_str):
        """Convert string log level to logging constant."""
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return levels.get(level_str.upper(), logging.INFO)


# Singleton logger instance
_logger_instance = None

def get_logger():
    """Access function to get the configured logger."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ApplicationLogger()
    return _logger_instance.get_logger()

def export_log_file(export_path=None):
    """Export the log file to a specified path or return current path."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ApplicationLogger()
    return _logger_instance.export_log(export_path)

def export_log_as_json(export_path=None):
    """Export the log as JSON to a specified path."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ApplicationLogger()
    return _logger_instance.export_log_as_json(export_path)