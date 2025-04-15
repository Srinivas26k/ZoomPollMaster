"""
GUI Module for the Automated Zoom Poll Generator.
Provides a simple user interface for monitoring and controlling the application.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import datetime
from typing import Callable, Dict, Optional

from logger import get_logger, export_log_file
from config import APP_NAME, APP_VERSION

logger = get_logger()


class ApplicationGUI:
    """
    Provides a simple graphical user interface for the application.
    """
    
    def __init__(self, callbacks: Dict[str, Callable] = None):
        """
        Initialize the application GUI.
        
        Args:
            callbacks: Dict of callback functions for various actions
        """
        self.root = None
        self.status_var = None
        self.log_text = None
        self.scheduler_status_var = None
        self.next_capture_var = None
        self.next_poll_var = None
        
        # Callbacks for various actions
        self.callbacks = callbacks or {}
        
        # Status update thread
        self.update_thread = None
        self.keep_updating = False
        
        logger.info("GUI module initialized")
    
    def create_window(self):
        """Create the main application window."""
        logger.info("Creating main application window")
        
        # Create main window
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("700x500")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Configure the grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)  # Title
        self.root.rowconfigure(1, weight=0)  # Status
        self.root.rowconfigure(2, weight=0)  # Buttons
        self.root.rowconfigure(3, weight=1)  # Log area
        self.root.rowconfigure(4, weight=0)  # Bottom status
        
        # App title
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.grid(row=0, column=0, sticky="ew")
        ttk.Label(
            title_frame, 
            text=APP_NAME, 
            font=("Helvetica", 16, "bold")
        ).pack(side="left")
        ttk.Label(
            title_frame, 
            text=f"v{APP_VERSION}", 
            font=("Helvetica", 10)
        ).pack(side="left", padx=(5, 0))
        
        # Status display
        status_frame = ttk.LabelFrame(self.root, text="Status", padding="10")
        status_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        status_frame.columnconfigure(0, weight=0)
        status_frame.columnconfigure(1, weight=1)
        
        # Application status
        ttk.Label(status_frame, text="Application:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.status_var = tk.StringVar(value="Initializing...")
        ttk.Label(status_frame, textvariable=self.status_var).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        # Scheduler status
        ttk.Label(status_frame, text="Scheduler:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.scheduler_status_var = tk.StringVar(value="Not started")
        ttk.Label(status_frame, textvariable=self.scheduler_status_var).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # Next capture time
        ttk.Label(status_frame, text="Next Capture:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.next_capture_var = tk.StringVar(value="Not scheduled")
        ttk.Label(status_frame, textvariable=self.next_capture_var).grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        # Next poll time
        ttk.Label(status_frame, text="Next Poll:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.next_poll_var = tk.StringVar(value="Not scheduled")
        ttk.Label(status_frame, textvariable=self.next_poll_var).grid(row=3, column=1, sticky="w", padx=5, pady=2)
        
        # Button area
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.grid(row=2, column=0, sticky="ew", padx=10)
        
        # Start button
        start_button = ttk.Button(
            button_frame, 
            text="Start", 
            command=self.on_start_click,
            width=12
        )
        start_button.pack(side="left", padx=5)
        
        # Stop button
        stop_button = ttk.Button(
            button_frame, 
            text="Stop", 
            command=self.on_stop_click,
            width=12
        )
        stop_button.pack(side="left", padx=5)
        
        # Manual capture button
        capture_button = ttk.Button(
            button_frame, 
            text="Capture Now", 
            command=self.on_capture_click,
            width=12
        )
        capture_button.pack(side="left", padx=5)
        
        # Manual poll button
        poll_button = ttk.Button(
            button_frame, 
            text="Generate Poll", 
            command=self.on_generate_poll_click,
            width=12
        )
        poll_button.pack(side="left", padx=5)
        
        # Export log button
        export_button = ttk.Button(
            button_frame, 
            text="Export Log", 
            command=self.on_export_log_click,
            width=12
        )
        export_button.pack(side="left", padx=5)
        
        # Log display area
        log_frame = ttk.LabelFrame(self.root, text="Log", padding="10")
        log_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Create log text widget with scrollbar
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=15)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Bottom status bar
        status_bar = ttk.Frame(self.root, relief=tk.SUNKEN, padding=(2, 2))
        status_bar.grid(row=4, column=0, sticky="ew")
        
        ttk.Label(
            status_bar, 
            text=f"© 2023 {APP_NAME}", 
            font=("Helvetica", 8)
        ).pack(side="left", padx=5)
        
        time_var = tk.StringVar()
        ttk.Label(
            status_bar, 
            textvariable=time_var, 
            font=("Helvetica", 8)
        ).pack(side="right", padx=5)
        
        # Update time every second
        def update_time():
            time_var.set(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            self.root.after(1000, update_time)
        
        update_time()
        
        # Start update thread
        self.start_update_thread()
        
        logger.info("GUI window created")
    
    def update_log_display(self, text):
        """
        Update the log display with new text.
        
        Args:
            text: Text to append to the log display
        """
        if self.log_text:
            self.log_text.insert(tk.END, f"{text}\n")
            self.log_text.see(tk.END)  # Scroll to the end
    
    def update_status(self, text):
        """
        Update the status display.
        
        Args:
            text: New status text
        """
        if self.status_var:
            self.status_var.set(text)
    
    def update_scheduler_status(self, scheduler_status):
        """
        Update the scheduler status display.
        
        Args:
            scheduler_status: Dict containing scheduler status information
        """
        if not self.scheduler_status_var:
            return
            
        if scheduler_status.get("is_running", False):
            self.scheduler_status_var.set("Running")
        else:
            self.scheduler_status_var.set("Stopped")
        
        # Update next capture time
        next_capture = scheduler_status.get("next_transcript_capture_time")
        if next_capture:
            time_str = next_capture.strftime("%H:%M:%S")
            self.next_capture_var.set(time_str)
        else:
            self.next_capture_var.set("Not scheduled")
        
        # Update next poll time
        next_poll = scheduler_status.get("next_poll_posting_time")
        if next_poll:
            time_str = next_poll.strftime("%H:%M:%S")
            self.next_poll_var.set(time_str)
        else:
            self.next_poll_var.set("Not scheduled")
    
    def start_update_thread(self):
        """Start the background thread for updating status information."""
        self.keep_updating = True
        self.update_thread = threading.Thread(target=self._update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def _update_loop(self):
        """Background loop for updating status information."""
        while self.keep_updating:
            # Update status if callback is provided
            if "get_status" in self.callbacks:
                try:
                    status = self.callbacks["get_status"]()
                    self.root.after(0, lambda: self.update_scheduler_status(status))
                except Exception as e:
                    logger.error(f"Error updating status: {str(e)}")
            
            # Sleep before next update
            time.sleep(1)
    
    def on_start_click(self):
        """Handle Start button click."""
        logger.info("Start button clicked")
        if "start" in self.callbacks:
            self.callbacks["start"]()
            self.update_status("Running")
    
    def on_stop_click(self):
        """Handle Stop button click."""
        logger.info("Stop button clicked")
        if "stop" in self.callbacks:
            self.callbacks["stop"]()
            self.update_status("Stopped")
    
    def on_capture_click(self):
        """Handle Capture Now button click."""
        logger.info("Capture Now button clicked")
        if "capture" in self.callbacks:
            self.update_status("Capturing transcript...")
            self.callbacks["capture"]()
    
    def on_generate_poll_click(self):
        """Handle Generate Poll button click."""
        logger.info("Generate Poll button clicked")
        if "generate_poll" in self.callbacks:
            self.update_status("Generating poll...")
            self.callbacks["generate_poll"]()
    
    def on_export_log_click(self):
        """Handle Export Log button click."""
        logger.info("Export Log button clicked")
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Export Log File"
            )
            
            if file_path:
                exported_path = export_log_file(file_path)
                if exported_path:
                    messagebox.showinfo(
                        "Export Successful", 
                        f"Log successfully exported to:\n{exported_path}"
                    )
                else:
                    messagebox.showerror(
                        "Export Failed", 
                        "Failed to export log file."
                    )
        except Exception as e:
            logger.error(f"Error exporting log: {str(e)}")
            messagebox.showerror(
                "Export Error", 
                f"An error occurred while exporting the log:\n{str(e)}"
            )
    
    def on_close(self):
        """Handle window close event."""
        logger.info("Application window closing")
        
        # Ask user to confirm
        confirm = messagebox.askyesno(
            "Confirm Exit",
            "Are you sure you want to exit the application?\nThis will stop all scheduled operations."
        )
        
        if confirm:
            # Stop update thread
            self.keep_updating = False
            if self.update_thread and self.update_thread.is_alive():
                self.update_thread.join(1)
            
            # Call stop callback if provided
            if "stop" in self.callbacks:
                self.callbacks["stop"]()
            
            # Call exit callback if provided
            if "exit" in self.callbacks:
                self.callbacks["exit"]()
            
            # Destroy window
            self.root.destroy()
    
    def run(self):
        """Run the GUI main loop."""
        if not self.root:
            self.create_window()
        
        logger.info("Starting GUI main loop")
        self.root.mainloop()
