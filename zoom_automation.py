"""
Zoom Automation Module for the Automated Zoom Poll Generator.
Handles direct interactions with the Zoom client using UI automation.
"""

import os
import sys
import time
import logging
import subprocess
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlparse
import psutil
import win32gui
import win32con
import win32process
import pyautogui

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
        """Initialize the Zoom automation module."""
        self.client_type = client_type.lower()
        self.meeting_id = None
        self.passcode = None
        self.display_name = None
        self.driver = None
        self.meeting_active = False
        self.zoom_window_handle = None
        
        # Initialize logger
        self.configure_logging()
        self.logger.info(f"ZoomAutomation initialized with {client_type} client type")

    def configure_logging(self):
        """Configure logging for the instance"""
        logging.basicConfig(level=logging.INFO,
                          format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def open_zoom_app(self):
        """Open Zoom application with error handling"""
        try:
            if sys.platform == 'darwin':  # macOS
                pyautogui.hotkey('command', 'space')
                pyautogui.write('zoom.us')
            else:  # Windows
                # Try direct path first
                zoom_paths = [
                    r"C:\Users\sonys\AppData\Roaming\Zoom\bin\Zoom.exe",
                    r"C:\Users\sonys\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Zoom\Zoom.lnk",
                    r"C:\Program Files\Zoom\bin\Zoom.exe",
                    r"C:\Program Files (x86)\Zoom\bin\Zoom.exe"
                ]
                
                for path in zoom_paths:
                    if os.path.exists(path):
                        self.logger.info(f"Found Zoom at {path}")
                        os.startfile(path)
                        time.sleep(2)  # Wait for launch
                        return True
                        
                # If direct paths fail, try using Run dialog
                self.logger.info("Direct paths failed, trying Run dialog...")
                pyautogui.hotkey('win', 'r')
                time.sleep(0.5)
                pyautogui.write('zoom')
                pyautogui.press('enter')
                
            time.sleep(2)  # Brief wait for initial launch
            self.logger.info("Launched Zoom application")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to open Zoom: {str(e)}")
            raise

    def _verify_zoom_window(self, timeout=10):
        """Verify Zoom window becomes active by checking for UI elements"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check for Participants button (visible in screenshot)
                participants_region = (850, 540, 150, 50)
                if pyautogui.locateOnScreen('assets/images/participants_button.png', 
                                          region=participants_region,
                                          confidence=0.8):
                    logger.info("Zoom window verified - found Participants button")
                    return True
                time.sleep(0.5)
            except Exception as e:
                logger.debug(f"Verification attempt failed: {e}")
        
        logger.warning("Could not verify Zoom window")
        return False
        
    def find_zoom_window(self) -> bool:
        """Find and activate the Zoom meeting window."""
        def enum_windows_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if "Zoom Meeting" in window_text or "Zoom" in window_text:
                    self.zoom_window_handle = hwnd
                    return False
            return True

        try:
            win32gui.EnumWindows(enum_windows_callback, None)
            if self.zoom_window_handle:
                # Bring window to front
                win32gui.ShowWindow(self.zoom_window_handle, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(self.zoom_window_handle)
                time.sleep(1)  # Give window time to activate
                return True
            return False
        except Exception as e:
            logger.error(f"Error finding Zoom window: {str(e)}")
            return False

    def _get_zoom_path(self) -> Optional[str]:
        """Get the Zoom executable path."""
        if os.name == 'nt':  # Windows
            # Use the provided Zoom path
            zoom_path = r"C:\Users\sonys\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Zoom\Zoom Workplace.lnk"
            if os.path.exists(zoom_path):
                return zoom_path
        return None

    def ensure_zoom_is_running(self) -> bool:
        """Ensure Zoom is running and find its process."""
        try:
            # First check if Zoom is already running
            zoom_running = False
            for proc in psutil.process_iter(['name']):
                if 'zoom' in proc.info['name'].lower():
                    zoom_running = True
                    break
            
            if not zoom_running:
                # Use the exact path we know works
                zoom_path = r"C:\Users\sonys\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Zoom\Zoom Workplace.lnk"
                if os.path.exists(zoom_path):
                    logger.info(f"Launching Zoom from: {zoom_path}")
                    os.startfile(zoom_path)  # Use os.startfile instead of subprocess
                    time.sleep(self.config["wait_times"]["zoom_launch"])
                else:
                    # Fallback to join URL method
                    logger.info("Using join URL method")
                    os.system('start zoommtg://zoom.us/join')
                    time.sleep(self.config["wait_times"]["zoom_launch"])
            
            # Try to find and activate the Zoom window
            def enum_windows_callback(hwnd, extra):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd).lower()
                    if 'zoom' in window_text:
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        win32gui.SetForegroundWindow(hwnd)
                        return True
                return True
            
            win32gui.EnumWindows(enum_windows_callback, None)
            return True
            
        except Exception as e:
            logger.error(f"Error ensuring Zoom is running: {str(e)}")
            return False

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
        """Leave the current Zoom meeting using UI coordinates from screenshot"""
        try:
            # Click End button at bottom right
            end_button_location = (960, 540)  # Location of End button
            pyautogui.click(end_button_location)
            time.sleep(1)
            
            # Click "Leave Meeting" in popup (coordinates from screenshot)
            leave_meeting_location = (960, 500)  # Location of Leave Meeting button
            pyautogui.click(leave_meeting_location)
            
            logger.info("Successfully left meeting")
            self.meeting_active = False
            return True
        except Exception as e:
            logger.error(f"Failed to leave meeting: {e}")
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
        """Join a Zoom meeting using the desktop client."""
        try:
            pyautogui.PAUSE = 1  # Add a 1-second pause between actions
            pyautogui.FAILSAFE = True
            
            # Step 1: Launch Zoom if not running
            logger.info("Step 1: Launching Zoom application...")
            zoom_path = r"C:\Users\sonys\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Zoom\Zoom Workplace.lnk"
            if os.path.exists(zoom_path):
                os.startfile(zoom_path)
                time.sleep(5)  # Wait for Zoom to launch
            
            # Step 2: Click Zoom icon in taskbar
            logger.info("Step 2: Clicking Zoom taskbar icon...")
            zoom_pos = self.locate_zoom_icon()
            pyautogui.click(zoom_pos)
            time.sleep(3)  # Increased wait time to ensure window appears
            
            # Step 3: Click Join Meeting button
            logger.info("Step 3: Clicking Join Meeting button...")
            pyautogui.click(x=1107, y=423)  # Coordinates for Join Meeting button
            time.sleep(2)
            
            # Rest of the steps for entering meeting ID and passcode
            logger.info("Step 4: Entering Meeting ID...")
            pyperclip.copy(self.meeting_id)
            time.sleep(1)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(2)
            
            logger.info("Step 5: Entering Passcode...")
            pyperclip.copy(self.passcode)
            time.sleep(1)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(1)
            pyautogui.press('enter')
            
            # Final verification
            logger.info("Step 6: Verifying meeting join...")
            time.sleep(5)  # Wait for meeting interface
            
            join_success = False
            for control in ['assets/mic_button.png', 'assets/participants_button.png']:
                try:
                    if pyautogui.locateOnScreen(control, confidence=0.8, grayscale=True):
                        join_success = True
                        break
                except Exception:
                    continue
            
            if join_success:
                self.meeting_active = True
                logger.info("Successfully joined meeting")
                return True
            else:
                logger.warning("Could not verify successful meeting join")
                return False
            
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
            # Look for the end meeting button
            end_button = pyautogui.locateOnScreen('assets/end_button.png', confidence=0.8)
            if not end_button:
                logger.warning("Could not find End Meeting button")
                return False
            
            # Click the end button
            pyautogui.click(pyautogui.center(end_button))
            time.sleep(1)
            
            # Look for and click the confirm end button if it appears
            confirm_button = pyautogui.locateOnScreen('assets/confirm_end_button.png', confidence=0.8)
            if confirm_button:
                pyautogui.click(pyautogui.center(confirm_button))
            
            # Wait for meeting to close
            time.sleep(3)
            
            self.meeting_active = False
            return True
            
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
            # Look for meeting control buttons to verify we're in a meeting
            controls = [
                'assets/mic_button.png',
                'assets/participants_button.png',
                'assets/polls_quizzes_button.jpg'
            ]
            
            for control in controls:
                if pyautogui.locateOnScreen(control, confidence=0.8):
                    return True
            
            return False
            
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
    
    def locate_zoom_icon(self):
        """Locate the Zoom icon on screen using multiple image variants"""
        icon_variants = [
            ('assets/images/zoom_icon_taskbar.png', 0.8),
            ('assets/images/zoom_icon_desktop.png', 0.8),
            ('assets/images/zoom_icon_start.png', 0.8)
        ]
        
        for img_path, confidence in icon_variants:
            try:
                pos = pyautogui.locateCenterOnScreen(img_path, confidence=confidence)
                if pos:
                    logger.info(f"Found Zoom icon using {img_path}")
                    return pos
            except Exception as e:
                logger.debug(f"Failed to find {img_path}: {e}")
                continue
        
        logger.warning("Could not find Zoom icon, using fallback coordinates")
        return (1039, 1056)
    
    def click_join_meeting(self):
        """Clicks the 'Join' button and handles the meeting ID input"""
        try:
            # Method 1: Try image recognition with high confidence
            self.logger.info("Attempting to find join button using image recognition...")
            join_button = None
            
            try:
                join_button = pyautogui.locateOnScreen(
                    'assets/images/zoom_join_meeting_button.png',
                    confidence=0.8
                )
                if join_button:
                    self.logger.info(f"Found join button at {join_button}")
                    pyautogui.click(pyautogui.center(join_button))
                    time.sleep(1)
                    return True
            except Exception as img_error:
                self.logger.debug(f"Image recognition attempt failed: {img_error}")

            # Method 2: Try with lower confidence
            try:
                self.logger.info("Trying with lower confidence threshold...")
                join_button = pyautogui.locateOnScreen(
                    'assets/images/zoom_join_meeting_button.png',
                    confidence=0.6
                )
                if join_button:
                    self.logger.info(f"Found join button with lower confidence at {join_button}")
                    pyautogui.click(pyautogui.center(join_button))
                    time.sleep(1)
                    return True
            except Exception as img_error:
                self.logger.debug(f"Lower confidence attempt failed: {img_error}")

            # Method 3: Try common coordinates
            self.logger.info("Trying predefined coordinates...")
            common_coords = [
                (1107, 423),  # Original coordinate
                (850, 480),   # Alternative 1
                (960, 540),   # Center of 1920x1080 screen
                (480, 270)    # Center of 960x540 screen
            ]
            
            for x, y in common_coords:
                try:
                    self.logger.info(f"Trying coordinates ({x}, {y})")
                    pyautogui.moveTo(x, y, duration=0.5)
                    # Check if the pixel color matches the typical Zoom blue
                    if pyautogui.pixelMatchesColor(x, y, (0, 122, 255), tolerance=30):
                        pyautogui.click(x, y)
                        self.logger.info(f"Successfully clicked join button at ({x}, {y})")
                        time.sleep(1)
                        return True
                except Exception as coord_error:
                    self.logger.debug(f"Coordinate attempt ({x}, {y}) failed: {coord_error}")
                    continue

            # If we get here, all methods failed
            self.logger.error("All attempts to find join button failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to click Join button: {str(e)}")
            return False
    
    def _find_join_button_desktop(self) -> Optional[Tuple[int, int]]:
        """
        Find the "Join a Meeting" button in the desktop client.
        
        Returns:
            Tuple (x, y) with button coordinates or None if not found
        """
        try:
            # Try to locate the Join Meeting button image
            location = pyautogui.locateOnScreen('assets/join_button.png', confidence=0.8)
            if location:
                return pyautogui.center(location)
            
            # Fallback to direct click if image not found
            # These coordinates are for a typical 1920x1080 screen
            return (960, 540)  # Center of screen
        except Exception as e:
            logger.error(f"Error finding join button: {str(e)}")
            return None
    
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
    
    def get_current_mouse_position(self):
        """Get the current mouse position for coordinate calibration."""
        try:
            while True:
                x, y = pyautogui.position()
                logger.info(f"Current mouse position: x={x}, y={y}")
                time.sleep(1)  # Update every second
        except KeyboardInterrupt:
            logger.info("Coordinate capture stopped")
    
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

    def configure_logging(self):
        logging.basicConfig(level=logging.INFO,
                          format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def wait_for_element(self, image_path: str, timeout: int = 10, confidence: float = 0.8) -> Optional[tuple]:
        """Wait for an element to appear on screen and return its position"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
                if location:
                    return location
            except Exception as e:
                self.logger.debug(f"Error locating element: {e}")
            time.sleep(0.5)
        return None

    def click_element(self, image_path: str, retries: int = 3) -> bool:
        """Click an element with retry mechanism"""
        for attempt in range(retries):
            location = self.wait_for_element(image_path)
            if location:
                pyautogui.click(location)
                self.logger.info(f"Successfully clicked element: {image_path}")
                return True
            self.logger.warning(f"Attempt {attempt + 1}/{retries} failed to find element: {image_path}")
        return False

    def open_zoom_and_click_join(self):
        """Ensures Zoom is open, then clicks the 'Join Meeting' button with proper error handling"""
        try:
            self.open_zoom_app()
            # Wait for Zoom to fully load and become interactive
            time.sleep(3)  # Keep minimal initial wait
            self.click_join_meeting()
            return True
        except Exception as e:
            self.logger.error(f"Failed to complete Zoom joining process: {e}")
            return False

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