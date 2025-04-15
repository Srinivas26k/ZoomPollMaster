"""
Automated Zoom Poll Generator
Main application module that orchestrates the workflow.

Usage:
1. Import and instantiate the ZoomPollGenerator class
2. Call setup() to perform initial setup
3. Call run() to start the application
4. Use perform_transcript_capture(), perform_poll_generation(), 
   and perform_poll_posting() for manual control
5. Call start() and stop() to control the automated workflow
"""

import os
import sys
import time
import json
import logging
import argparse
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dotenv import load_dotenv

# Import required modules
import os
import sys
import time
import logging
from dotenv import load_dotenv

# Try to load environment variables
load_dotenv()

# Check if running in web mode
WEB_MODE = True

# If we're not in web mode, import the desktop app modules
if not WEB_MODE:
    try:
        from logger import get_logger
        from config import WAIT_MEDIUM
        from credential_manager import CredentialManager
        from transcript_capture import TranscriptCapture
        from chatgpt_integration import ChatGPTIntegration
        from poll_posting import PollPosting
        from scheduler import TaskScheduler
        from gui import ApplicationGUI
        
        # Set up logger
        logger = get_logger()
        
        # Desktop application class
        class ZoomPollGenerator:
            """
            Main application class that orchestrates the workflow.
            """
            
            def __init__(self):
                """Initialize the application."""
                # Create module instances
                self.credential_manager = CredentialManager()
                self.transcript_capture = TranscriptCapture()
                self.chatgpt_integration = ChatGPTIntegration()
                self.poll_posting = PollPosting()
                self.scheduler = TaskScheduler()
                
                # Application state
                self.is_running = False
                self.recent_transcript = ""
                self.current_poll = None
                
                # Setup GUI with callbacks
                self.gui = ApplicationGUI({
                    "start": self.start,
                    "stop": self.stop,
                    "capture": self.perform_transcript_capture,
                    "generate_poll": self.perform_poll_generation,
                    "get_status": self.get_status,
                    "exit": self.exit
                })
                
                logger.info("Automated Zoom Poll Generator initialized")
            
            def setup(self):
                """Perform initial setup, prompt for credentials."""
                logger.info("Performing initial setup")
                
                # Prompt for Zoom credentials
                zoom_credentials = self.credential_manager.prompt_for_zoom_credentials()
                if not zoom_credentials:
                    logger.error("No Zoom credentials provided - cannot continue")
                    return False
                
                # Prompt for ChatGPT credentials
                chatgpt_credentials = self.credential_manager.prompt_for_chatgpt_credentials()
                if not chatgpt_credentials:
                    logger.error("No ChatGPT credentials provided - cannot continue")
                    return False
                
                # Initialize browser for ChatGPT
                if not self.chatgpt_integration.initialize_browser():
                    logger.error("Failed to initialize browser for ChatGPT")
                    return False
                
                # Login to ChatGPT
                if not self.chatgpt_integration.login_to_chatgpt(chatgpt_credentials):
                    logger.error("Failed to log in to ChatGPT")
                    return False
                
                logger.info("Initial setup completed successfully")
                return True
            
            def start(self):
                """Start the application workflow."""
                if self.is_running:
                    logger.warning("Application already running")
                    return
                
                logger.info("Starting application")
                
                try:
                    # Make sure setup is complete
                    if not self.setup():
                        logger.error("Setup failed - cannot start application")
                        return
                    
                    # Start scheduler
                    if not self.scheduler.start():
                        logger.error("Failed to start scheduler")
                        return
                    
                    # Schedule regular transcript capture
                    self.scheduler.schedule_transcript_capture(self.perform_transcript_capture)
                    
                    # Schedule regular poll posting
                    self.scheduler.schedule_poll_posting(self.perform_poll_workflow)
                    
                    self.is_running = True
                    logger.info("Application started successfully")
                    
                except Exception as e:
                    logger.error(f"Error starting application: {str(e)}")
            
            def stop(self):
                """Stop the application workflow."""
                if not self.is_running:
                    logger.warning("Application not running")
                    return
                
                logger.info("Stopping application")
                
                try:
                    # Stop scheduler
                    self.scheduler.stop()
                    
                    # Close browser
                    self.chatgpt_integration.close_browser()
                    
                    self.is_running = False
                    logger.info("Application stopped successfully")
                    
                except Exception as e:
                    logger.error(f"Error stopping application: {str(e)}")
            
            def exit(self):
                """Clean up resources and exit the application."""
                logger.info("Exiting application")
                
                try:
                    # Stop application if running
                    if self.is_running:
                        self.stop()
                    
                    # Clear credentials
                    self.credential_manager.clear_credentials()
                    
                    logger.info("Application exit complete")
                    
                except Exception as e:
                    logger.error(f"Error during application exit: {str(e)}")
            
            def perform_transcript_capture(self):
                """Perform transcript capture from Zoom."""
                logger.info("Performing transcript capture")
                
                try:
                    # Capture transcript
                    transcript = self.transcript_capture.capture_transcript()
                    
                    if not transcript:
                        logger.warning("No transcript captured")
                        return False
                    
                    self.recent_transcript = transcript
                    logger.info(f"Transcript captured successfully ({len(transcript)} characters)")
                    
                    # Schedule poll generation after capture
                    self.scheduler.schedule_one_time_task(
                        self.perform_poll_generation,
                        WAIT_MEDIUM,
                        "poll_generation_after_capture"
                    )
                    
                    return True
                    
                except Exception as e:
                    logger.error(f"Error during transcript capture: {str(e)}")
                    return False
            
            def perform_poll_generation(self):
                """Generate a poll using the recent transcript."""
                logger.info("Performing poll generation")
                
                try:
                    # Make sure we have a transcript
                    if not self.recent_transcript:
                        logger.warning("No recent transcript available for poll generation")
                        return False
                    
                    # Generate poll with ChatGPT
                    poll_data = self.chatgpt_integration.generate_poll_with_chatgpt(self.recent_transcript)
                    
                    if not poll_data:
                        logger.error("Failed to generate poll")
                        return False
                    
                    self.current_poll = poll_data
                    logger.info(f"Poll generated successfully: {poll_data['question']}")
                    
                    return True
                    
                except Exception as e:
                    logger.error(f"Error during poll generation: {str(e)}")
                    return False
            
            def perform_poll_posting(self):
                """Post the current poll to Zoom."""
                logger.info("Performing poll posting")
                
                try:
                    # Make sure we have a poll
                    if not self.current_poll:
                        logger.warning("No current poll available for posting")
                        return False
                    
                    # Post poll to Zoom
                    result = self.poll_posting.post_poll_to_zoom(self.current_poll)
                    
                    if not result:
                        logger.error("Failed to post poll to Zoom")
                        return False
                    
                    logger.info("Poll posted to Zoom successfully")
                    
                    # Clear current poll after posting
                    self.current_poll = None
                    
                    return True
                    
                except Exception as e:
                    logger.error(f"Error during poll posting: {str(e)}")
                    return False
            
            def perform_poll_workflow(self):
                """
                Perform the complete poll workflow:
                1. Capture transcript (if needed)
                2. Generate poll (if needed)
                3. Post poll
                """
                logger.info("Starting poll workflow")
                
                try:
                    # Capture transcript if we don't have a recent one
                    if not self.recent_transcript:
                        if not self.perform_transcript_capture():
                            logger.error("Failed to capture transcript - cannot continue workflow")
                            return False
                    
                    # Generate poll if we don't have a current one
                    if not self.current_poll:
                        if not self.perform_poll_generation():
                            logger.error("Failed to generate poll - cannot continue workflow")
                            return False
                    
                    # Post the poll
                    if not self.perform_poll_posting():
                        logger.error("Failed to post poll")
                        return False
                    
                    logger.info("Poll workflow completed successfully")
                    return True
                    
                except Exception as e:
                    logger.error(f"Error during poll workflow: {str(e)}")
                    return False
            
            def get_status(self):
                """
                Get the current status of the application.
                
                Returns:
                    Dict containing status information
                """
                status = {
                    "is_running": self.is_running,
                    "has_recent_transcript": bool(self.recent_transcript),
                    "has_current_poll": bool(self.current_poll)
                }
                
                # Add scheduler status if available
                if self.scheduler:
                    scheduler_status = self.scheduler.get_status()
                    status.update(scheduler_status)
                
                return status
            
            def run(self):
                """Run the application with GUI."""
                logger.info("Starting Automated Zoom Poll Generator")
                
                try:
                    # Create and run GUI
                    self.gui.run()
                    
                except Exception as e:
                    logger.error(f"Error running application: {str(e)}")
                    
                finally:
                    # Clean up on exit
                    self.exit()
    
    except ImportError as e:
        print(f"Warning: Import error when loading desktop modules: {e}")
        print("Running in web mode instead")
        WEB_MODE = True

# Web application import and setup
if WEB_MODE:
    # Import Flask app
    try:
        from app import app
        print("Successfully loaded Flask web application")
    except ImportError as e:
        print(f"Error: Could not import Flask app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if WEB_MODE:
        # Run Flask app
        port = int(os.environ.get("PORT", 5000))
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        # Create and run desktop application
        app = ZoomPollGenerator()
        app.run()