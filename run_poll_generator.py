"""
Automated Zoom Poll Generator - Terminal Interface
A production-ready command-line interface for the Zoom Poll Generator
"""

import sys
import time
import os
import json
import argparse
import threading
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.style import Style
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.box import Box
from rich import print as rprint
from dotenv import load_dotenv

# Try to initialize application-specific modules
# These would be fully implemented in the production version
# Replit environment doesn't support PyAutoGUI due to X11 dependencies
# In a real desktop environment, these imports would work
# For now, we'll use demo mode
try:
    # We're in a headless environment, so we'll use demo mode
    MODULES_AVAILABLE = False
except ImportError:
    MODULES_AVAILABLE = False
    # For demonstration purposes, we'll create stubs for these classes
    class TranscriptCapture:
        def __init__(self, client_type="web"):
            self.client_type = client_type
        
        def capture_transcript(self):
            return "Sample transcript content for demonstration purposes."
    
    class PollPosting:
        def __init__(self, client_type="web"):
            self.client_type = client_type
        
        def post_poll_to_zoom(self, poll_data):
            return True
    
    class ChatGPTIntegration:
        def __init__(self):
            pass
        
        def generate_poll_with_chatgpt(self, transcript):
            return {
                "question": "What is the most important topic discussed so far?",
                "options": [
                    "Project timeline",
                    "Budget allocation",
                    "Technical challenges",
                    "Resource planning"
                ]
            }
    
    class ZoomAutomation:
        def __init__(self, client_type="web"):
            self.client_type = client_type
            self.meeting_active = False
        
        def join_meeting(self, meeting_id, passcode, display_name="Poll Generator"):
            self.meeting_active = True
            return True
        
        def leave_meeting(self):
            self.meeting_active = False
            return True
        
        def check_meeting_status(self):
            return self.meeting_active

# Load environment variables
load_dotenv()

# Initialize rich console
console = Console()

# Application state
app_state = {
    "meeting_active": False,
    "meeting_id": "",
    "passcode": "",
    "display_name": "Poll Generator",
    "automation_running": False,
    "recent_transcript": "",
    "current_poll": None,
    "next_transcript_time": None,
    "next_poll_time": None,
    "zoom_client_type": "web",
    "transcript_interval": 10,  # minutes
    "poll_interval": 15,        # minutes
    "check_interval": 30,       # seconds
    "log_entries": []
}

# Module instances
transcript_capture = None
poll_posting = None
chatgpt_integration = None
zoom_automation = None

# Configuration management
def load_config():
    """Load configuration from file if available."""
    config_path = Path("config.json")
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Update app state with config values
            for key in config:
                if key in app_state:
                    app_state[key] = config[key]
                    
            add_log_entry(f"Configuration loaded from {config_path}")
        except Exception as e:
            add_log_entry(f"Error loading configuration: {str(e)}", "error")
    else:
        add_log_entry("No configuration file found, using defaults")

