"""
Automated Zoom Poll Generator - Production Version
Main application script for the desktop automation tool
"""

import os
import sys
import time
import logging
import platform
import argparse
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import threading
import PySimpleGUI as sg
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import print as rprint
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import custom modules
from logger import get_logger, export_log_file
from transcript_capture import TranscriptCapture
from chatgpt_integration import ChatGPTIntegration
from poll_posting import PollPosting
from scheduler import TaskScheduler
from zoom_automation import ZoomAutomation

# Initialize logger
logger = get_logger()

# Set up Rich console
console = Console(theme=Theme({
    "info": "bright_blue",
    "warning": "yellow",
    "error": "bold red",
    "success": "green"
}))

# Default configuration
DEFAULT_CONFIG = {
    "zoom_client_type": "web",  # "web" or "desktop"
    "transcript_interval": 10,   # minutes
    "poll_interval": 15,         # minutes
    "display_name": "Poll Generator",
    "auto_enable_captions": True,
    "auto_start": False,
    "chatgpt_integration_method": "browser",  # "browser" or "api"
    "check_interval": 30,        # seconds
    "save_transcripts": True,
    "transcripts_folder": "./transcripts"
}

# Runtime state
app_state = {
    "is_running": False,
    "meeting_active": False,
    "meeting_id": "",
    "passcode": "",
    "recent_transcript": "",
    "current_poll": None,
    "next_transcript_time": None,
    "next_poll_time": None,
    "config": DEFAULT_CONFIG.copy()
}

# Module instances
transcript_capture = None
chatgpt_integration = None
poll_posting = None
scheduler = None
zoom_automation = None


def initialize_modules():
    """Initialize all application modules based on configuration."""
    global transcript_capture, chatgpt_integration, poll_posting, scheduler, zoom_automation
    
    try:
        # Get client type from config
        client_type = app_state["config"]["zoom_client_type"]
        logger.info(f"Initializing modules with client type: {client_type}")
        
        # Initialize modules
        transcript_capture = TranscriptCapture(client_type)
        chatgpt_integration = ChatGPTIntegration()
        poll_posting = PollPosting(client_type)
        scheduler = TaskScheduler()
        zoom_automation = ZoomAutomation(client_type)
        
        # Create transcripts directory if it doesn't exist
        if app_state["config"]["save_transcripts"]:
            os.makedirs(app_state["config"]["transcripts_folder"], exist_ok=True)
        
        logger.info("All modules initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing modules: {str(e)}")
        console.print(f"[error]Error initializing application modules: {str(e)}")
        return False


def load_config():
    """Load configuration from config file."""
    config_path = Path("./config.json")
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Update default config with loaded values
            app_state["config"].update(config)
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            console.print(f"[warning]Warning: Could not load configuration. Using defaults.")
    else:
        logger.info("No configuration file found. Using defaults.")
        save_config()  # Create default config file


def save_config():
    """Save current configuration to config file."""
    config_path = Path("./config.json")
    
    try:
        with open(config_path, 'w') as f:
            json.dump(app_state["config"], f, indent=4)
        logger.info("Configuration saved successfully")
    except Exception as e:
        logger.error(f"Error saving configuration: {str(e)}")
        console.print(f"[warning]Warning: Could not save configuration: {str(e)}")


def join_meeting(meeting_id, passcode):
    """Join a Zoom meeting."""
    global zoom_automation
    
    # Store meeting details
    app_state["meeting_id"] = meeting_id
    app_state["passcode"] = passcode
    
    # Join meeting
    display_name = app_state["config"]["display_name"]
    client_type = app_state["config"]["zoom_client_type"]
    
    console.print(f"[info]Joining Zoom meeting with ID {meeting_id}...")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[blue]Joining meeting...", total=None)
        
        result = zoom_automation.join_meeting(meeting_id, passcode, display_name)
        progress.update(task, completed=1)
    
    if result:
        app_state["meeting_active"] = True
        logger.info(f"Successfully joined meeting {meeting_id}")
        console.print(f"[success]Successfully joined meeting!")
        
        # Enable captions if configured
        if app_state["config"]["auto_enable_captions"]:
            console.print("[info]Enabling closed captions...")
            if zoom_automation.enable_closed_captioning():
                console.print("[success]Closed captions enabled")
            else:
                console.print("[warning]Could not enable closed captions - may not be available")
        
        return True
    else:
        logger.error(f"Failed to join meeting {meeting_id}")
        console.print(f"[error]Failed to join meeting. Please check your meeting ID and passcode.")
        return False


