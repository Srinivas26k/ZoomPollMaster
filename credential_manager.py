"""
Credential Manager for the Automated Zoom Poll Generator.
Handles secure storage and retrieval of user credentials.
"""

import tkinter as tk
from tkinter import simpledialog, messagebox
import threading
import time
from typing import Dict, Optional
import logging

from config import CREDENTIAL_TIMEOUT
from logger import get_logger

logger = get_logger()


class CredentialManager:
    """
    Manages user credentials for Zoom and ChatGPT.
    Stores credentials in memory only and never writes them to disk.
    """
    
    def __init__(self):
        """Initialize the credential manager."""
        self._zoom_credentials: Dict[str, str] = {}
        self._chatgpt_credentials: Dict[str, str] = {}
        self._credential_lock = threading.Lock()
        self._root = None
        self._credential_timer = None
        
        logger.info("Credential manager initialized")
    
    def prompt_for_zoom_credentials(self) -> Optional[Dict[str, str]]:
        """
        Display a dialog to collect Zoom credentials.
        
        Returns:
            Dict containing Zoom credentials or None if user cancels.
        """
        logger.info("Prompting user for Zoom credentials")
        
        self._root = tk.Tk()
        self._root.withdraw()  # Hide the main window
        
        # Create a new dialog window
        dialog = tk.Toplevel(self._root)
        dialog.title("Zoom Credentials")
        dialog.geometry("400x250")
        dialog.protocol("WM_DELETE_WINDOW", lambda: self._cancel_credentials(dialog))
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Instructions
        tk.Label(dialog, text="Enter your Zoom meeting credentials", font=("Helvetica", 12)).pack(pady=10)
        
        # Meeting ID
        frame1 = tk.Frame(dialog)
        frame1.pack(fill='x', padx=20, pady=5)
        tk.Label(frame1, text="Meeting ID:", width=12, anchor='w').pack(side='left')
        meeting_id_var = tk.StringVar()
        meeting_id_entry = tk.Entry(frame1, textvariable=meeting_id_var, width=30)
        meeting_id_entry.pack(side='left', padx=5, fill='x', expand=True)
        
        # Passcode
        frame2 = tk.Frame(dialog)
        frame2.pack(fill='x', padx=20, pady=5)
        tk.Label(frame2, text="Passcode:", width=12, anchor='w').pack(side='left')
        passcode_var = tk.StringVar()
        passcode_entry = tk.Entry(frame2, textvariable=passcode_var, width=30, show="*")
        passcode_entry.pack(side='left', padx=5, fill='x', expand=True)
        
        # Host Key (optional)
        frame3 = tk.Frame(dialog)
        frame3.pack(fill='x', padx=20, pady=5)
        tk.Label(frame3, text="Host Key:", width=12, anchor='w').pack(side='left')
        host_key_var = tk.StringVar()
        host_key_entry = tk.Entry(frame3, textvariable=host_key_var, width=30, show="*")
        host_key_entry.pack(side='left', padx=5, fill='x', expand=True)
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        result = [None]  # Using list to store result for access within nested function
        
        def on_submit():
            creds = {
                "meeting_id": meeting_id_var.get().strip(),
                "passcode": passcode_var.get().strip(),
                "host_key": host_key_var.get().strip()
            }
            
            # Validate inputs
            if not creds["meeting_id"]:
                messagebox.showerror("Error", "Meeting ID is required", parent=dialog)
                return
            
            result[0] = creds
            dialog.destroy()
        
        submit_button = tk.Button(button_frame, text="Submit", command=on_submit, width=10)
        submit_button.pack(side='left', padx=10)
        
        cancel_button = tk.Button(
            button_frame, 
            text="Cancel", 
            command=lambda: self._cancel_credentials(dialog), 
            width=10
        )
        cancel_button.pack(side='left', padx=10)
        
        # Focus on the first field
        meeting_id_entry.focus_set()
        
        # Make dialog modal
        dialog.transient(self._root)
        dialog.grab_set()
        self._root.wait_window(dialog)
        
        # Destroy the root window after dialog is closed
        if self._root:
            self._root.destroy()
            self._root = None
        
        if result[0] is not None:
            logger.info("Zoom credentials collected successfully")
            self._zoom_credentials = result[0]
            self._start_credential_timeout()
            return result[0]
        else:
            logger.warning("User cancelled Zoom credential entry")
            return None
    
    def prompt_for_chatgpt_credentials(self) -> Optional[Dict[str, str]]:
        """
        Display a dialog to collect ChatGPT credentials.
        
        Returns:
            Dict containing ChatGPT credentials or None if user cancels.
        """
        logger.info("Prompting user for ChatGPT credentials")
        
        self._root = tk.Tk()
        self._root.withdraw()  # Hide the main window
        
        # Create a new dialog window
        dialog = tk.Toplevel(self._root)
        dialog.title("ChatGPT Credentials")
        dialog.geometry("400x200")
        dialog.protocol("WM_DELETE_WINDOW", lambda: self._cancel_credentials(dialog))
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Instructions
        tk.Label(dialog, text="Enter your ChatGPT credentials", font=("Helvetica", 12)).pack(pady=10)
        
        # Email/Username
        frame1 = tk.Frame(dialog)
        frame1.pack(fill='x', padx=20, pady=5)
        tk.Label(frame1, text="Email:", width=12, anchor='w').pack(side='left')
        email_var = tk.StringVar()
        email_entry = tk.Entry(frame1, textvariable=email_var, width=30)
        email_entry.pack(side='left', padx=5, fill='x', expand=True)
        
        # Password
        frame2 = tk.Frame(dialog)
        frame2.pack(fill='x', padx=20, pady=5)
        tk.Label(frame2, text="Password:", width=12, anchor='w').pack(side='left')
        password_var = tk.StringVar()
        password_entry = tk.Entry(frame2, textvariable=password_var, width=30, show="*")
        password_entry.pack(side='left', padx=5, fill='x', expand=True)
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        result = [None]  # Using list to store result for access within nested function
        
        def on_submit():
            creds = {
                "email": email_var.get().strip(),
                "password": password_var.get().strip()
            }
            
            # Validate inputs
            if not creds["email"] or not creds["password"]:
                messagebox.showerror("Error", "Email and password are required", parent=dialog)
                return
            
            result[0] = creds
            dialog.destroy()
        
        submit_button = tk.Button(button_frame, text="Submit", command=on_submit, width=10)
        submit_button.pack(side='left', padx=10)
        
        cancel_button = tk.Button(
            button_frame, 
            text="Cancel", 
            command=lambda: self._cancel_credentials(dialog), 
            width=10
        )
        cancel_button.pack(side='left', padx=10)
        
        # Focus on the first field
        email_entry.focus_set()
        
        # Make dialog modal
        dialog.transient(self._root)
        dialog.grab_set()
        self._root.wait_window(dialog)
        
        # Destroy the root window after dialog is closed
        if self._root:
            self._root.destroy()
            self._root = None
        
        if result[0] is not None:
            logger.info("ChatGPT credentials collected successfully")
            self._chatgpt_credentials = result[0]
            self._start_credential_timeout()
            return result[0]
        else:
            logger.warning("User cancelled ChatGPT credential entry")
            return None
    
    def get_zoom_credentials(self) -> Dict[str, str]:
        """
        Get the stored Zoom credentials.
        
        Returns:
            Dict containing Zoom credentials.
        """
        with self._credential_lock:
            if not self._zoom_credentials:
                self.prompt_for_zoom_credentials()
            return self._zoom_credentials.copy()
    
    def get_chatgpt_credentials(self) -> Dict[str, str]:
        """
        Get the stored ChatGPT credentials.
        
        Returns:
            Dict containing ChatGPT credentials.
        """
        with self._credential_lock:
            if not self._chatgpt_credentials:
                self.prompt_for_chatgpt_credentials()
            return self._chatgpt_credentials.copy()
    
    def clear_credentials(self):
        """Clear all stored credentials from memory."""
        with self._credential_lock:
            self._zoom_credentials = {}
            self._chatgpt_credentials = {}
        logger.info("All credentials cleared from memory")
    
    def _cancel_credentials(self, dialog):
        """Handle dialog cancellation."""
        dialog.destroy()
    
    def _start_credential_timeout(self):
        """Start a timer to clear credentials after the configured timeout."""
        # Cancel existing timer if running
        if self._credential_timer:
            self._credential_timer.cancel()
        
        # Create new timer
        self._credential_timer = threading.Timer(CREDENTIAL_TIMEOUT, self.clear_credentials)
        self._credential_timer.daemon = True
        self._credential_timer.start()
        
        logger.debug(f"Credential timeout set for {CREDENTIAL_TIMEOUT} seconds")
