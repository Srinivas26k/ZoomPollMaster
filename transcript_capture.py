"""
Transcript Capture Module for the Automated Zoom Poll Generator.
Handles the capture of meeting transcripts from Zoom using UI automation.
"""

import os
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import pyperclip

# Configure logger
logger = logging.getLogger(__name__)

class TranscriptCapture:
    """
    Handles the capture of meeting transcripts from Zoom meetings.
    Supports both desktop and web Zoom clients.
    """
    
    def __init__(self, client_type: str = "web", enable_ocr: bool = False):
        """
        Initialize the transcript capture module.
        
        Args:
            client_type: Type of Zoom client ('web' or 'desktop')
            enable_ocr: Whether to enable OCR for text extraction (requires pytesseract and OpenCV)
        """
        self.client_type = client_type.lower()
        self.enable_ocr = enable_ocr
        self.last_capture_time = None
        self.save_transcripts = True
        self.transcripts_folder = "./transcripts"
        
        # Create transcripts folder if it doesn't exist
        if self.save_transcripts:
            os.makedirs(self.transcripts_folder, exist_ok=True)
        
        logger.info(f"TranscriptCapture initialized with {client_type} client type")
        
        # Initialize OCR if enabled
        if self.enable_ocr:
            try:
                # Import OCR-related libraries only if needed
                import pytesseract
                import cv2
                self.pytesseract = pytesseract
                self.cv2 = cv2
                logger.info("OCR functionality enabled")
            except ImportError as e:
                logger.error(f"Failed to import OCR libraries: {e}")
                self.enable_ocr = False
    
    def capture_transcript(self) -> Optional[str]:
        """
        Capture transcript from the current Zoom meeting.
        
        Returns:
            The captured transcript as a string, or None if capture failed
        """
        logger.info("Starting transcript capture")
        
        try:
            if self.client_type == "desktop":
                transcript = self._capture_from_desktop_client()
            else:  # web client
                transcript = self._capture_from_web_client()
            
            if transcript:
                self.last_capture_time = datetime.now()
                
                # Save transcript to file if enabled
                if self.save_transcripts:
                    self._save_transcript_to_file(transcript)
                
                logger.info(f"Successfully captured transcript ({len(transcript)} characters)")
                return transcript
            else:
                logger.warning("Transcript capture returned empty result")
                return None
                
        except Exception as e:
            logger.error(f"Error during transcript capture: {str(e)}")
            return None
    
    def _capture_from_desktop_client(self) -> Optional[str]:
        """
        Capture transcript from Zoom desktop client using UI automation.
        
        Returns:
            The captured transcript, or None if capture failed
        """
        logger.info("Capturing transcript from Zoom desktop client")
        
        try:
            import pyautogui
            
            # 1. Access transcript in Zoom desktop client
            # Click on "Live Transcript" button in the meeting toolbar
            transcript_button_position = self._find_live_transcript_button()
            if not transcript_button_position:
                logger.warning("Could not find Live Transcript button")
                return None
            
            pyautogui.click(transcript_button_position)
            time.sleep(1)  # Wait for transcript panel to open
            
            # 2. Select and copy the transcript text
            # Use pyautogui to drag-select the text and Ctrl+A/Ctrl+C
            pyautogui.hotkey('ctrl', 'a')  # Select all text
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'c')  # Copy text
            time.sleep(0.5)
            
            # Get text from clipboard
            transcript = pyperclip.paste()
            
            # 3. Close the transcript panel
            pyautogui.press('esc')
            
            if not transcript:
                logger.warning("Failed to capture transcript from clipboard")
                # Fallback to OCR if enabled
                if self.enable_ocr:
                    return self._capture_using_ocr()
                return None
            
            return self._clean_transcript(transcript)
            
        except Exception as e:
            logger.error(f"Error capturing from desktop client: {str(e)}")
            return None
    
    def _capture_from_web_client(self) -> Optional[str]:
        """
        Capture transcript from Zoom web client using UI automation.
        
        Returns:
            The captured transcript, or None if capture failed
        """
        logger.info("Capturing transcript from Zoom web client")
        
        try:
            import pyautogui
            
            # 1. Access transcript in Zoom web client
            # Locate and click on "CC" or "Live Transcript" button
            cc_button_position = self._find_cc_button_web()
            if not cc_button_position:
                logger.warning("Could not find CC button in web client")
                return None
            
            pyautogui.click(cc_button_position)
            time.sleep(1)
            
            # 2. Select and copy the transcript text
            # Find the transcript panel and click on it
            transcript_panel = self._find_transcript_panel_web()
            if not transcript_panel:
                logger.warning("Could not find transcript panel in web client")
                return None
            
            pyautogui.click(transcript_panel)
            time.sleep(0.5)
            
            # Select all text and copy
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.5)
            
            # Get text from clipboard
            transcript = pyperclip.paste()
            
            # 3. Close the transcript panel
            pyautogui.press('esc')
            
            if not transcript:
                logger.warning("Failed to capture transcript from clipboard")
                # Fallback to OCR if enabled
                if self.enable_ocr:
                    return self._capture_using_ocr()
                return None
            
            return self._clean_transcript(transcript)
            
        except Exception as e:
            logger.error(f"Error capturing from web client: {str(e)}")
            return None
    
    def _capture_using_ocr(self) -> Optional[str]:
        """
        Capture transcript using OCR (Optical Character Recognition).
        This is a fallback method when direct text copying fails.
        
        Returns:
            The captured transcript, or None if capture failed
        """
        if not self.enable_ocr:
            logger.warning("OCR capture requested but OCR is not enabled")
            return None
        
        logger.info("Attempting to capture transcript using OCR")
        
        try:
            import pyautogui
            
            # 1. Take screenshot of the transcript area
            screenshot = pyautogui.screenshot()
            
            # 2. Convert to format compatible with OpenCV
            screenshot = self.cv2.cvtColor(numpy.array(screenshot), self.cv2.COLOR_RGB2BGR)
            
            # 3. Process the image to improve OCR accuracy
            # Convert to grayscale
            gray = self.cv2.cvtColor(screenshot, self.cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get black and white image
            _, threshold = self.cv2.threshold(gray, 150, 255, self.cv2.THRESH_BINARY)
            
            # 4. Perform OCR on the processed image
            transcript = self.pytesseract.image_to_string(threshold)
            
            if not transcript:
                logger.warning("OCR returned empty result")
                return None
            
            return self._clean_transcript(transcript)
            
        except Exception as e:
            logger.error(f"Error during OCR capture: {str(e)}")
            return None
    
    def _find_live_transcript_button(self):
        """
        Locate the Live Transcript button in the Zoom desktop client.
        
        Returns:
            The position (x, y) of the button, or None if not found
        """
        # This is a placeholder for the actual implementation
        # In a real implementation, you would use pyautogui.locateOnScreen()
        # with an image of the Live Transcript button
        
        # Placeholder implementation returns a fixed position
        # In production, this would need to be calibrated for the user's screen
        return (100, 100)  # Example coordinates
    
    def _find_cc_button_web(self):
        """
        Locate the CC (Closed Caption) button in the Zoom web client.
        
        Returns:
            The position (x, y) of the button, or None if not found
        """
        # This is a placeholder for the actual implementation
        # In a real implementation, you would use pyautogui.locateOnScreen()
        
        # Placeholder implementation returns a fixed position
        return (200, 200)  # Example coordinates
    
    def _find_transcript_panel_web(self):
        """
        Locate the transcript panel in the Zoom web client.
        
        Returns:
            The position (x, y) of the panel, or None if not found
        """
        # This is a placeholder for the actual implementation
        
        # Placeholder implementation returns a fixed position
        return (300, 300)  # Example coordinates
    
    def _clean_transcript(self, transcript: str) -> str:
        """
        Clean and format the captured transcript.
        
        Args:
            transcript: The raw transcript text
        
        Returns:
            Cleaned transcript text
        """
        # Remove unnecessary whitespace
        transcript = transcript.strip()
        
        # Additional cleaning can be added here
        
        return transcript
    
    def _save_transcript_to_file(self, transcript: str) -> None:
        """
        Save the captured transcript to a file.
        
        Args:
            transcript: The transcript text to save
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transcript_{timestamp}.txt"
            filepath = os.path.join(self.transcripts_folder, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(transcript)
            
            logger.info(f"Transcript saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving transcript to file: {str(e)}")

# Helper function to create an instance with default settings
def create_transcript_capture(client_type: str = "web") -> TranscriptCapture:
    """
    Create and return a TranscriptCapture instance with default settings.
    
    Args:
        client_type: Type of Zoom client ('web' or 'desktop')
    
    Returns:
        Configured TranscriptCapture instance
    """
    return TranscriptCapture(client_type=client_type)