def leave_meeting():
    """Leave the current Zoom meeting."""
    global zoom_automation
    
    if not app_state["meeting_active"]:
        console.print("[warning]No active meeting to leave")
        return True
    
    console.print("[info]Leaving Zoom meeting...")
    result = zoom_automation.leave_meeting()
    
    if result:
        app_state["meeting_active"] = False
        app_state["meeting_id"] = ""
        app_state["passcode"] = ""
        logger.info("Left meeting successfully")
        console.print("[success]Left meeting successfully")
        return True
    else:
        logger.error("Failed to leave meeting")
        console.print("[error]Failed to leave meeting properly. You may need to close Zoom manually.")
        return False


def capture_transcript():
    """Capture a transcript from the current meeting."""
    global transcript_capture
    
    if not app_state["meeting_active"]:
        logger.warning("Cannot capture transcript - no active meeting")
        console.print("[warning]Cannot capture transcript - not in a meeting")
        return False
    
    console.print("[info]Capturing transcript from meeting...")
    
    transcript = transcript_capture.capture_transcript()
    
    if transcript:
        app_state["recent_transcript"] = transcript
        # Save transcript if configured
        if app_state["config"]["save_transcripts"]:
            save_transcript(transcript)
            
        # Update next transcript capture time
        app_state["next_transcript_time"] = datetime.now() + timedelta(minutes=app_state["config"]["transcript_interval"])
        
        logger.info(f"Transcript captured: {len(transcript)} characters")
        console.print(f"[success]Transcript captured successfully ({len(transcript)} characters)")
        return True
    else:
        logger.error("Failed to capture transcript")
        console.print("[error]Failed to capture transcript")
        return False


