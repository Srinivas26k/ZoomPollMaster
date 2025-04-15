"""
Credential Manager Module for the Automated Zoom Poll Generator.
Handles secure management of user credentials.
"""

import os
import json
import logging
import getpass
from typing import Dict, Any, Optional, List

# Configure logger
logger = logging.getLogger(__name__)

class CredentialManager:
    """
    Manages credentials for Zoom and ChatGPT.
    Handles storing, retrieving, and clearing credentials securely.
    """
    
    def __init__(self):
        """Initialize the credential manager."""
        self.service_name = "ZoomPollGenerator"
        self.zoom_credentials = None
        self.chatgpt_credentials = None
        
        logger.info("CredentialManager initialized")
        
    def prompt_for_zoom_credentials(self) -> Optional[Dict[str, str]]:
        """
        Prompt the user for Zoom credentials interactively.
        
        Returns:
            Dict containing Zoom credentials or None if cancelled
        """
        try:
            logger.info("Prompting for Zoom credentials")
            
            print("\n=== Zoom Meeting Credentials ===")
            meeting_id = input("Meeting ID: ").strip()
            
            # Check if the user wants to cancel
            if not meeting_id:
                logger.warning("Zoom credential input cancelled by user")
                return None
            
            passcode = input("Passcode: ").strip()
            display_name = input("Display Name [Poll Generator]: ").strip() or "Poll Generator"
            
            credentials = {
                "meeting_id": meeting_id,
                "passcode": passcode,
                "display_name": display_name
            }
            
            # Store credentials
            self.zoom_credentials = credentials
            
            # Ask if the user wants to save the credentials
            save_creds = input("Save these credentials for future use? (y/n): ").strip().lower() == 'y'
            
            if save_creds:
                self._save_credentials("zoom", credentials)
                logger.info("Zoom credentials saved")
            
            return credentials
            
        except Exception as e:
            logger.error(f"Error prompting for Zoom credentials: {str(e)}")
            return None
    
    def prompt_for_chatgpt_credentials(self) -> Optional[Dict[str, str]]:
        """
        Prompt the user for ChatGPT credentials interactively.
        
        Returns:
            Dict containing ChatGPT credentials or None if cancelled
        """
        try:
            logger.info("Prompting for ChatGPT credentials")
            
            print("\n=== ChatGPT Credentials ===")
            email = input("Email: ").strip()
            
            # Check if the user wants to cancel
            if not email:
                logger.warning("ChatGPT credential input cancelled by user")
                return None
            
            # Use getpass for password to avoid showing it on screen
            password = getpass.getpass("Password: ")
            
            credentials = {
                "email": email,
                "password": password
            }
            
            # Store credentials
            self.chatgpt_credentials = credentials
            
            # Ask if the user wants to save the credentials
            save_creds = input("Save these credentials for future use? (y/n): ").strip().lower() == 'y'
            
            if save_creds:
                self._save_credentials("chatgpt", credentials)
                logger.info("ChatGPT credentials saved")
            
            return credentials
            
        except Exception as e:
            logger.error(f"Error prompting for ChatGPT credentials: {str(e)}")
            return None
    
    def load_zoom_credentials(self) -> Optional[Dict[str, str]]:
        """
        Load saved Zoom credentials.
        
        Returns:
            Dict containing Zoom credentials or None if not found
        """
        if self.zoom_credentials:
            return self.zoom_credentials
            
        credentials = self._load_credentials("zoom")
        
        if credentials:
            logger.info("Loaded saved Zoom credentials")
            self.zoom_credentials = credentials
        else:
            logger.warning("No saved Zoom credentials found")
            
        return credentials
    
    def load_chatgpt_credentials(self) -> Optional[Dict[str, str]]:
        """
        Load saved ChatGPT credentials.
        
        Returns:
            Dict containing ChatGPT credentials or None if not found
        """
        if self.chatgpt_credentials:
            return self.chatgpt_credentials
            
        credentials = self._load_credentials("chatgpt")
        
        if credentials:
            logger.info("Loaded saved ChatGPT credentials")
            self.chatgpt_credentials = credentials
        else:
            logger.warning("No saved ChatGPT credentials found")
            
        return credentials
    
    def clear_credentials(self, credential_type: str = None) -> bool:
        """
        Clear stored credentials.
        
        Args:
            credential_type: Type of credentials to clear ('zoom', 'chatgpt', or None for all)
            
        Returns:
            Boolean indicating whether clearing was successful
        """
        try:
            if credential_type is None or credential_type == "zoom":
                self.zoom_credentials = None
                self._delete_credentials("zoom")
                logger.info("Zoom credentials cleared")
                
            if credential_type is None or credential_type == "chatgpt":
                self.chatgpt_credentials = None
                self._delete_credentials("chatgpt")
                logger.info("ChatGPT credentials cleared")
                
            return True
            
        except Exception as e:
            logger.error(f"Error clearing credentials: {str(e)}")
            return False
    
    def update_zoom_credentials(self, credentials: Dict[str, str]) -> bool:
        """
        Update Zoom credentials.
        
        Args:
            credentials: Dict containing updated Zoom credentials
            
        Returns:
            Boolean indicating whether update was successful
        """
        try:
            if not isinstance(credentials, dict):
                logger.error("Invalid credentials format")
                return False
                
            # Validate required fields
            required_fields = ["meeting_id", "passcode"]
            for field in required_fields:
                if field not in credentials:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Store credentials
            self.zoom_credentials = credentials
            self._save_credentials("zoom", credentials)
            
            logger.info("Zoom credentials updated")
            return True
            
        except Exception as e:
            logger.error(f"Error updating Zoom credentials: {str(e)}")
            return False
    
    def update_chatgpt_credentials(self, credentials: Dict[str, str]) -> bool:
        """
        Update ChatGPT credentials.
        
        Args:
            credentials: Dict containing updated ChatGPT credentials
            
        Returns:
            Boolean indicating whether update was successful
        """
        try:
            if not isinstance(credentials, dict):
                logger.error("Invalid credentials format")
                return False
                
            # Validate required fields
            required_fields = ["email", "password"]
            for field in required_fields:
                if field not in credentials:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Store credentials
            self.chatgpt_credentials = credentials
            self._save_credentials("chatgpt", credentials)
            
            logger.info("ChatGPT credentials updated")
            return True
            
        except Exception as e:
            logger.error(f"Error updating ChatGPT credentials: {str(e)}")
            return False
    
    def _save_credentials(self, credential_type: str, credentials: Dict[str, str]) -> bool:
        """
        Save credentials securely.
        
        Args:
            credential_type: Type of credentials ('zoom' or 'chatgpt')
            credentials: Dict containing credentials to save
            
        Returns:
            Boolean indicating whether save was successful
        """
        try:
            # Use file-based storage
            cred_file = f".{credential_type}_credentials.json"
            with open(cred_file, 'w') as f:
                json.dump(credentials, f)
            
            # Attempt to set restrictive permissions
            try:
                os.chmod(cred_file, 0o600)  # Read/write for owner only
            except:
                logger.warning(f"Could not set restrictive permissions on {cred_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving credentials: {str(e)}")
            return False
    
    def _load_credentials(self, credential_type: str) -> Optional[Dict[str, str]]:
        """
        Load credentials securely.
        
        Args:
            credential_type: Type of credentials ('zoom' or 'chatgpt')
            
        Returns:
            Dict containing credentials or None if not found
        """
        try:
            # Use file-based storage
            cred_file = f".{credential_type}_credentials.json"
            
            if os.path.exists(cred_file):
                with open(cred_file, 'r') as f:
                    return json.load(f)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error loading credentials: {str(e)}")
            return None
    
    def _delete_credentials(self, credential_type: str) -> bool:
        """
        Delete stored credentials.
        
        Args:
            credential_type: Type of credentials ('zoom' or 'chatgpt')
            
        Returns:
            Boolean indicating whether deletion was successful
        """
        try:
            # Delete from file-based storage
            cred_file = f".{credential_type}_credentials.json"
            
            if os.path.exists(cred_file):
                os.remove(cred_file)
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting credentials: {str(e)}")
            return False

# Helper function to create an instance
def create_credential_manager() -> CredentialManager:
    """
    Create and return a CredentialManager instance.
    
    Returns:
        CredentialManager instance
    """
    return CredentialManager()