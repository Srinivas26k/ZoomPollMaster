"""
Transcript Capture Module for the Automated Zoom Poll Generator.
Uses PyAutoGUI to capture a 10-minute transcript from Zoom.
"""

import time
import pyautogui
import pyperclip
import logging
from typing import Optional, Tuple
import os

from logger import get_logger
from config import WAIT_SHORT, WAIT_MEDIUM, WAIT_LONG

logger = get_logger()


class TranscriptCapture:
    """
    Handles the capture of transcripts directly from the Zoom application.
    Uses UI automation to locate and copy transcript text.
    """
    
    def __init__(self):
        """Initialize the transcript capture module."""
        self.last_transcript = ""
        self.transcript_history = []
        # Coordinates for transcript area (will be calibrated)
        self.transcript_area = None
        logger.info("Transcript capture module initialized")
    
    def find_transcript_area(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Find the transcript area in the Zoom window.
        
        Returns:
            Tuple of (x, y, width, height) for the transcript area, or None if not found.
        """
        logger.info("Attempting to locate Zoom transcript area")
        
        try:
            # Look for the "Live Transcript" text or icon
            transcript_button = pyautogui.locateOnScreen('transcript_button.png', confidence=0.7)
            
            if not transcript_button:
                # If image search fails, try to find the transcript panel by coordinates
                # This is a fallback method and may need adjustment based on screen resolution
                logger.warning("Could not find transcript button - using default coordinates")
                
                # Get screen size for relative positioning
                screen_width, screen_height = pyautogui.size()
                
                # Estimate transcript panel location (right side of screen, middle section)
                # These are rough estimates and may need adjustment
                x = int(screen_width * 0.75)
                y = int(screen_height * 0.3)
                width = int(screen_width * 0.20)
                height = int(screen_height * 0.5)
                
                self.transcript_area = (x, y, width, height)
                logger.info(f"Using estimated transcript area: {self.transcript_area}")
                return self.transcript_area
            
            # If button found, the transcript panel is likely nearby
            button_x, button_y = pyautogui.center(transcript_button)
            
            # Transcript panel is typically below the button
            panel_x = button_x
            panel_y = button_y + 50  # Offset from button
            panel_width = 300  # Estimated width
            panel_height = 400  # Estimated height
            
            self.transcript_area = (panel_x, panel_y, panel_width, panel_height)
            logger.info(f"Located transcript area: {self.transcript_area}")
            return self.transcript_area
            
        except Exception as e:
            logger.error(f"Error finding transcript area: {str(e)}")
            return None
    
    def capture_transcript(self) -> str:
        """
        Capture the current transcript from Zoom.
        
        Returns:
            String containing the captured transcript text.
        """
        logger.info("Starting transcript capture process")
        
        try:
            # Find transcript area if not already known
            if not self.transcript_area:
                self.find_transcript_area()
                if not self.transcript_area:
                    logger.error("Failed to locate transcript area")
                    return ""
            
            # Save current clipboard content
            original_clipboard = pyperclip.paste()
            
            # Click on the transcript area to activate it
            area_center_x = self.transcript_area[0] + (self.transcript_area[2] // 2)
            area_center_y = self.transcript_area[1] + (self.transcript_area[3] // 2)
            pyautogui.click(area_center_x, area_center_y)
            time.sleep(WAIT_SHORT)
            
            # Select all transcript text (Ctrl+A)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(WAIT_SHORT)
            
            # Copy selected text (Ctrl+C)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(WAIT_SHORT)
            
            # Get copied text from clipboard
            transcript_text = pyperclip.paste()
            
            # Restore original clipboard content
            pyperclip.copy(original_clipboard)
            
            # Clean up the transcript text (remove unwanted characters, etc.)
            transcript_text = self._clean_transcript(transcript_text)
            
            # Update transcript history
            self._update_transcript_history(transcript_text)
            
            logger.info(f"Successfully captured transcript ({len(transcript_text)} characters)")
            return transcript_text
            
        except Exception as e:
            logger.error(f"Error during transcript capture: {str(e)}")
            return ""
    
    def get_recent_transcript(self, minutes: int = 10) -> str:
        """
        Get the transcript from the last specified number of minutes.
        
        Args:
            minutes: Number of minutes of transcript to retrieve
            
        Returns:
            String containing the recent transcript
        """
        logger.info(f"Retrieving {minutes}-minute recent transcript")
        
        # Capture current transcript if we haven't done it already
        if not self.last_transcript:
            self.capture_transcript()
            
        # Extract the relevant portion of the transcript (last N minutes)
        # This is a simplified version - in a real implementation, you'd need to
        # parse timestamps from the transcript to extract exactly N minutes
        
        # For now, just return the whole transcript as a simplification
        return self.last_transcript
    
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
            
        # Remove redundant whitespace
        text = " ".join(text.split())
        
        # Other cleaning operations can be added here
        
        return text
    
    def _update_transcript_history(self, new_transcript: str):
        """
        Update the transcript history with new content.
        
        Args:
            new_transcript: New transcript content to add to history
        """
        if new_transcript:
            self.last_transcript = new_transcript
            self.transcript_history.append(new_transcript)
            
            # Keep only the last 3 transcript snapshots to avoid memory bloat
            if len(self.transcript_history) > 3:
                self.transcript_history.pop(0)