def save_transcript(transcript):
    """Save the transcript to a file."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transcript_{timestamp}.txt"
        filepath = os.path.join(app_state["config"]["transcripts_folder"], filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(transcript)
            
        logger.info(f"Transcript saved to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error saving transcript: {str(e)}")
        return False


def generate_poll():
    """Generate a poll from the recent transcript."""
    global chatgpt_integration
    
    if not app_state["recent_transcript"]:
        logger.warning("Cannot generate poll - no transcript available")
        console.print("[warning]Cannot generate poll - no transcript available")
        return False
    
    console.print("[info]Generating poll from transcript...")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[blue]Processing with ChatGPT...", total=None)
        
        poll_data = chatgpt_integration.generate_poll_with_chatgpt(app_state["recent_transcript"])
        progress.update(task, completed=1)
    
    if poll_data:
        app_state["current_poll"] = poll_data
        logger.info(f"Poll generated: {poll_data['question']}")
        console.print(f"[success]Poll generated successfully:")
        console.print(Panel(f"{poll_data['question']}\n\n" + "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(poll_data['options'])]), 
                           title="Generated Poll", border_style="green"))
        return True
    else:
        logger.error("Failed to generate poll")
        console.print("[error]Failed to generate poll from transcript")
        return False


def post_poll():
    """Post the current poll to the Zoom meeting."""
    global poll_posting
    
    if not app_state["meeting_active"]:
        logger.warning("Cannot post poll - no active meeting")
        console.print("[warning]Cannot post poll - not in a meeting")
        return False
    
    if not app_state["current_poll"]:
        logger.warning("Cannot post poll - no poll generated")
        console.print("[warning]Cannot post poll - no poll has been generated")
        return False
    
    console.print("[info]Posting poll to meeting...")
    
    result = poll_posting.post_poll_to_zoom(app_state["current_poll"])
    
    if result:
        # Clear current poll after posting
        poll_data = app_state["current_poll"]
        app_state["current_poll"] = None
        
        # Update next poll time
        app_state["next_poll_time"] = datetime.now() + timedelta(minutes=app_state["config"]["poll_interval"])
        
        logger.info(f"Poll posted successfully: {poll_data['question']}")
        console.print("[success]Poll posted successfully")
        return True
    else:
        logger.error("Failed to post poll")
        console.print("[error]Failed to post poll. Please check if polling is enabled for your account.")
        return False


def run_scheduled_workflow():
    """Run the main workflow on a schedule."""
    if not app_state["is_running"]:
        return
    
    try:
        # Check if meeting is still active
        if app_state["meeting_active"] and not zoom_automation.check_meeting_status():
            logger.warning("Meeting appears to have ended")
            console.print("[warning]Meeting appears to have ended")
            app_state["meeting_active"] = False
            stop_automation()
            return
        
        now = datetime.now()
        
        # Check if it's time to capture transcript
        if app_state["next_transcript_time"] and now >= app_state["next_transcript_time"]:
            logger.info("Scheduled transcript capture triggered")
            capture_transcript()
            
            # Schedule poll generation after transcript capture
            threading.Timer(10, generate_poll).start()
        
        # Check if it's time to post poll
        if app_state["next_poll_time"] and now >= app_state["next_poll_time"]:
            logger.info("Scheduled poll posting triggered")
            
            # If we have a current poll, post it
            if app_state["current_poll"]:
                post_poll()
            # Otherwise try to generate and post a new one
            elif app_state["recent_transcript"]:
                if generate_poll():
                    threading.Timer(5, post_poll).start()
        
        # Schedule next check
        if app_state["is_running"]:
            threading.Timer(app_state["config"]["check_interval"], run_scheduled_workflow).start()
            
    except Exception as e:
        logger.error(f"Error in scheduled workflow: {str(e)}")
        console.print(f"[error]Error in automation workflow: {str(e)}")


def start_automation():
    """Start the automated workflow."""
    if app_state["is_running"]:
        console.print("[warning]Automation is already running")
        return
    
    if not app_state["meeting_active"]:
        console.print("[warning]Cannot start automation - not in a meeting")
        return
    
    app_state["is_running"] = True
    
    # Set initial scheduled times
    app_state["next_transcript_time"] = datetime.now() + timedelta(minutes=app_state["config"]["transcript_interval"])
    app_state["next_poll_time"] = datetime.now() + timedelta(minutes=app_state["config"]["poll_interval"])
    
    # Perform initial capture and poll
    capture_transcript()
    threading.Timer(5, generate_poll).start()
    
    # Start the scheduled workflow
    threading.Timer(app_state["config"]["check_interval"], run_scheduled_workflow).start()
    
    logger.info("Automation started")
    console.print("[success]Automation started successfully")
    console.print(f"[info]Next transcript capture: {app_state['next_transcript_time'].strftime('%H:%M:%S')}")
    console.print(f"[info]Next poll posting: {app_state['next_poll_time'].strftime('%H:%M:%S')}")


def stop_automation():
    """Stop the automated workflow."""
    if not app_state["is_running"]:
        console.print("[warning]Automation is not running")
        return
    
    app_state["is_running"] = False
    logger.info("Automation stopped")
    console.print("[info]Automation stopped")


def cleanup():
    """Clean up resources before exiting."""
    logger.info("Cleaning up resources")
    
    # Stop automation if running
    if app_state["is_running"]:
        stop_automation()
    
    # Leave meeting if active
    if app_state["meeting_active"]:
        leave_meeting()
    
    # Close browser if open
    if chatgpt_integration:
        chatgpt_integration.close_browser()
    if zoom_automation and zoom_automation.driver:
        zoom_automation.close_browser()
    
    # Save configuration
    save_config()
    
    logger.info("Cleanup complete")


def show_status():
    """Display the current application status."""
    table = Table(title="Application Status")
    
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Running", "✓ Yes" if app_state["is_running"] else "✗ No")
    table.add_row("Meeting Active", "✓ Yes" if app_state["meeting_active"] else "✗ No")
    if app_state["meeting_active"]:
        table.add_row("Meeting ID", app_state["meeting_id"])
    table.add_row("Zoom Client", app_state["config"]["zoom_client_type"].capitalize())
    table.add_row("Transcript Available", "✓ Yes" if app_state["recent_transcript"] else "✗ No")
    table.add_row("Poll Ready", "✓ Yes" if app_state["current_poll"] else "✗ No")
    
    if app_state["next_transcript_time"]:
        table.add_row("Next Transcript", app_state["next_transcript_time"].strftime("%H:%M:%S"))
    if app_state["next_poll_time"]:
        table.add_row("Next Poll", app_state["next_poll_time"].strftime("%H:%M:%S"))
    
    console.print(table)


def show_config():
    """Display the current configuration."""
    table = Table(title="Application Configuration")
    
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    for key, value in app_state["config"].items():
        table.add_row(key.replace("_", " ").title(), str(value))
    
    console.print(table)


def change_config():
    """Change configuration settings."""
    console.print("[info]Change Configuration")
    console.print("Current configuration:")
    show_config()
    
    config = app_state["config"]
    
    # Client type
    client_type = Prompt.ask(
        "Zoom client type",
        choices=["web", "desktop"],
        default=config["zoom_client_type"]
    )
    
    # Intervals
    transcript_interval = int(Prompt.ask(
        "Transcript capture interval (minutes)",
        default=str(config["transcript_interval"])
    ))
    
    poll_interval = int(Prompt.ask(
        "Poll posting interval (minutes)",
        default=str(config["poll_interval"])
    ))
    
    # Display name
    display_name = Prompt.ask(
        "Display name in meetings",
        default=config["display_name"]
    )
    
    # Auto-enable captions
    auto_captions = Confirm.ask(
        "Automatically enable closed captions?",
        default=config["auto_enable_captions"]
    )
    
    # Integration method
    integration_method = Prompt.ask(
        "ChatGPT integration method",
        choices=["browser", "api"],
        default=config["chatgpt_integration_method"]
    )
    
    # Save transcripts
    save_transcripts = Confirm.ask(
        "Save transcripts to files?",
        default=config["save_transcripts"]
    )
    
    # Update config
    config["zoom_client_type"] = client_type
    config["transcript_interval"] = transcript_interval
    config["poll_interval"] = poll_interval
    config["display_name"] = display_name
    config["auto_enable_captions"] = auto_captions
    config["chatgpt_integration_method"] = integration_method
    config["save_transcripts"] = save_transcripts
    
    # Reinitialize modules if client type changed
    if client_type != app_state["config"]["zoom_client_type"]:
        console.print("[info]Client type changed, reinitializing modules...")
        initialize_modules()
    
    # Save configuration
    save_config()
    
    console.print("[success]Configuration updated successfully")


def run_cli():
    """Run the application in CLI mode."""
    console.print(Panel.fit(
        "[bold green]Automated Zoom Poll Generator[/bold green]\n"
        "[blue]Version 1.0.0[/blue]\n\n"
        "This application automates capturing transcripts from Zoom meetings,\n"
        "generating polls based on the content, and posting them automatically.",
        title="Welcome", subtitle="Production Version"
    ))
    
    # Load configuration
    load_config()
    
    # Initialize modules
    if not initialize_modules():
        console.print("[error]Failed to initialize application. Exiting.")
        return
    
    try:
        while True:
            console.print("\n[bold cyan]Main Menu[/bold cyan]")
            console.print("1. Join a meeting")
            console.print("2. Leave meeting")
            console.print("3. Start automation")
            console.print("4. Stop automation")
            console.print("5. Capture transcript now")
            console.print("6. Generate poll now")
            console.print("7. Post poll now")
            console.print("8. Show status")
            console.print("9. Show/change configuration")
            console.print("0. Exit")
            
            choice = Prompt.ask("Select an option", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
            
            if choice == "1":  # Join a meeting
                meeting_id = Prompt.ask("Enter meeting ID")
                passcode = Prompt.ask("Enter meeting passcode")
                join_meeting(meeting_id, passcode)
                
                if app_state["meeting_active"] and app_state["config"]["auto_start"]:
                    start_automation()
                    
            elif choice == "2":  # Leave meeting
                leave_meeting()
                
            elif choice == "3":  # Start automation
                start_automation()
                
            elif choice == "4":  # Stop automation
                stop_automation()
                
            elif choice == "5":  # Capture transcript
                capture_transcript()
                
            elif choice == "6":  # Generate poll
                generate_poll()
                
            elif choice == "7":  # Post poll
                post_poll()
                
            elif choice == "8":  # Show status
                show_status()
                
            elif choice == "9":  # Show/change configuration
                subchoice = Prompt.ask("1. Show configuration\n2. Change configuration", choices=["1", "2"])
                if subchoice == "1":
                    show_config()
                else:
                    change_config()
                    
            elif choice == "0":  # Exit
                if Confirm.ask("Are you sure you want to exit?"):
                    break
    
    except KeyboardInterrupt:
        console.print("\n[warning]Interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        console.print(f"[error]Unexpected error: {str(e)}")
    finally:
        # Clean up resources
        cleanup()
        console.print("\n[info]Exiting Automated Zoom Poll Generator. Goodbye!")


def create_gui_window():
    """Create the main GUI window."""
    sg.theme('DarkBlue3')  # Set the theme
    
    # Define the layout
    layout = [
        [sg.Text('Automated Zoom Poll Generator', font=('Helvetica', 16), justification='center', expand_x=True)],
        [sg.Text('Meeting Details', font=('Helvetica', 11))],
        [sg.Text('Meeting ID:'), sg.InputText(key='-MEETING_ID-', size=(20, 1)), 
         sg.Text('Passcode:'), sg.InputText(key='-PASSCODE-', size=(15, 1)), 
         sg.Button('Join Meeting', key='-JOIN-'), sg.Button('Leave Meeting', key='-LEAVE-', disabled=True)],
        [sg.HSeparator()],
        [sg.Text('Automation Controls', font=('Helvetica', 11))],
        [sg.Button('Start Automation', key='-START-', disabled=True), 
         sg.Button('Stop Automation', key='-STOP-', disabled=True),
         sg.Button('Capture Now', key='-CAPTURE-', disabled=True),
         sg.Button('Generate Poll', key='-GENERATE-', disabled=True),
         sg.Button('Post Poll', key='-POST-', disabled=True)],
        [sg.HSeparator()],
        [sg.Text('Status', font=('Helvetica', 11))],
        [sg.Column([
            [sg.Text('Meeting Status:'), sg.Text('Not in meeting', key='-MEETING_STATUS-')],
            [sg.Text('Automation:'), sg.Text('Not running', key='-AUTO_STATUS-')],
            [sg.Text('Transcript:'), sg.Text('Not available', key='-TRANSCRIPT_STATUS-')],
            [sg.Text('Poll:'), sg.Text('Not available', key='-POLL_STATUS-')],
            [sg.Text('Next Transcript:'), sg.Text('Not scheduled', key='-NEXT_TRANSCRIPT-')],
            [sg.Text('Next Poll:'), sg.Text('Not scheduled', key='-NEXT_POLL-')]
        ], expand_x=True, expand_y=True)],
        [sg.HSeparator()],
        [sg.Text('Log Output', font=('Helvetica', 11))],
        [sg.Multiline(size=(80, 15), key='-LOG-', autoscroll=True, disabled=True, background_color='black', text_color='white')],
        [sg.Button('Configuration', key='-CONFIG-'), sg.Button('Export Logs', key='-EXPORT-'), 
         sg.Button('About', key='-ABOUT-'), sg.Button('Exit', key='-EXIT-')]
    ]
    
    # Create the window
    window = sg.Window('Automated Zoom Poll Generator', layout, finalize=True, resizable=True, size=(800, 600))
    
    return window


def update_gui(window):
    """Update the GUI with current application state."""
    # Update meeting status
    if app_state["meeting_active"]:
        window['-MEETING_STATUS-'].update('In meeting')
        window['-JOIN-'].update(disabled=True)
        window['-LEAVE-'].update(disabled=False)
        window['-CAPTURE-'].update(disabled=False)
        window['-START-'].update(disabled=False)
    else:
        window['-MEETING_STATUS-'].update('Not in meeting')
        window['-JOIN-'].update(disabled=False)
        window['-LEAVE-'].update(disabled=True)
        window['-CAPTURE-'].update(disabled=True)
        window['-START-'].update(disabled=True)
        window['-GENERATE-'].update(disabled=True)
        window['-POST-'].update(disabled=True)
    
    # Update automation status
    if app_state["is_running"]:
        window['-AUTO_STATUS-'].update('Running')
        window['-START-'].update(disabled=True)
        window['-STOP-'].update(disabled=False)
    else:
        window['-AUTO_STATUS-'].update('Not running')
        window['-START-'].update(disabled=not app_state["meeting_active"])
        window['-STOP-'].update(disabled=True)
    
    # Update transcript status
    if app_state["recent_transcript"]:
        window['-TRANSCRIPT_STATUS-'].update('Available')
        window['-GENERATE-'].update(disabled=False)
    else:
        window['-TRANSCRIPT_STATUS-'].update('Not available')
        window['-GENERATE-'].update(disabled=True)
    
    # Update poll status
    if app_state["current_poll"]:
        window['-POLL_STATUS-'].update('Ready to post')
        window['-POST-'].update(disabled=not app_state["meeting_active"])
    else:
        window['-POLL_STATUS-'].update('Not available')
        window['-POST-'].update(disabled=True)
    
    # Update scheduled times
    if app_state["next_transcript_time"]:
        window['-NEXT_TRANSCRIPT-'].update(app_state["next_transcript_time"].strftime("%H:%M:%S"))
    else:
        window['-NEXT_TRANSCRIPT-'].update('Not scheduled')
        
    if app_state["next_poll_time"]:
        window['-NEXT_POLL-'].update(app_state["next_poll_time"].strftime("%H:%M:%S"))
    else:
        window['-NEXT_POLL-'].update('Not scheduled')


def add_log_to_gui(window, message):
    """Add a log message to the GUI log output."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    window['-LOG-'].print(f"[{timestamp}] {message}")


