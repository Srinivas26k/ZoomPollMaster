"""
Zoom Automation Module for the Automated Zoom Poll Generator.
Handles direct interactions with the Zoom client using UI automation.
"""

import os
import time
import logging
import subprocess
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlparse

# Import selenium for web automation
import selenium
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logger
logger = logging.getLogger(__name__)

class ZoomAutomation:
    """
    Handles direct interactions with the Zoom client.
    Supports both desktop and web Zoom clients.
    """
    
    def __init__(self, client_type: str = "web"):
        """
        Initialize the Zoom automation module.
        
        Args:
            client_type: Type of Zoom client ('web' or 'desktop')
        """
        self.client_type = client_type.lower()
        self.meeting_id = None
        self.passcode = None
        self.display_name = None
        self.driver = None  # For web client
        self.meeting_active = False
        
        logger.info(f"ZoomAutomation initialized with {client_type} client type")
    
    def join_meeting(self, meeting_id: str, passcode: str, display_name: str = "Poll Generator") -> bool:
        """
        Join a Zoom meeting using the specified credentials.
        
        Args:
            meeting_id: The Zoom meeting ID
            passcode: The meeting passcode
            display_name: The name to display in the meeting
        
        Returns:
            Boolean indicating whether joining was successful
        """
        logger.info(f"Attempting to join meeting {meeting_id}")
        
        # Store meeting credentials
        self.meeting_id = meeting_id
        self.passcode = passcode
        self.display_name = display_name
        
        try:
            # Use appropriate join method based on client type
            if self.client_type == "desktop":
                result = self._join_meeting_desktop()
            else:  # web client
                result = self._join_meeting_web()
            
            if result:
                self.meeting_active = True
                logger.info(f"Successfully joined meeting {meeting_id}")
                return True
            else:
                logger.error(f"Failed to join meeting {meeting_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error joining meeting: {str(e)}")
            return False
    
    def leave_meeting(self) -> bool:
        """
        Leave the current Zoom meeting.
        
        Returns:
            Boolean indicating whether leaving was successful
        """
        if not self.meeting_active:
            logger.warning("No active meeting to leave")
            return False
        
        logger.info("Attempting to leave meeting")
        
        try:
            # Use appropriate leave method based on client type
            if self.client_type == "desktop":
                result = self._leave_meeting_desktop()
            else:  # web client
                result = self._leave_meeting_web()
            
            if result:
                self.meeting_active = False
                self.meeting_id = None
                self.passcode = None
                logger.info("Successfully left meeting")
                return True
            else:
                logger.error("Failed to leave meeting")
                return False
                
        except Exception as e:
            logger.error(f"Error leaving meeting: {str(e)}")
            return False
    
    def check_meeting_status(self) -> bool:
        """
        Check if currently in an active meeting.
        
        Returns:
            Boolean indicating whether in an active meeting
        """
        try:
            # Use appropriate check method based on client type
            if self.client_type == "desktop":
                return self._check_meeting_status_desktop()
            else:  # web client
                return self._check_meeting_status_web()
                
        except Exception as e:
            logger.error(f"Error checking meeting status: {str(e)}")
            return False
    
    def enable_closed_captioning(self) -> bool:
        """
        Enable closed captioning in the current meeting.
        
        Returns:
            Boolean indicating whether enabling was successful
        """
        if not self.meeting_active:
            logger.warning("Cannot enable closed captioning - not in a meeting")
            return False
        
        logger.info("Attempting to enable closed captioning")
        
        try:
            # Use appropriate method based on client type
            if self.client_type == "desktop":
                result = self._enable_cc_desktop()
            else:  # web client
                result = self._enable_cc_web()
            
            if result:
                logger.info("Successfully enabled closed captioning")
                return True
            else:
                logger.error("Failed to enable closed captioning")
                return False
                
        except Exception as e:
            logger.error(f"Error enabling closed captioning: {str(e)}")
            return False
    
    def _join_meeting_desktop(self) -> bool:
        """
        Join a Zoom meeting using the desktop client.
        
        Returns:
            Boolean indicating whether joining was successful
        """
        try:
            import pyautogui
            
            # Launch Zoom desktop client
            # On Windows, typically: subprocess.Popen(["start", "zoommtg://zoom.us/join?confno={}".format(self.meeting_id)], shell=True)
            # This is a placeholder implementation
            
            # Use system-specific command to open Zoom
            if os.name == 'nt':  # Windows
                # Using zoommtg:// protocol to open Zoom
                os.system(f'start zoommtg://zoom.us/join?confno={self.meeting_id}')
            elif os.name == 'posix':  # macOS/Linux
                # Using open command on macOS
                os.system(f'open zoommtg://zoom.us/join?confno={self.meeting_id}')
            
            # Wait for Zoom to launch
            time.sleep(3)
            
            # Find and click "Join a Meeting" button if needed
            join_button = self._find_join_button_desktop()
            if join_button:
                pyautogui.click(join_button)
                time.sleep(1)
            
            # Enter meeting ID if prompted
            # This is a placeholder - in a real implementation, you'd need to locate the input field
            pyautogui.write(self.meeting_id)
            pyautogui.press('tab')
            pyautogui.write(self.display_name)
            pyautogui.press('tab')
            pyautogui.press('tab')  # Navigate to the Join button
            pyautogui.press('enter')
            
            # Wait for passcode prompt
            time.sleep(2)
            
            # Enter passcode
            pyautogui.write(self.passcode)
            pyautogui.press('enter')
            
            # Wait for meeting to join
            time.sleep(5)
            
            # Verify we're in the meeting
            return self._check_meeting_status_desktop()
            
        except Exception as e:
            logger.error(f"Error in desktop join process: {str(e)}")
            return False
    
    def _join_meeting_web(self) -> bool:
        """
        Join a Zoom meeting using the web client.
        
        Returns:
            Boolean indicating whether joining was successful
        """
        try:
            # Initialize Selenium WebDriver if not already done
            if not self.driver:
                self._initialize_web_driver()
            
            if not self.driver:
                logger.error("Failed to initialize web driver")
                return False
            
            # Construct the Zoom web join URL
            join_url = f"https://zoom.us/wc/join/{self.meeting_id}"
            
            # Navigate to the join page
            self.driver.get(join_url)
            
            # Wait for the page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "inputname"))
            )
            
            # Enter display name
            name_input = self.driver.find_element(By.ID, "inputname")
            name_input.clear()
            name_input.send_keys(self.display_name)
            
            # Click Join button
            join_button = self.driver.find_element(By.ID, "joinBtn")
            join_button.click()
            
            # Wait for passcode input to appear
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "inputpasscode"))
            )
            
            # Enter passcode
            passcode_input = self.driver.find_element(By.ID, "inputpasscode")
            passcode_input.send_keys(self.passcode)
            
            # Click Submit button
            submit_button = self.driver.find_element(By.ID, "passcodeBtn")
            submit_button.click()
            
            # Wait for meeting to load
            # This is a placeholder - you'd need to identify a reliable element that indicates the meeting is loaded
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".meeting-app"))
            )
            
            # Verify we're in the meeting
            return self._check_meeting_status_web()
            
        except Exception as e:
            logger.error(f"Error in web join process: {str(e)}")
            return False
    
    def _leave_meeting_desktop(self) -> bool:
        """
        Leave a Zoom meeting using the desktop client.
        
        Returns:
            Boolean indicating whether leaving was successful
        """
        try:
            import pyautogui
            
            # Find and click "End" or "Leave" button
            # This is a placeholder - you'd need to locate the button in the actual interface
            end_button = self._find_leave_button_desktop()
            if not end_button:
                logger.warning("Could not find Leave button")
                return False
            
            pyautogui.click(end_button)
            time.sleep(1)
            
            # If prompted to confirm leaving
            confirm_button = self._find_leave_confirm_button_desktop()
            if confirm_button:
                pyautogui.click(confirm_button)
            
            # Wait a moment for the meeting to close
            time.sleep(2)
            
            # Verify we've left the meeting
            return not self._check_meeting_status_desktop()
            
        except Exception as e:
            logger.error(f"Error in desktop leave process: {str(e)}")
            return False
    
    def _leave_meeting_web(self) -> bool:
        """
        Leave a Zoom meeting using the web client.
        
        Returns:
            Boolean indicating whether leaving was successful
        """
        if not self.driver:
            logger.error("Web driver not initialized")
            return False
        
        try:
            # Find and click the Leave button
            leave_button = self.driver.find_element(By.CSS_SELECTOR, ".leave-meeting-button")
            leave_button.click()
            
            # Wait for confirmation dialog
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".leave-meeting-dialog"))
            )
            
            # Click confirm button
            confirm_button = self.driver.find_element(By.CSS_SELECTOR, ".leave-meeting-dialog .confirm-button")
            confirm_button.click()
            
            # Wait for meeting to close
            time.sleep(2)
            
            # Verify we've left the meeting
            return not self._check_meeting_status_web()
            
        except Exception as e:
            logger.error(f"Error in web leave process: {str(e)}")
            return False
    
    def _check_meeting_status_desktop(self) -> bool:
        """
        Check if in an active meeting using desktop client indicators.
        
        Returns:
            Boolean indicating whether in an active meeting
        """
        try:
            import pyautogui
            
            # This is a placeholder implementation
            # In a real implementation, you would look for visual indicators that we're in a meeting
            # For example, looking for the "Leave Meeting" button or meeting controls
            
            # For now, we'll rely on our internal state
            return self.meeting_active
            
        except Exception as e:
            logger.error(f"Error checking desktop meeting status: {str(e)}")
            return False
    
    def _check_meeting_status_web(self) -> bool:
        """
        Check if in an active meeting using web client indicators.
        
        Returns:
            Boolean indicating whether in an active meeting
        """
        if not self.driver:
            return False
        
        try:
            # Check for presence of meeting UI elements
            # This is a placeholder - you'd need to identify reliable elements
            try:
                leave_button = self.driver.find_element(By.CSS_SELECTOR, ".leave-meeting-button")
                return True
            except NoSuchElementException:
                return False
                
        except Exception as e:
            logger.error(f"Error checking web meeting status: {str(e)}")
            return False
    
    def _enable_cc_desktop(self) -> bool:
        """
        Enable closed captioning in desktop client.
        
        Returns:
            Boolean indicating whether enabling was successful
        """
        try:
            import pyautogui
            
            # Find and click on "CC" button in the meeting controls
            cc_button = self._find_cc_button_desktop()
            if not cc_button:
                logger.warning("Could not find CC button")
                return False
            
            pyautogui.click(cc_button)
            time.sleep(1)
            
            # Enable closed captioning
            # This is a placeholder - in a real implementation, you'd need to interact with the CC menu
            
            return True
            
        except Exception as e:
            logger.error(f"Error enabling CC in desktop client: {str(e)}")
            return False
    
    def _enable_cc_web(self) -> bool:
        """
        Enable closed captioning in web client.
        
        Returns:
            Boolean indicating whether enabling was successful
        """
        if not self.driver:
            logger.error("Web driver not initialized")
            return False
        
        try:
            # Find and click on "CC" button
            cc_button = self.driver.find_element(By.CSS_SELECTOR, ".closed-caption-button")
            cc_button.click()
            
            # Enable closed captioning
            # This is a placeholder - you'd need to interact with the CC menu
            
            return True
            
        except Exception as e:
            logger.error(f"Error enabling CC in web client: {str(e)}")
            return False
    
    def _initialize_web_driver(self) -> None:
        """
        Initialize Selenium WebDriver for web client automation.
        """
        try:
            from selenium import webdriver
            import chromedriver_autoinstaller
            
            # Auto-install Chrome driver if needed
            chromedriver_autoinstaller.install()
            
            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Auto-accept webcam/mic permissions
            
            # Initialize WebDriver
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("WebDriver initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing WebDriver: {str(e)}")
            self.driver = None
    
    def _find_join_button_desktop(self) -> Optional[Tuple[int, int]]:
        """
        Find the "Join a Meeting" button in the desktop client.
        
        Returns:
            Tuple (x, y) with button coordinates or None if not found
        """
        # This is a placeholder for the actual implementation
        # In a real implementation, you would use pyautogui.locateOnScreen()
        return (500, 300)  # Example coordinates
    
    def _find_leave_button_desktop(self) -> Optional[Tuple[int, int]]:
        """
        Find the "Leave Meeting" button in the desktop client.
        
        Returns:
            Tuple (x, y) with button coordinates or None if not found
        """
        # This is a placeholder for the actual implementation
        return (800, 600)  # Example coordinates
    
    def _find_leave_confirm_button_desktop(self) -> Optional[Tuple[int, int]]:
        """
        Find the "Leave" confirmation button in the desktop client.
        
        Returns:
            Tuple (x, y) with button coordinates or None if not found
        """
        # This is a placeholder for the actual implementation
        return (500, 400)  # Example coordinates
    
    def _find_cc_button_desktop(self) -> Optional[Tuple[int, int]]:
        """
        Find the "CC" (Closed Caption) button in the desktop client.
        
        Returns:
            Tuple (x, y) with button coordinates or None if not found
        """
        # This is a placeholder for the actual implementation
        return (600, 700)  # Example coordinates
    
    def close(self) -> None:
        """
        Clean up resources (e.g., WebDriver for web client).
        """
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {str(e)}")
            finally:
                self.driver = None

# Helper function to create an instance with default settings
def create_zoom_automation(client_type: str = "web") -> ZoomAutomation:
    """
    Create and return a ZoomAutomation instance with default settings.
    
    Args:
        client_type: Type of Zoom client ('web' or 'desktop')
    
    Returns:
        Configured ZoomAutomation instance
    """
    return ZoomAutomation(client_type=client_type)