"""
Poll Posting Module for the Automated Zoom Poll Generator.
Uses PyAutoGUI to post polls to Zoom meetings.
"""

import time
import pyautogui
import logging
from typing import Dict, List, Optional, Tuple

from logger import get_logger
from config import WAIT_SHORT, WAIT_MEDIUM, WAIT_LONG

logger = get_logger()


class PollPosting:
    """
    Handles posting of generated polls to Zoom meetings via UI automation.
    """
    
    def __init__(self):
        """Initialize the poll posting module."""
        # Coordinates for Zoom UI elements (will be calibrated)
        self.poll_menu_location = None
        self.poll_button_location = None
        logger.info("Poll posting module initialized")
    
    def find_zoom_window(self) -> bool:
        """
        Locate the Zoom meeting window and bring it to focus.
        
        Returns:
            Boolean indicating whether Zoom window was found and focused
        """
        logger.info("Locating Zoom meeting window")
        
        try:
            # Try to find Zoom window by its title bar
            zoom_window = pyautogui.getWindowsWithTitle("Zoom Meeting")
            
            if not zoom_window:
                # Try alternative titles
                zoom_window = pyautogui.getWindowsWithTitle("Zoom")
                
                if not zoom_window:
                    logger.error("Could not find Zoom window")
                    return False
            
            # Activate the Zoom window
            zoom_window[0].activate()
            time.sleep(WAIT_SHORT)
            
            logger.info("Zoom window located and focused")
            return True
            
        except Exception as e:
            logger.error(f"Error finding Zoom window: {str(e)}")
            return False
    
    def find_poll_menu(self) -> Optional[Tuple[int, int]]:
        """
        Find the polling menu button in the Zoom interface.
        
        Returns:
            Tuple of (x, y) coordinates for poll menu button, or None if not found
        """
        logger.info("Locating Zoom poll menu button")
        
        try:
            # Try to locate the poll button by image
            poll_button = pyautogui.locateOnScreen('poll_button.png', confidence=0.7)
            
            if poll_button:
                self.poll_button_location = pyautogui.center(poll_button)
                logger.info(f"Poll button located at {self.poll_button_location}")
                return self.poll_button_location
            
            # Fallback: try to locate using text
            poll_text_locations = list(pyautogui.locateAllOnScreen('poll_text.png', confidence=0.7))
            
            if poll_text_locations:
                self.poll_button_location = pyautogui.center(poll_text_locations[0])
                logger.info(f"Poll text located at {self.poll_button_location}")
                return self.poll_button_location
            
            # Second fallback: check in the meeting controls area
            # This is a rough estimate and may need adjustment
            screen_width, screen_height = pyautogui.size()
            controls_y = int(screen_height * 0.9)  # Assuming controls are at the bottom
            
            # Scan along the bottom for potential poll button
            for x in range(100, screen_width - 100, 100):
                pyautogui.moveTo(x, controls_y)
                time.sleep(0.1)
                
                # Check if a tooltip appears with "Poll" in it
                poll_tooltip = pyautogui.locateOnScreen('poll_tooltip.png', confidence=0.7)
                if poll_tooltip:
                    self.poll_button_location = (x, controls_y)
                    logger.info(f"Poll button estimated at {self.poll_button_location}")
                    return self.poll_button_location
            
            logger.warning("Could not locate poll button - using fallback method")
            
            # Last resort: Use "More" button and then find Poll
            more_button = pyautogui.locateOnScreen('more_button.png', confidence=0.7)
            
            if more_button:
                more_center = pyautogui.center(more_button)
                pyautogui.click(more_center)
                time.sleep(WAIT_SHORT)
                
                # Look for Poll in the dropdown
                poll_menu_item = pyautogui.locateOnScreen('poll_menu_item.png', confidence=0.7)
                
                if poll_menu_item:
                    self.poll_button_location = pyautogui.center(poll_menu_item)
                    logger.info(f"Poll menu item located at {self.poll_button_location}")
                    # Don't click yet, just return the location
                    return self.poll_button_location
            
            logger.error("Could not locate poll button or menu")
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
        logger.info("Starting process to post poll to Zoom")
        
        try:
            # Find and focus the Zoom window
            if not self.find_zoom_window():
                return False
            
            # Find poll menu button if not already known
            if not self.poll_button_location:
                self.poll_button_location = self.find_poll_menu()
                
                if not self.poll_button_location:
                    logger.error("Failed to locate poll button")
                    return False
            
            # Click on poll button
            logger.info("Clicking poll button")
            pyautogui.click(self.poll_button_location)
            time.sleep(WAIT_MEDIUM)
            
            # Look for "Launch Polling" or similar button
            launch_button = pyautogui.locateOnScreen('launch_polling.png', confidence=0.7)
            
            if not launch_button:
                # Try to find "Add a Poll" or "Create" button if no existing polls
                add_button = pyautogui.locateOnScreen('add_poll.png', confidence=0.7)
                
                if not add_button:
                    # Try generic "create" text
                    add_button = pyautogui.locateOnScreen('create_button.png', confidence=0.7)
                
                if add_button:
                    logger.info("Clicking add/create poll button")
                    pyautogui.click(pyautogui.center(add_button))
                    time.sleep(WAIT_MEDIUM)
                else:
                    logger.error("Could not find add poll button")
                    return False
            
            # Now we should be in the poll creation interface
            
            # Enter poll question
            # Try to find question field
            question_field = pyautogui.locateOnScreen('question_field.png', confidence=0.7)
            
            if not question_field:
                # Fallback: Try to locate based on typical UI layout
                # Most likely the first text field in the form
                logger.info("Using fallback method to locate question field")
                
                # Move to estimated position and click
                screen_width, screen_height = pyautogui.size()
                question_x = int(screen_width * 0.5)
                question_y = int(screen_height * 0.3)
                
                pyautogui.click(question_x, question_y)
                time.sleep(WAIT_SHORT)
            else:
                pyautogui.click(pyautogui.center(question_field))
                time.sleep(WAIT_SHORT)
            
            # Enter question text
            pyautogui.write(poll_data['question'])
            time.sleep(WAIT_SHORT)
            
            # Tab to first option field
            pyautogui.press('tab')
            time.sleep(WAIT_SHORT)
            
            # Enter options
            for option in poll_data['options']:
                pyautogui.write(option)
                pyautogui.press('tab')
                time.sleep(WAIT_SHORT)
            
            # Look for save button
            save_button = pyautogui.locateOnScreen('save_button.png', confidence=0.7)
            
            if not save_button:
                # Try alternative terms
                save_button = pyautogui.locateOnScreen('done_button.png', confidence=0.7)
                
                if not save_button:
                    logger.warning("Could not find save/done button - trying generic location")
                    # Estimate button position (usually bottom right)
                    screen_width, screen_height = pyautogui.size()
                    save_x = int(screen_width * 0.8)
                    save_y = int(screen_height * 0.8)
                    
                    pyautogui.click(save_x, save_y)
                else:
                    logger.info("Clicking done button")
                    pyautogui.click(pyautogui.center(save_button))
            else:
                logger.info("Clicking save button")
                pyautogui.click(pyautogui.center(save_button))
            
            time.sleep(WAIT_MEDIUM)
            
            # Look for launch button
            launch_button = pyautogui.locateOnScreen('launch_poll.png', confidence=0.7)
            
            if not launch_button:
                # Try alternative terms
                launch_button = pyautogui.locateOnScreen('start_poll.png', confidence=0.7)
                
                if not launch_button:
                    logger.warning("Could not find launch/start button - trying generic location")
                    # Estimate button position (usually bottom right)
                    screen_width, screen_height = pyautogui.size()
                    launch_x = int(screen_width * 0.8)
                    launch_y = int(screen_height * 0.8)
                    
                    pyautogui.click(launch_x, launch_y)
                else:
                    logger.info("Clicking start poll button")
                    pyautogui.click(pyautogui.center(launch_button))
            else:
                logger.info("Clicking launch poll button")
                pyautogui.click(pyautogui.center(launch_button))
            
            logger.info("Poll successfully posted to Zoom")
            return True
            
        except Exception as e:
            logger.error(f"Error posting poll to Zoom: {str(e)}")
            return False
