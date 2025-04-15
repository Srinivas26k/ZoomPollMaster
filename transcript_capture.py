"""
Transcript Capture Module for the Automated Zoom Poll Generator.
Uses PyAutoGUI to capture a 10-minute transcript from Zoom.
"""

import time
import re
import logging
import pyautogui
import pyperclip
from typing import Optional, Tuple, List, Dict
from datetime import datetime, timedelta

from logger import get_logger
from config import WAIT_SHORT, WAIT_MEDIUM, WAIT_LONG, TRANSCRIPT_BUTTON_IMAGE

logger = get_logger()


class TranscriptCapture:
    """
    Handles the capture of transcripts directly from the Zoom application.
    Uses UI automation to locate and copy transcript text.
    """
    
    def __init__(self, zoom_client_type="desktop"):
        """
        Initialize the transcript capture module.
        
        Args:
            zoom_client_type: Type of Zoom client ("desktop" or "web")
        """
        self.zoom_client_type = zoom_client_type
        self.transcript_history = []
        
        # Set confidence level for image recognition
        self.confidence_level = 0.7
        
        logger.info(f"Transcript capture module initialized for {zoom_client_type} client")
    
    def find_transcript_area(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Find the transcript area in the Zoom window.
        
        Returns:
            Tuple of (x, y, width, height) for the transcript area, or None if not found.
        """
        logger.info("Looking for transcript area in Zoom window")
        
        try:
            if self.zoom_client_type == "desktop":
                # For desktop client, look for the transcript button first
                transcript_btn = pyautogui.locateOnScreen(
                    TRANSCRIPT_BUTTON_IMAGE, 
                    confidence=self.confidence_level
                )
                
                if not transcript_btn:
                    logger.warning("Could not find transcript button in Zoom desktop client")
                    
                    # Try alternative method - look for text elements that might indicate transcript area
                    # This is a fallback approach that might be less reliable
                    transcript_region = None
                    for text in ["Transcript", "Live Transcript", "Closed Caption"]:
                        try:
                            transcript_region = pyautogui.locateOnScreen(
                                f"Searching for text: {text}",
                                confidence=0.6
                            )
                            if transcript_region:
                                logger.info(f"Found potential transcript area using text search: {text}")
                                break
                        except Exception:
                            continue
                    
                    return transcript_region
                
                # Click on transcript button to ensure transcript panel is visible
                transcript_btn_center = pyautogui.center(transcript_btn)
                pyautogui.click(transcript_btn_center)
                time.sleep(WAIT_SHORT)
                
                # The transcript panel should now be visible
                # For simplicity, we'll use a region estimate based on typical Zoom UI layout
                # This would need refinement for different screen sizes and Zoom versions
                screen_width, screen_height = pyautogui.size()
                transcript_area = (
                    screen_width - 350,  # Typical transcript panel width
                    150,                # Allow space for top controls
                    330,                # Panel width estimate
                    screen_height - 250  # Leave space for bottom controls
                )
                
                logger.info(f"Estimated transcript area at {transcript_area}")
                return transcript_area
                
            elif self.zoom_client_type == "web":
                # For web client, we'll need to use different detection approaches
                # Web client usually shows transcript in a more standardized area
                # This is a simplified approach that would need refinement
                screen_width, screen_height = pyautogui.size()
                
                # Estimate based on typical web client layout
                transcript_area = (
                    screen_width - 380,
                    200,
                    360,
                    screen_height - 300
                )
                
                logger.info(f"Estimated web client transcript area at {transcript_area}")
                return transcript_area
                
            else:
                logger.error(f"Unsupported Zoom client type: {self.zoom_client_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error finding transcript area: {str(e)}")
            return None
    
    def capture_transcript(self) -> str:
        """
        Capture the current transcript from Zoom.
        
        Returns:
            String containing the captured transcript text.
        """
        logger.info(f"Capturing transcript from {self.zoom_client_type} client")
        
        try:
            # Find the transcript area
            transcript_area = self.find_transcript_area()
            
            if not transcript_area:
                logger.error("Failed to find transcript area")
                return ""
            
            # Capture strategy depends on client type
            if self.zoom_client_type == "desktop":
                # Desktop client approach: Triple-click to select all text, then copy
                # Move to the center of the transcript area
                x, y, width, height = transcript_area
                center_x = x + width // 2
                center_y = y + height // 2
                
                # Click to focus the area
                pyautogui.click(center_x, center_y)
                time.sleep(WAIT_SHORT)
                
                # Triple-click to select all text
                pyautogui.tripleClick(center_x, center_y)
                time.sleep(WAIT_SHORT)
                
                # Copy selected text
                pyautogui.hotkey('ctrl', 'c')  # Windows/Linux
                # For macOS compatibility, we could detect OS and use 'command' instead of 'ctrl'
                
                # Wait for clipboard to update
                time.sleep(WAIT_SHORT)
                
                # Get text from clipboard
                transcript_text = pyperclip.paste()
                
            elif self.zoom_client_type == "web":
                # Web client approach: Take screenshot and perform OCR (simplified here)
                # In a real implementation, we would use Selenium for web client
                # For now, we're using a similar approach to desktop
                x, y, width, height = transcript_area
                center_x = x + width // 2
                center_y = y + height // 2
                
                # Click to focus the area
                pyautogui.click(center_x, center_y)
                time.sleep(WAIT_SHORT)
                
                # Use keyboard shortcuts to select all and copy
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(WAIT_SHORT)
                pyautogui.hotkey('ctrl', 'c')
                
                # Wait for clipboard to update
                time.sleep(WAIT_SHORT)
                
                # Get text from clipboard
                transcript_text = pyperclip.paste()
            
            else:
                logger.error(f"Unsupported Zoom client type: {self.zoom_client_type}")
                return ""
            
            # Clean up the transcript text
            cleaned_transcript = self._clean_transcript(transcript_text)
            
            if cleaned_transcript:
                logger.info(f"Successfully captured transcript: {len(cleaned_transcript)} characters")
                
                # Update transcript history
                self._update_transcript_history(cleaned_transcript)
                
                return cleaned_transcript
            else:
                logger.warning("Captured transcript is empty after cleaning")
                return ""
            
        except Exception as e:
            logger.error(f"Error capturing transcript: {str(e)}")
            return ""
    
    def get_recent_transcript(self, minutes: int = 10) -> str:
        """
        Get the transcript from the last specified number of minutes.
        
        Args:
            minutes: Number of minutes of transcript to retrieve
            
        Returns:
            String containing the recent transcript
        """
        logger.info(f"Retrieving transcript from last {minutes} minutes")
        
        try:
            # If we don't have history, capture a new transcript
            if not self.transcript_history:
                return self.capture_transcript()
            
            # Filter transcript entries by time
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            recent_entries = [
                entry for entry in self.transcript_history 
                if entry['timestamp'] >= cutoff_time
            ]
            
            if not recent_entries:
                logger.warning(f"No transcript entries found in the last {minutes} minutes")
                return ""
            
            # Combine all recent entries
            recent_transcript = "\n".join([entry['text'] for entry in recent_entries])
            
            logger.info(f"Retrieved {len(recent_entries)} transcript entries from last {minutes} minutes")
            return recent_transcript
            
        except Exception as e:
            logger.error(f"Error retrieving recent transcript: {str(e)}")
            return ""
    
    def _clean_transcript(self, text: str) -> str:
        """
        Clean up the transcript text by removing unnecessary characters, etc.
        
        Args:
            text: Raw transcript text
            
        Returns:
            Cleaned transcript text
        """
        if not text:
            return ""
            
        try:
            # Remove timestamps and speaker identifiers
            # Common format: "10:15:32 John Doe: Hello everyone"
            cleaned_text = re.sub(r'\d{1,2}:\d{2}:\d{2}\s+[\w\s]+:', '', text)
            
            # Alternative format: "[10:15:32] John Doe: Hello everyone"
            cleaned_text = re.sub(r'\[\d{1,2}:\d{2}:\d{2}\]\s+[\w\s]+:', '', cleaned_text)
            
            # Remove remaining timestamps
            cleaned_text = re.sub(r'\d{1,2}:\d{2}:\d{2}', '', cleaned_text)
            cleaned_text = re.sub(r'\[\d{1,2}:\d{2}:\d{2}\]', '', cleaned_text)
            
            # Remove extra whitespace
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
            
            # Remove Zoom system messages
            cleaned_text = re.sub(r'Recording started\.', '', cleaned_text)
            cleaned_text = re.sub(r'Recording stopped\.', '', cleaned_text)
            cleaned_text = re.sub(r'[\w\s]+ has joined the meeting\.', '', cleaned_text)
            cleaned_text = re.sub(r'[\w\s]+ has left the meeting\.', '', cleaned_text)
            
            # Trim whitespace
            cleaned_text = cleaned_text.strip()
            
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error cleaning transcript: {str(e)}")
            return text  # Return original text if cleaning fails
    
    def _update_transcript_history(self, new_transcript: str):
        """
        Update the transcript history with new content.
        
        Args:
            new_transcript: New transcript content to add to history
        """
        try:
            # Create a new entry with timestamp
            new_entry = {
                'timestamp': datetime.now(),
                'text': new_transcript
            }
            
            # Add to history
            self.transcript_history.append(new_entry)
            
            # Limit history size (keep last 10 entries)
            if len(self.transcript_history) > 10:
                self.transcript_history = self.transcript_history[-10:]
                
            logger.debug(f"Updated transcript history, now has {len(self.transcript_history)} entries")
            
        except Exception as e:
            logger.error(f"Error updating transcript history: {str(e)}")
            
    def set_zoom_client_type(self, client_type: str):
        """
        Change the Zoom client type.
        
        Args:
            client_type: "desktop" or "web"
        """
        if client_type not in ["desktop", "web"]:
            logger.error(f"Invalid Zoom client type: {client_type}")
            return
            
        self.zoom_client_type = client_type
        logger.info(f"Zoom client type changed to {client_type}")
        
    def reset_history(self):
        """Clear the transcript history."""
        self.transcript_history = []
        logger.info("Transcript history has been reset")