"""
Main entry point for the Automated Zoom Poll Generator.
"""

import os
import sys
import time
import signal
import logging
import argparse
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Any, Optional

# Configure basic logging before imports
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the Flask app for gunicorn
from app import app

# Import application modules
try:
    from dotenv import load_dotenv
    
    # Import core modules
    from logger import get_logger
    from config import load_config, save_config
    from transcript_capture import create_transcript_capture
    from chatgpt_integration import create_chatgpt_integration
    from poll_posting import create_poll_posting
    from zoom_automation import create_zoom_automation
    from scheduler import create_scheduler
    from credential_manager import create_credential_manager
    
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    logger.error("Please install required packages using pip install -r requirements.txt")
    sys.exit(1)

# Load environment variables from .env file if it exists
load_dotenv()

# Global variables
transcript_capture = None
chatgpt_integration = None
poll_posting = None
zoom_automation = None
scheduler = None
credential_manager = None
config = None
recent_transcript = None
current_poll = None
session_active = False

class CredentialsDialog:
    def __init__(self, parent):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Enter Zoom Meeting Credentials")
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create widgets
        frame = ttk.Frame(self.dialog, padding="10")
        frame.grid(row=0, column=0, sticky="nsew")
        
        ttk.Label(frame, text="Meeting ID:").grid(row=0, column=0, sticky="w", pady=5)
        self.meeting_id = ttk.Entry(frame, width=30)
        self.meeting_id.grid(row=0, column=1, sticky="w", pady=5)
        
        ttk.Label(frame, text="Passcode:").grid(row=1, column=0, sticky="w", pady=5)
        self.passcode = ttk.Entry(frame, width=30)
        self.passcode.grid(row=1, column=1, sticky="w", pady=5)
        
        ttk.Label(frame, text="Display Name:").grid(row=2, column=0, sticky="w", pady=5)
        self.display_name = ttk.Entry(frame, width=30)
        self.display_name.insert(0, "Poll Generator")
        self.display_name.grid(row=2, column=1, sticky="w", pady=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Join", command=self.on_join).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.on_cancel).pack(side="left", padx=5)

    def on_join(self):
        if not self.meeting_id.get() or not self.passcode.get():
            messagebox.showerror("Error", "Please enter both Meeting ID and Passcode")
            return
            
        self.result = {
            "meeting_id": self.meeting_id.get(),
            "passcode": self.passcode.get(),
            "display_name": self.display_name.get()
        }
        self.dialog.destroy()
        
    def on_cancel(self):
        self.dialog.destroy()

def prompt_credentials():
    """Prompt for Zoom meeting credentials using a GUI dialog."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    dialog = CredentialsDialog(root)
    root.wait_window(dialog.dialog)
    
    root.destroy()
    return dialog.result

def initialize() -> bool:
    """Initialize the application."""
    global transcript_capture, chatgpt_integration, poll_posting, zoom_automation, scheduler, credential_manager, config, session_active
    
    try:
        logger.debug("Logger initialized")
        logger.info("Initializing application")
        
        # Load configuration with desktop client type
        config = load_config()
        config["zoom_client_type"] = "desktop"  # Force desktop client type
        save_config(config)
        
        # Create component instances
        client_type = "desktop"  # Force desktop client type
        logger.info(f"Using Zoom client type: {client_type}")
        
        transcript_capture = create_transcript_capture(client_type=client_type)
        chatgpt_integration = create_chatgpt_integration()
        poll_posting = create_poll_posting(client_type=client_type)
        zoom_automation = create_zoom_automation(client_type=client_type)
        scheduler = create_scheduler(use_simple_scheduler=False)
        credential_manager = create_credential_manager()
        
        # Set up signal handling
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("Application initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        return False

def capture_transcript_task() -> Optional[str]:
    """
    Task to capture transcript from Zoom.
    This function is called by the scheduler.
    
    Returns:
        The captured transcript or None if capture failed
    """
    global recent_transcript
    
    logger.info("Executing scheduled transcript capture")
    
    try:
        # Capture transcript
        transcript = transcript_capture.capture_transcript()
        
        if transcript:
            recent_transcript = transcript
            logger.info(f"Transcript captured successfully ({len(transcript)} characters)")
            
            # Generate poll immediately after capturing transcript
            generate_poll_task()
            
            return transcript
        else:
            logger.warning("Failed to capture transcript")
            return None
            
    except Exception as e:
        logger.error(f"Error in transcript capture task: {str(e)}")
        return None

def generate_poll_task() -> Optional[Dict[str, Any]]:
    """
    Task to generate a poll from the recent transcript.
    This function can be called directly or after transcript capture.
    
    Returns:
        Dictionary containing poll data or None if generation failed
    """
    global recent_transcript, current_poll
    
    if not recent_transcript:
        logger.warning("No transcript available for poll generation")
        return None
    
    logger.info("Generating poll from transcript")
    
    try:
        # Generate poll using ChatGPT
        poll_data = chatgpt_integration.generate_poll_with_chatgpt(recent_transcript)
        
        if poll_data:
            current_poll = poll_data
            logger.info(f"Poll generated successfully: {poll_data['question']}")
            return poll_data
        else:
            logger.warning("Failed to generate poll")
            return None
            
    except Exception as e:
        logger.error(f"Error in poll generation task: {str(e)}")
        return None

def post_poll_task() -> bool:
    """
    Task to post the current poll to Zoom.
    This function is called by the scheduler.
    
    Returns:
        Boolean indicating whether posting was successful
    """
    global current_poll
    
    if not current_poll:
        logger.warning("No poll available to post")
        return False
    
    logger.info("Posting poll to Zoom")
    
    try:
        # Post poll to Zoom
        result = poll_posting.post_poll_to_zoom(current_poll)
        
        if result:
            logger.info("Poll posted successfully")
            return True
        else:
            logger.warning("Failed to post poll")
            return False
            
    except Exception as e:
        logger.error(f"Error in poll posting task: {str(e)}")
        return False

def start_session() -> bool:
    """
    Start a new poll generation session.
    
    Returns:
        Boolean indicating whether session start was successful
    """
    global session_active
    
    if session_active:
        logger.warning("Session is already active")
        return True
    
    logger.info("Starting new session")
    
    try:
        # Check if Zoom credentials are available
        zoom_credentials = credential_manager.load_zoom_credentials()
        if not zoom_credentials:
            zoom_credentials = credential_manager.prompt_for_zoom_credentials()
            if not zoom_credentials:
                logger.error("Zoom credentials are required to start a session")
                return False
        
        # Check if ChatGPT credentials are available
        chatgpt_credentials = credential_manager.load_chatgpt_credentials()
        if not chatgpt_credentials:
            chatgpt_credentials = credential_manager.prompt_for_chatgpt_credentials()
            if not chatgpt_credentials:
                logger.error("ChatGPT credentials are required to start a session")
                return False
        
        # Initialize browser for ChatGPT
        if not chatgpt_integration.initialize_browser():
            logger.error("Failed to initialize browser for ChatGPT")
            return False
        
        # Login to ChatGPT
        if not chatgpt_integration.login_to_chatgpt(chatgpt_credentials):
            logger.error("Failed to log in to ChatGPT")
            return False
        
        # Join Zoom meeting
        if not zoom_automation.join_meeting(
            zoom_credentials["meeting_id"],
            zoom_credentials["passcode"],
            zoom_credentials.get("display_name", "Poll Generator")
        ):
            logger.error("Failed to join Zoom meeting")
            return False
        
        # Enable closed captioning if configured
        if config.get("auto_enable_captions", True):
            if not zoom_automation.enable_closed_captioning():
                logger.warning("Failed to enable closed captioning")
        
        # Start the scheduler
        if not scheduler.start():
            logger.error("Failed to start scheduler")
            return False
        
        # Schedule regular transcript captures
        transcript_interval = config.get("transcript_interval", 10)  # minutes
        if not scheduler.schedule_transcript_capture(capture_transcript_task, transcript_interval):
            logger.error("Failed to schedule transcript captures")
            return False
        
        # Schedule regular poll postings
        poll_interval = config.get("poll_interval", 15)  # minutes
        if not scheduler.schedule_poll_posting(post_poll_task, poll_interval):
            logger.error("Failed to schedule poll postings")
            return False
        
        session_active = True
        logger.info(f"Session started successfully - capturing transcripts every {transcript_interval} minutes and posting polls every {poll_interval} minutes")
        return True
        
    except Exception as e:
        logger.error(f"Error starting session: {str(e)}")
        return False

def end_session() -> bool:
    """
    End the current poll generation session.
    
    Returns:
        Boolean indicating whether session end was successful
    """
    global session_active, recent_transcript, current_poll
    
    if not session_active:
        logger.warning("No active session to end")
        return True
    
    logger.info("Ending session")
    
    try:
        # Stop the scheduler
        scheduler.stop()
        
        # Leave Zoom meeting
        if zoom_automation:
            zoom_automation.leave_meeting()
        
        # Close browser
        if chatgpt_integration:
            chatgpt_integration.close_browser()
        
        # Reset session variables
        session_active = False
        recent_transcript = None
        current_poll = None
        
        logger.info("Session ended successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error ending session: {str(e)}")
        return False

def signal_handler(sig, frame):
    """
    Handle termination signals.
    """
    logger.info(f"Received signal {sig}, shutting down...")
    end_session()
    sys.exit(0)

def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Automated Zoom Poll Generator")
    
    parser.add_argument("--start", action="store_true", help="Start a poll generation session automatically")
    parser.add_argument("--client", choices=["web", "desktop"], help="Specify the Zoom client type to use")
    parser.add_argument("--transcript-interval", type=int, help="Interval between transcript captures in minutes")
    parser.add_argument("--poll-interval", type=int, help="Interval between poll postings in minutes")
    
    return parser.parse_args()

def main():
    """Main entry point."""
    if not initialize():
        logger.error("Failed to initialize application")
        sys.exit(1)
    
    try:
        # Prompt for credentials
        credentials = prompt_credentials()
        if not credentials:
            logger.info("User cancelled credential input")
            sys.exit(0)
        
        # Clean up existing Zoom processes
        try:
            import psutil
            for proc in psutil.process_iter(['name']):
                if 'zoom' in proc.info['name'].lower():
                    logger.info(f"Terminating existing Zoom process: {proc.info['name']}")
                    proc.kill()
                    time.sleep(2)
        except Exception as e:
            logger.warning(f"Could not check for existing Zoom process: {str(e)}")
        
        # Start session
        if not start_session():
            logger.error("Failed to start session")
            messagebox.showerror("Error", "Failed to start session. Please check logs for details.")
            sys.exit(1)
        
        # Join the meeting
        if not zoom_automation.join_meeting(
            credentials["meeting_id"],
            credentials["passcode"],
            credentials["display_name"]
        ):
            logger.error("Failed to join meeting")
            messagebox.showerror("Error", "Failed to join meeting. Please check your credentials and try again.")
            sys.exit(1)
        
        # Main application loop
        try:
            logger.info("Application is running. Press Ctrl+C to exit.")
            while True:
                # Check meeting status every 5 seconds
                if not zoom_automation.check_meeting_status():
                    logger.warning("Meeting status check failed, attempting to rejoin...")
                    zoom_automation.join_meeting(
                        credentials["meeting_id"],
                        credentials["passcode"],
                        credentials["display_name"]
                    )
                    
                # If transcripts are enabled, check and create directory
                if config["save_transcripts"]:
                    os.makedirs(config["transcripts_folder"], exist_ok=True)
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        messagebox.showerror("Error", f"A fatal error occurred: {str(e)}")
        sys.exit(1)
        
    finally:
        # Clean up
        try:
            if zoom_automation:
                zoom_automation.leave_meeting()
            end_session()
            logger.info("Application shutdown complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
        sys.exit(0)

if __name__ == "__main__":
    main()