def run_gui():
    """Run the application in GUI mode."""
    # Load configuration
    load_config()
    
    # Initialize modules
    if not initialize_modules():
        sg.popup_error("Failed to initialize application modules. Please check logs for details.")
        return
    
    # Create main window
    window = create_gui_window()
    
    # Setup GUI logging
    class GUILogHandler(logging.Handler):
        def emit(self, record):
            log_message = self.format(record)
            add_log_to_gui(window, log_message)
    
    # Add GUI handler to logger
    gui_handler = GUILogHandler()
    gui_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(gui_handler)
    
    # Log startup
    add_log_to_gui(window, "Application started")
    
    # Main event loop
    try:
        while True:
            event, values = window.read(timeout=1000)  # Update GUI every second
            
            if event == sg.WIN_CLOSED or event == '-EXIT-':
                if sg.popup_yes_no("Are you sure you want to exit?") == "Yes":
                    break
            
            elif event == '-JOIN-':
                meeting_id = values['-MEETING_ID-']
                passcode = values['-PASSCODE-']
                
                if not meeting_id or not passcode:
                    sg.popup_error("Please enter both meeting ID and passcode")
                    continue
                
                # Join meeting in a separate thread to keep GUI responsive
                def join_thread():
                    result = join_meeting(meeting_id, passcode)
                    if result and app_state["config"]["auto_start"]:
                        start_automation()
                
                threading.Thread(target=join_thread, daemon=True).start()
            
            elif event == '-LEAVE-':
                threading.Thread(target=leave_meeting, daemon=True).start()
            
            elif event == '-START-':
                threading.Thread(target=start_automation, daemon=True).start()
            
            elif event == '-STOP-':
                stop_automation()
            
            elif event == '-CAPTURE-':
                threading.Thread(target=capture_transcript, daemon=True).start()
            
            elif event == '-GENERATE-':
                threading.Thread(target=generate_poll, daemon=True).start()
            
            elif event == '-POST-':
                threading.Thread(target=post_poll, daemon=True).start()
            
            elif event == '-CONFIG-':
                # Open configuration window
                config_layout = [
                    [sg.Text('Zoom Configuration')],
                    [sg.Text('Zoom Client Type:'), 
                     sg.Radio('Web Client', 'CLIENT', key='-WEB-', default=app_state["config"]["zoom_client_type"]=="web"),
                     sg.Radio('Desktop Client', 'CLIENT', key='-DESKTOP-', default=app_state["config"]["zoom_client_type"]=="desktop")],
                    [sg.Text('Display Name:'), sg.InputText(app_state["config"]["display_name"], key='-DISPLAY_NAME-')],
                    [sg.Checkbox('Auto-enable Captions', key='-CAPTIONS-', default=app_state["config"]["auto_enable_captions"])],
                    [sg.HSeparator()],
                    [sg.Text('Automation Settings')],
                    [sg.Text('Transcript Interval (minutes):'), 
                     sg.Spin([i for i in range(1, 61)], initial_value=app_state["config"]["transcript_interval"], key='-TRANSCRIPT_INT-')],
                    [sg.Text('Poll Interval (minutes):'), 
                     sg.Spin([i for i in range(1, 61)], initial_value=app_state["config"]["poll_interval"], key='-POLL_INT-')],
                    [sg.Text('ChatGPT Integration:'), 
                     sg.Radio('Browser', 'INTEGRATION', key='-BROWSER-', default=app_state["config"]["chatgpt_integration_method"]=="browser"),
                     sg.Radio('API', 'INTEGRATION', key='-API-', default=app_state["config"]["chatgpt_integration_method"]=="api")],
                    [sg.Checkbox('Save Transcripts', key='-SAVE_TRANSCRIPTS-', default=app_state["config"]["save_transcripts"])],
                    [sg.Button('Save'), sg.Button('Cancel')]
                ]
                
                config_window = sg.Window('Configuration', config_layout, modal=True)
                
                while True:
                    config_event, config_values = config_window.read()
                    
                    if config_event in (sg.WIN_CLOSED, 'Cancel'):
                        break
                    
                    if config_event == 'Save':
                        # Update configuration
                        new_client_type = "web" if config_values['-WEB-'] else "desktop"
                        new_integration = "browser" if config_values['-BROWSER-'] else "api"
                        
                        app_state["config"]["zoom_client_type"] = new_client_type
                        app_state["config"]["display_name"] = config_values['-DISPLAY_NAME-']
                        app_state["config"]["auto_enable_captions"] = config_values['-CAPTIONS-']
                        app_state["config"]["transcript_interval"] = int(config_values['-TRANSCRIPT_INT-'])
                        app_state["config"]["poll_interval"] = int(config_values['-POLL_INT-'])
                        app_state["config"]["chatgpt_integration_method"] = new_integration
                        app_state["config"]["save_transcripts"] = config_values['-SAVE_TRANSCRIPTS-']
                        
                        # Reinitialize modules if client type changed
                        if new_client_type != app_state["config"]["zoom_client_type"] and not app_state["meeting_active"]:
                            initialize_modules()
                        
                        # Save configuration
                        save_config()
                        add_log_to_gui(window, "Configuration updated")
                        break
                
                config_window.close()
            
            elif event == '-EXPORT-':
                # Export logs
                export_path = sg.popup_get_file('Save log file as', save_as=True, file_types=(("Text Files", "*.txt"),))
                if export_path:
                    if export_log_file(export_path):
                        sg.popup(f"Logs exported to {export_path}")
                    else:
                        sg.popup_error("Failed to export logs")
            
            elif event == '-ABOUT-':
                sg.popup("Automated Zoom Poll Generator", 
                       "Version 1.0.0", 
                       "This application automates capturing transcripts from Zoom meetings,",
                       "generating polls based on the content, and posting them automatically.")
            
            # Update GUI with current state
            update_gui(window)
    
    except Exception as e:
        logger.error(f"Unexpected error in GUI: {str(e)}")
        sg.popup_error(f"An unexpected error occurred: {str(e)}")
    finally:
        # Clean up resources
        cleanup()
        window.close()


def main():
    """Application entry point."""
    parser = argparse.ArgumentParser(description="Automated Zoom Poll Generator")
    parser.add_argument('--cli', action='store_true', help="Use command-line interface instead of GUI")
    parser.add_argument('--meeting', type=str, help="Meeting ID to join automatically on startup")
    parser.add_argument('--passcode', type=str, help="Meeting passcode")
    parser.add_argument('--auto-start', action='store_true', help="Automatically start automation after joining")
    
    args = parser.parse_args()
    
    # Set auto-start flag if provided
    if args.auto_start:
        app_state["config"]["auto_start"] = True
    
    try:
        # Run in CLI or GUI mode
        if args.cli:
            run_cli()
        else:
            # If meeting ID and passcode provided, join automatically after GUI starts
            if args.meeting and args.passcode:
                def auto_join():
                    time.sleep(1)  # Short delay to ensure GUI is ready
                    join_meeting(args.meeting, args.passcode)
                    if app_state["meeting_active"] and app_state["config"]["auto_start"]:
                        start_automation()
                
                threading.Thread(target=auto_join, daemon=True).start()
            
            run_gui()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        console.print(f"[error]Fatal error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())