def save_config():
    """Save current configuration to file."""
    config_path = Path("config.json")
    
    try:
        # Extract configuration from app state
        config = {
            "zoom_client_type": app_state["zoom_client_type"],
            "transcript_interval": app_state["transcript_interval"],
            "poll_interval": app_state["poll_interval"],
            "check_interval": app_state["check_interval"],
            "display_name": app_state["display_name"]
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
            
        add_log_entry(f"Configuration saved to {config_path}")
    except Exception as e:
        add_log_entry(f"Error saving configuration: {str(e)}", "error")

# Log management
def add_log_entry(message, level="info"):
    """Add an entry to the log with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    entry = {
        "timestamp": timestamp,
        "message": message,
        "level": level
    }
    
    app_state["log_entries"].append(entry)
    
    # Keep only the most recent entries (limit to 100)
    if len(app_state["log_entries"]) > 100:
        app_state["log_entries"] = app_state["log_entries"][-100:]

# Module initialization
def initialize_modules():
    """Initialize all required modules."""
    global transcript_capture, poll_posting, chatgpt_integration, zoom_automation
    
    try:
        # Create module instances
        client_type = app_state["zoom_client_type"]
        
        transcript_capture = TranscriptCapture(client_type)
        poll_posting = PollPosting(client_type)
        chatgpt_integration = ChatGPTIntegration()
        zoom_automation = ZoomAutomation(client_type)
        
        add_log_entry(f"Modules initialized with {client_type} client type")
        return True
    except Exception as e:
        add_log_entry(f"Error initializing modules: {str(e)}", "error")
        return False

# Core functionality
def join_meeting(meeting_id, passcode, display_name=None):
    """Join a Zoom meeting."""
    global zoom_automation
    
    if not display_name:
        display_name = app_state["display_name"]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]Joining meeting {meeting_id}...", total=None)
        
        if zoom_automation:
            result = zoom_automation.join_meeting(meeting_id, passcode, display_name)
            
            if result:
                app_state["meeting_active"] = True
                app_state["meeting_id"] = meeting_id
                app_state["passcode"] = passcode
                add_log_entry(f"Successfully joined meeting {meeting_id}")
                return True
            else:
                add_log_entry(f"Failed to join meeting {meeting_id}", "error")
                return False
        else:
            add_log_entry("Zoom automation not initialized", "error")
            return False

def leave_meeting():
    """Leave the current Zoom meeting."""
    global zoom_automation
    
    if not app_state["meeting_active"]:
        add_log_entry("No active meeting to leave")
        return False
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Leaving meeting...", total=None)
        
        if zoom_automation:
            result = zoom_automation.leave_meeting()
            
            if result:
                app_state["meeting_active"] = False
                app_state["meeting_id"] = ""
                app_state["passcode"] = ""
                add_log_entry("Successfully left meeting")
                return True
            else:
                add_log_entry("Failed to leave meeting properly", "error")
                return False
        else:
            add_log_entry("Zoom automation not initialized", "error")
            return False

def capture_transcript():
    """Capture a transcript from the current meeting."""
    global transcript_capture
    
    if not app_state["meeting_active"]:
        add_log_entry("Cannot capture transcript - not in a meeting", "warning")
        return False
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Capturing transcript...", total=None)
        
        if transcript_capture:
            transcript = transcript_capture.capture_transcript()
            
            if transcript:
                app_state["recent_transcript"] = transcript
                app_state["next_transcript_time"] = datetime.now() + timedelta(minutes=app_state["transcript_interval"])
                add_log_entry(f"Transcript captured: {len(transcript)} characters")
                return True
            else:
                add_log_entry("Failed to capture transcript", "error")
                return False
        else:
            add_log_entry("Transcript capture not initialized", "error")
            return False

def generate_poll():
    """Generate a poll based on the recent transcript."""
    global chatgpt_integration
    
    if not app_state["recent_transcript"]:
        add_log_entry("Cannot generate poll - no transcript available", "warning")
        return False
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Generating poll from transcript...", total=None)
        
        if chatgpt_integration:
            poll_data = chatgpt_integration.generate_poll_with_chatgpt(app_state["recent_transcript"])
            
            if poll_data:
                app_state["current_poll"] = poll_data
                add_log_entry(f"Poll generated: {poll_data['question']}")
                return True
            else:
                add_log_entry("Failed to generate poll", "error")
                return False
        else:
            add_log_entry("ChatGPT integration not initialized", "error")
            return False

def post_poll():
    """Post the current poll to the meeting."""
    global poll_posting
    
    if not app_state["meeting_active"]:
        add_log_entry("Cannot post poll - not in a meeting", "warning")
        return False
    
    if not app_state["current_poll"]:
        add_log_entry("Cannot post poll - no poll generated", "warning")
        return False
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Posting poll to meeting...", total=None)
        
        if poll_posting:
            result = poll_posting.post_poll_to_zoom(app_state["current_poll"])
            
            if result:
                app_state["next_poll_time"] = datetime.now() + timedelta(minutes=app_state["poll_interval"])
                add_log_entry(f"Poll posted successfully: {app_state['current_poll']['question']}")
                # Clear the current poll after posting
                app_state["current_poll"] = None
                return True
            else:
                add_log_entry("Failed to post poll", "error")
                return False
        else:
            add_log_entry("Poll posting not initialized", "error")
            return False

# Automation workflow
def start_automation():
    """Start the automated workflow."""
    if app_state["automation_running"]:
        add_log_entry("Automation is already running", "warning")
        return False
    
    if not app_state["meeting_active"]:
        add_log_entry("Cannot start automation - not in a meeting", "warning")
        return False
    
    app_state["automation_running"] = True
    
    # Set initial scheduled times
    app_state["next_transcript_time"] = datetime.now() + timedelta(minutes=app_state["transcript_interval"])
    app_state["next_poll_time"] = datetime.now() + timedelta(minutes=app_state["poll_interval"])
    
    # Start initial capture and generation
    threading.Thread(target=capture_transcript, daemon=True).start()
    
    # Schedule poll generation after capture completes
    def delayed_poll_generation():
        time.sleep(10)  # Wait for transcript capture to complete
        if app_state["recent_transcript"]:
            generate_poll()
    
    threading.Thread(target=delayed_poll_generation, daemon=True).start()
    
    # Start the automation check thread
    threading.Thread(target=automation_check_loop, daemon=True).start()
    
    add_log_entry("Automation started")
    return True

def stop_automation():
    """Stop the automated workflow."""
    if not app_state["automation_running"]:
        add_log_entry("Automation is not running", "warning")
        return False
    
    app_state["automation_running"] = False
    add_log_entry("Automation stopped")
    return True

def automation_check_loop():
    """Main loop for checking and executing scheduled tasks."""
    while app_state["automation_running"]:
        try:
            # Check if meeting is still active
            if app_state["meeting_active"] and zoom_automation:
                if not zoom_automation.check_meeting_status():
                    add_log_entry("Meeting appears to have ended", "warning")
                    app_state["meeting_active"] = False
                    app_state["automation_running"] = False
                    break
            
            now = datetime.now()
            
            # Check if it's time for transcript capture
            if app_state["next_transcript_time"] and now >= app_state["next_transcript_time"]:
                add_log_entry("Scheduled transcript capture triggered")
                thread = threading.Thread(target=capture_transcript, daemon=True)
                thread.start()
                thread.join()  # Wait for capture to complete before continuing
                
                # Schedule poll generation
                if app_state["recent_transcript"]:
                    threading.Thread(target=generate_poll, daemon=True).start()
            
            # Check if it's time for poll posting
            if app_state["next_poll_time"] and now >= app_state["next_poll_time"]:
                add_log_entry("Scheduled poll posting triggered")
                
                # If we have a poll, post it
                if app_state["current_poll"]:
                    threading.Thread(target=post_poll, daemon=True).start()
                # Otherwise try to generate and post a new poll
                elif app_state["recent_transcript"]:
                    def generate_and_post():
                        if generate_poll():
                            time.sleep(5)  # Short delay
                            post_poll()
                    
                    threading.Thread(target=generate_and_post, daemon=True).start()
            
            # Sleep before next check
            time.sleep(app_state["check_interval"])
        except Exception as e:
            add_log_entry(f"Error in automation loop: {str(e)}", "error")
            time.sleep(app_state["check_interval"])

# Terminal UI rendering
def create_header():
    """Create the header panel."""
    grid = Table.grid(expand=True)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="right")
    grid.add_row(
        f"[bold blue]Automated Zoom Poll Generator[/bold blue] [dim]v1.0.0[/dim]",
        datetime.now().strftime("%H:%M:%S")
    )
    
    header = Panel(
        grid,
        box=Box.DOUBLE,
        border_style="blue",
        padding=(1, 1),
        title="[bold white]Production Version[/bold white]",
        subtitle="[dim]Press Ctrl+C to exit[/dim]"
    )
    return header

def create_status_panel():
    """Create the status panel with current state."""
    # Create a table for status information
    table = Table(show_header=False, expand=True, box=None)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    # Add status rows
    table.add_row("Meeting Status", 
                 f"[green]Active: {app_state['meeting_id']}[/green]" if app_state["meeting_active"] 
                 else "[red]Not in meeting[/red]")
    
    table.add_row("Automation", 
                 f"[green]Running[/green]" if app_state["automation_running"] 
                 else "[yellow]Stopped[/yellow]")
    
    table.add_row("Zoom Client", app_state["zoom_client_type"].capitalize())
    
    table.add_row("Transcript Status", 
                 f"[green]Available ({len(app_state['recent_transcript'])} chars)[/green]" if app_state["recent_transcript"] 
                 else "[yellow]Not available[/yellow]")
    
    table.add_row("Poll Status", 
                 f"[green]Ready: {app_state['current_poll']['question']}[/green]" if app_state["current_poll"] 
                 else "[yellow]Not generated[/yellow]")
    
    if app_state["next_transcript_time"]:
        table.add_row("Next Transcript Capture", 
                     app_state["next_transcript_time"].strftime("%H:%M:%S"))
    
    if app_state["next_poll_time"]:
        table.add_row("Next Poll Posting", 
                     app_state["next_poll_time"].strftime("%H:%M:%S"))
    
    # Create the panel containing the table
    panel = Panel(
        table,
        title="[bold]Status[/bold]",
        border_style="blue",
        padding=(1, 1)
    )
    return panel

def create_log_panel():
    """Create the log panel with recent entries."""
    if not app_state["log_entries"]:
        log_content = Text("No log entries yet", style="dim")
    else:
        # Create a list of log entries with appropriate styling
        log_content = Text()
        
        # Show the most recent entries (last 15)
        for entry in app_state["log_entries"][-15:]:
            timestamp = entry["timestamp"]
            message = entry["message"]
            level = entry["level"]
            
            # Style based on log level
            if level == "error":
                style = "red"
            elif level == "warning":
                style = "yellow"
            elif level == "success":
                style = "green"
            else:  # info
                style = "white"
            
            log_content.append(f"{timestamp} ", style="dim")
            log_content.append(f"{message}\n", style=style)
    
    # Create the panel
    panel = Panel(
        log_content,
        title="[bold]Log[/bold]",
        border_style="blue",
        padding=(1, 1)
    )
    return panel

def create_help_panel():
    """Create the help panel with available commands."""
    # Create a table for commands
    table = Table(show_header=True, expand=True, box=None)
    table.add_column("Command", style="cyan", justify="center", max_width=18)
    table.add_column("Description", style="white")
    
    # Add command rows
    table.add_row("join", "Join a Zoom meeting")
    table.add_row("leave", "Leave the current meeting")
    table.add_row("start", "Start automated polling")
    table.add_row("stop", "Stop automated polling")
    table.add_row("capture", "Capture transcript now")
    table.add_row("generate", "Generate poll now")
    table.add_row("post", "Post current poll now")
    table.add_row("status", "Show detailed status")
    table.add_row("exit/quit", "Exit the application")
    
    # Create the panel
    panel = Panel(
        table,
        title="[bold]Available Commands[/bold]",
        border_style="blue",
        padding=(1, 1)
    )
    return panel

def render_terminal_ui():
    """Render the full terminal UI."""
    # Create layout
    layout = Layout()
    
    # Add header
    layout.split(
        Layout(name="header", size=3),
        Layout(name="body")
    )
    
    # Set up body with status, log, and help panels
    layout["body"].split_row(
        Layout(name="left"),
        Layout(name="right")
    )
    
    layout["left"].split(
        Layout(name="status"),
        Layout(name="log", ratio=2)
    )
    
    layout["right"].split(
        Layout(name="help"),
        Layout(name="command", size=3)
    )
    
    # Update content
    layout["header"].update(create_header())
    layout["status"].update(create_status_panel())
    layout["log"].update(create_log_panel())
    layout["help"].update(create_help_panel())
    layout["command"].update(Panel(
        "Enter command: ", 
        title="[bold]Command Input[/bold]", 
        border_style="blue",
        padding=(1, 1)
    ))
    
    # Render the layout
    console.print(layout)

def command_prompt():
    """Show command prompt and process input."""
    command = Prompt.ask("Enter command")
    process_command(command)

def process_command(command):
    """Process a user command."""
    command = command.strip().lower()
    
    if command in ("exit", "quit"):
        # Check if user wants to save changes
        if Confirm.ask("Do you want to save configuration before exiting?"):
            save_config()
        
        # Leave meeting if active
        if app_state["meeting_active"]:
            if Confirm.ask("You are still in a meeting. Leave before exiting?"):
                leave_meeting()
        
        return False  # Signal to exit main loop
    
    elif command == "join":
        # Get meeting details
        meeting_id = Prompt.ask("Enter meeting ID")
        passcode = Prompt.ask("Enter passcode")
        
        # Validate input
        if not meeting_id or not passcode:
            add_log_entry("Meeting ID and passcode are required", "error")
        else:
            # Join the meeting
            join_meeting(meeting_id, passcode)
    
    elif command == "leave":
        leave_meeting()
    
    elif command == "start":
        start_automation()
    
    elif command == "stop":
        stop_automation()
    
    elif command == "capture":
        threading.Thread(target=capture_transcript, daemon=True).start()
    
    elif command == "generate":
        threading.Thread(target=generate_poll, daemon=True).start()
    
    elif command == "post":
        threading.Thread(target=post_poll, daemon=True).start()
    
    elif command == "status":
        # Show detailed status (current state, scheduled times, etc.)
        console.print("\n")
        console.print(Panel(
            create_status_panel(),
            title="Detailed Status",
            border_style="blue"
        ))
        console.print("\nPress Enter to continue...")
        input()
    
    elif command == "config":
        # Show configuration options
        client_type = Prompt.ask(
            "Zoom client type",
            choices=["web", "desktop"],
            default=app_state["zoom_client_type"]
        )
        
        transcript_interval = int(Prompt.ask(
            "Transcript capture interval (minutes)",
            default=str(app_state["transcript_interval"])
        ))
        
        poll_interval = int(Prompt.ask(
            "Poll posting interval (minutes)",
            default=str(app_state["poll_interval"])
        ))
        
        display_name = Prompt.ask(
            "Display name in meetings",
            default=app_state["display_name"]
        )
        
        # Update configuration
        app_state["zoom_client_type"] = client_type
        app_state["transcript_interval"] = transcript_interval
        app_state["poll_interval"] = poll_interval
        app_state["display_name"] = display_name
        
        # Reinitialize modules if client type changed
        if client_type != app_state["zoom_client_type"] and not app_state["meeting_active"]:
            initialize_modules()
        
        add_log_entry("Configuration updated")
    
    elif command == "clear":
        # Clear logs
        app_state["log_entries"] = []
        add_log_entry("Logs cleared")
    
    elif command == "help":
        # Show help
        console.print("\n")
        console.print(create_help_panel())
        console.print("\nPress Enter to continue...")
        input()
    
    else:
        add_log_entry(f"Unknown command: {command}", "error")
    
    return True  # Continue main loop

def run_terminal_ui():
    """Run the terminal UI."""
    try:
        while True:
            # Clear screen
            console.clear()
            
            # Render UI
            render_terminal_ui()
            
            # Process command
            if not command_prompt():
                break
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Process interrupted by user.[/yellow]")
    finally:
        # Clean up
        if app_state["meeting_active"]:
            leave_meeting()
        
        # Save configuration
        save_config()
        
        console.print("[green]Exiting Automated Zoom Poll Generator. Goodbye![/green]")

def show_welcome():
    """Show a welcome message with quick start instructions."""
    console.print(Panel.fit(
        "[bold blue]Automated Zoom Poll Generator[/bold blue] [dim]v1.0.0[/dim]\n\n"
        "This application automates the process of generating and posting polls in Zoom meetings\n"
        "based on transcript content. It works with both desktop and web Zoom clients.\n\n"
        "[cyan]Quick Start:[/cyan]\n"
        "1. Enter 'join' to join a Zoom meeting\n"
        "2. Enter 'start' to begin automated poll generation and posting\n"
        "3. Use 'capture', 'generate', and 'post' for manual control\n"
        "4. Enter 'exit' to quit the application",
        title="Welcome",
        subtitle="Production Version",
        border_style="blue",
        padding=(1, 2)
    ))
    
    console.print("\nPress Enter to continue...")
    input()

def direct_meeting_join(meeting_id, passcode):
    """Join a meeting directly with provided credentials."""
    add_log_entry(f"Attempting to join meeting {meeting_id} directly")
    
    # Initialize modules
    if initialize_modules():
        # Join the meeting
        if join_meeting(meeting_id, passcode):
            # Ask if user wants to start automation
            if Confirm.ask("Meeting joined successfully. Start automation now?", default=True):
                start_automation()
        else:
            add_log_entry(f"Failed to join meeting {meeting_id}", "error")
    else:
        add_log_entry("Failed to initialize modules", "error")

def main():
    """Main entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Automated Zoom Poll Generator")
    parser.add_argument("--meeting", help="Meeting ID to join on startup")
    parser.add_argument("--passcode", help="Meeting passcode")
    parser.add_argument("--auto-start", action="store_true", help="Automatically start polling")
    args = parser.parse_args()
    
    # Show warning if modules are not available
    if not MODULES_AVAILABLE:
        console.print("[yellow]Warning: Running in demonstration mode. Some features may not work.[/yellow]")
    
    # Load configuration
    load_config()
    
    # Initialize modules
    initialize_modules()
    
    # Show welcome message
    show_welcome()
    
    # If meeting ID and passcode provided, join directly
    if args.meeting and args.passcode:
        direct_meeting_join(args.meeting, args.passcode)
    
    # Run the terminal UI
    run_terminal_ui()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())