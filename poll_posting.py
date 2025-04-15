"""
Poll Posting Module for the Automated Zoom Poll Generator.
Uses PyAutoGUI to post polls to Zoom meetings.
"""

import time
import re
import logging
import pyautogui
import pyperclip
from typing import Optional, Tuple, Dict, List

from logger import get_logger
from config import WAIT_SHORT, WAIT_MEDIUM, WAIT_LONG, POLL_BUTTON_IMAGE, LAUNCH_POLL_IMAGE

logger = get_logger()


class PollPosting:
    """
    Handles posting of generated polls to Zoom meetings via UI automation.
    """
    
    def __init__(self, zoom_client_type="desktop"):
        """
        Initialize the poll posting module.
        
        Args:
            zoom_client_type: Type of Zoom client ("desktop" or "web")
        """
        self.zoom_client_type = zoom_client_type
        
        # Set confidence level for image recognition
        self.confidence_level = 0.7
        
        logger.info(f"Poll posting module initialized for {zoom_client_type} client")
    
    def find_zoom_window(self) -> bool:
        """
        Locate the Zoom meeting window and bring it to focus.
        
        Returns:
            Boolean indicating whether Zoom window was found and focused
        """
        logger.info("Looking for Zoom window")
        
        try:
            if self.zoom_client_type == "desktop":
                # For desktop client, look for the Zoom window by title pattern
                # This is a simplified approach and might need improvement
                # In a real implementation, we would use platform-specific methods
                
                # Simulate Alt+Tab to switch windows (simplistic approach)
                pyautogui.keyDown('alt')
                time.sleep(WAIT_SHORT)
                pyautogui.press('tab')
                time.sleep(WAIT_SHORT)
                pyautogui.keyUp('alt')
                
                # Give the window time to come into focus
                time.sleep(WAIT_MEDIUM)
                
                logger.info("Attempted to bring Zoom window to focus")
                return True
                
            elif self.zoom_client_type == "web":
                # For web client, we would use browser automation
                # This is a simplified approach for demonstration
                
                # In a real implementation with Selenium, we would switch to the Zoom tab
                # For now, we'll use a simple Alt+Tab approach
                pyautogui.keyDown('alt')
                time.sleep(WAIT_SHORT)
                pyautogui.press('tab')
                time.sleep(WAIT_SHORT)
                pyautogui.keyUp('alt')
                
                # Give the window time to come into focus
                time.sleep(WAIT_MEDIUM)
                
                logger.info("Attempted to bring Zoom web client to focus")
                return True
                
            else:
                logger.error(f"Unsupported Zoom client type: {self.zoom_client_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error finding Zoom window: {str(e)}")
            return False
    
    def find_poll_menu(self) -> Optional[Tuple[int, int]]:
        """
        Find the polling menu button in the Zoom interface.
        
        Returns:
            Tuple of (x, y) coordinates for poll menu button, or None if not found
        """
        logger.info("Looking for poll menu button")
        
        try:
            if self.zoom_client_type == "desktop":
                # Look for the poll button image
                poll_button = pyautogui.locateOnScreen(
                    POLL_BUTTON_IMAGE,
                    confidence=self.confidence_level
                )
                
                if not poll_button:
                    logger.warning("Could not find poll button using image recognition")
                    
                    # Try alternative method - look for text elements like "Polls" or "Polling"
                    # This is a fallback approach that might be less reliable
                    for text in ["Polls", "Polling", "Poll"]:
                        try:
                            poll_region = pyautogui.locateOnScreen(
                                f"Searching for text: {text}",
                                confidence=0.6
                            )
                            if poll_region:
                                logger.info(f"Found potential poll button using text search: {text}")
                                return pyautogui.center(poll_region)
                        except Exception:
                            continue
                    
                    logger.error("Could not find poll button in Zoom interface")
                    return None
                
                # Get center of poll button
                button_center = pyautogui.center(poll_button)
                logger.info(f"Found poll button at {button_center}")
                return button_center
                
            elif self.zoom_client_type == "web":
                # For web client, look for poll button in the web interface
                # This is a simplified approach for demonstration
                
                # In a real implementation with Selenium, we would use XPath or CSS selectors
                # For now, we'll use image recognition similar to desktop
                poll_button = pyautogui.locateOnScreen(
                    POLL_BUTTON_IMAGE,
                    confidence=self.confidence_level
                )
                
                if not poll_button:
                    logger.warning("Could not find poll button in web interface")
                    return None
                
                button_center = pyautogui.center(poll_button)
                logger.info(f"Found poll button in web interface at {button_center}")
                return button_center
                
            else:
                logger.error(f"Unsupported Zoom client type: {self.zoom_client_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error finding poll menu: {str(e)}")
            return None
    
    def post_poll_to_zoom(self, poll_data: Dict[str, str]) -> bool:
        """
        Post a poll to Zoom using UI automation.
        
        Args:
            poll_data: Dict containing 'question' and 'options' keys
            
        Returns:
            Boolean indicating whether poll was successfully posted
        """
        logger.info("Posting poll to Zoom")
        
        try:
            # Validate poll data
            if not poll_data or 'question' not in poll_data or 'options' not in poll_data:
                logger.error("Invalid poll data structure")
                return False
            
            question = poll_data['question']
            options = poll_data['options']
            
            if not question or not options or len(options) < 2:
                logger.error(f"Invalid poll content: Question: '{question}', Options: {options}")
                return False
            
            # Find and focus the Zoom window
            if not self.find_zoom_window():
                logger.error("Failed to find Zoom window")
                return False
            
            # Find the poll menu button
            poll_button_pos = self.find_poll_menu()
            
            if not poll_button_pos:
                logger.error("Failed to find poll menu button")
                return False
            
            # Click on the poll button to open the poll menu
            x, y = poll_button_pos
            pyautogui.click(x, y)
            time.sleep(WAIT_MEDIUM)
            
            # The approach from here depends on client type
            if self.zoom_client_type == "desktop":
                # For desktop client, we need to:
                # 1. Look for "Add a Poll" or "Create a Poll" option
                # 2. Fill in the poll question and options
                # 3. Click "Launch Poll" button
                
                # Look for "Add a Poll" or similar text
                # This is simplified and would need refinement in real implementation
                for text in ["Add a Poll", "Create a Poll", "New Poll"]:
                    try:
                        # Try to find the text on screen
                        add_poll_btn = pyautogui.locateOnScreen(
                            f"Searching for text: {text}",
                            confidence=0.6
                        )
                        if add_poll_btn:
                            # Click on "Add a Poll"
                            add_poll_center = pyautogui.center(add_poll_btn)
                            pyautogui.click(add_poll_center)
                            time.sleep(WAIT_MEDIUM)
                            break
                    except Exception:
                        continue
                
                # Now we should be in the poll creation interface
                # Tab to move between fields and fill in content
                
                # Fill in the question
                pyautogui.write(question)
                time.sleep(WAIT_SHORT)
                
                # Tab to the first option field
                pyautogui.press('tab')
                time.sleep(WAIT_SHORT)
                
                # Fill in options
                for option in options:
                    pyautogui.write(option)
                    time.sleep(WAIT_SHORT)
                    pyautogui.press('tab')  # Move to next field or button
                    time.sleep(WAIT_SHORT)
                
                # Find and click the "Save" or "Create" button
                # This is simplified and would need refinement
                for text in ["Save", "Create", "Done"]:
                    try:
                        save_btn = pyautogui.locateOnScreen(
                            f"Searching for text: {text}",
                            confidence=0.6
                        )
                        if save_btn:
                            save_center = pyautogui.center(save_btn)
                            pyautogui.click(save_center)
                            time.sleep(WAIT_MEDIUM)
                            break
                    except Exception:
                        continue
                
                # Now find and click "Launch Poll"
                launch_poll = pyautogui.locateOnScreen(
                    LAUNCH_POLL_IMAGE,
                    confidence=self.confidence_level
                )
                
                if not launch_poll:
                    # Try text-based recognition as fallback
                    for text in ["Launch Poll", "Start Poll", "Launch"]:
                        try:
                            launch_btn = pyautogui.locateOnScreen(
                                f"Searching for text: {text}",
                                confidence=0.6
                            )
                            if launch_btn:
                                launch_center = pyautogui.center(launch_btn)
                                pyautogui.click(launch_center)
                                time.sleep(WAIT_MEDIUM)
                                logger.info("Poll launched successfully")
                                return True
                        except Exception:
                            continue
                    
                    logger.error("Could not find Launch Poll button")
                    return False
                else:
                    # Click Launch Poll
                    launch_center = pyautogui.center(launch_poll)
                    pyautogui.click(launch_center)
                    time.sleep(WAIT_MEDIUM)
                    logger.info("Poll launched successfully")
                    return True
                
            elif self.zoom_client_type == "web":
                # For web client, the process is similar but the UI elements are different
                # This would be more reliable with Selenium, but we'll use a similar approach
                
                # Look for "Add a Poll" or similar text
                for text in ["Add a Poll", "Create a Poll", "New Poll"]:
                    try:
                        add_poll_btn = pyautogui.locateOnScreen(
                            f"Searching for text: {text}",
                            confidence=0.6
                        )
                        if add_poll_btn:
                            add_poll_center = pyautogui.center(add_poll_btn)
                            pyautogui.click(add_poll_center)
                            time.sleep(WAIT_MEDIUM)
                            break
                    except Exception:
                        continue
                
                # Fill in the poll information
                # Web client might have different UI layout
                # This is a simplified approach
                
                # Fill in the question
                pyautogui.write(question)
                time.sleep(WAIT_SHORT)
                
                # Tab to the first option field
                pyautogui.press('tab')
                time.sleep(WAIT_SHORT)
                
                # Fill in options
                for option in options:
                    pyautogui.write(option)
                    time.sleep(WAIT_SHORT)
                    pyautogui.press('tab')
                    time.sleep(WAIT_SHORT)
                
                # Find and click Save/Create button
                for text in ["Save", "Create", "Done"]:
                    try:
                        save_btn = pyautogui.locateOnScreen(
                            f"Searching for text: {text}",
                            confidence=0.6
                        )
                        if save_btn:
                            save_center = pyautogui.center(save_btn)
                            pyautogui.click(save_center)
                            time.sleep(WAIT_MEDIUM)
                            break
                    except Exception:
                        continue
                
                # Launch the poll
                for text in ["Launch Poll", "Start Poll", "Launch"]:
                    try:
                        launch_btn = pyautogui.locateOnScreen(
                            f"Searching for text: {text}",
                            confidence=0.6
                        )
                        if launch_btn:
                            launch_center = pyautogui.center(launch_btn)
                            pyautogui.click(launch_center)
                            time.sleep(WAIT_MEDIUM)
                            logger.info("Poll launched successfully in web client")
                            return True
                    except Exception:
                        continue
                
                logger.error("Could not launch poll in web client")
                return False
                
            else:
                logger.error(f"Unsupported Zoom client type: {self.zoom_client_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error posting poll to Zoom: {str(e)}")
            return False
            
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
            
    def set_confidence_level(self, level: float):
        """
        Set the confidence level for image recognition.
        
        Args:
            level: Confidence level (0.0 to 1.0)
        """
        if level < 0.1 or level > 1.0:
            logger.error(f"Invalid confidence level: {level}")
            return
            
        self.confidence_level = level
        logger.info(f"Image recognition confidence level set to {level}")
            
    def has_poll_capability(self) -> bool:
        """
        Check if polling capability is available in the current Zoom meeting.
        
        Returns:
            Boolean indicating whether polling is available
        """
        # Find and focus the Zoom window
        if not self.find_zoom_window():
            logger.error("Failed to find Zoom window")
            return False
        
        # Look for the poll button to verify if polling is available
        poll_button_pos = self.find_poll_menu()
        
        if poll_button_pos:
            logger.info("Poll capability is available")
            return True
        else:
            logger.warning("Poll capability not found - may not be enabled for this meeting")
            return False