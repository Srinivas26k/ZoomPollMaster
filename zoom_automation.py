"""
Zoom Automation Module for the Automated Zoom Poll Generator.
Handles joining meetings and automating Zoom interactions.
"""

import time
import logging
import os
import re
import subprocess
import platform
from typing import Dict, Optional, Tuple, Union
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from logger import get_logger
from config import ZOOM_WEB_URL, WAIT_SHORT, WAIT_MEDIUM, WAIT_LONG

logger = get_logger()


class ZoomAutomation:
    """
    Handles automation of Zoom meetings, including joining, leaving,
    and various interactions within the meeting.
    """
    
    def __init__(self, zoom_client_type="web"):
        """
        Initialize the Zoom automation module.
        
        Args:
            zoom_client_type: Type of Zoom client ("desktop" or "web")
        """
        self.zoom_client_type = zoom_client_type
        self.driver = None
        self.meeting_active = False
        logger.info(f"Zoom automation module initialized for {zoom_client_type} client")
    
    def initialize_browser(self):
        """Initialize the Chrome browser with Selenium WebDriver for web client."""
        if self.driver:
            return True
            
        logger.info("Initializing Chrome browser for Zoom Web Client")
        
        try:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-notifications")
            
            # Add required permissions for media
            chrome_options.add_argument("--use-fake-ui-for-media-stream")
            chrome_options.add_argument("--use-fake-device-for-media-stream")
            
            # Headless mode for server environments
            if self._is_server_environment():
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Initialize browser
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome browser initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Chrome browser: {str(e)}")
            return False
    
    def join_meeting_web(self, meeting_id: str, passcode: str, display_name: str = "Poll Generator") -> bool:
        """
        Join a Zoom meeting using the web client.
        
        Args:
            meeting_id: The Zoom meeting ID
            passcode: The meeting passcode
            display_name: Name to display in the meeting
            
        Returns:
            Boolean indicating whether joining was successful
        """
        if not self.initialize_browser():
            logger.error("Failed to initialize browser for Zoom Web Client")
            return False
            
        try:
            # Format meeting ID (remove spaces and dashes)
            meeting_id = meeting_id.replace(" ", "").replace("-", "")
            
            # Navigate to Zoom join page
            join_url = f"{ZOOM_WEB_URL}/{meeting_id}"
            logger.info(f"Navigating to Zoom join page: {join_url}")
            self.driver.get(join_url)
            
            # Wait for page to load
            time.sleep(WAIT_MEDIUM)
            
            # Enter display name if prompted
            try:
                name_input = WebDriverWait(self.driver, WAIT_MEDIUM).until(
                    EC.presence_of_element_located((By.ID, "inputname"))
                )
                name_input.clear()
                name_input.send_keys(display_name)
                logger.info(f"Entered display name: {display_name}")
            except TimeoutException:
                logger.info("Name input not found or not required")
            
            # Join meeting button
            try:
                join_button = WebDriverWait(self.driver, WAIT_MEDIUM).until(
                    EC.element_to_be_clickable((By.ID, "joinBtn"))
                )
                join_button.click()
                logger.info("Clicked join button")
            except TimeoutException:
                logger.error("Join button not found or not clickable")
                return False
            
            # Enter passcode if prompted
            try:
                passcode_input = WebDriverWait(self.driver, WAIT_MEDIUM).until(
                    EC.presence_of_element_located((By.ID, "inputpasscode"))
                )
                passcode_input.clear()
                passcode_input.send_keys(passcode)
                
                # Click the submit button for the passcode
                passcode_submit = WebDriverWait(self.driver, WAIT_SHORT).until(
                    EC.element_to_be_clickable((By.ID, "passcodeSubmit"))
                )
                passcode_submit.click()
                logger.info("Entered passcode")
            except TimeoutException:
                logger.info("Passcode input not found or not required")
            
            # Handle browser permission prompts
            time.sleep(WAIT_MEDIUM)
            
            # Wait for meeting to join (look for meeting controls)
            try:
                WebDriverWait(self.driver, WAIT_LONG*2).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "footer__btns-container"))
                )
                logger.info("Successfully joined meeting via web client")
                self.meeting_active = True
                return True
            except TimeoutException:
                logger.error("Failed to detect meeting join - meeting controls not found")
                return False
                
        except Exception as e:
            logger.error(f"Error joining meeting via web client: {str(e)}")
            return False
    
    def join_meeting_desktop(self, meeting_id: str, passcode: str, display_name: str = "Poll Generator") -> bool:
        """
        Join a Zoom meeting using the desktop client.
        
        Args:
            meeting_id: The Zoom meeting ID
            passcode: The meeting passcode
            display_name: Name to display in the meeting
            
        Returns:
            Boolean indicating whether joining was successful
        """
        logger.info(f"Attempting to join meeting {meeting_id} via desktop client")
        
        try:
            # Format meeting ID (remove spaces and dashes)
            meeting_id = meeting_id.replace(" ", "").replace("-", "")
            
            # Construct the zoom: URL to launch the desktop client
            zoom_url = f"zoommtg://zoom.us/join?confno={meeting_id}&pwd={passcode}&zc=0&browser=chrome&uname={display_name}"
            
            # Use platform-specific methods to open the URL
            os_type = platform.system()
            
            if os_type == "Windows":
                subprocess.Popen(['start', '', zoom_url], shell=True)
            elif os_type == "Darwin":  # macOS
                subprocess.Popen(['open', zoom_url])
            else:  # Linux and others
                subprocess.Popen(['xdg-open', zoom_url])
                
            logger.info(f"Launched Zoom desktop client for meeting {meeting_id}")
            
            # Wait some time for the client to launch
            time.sleep(WAIT_LONG)
            
            # We can't easily verify if join was successful with the desktop client
            # without UI automation, so we'll assume it launched correctly
            self.meeting_active = True
            return True
            
        except Exception as e:
            logger.error(f"Error joining meeting via desktop client: {str(e)}")
            return False
    
    def join_meeting(self, meeting_id: str, passcode: str, display_name: str = "Poll Generator") -> bool:
        """
        Join a Zoom meeting using the configured client type.
        
        Args:
            meeting_id: The Zoom meeting ID
            passcode: The meeting passcode
            display_name: Name to display in the meeting
            
        Returns:
            Boolean indicating whether joining was successful
        """
        if self.zoom_client_type == "web":
            return self.join_meeting_web(meeting_id, passcode, display_name)
        elif self.zoom_client_type == "desktop":
            return self.join_meeting_desktop(meeting_id, passcode, display_name)
        else:
            logger.error(f"Unsupported Zoom client type: {self.zoom_client_type}")
            return False
    
    def leave_meeting(self) -> bool:
        """
        Leave the current Zoom meeting.
        
        Returns:
            Boolean indicating whether leaving was successful
        """
        if not self.meeting_active:
            logger.warning("No active meeting to leave")
            return True
            
        try:
            if self.zoom_client_type == "web" and self.driver:
                # Look for the leave button in the footer
                try:
                    leave_button = WebDriverWait(self.driver, WAIT_MEDIUM).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Leave')]"))
                    )
                    leave_button.click()
                    
                    # Confirm leaving
                    try:
                        confirm_button = WebDriverWait(self.driver, WAIT_MEDIUM).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Leave Meeting')]"))
                        )
                        confirm_button.click()
                    except TimeoutException:
                        logger.info("No leave confirmation dialog found")
                    
                    logger.info("Left meeting successfully via web client")
                    
                except TimeoutException:
                    logger.warning("Leave button not found - meeting may have already ended")
                
                # Close the browser to ensure we're fully out of the meeting
                self.close_browser()
                
            else:  # Desktop client - can't easily automate leaving
                logger.info("Note: For desktop client, please manually leave the meeting")
                
            self.meeting_active = False
            return True
            
        except Exception as e:
            logger.error(f"Error leaving meeting: {str(e)}")
            return False
    
    def enable_closed_captioning(self) -> bool:
        """
        Enable closed captioning in the meeting if available.
        
        Returns:
            Boolean indicating whether the operation was successful
        """
        if not self.meeting_active:
            logger.warning("No active meeting")
            return False
            
        try:
            if self.zoom_client_type == "web" and self.driver:
                # Look for CC button in meeting controls
                try:
                    cc_button = WebDriverWait(self.driver, WAIT_MEDIUM).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Caption') or contains(@aria-label, 'cc')]"))
                    )
                    cc_button.click()
                    logger.info("Enabled closed captioning")
                    return True
                except TimeoutException:
                    logger.warning("Closed captioning button not found - may not be available")
                    return False
                    
            else:  # Desktop client
                logger.warning("Closed captioning automation not supported for desktop client")
                return False
                
        except Exception as e:
            logger.error(f"Error enabling closed captioning: {str(e)}")
            return False
    
    def check_meeting_status(self) -> bool:
        """
        Check if still connected to the meeting.
        
        Returns:
            Boolean indicating whether still in a meeting
        """
        if not self.meeting_active:
            return False
            
        try:
            if self.zoom_client_type == "web" and self.driver:
                # Check for meeting controls element to verify we're still in the meeting
                try:
                    controls = self.driver.find_elements(By.CLASS_NAME, "footer__btns-container")
                    return len(controls) > 0
                except:
                    return False
            else:
                # For desktop client, we can't easily check - assume still in meeting
                return True
                
        except Exception as e:
            logger.error(f"Error checking meeting status: {str(e)}")
            return False
    
    def close_browser(self):
        """Close the browser and clean up resources."""
        if self.driver:
            logger.info("Closing browser")
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Error closing browser: {str(e)}")
            finally:
                self.driver = None
                self.meeting_active = False
    
    def set_zoom_client_type(self, client_type: str):
        """
        Change the Zoom client type.
        
        Args:
            client_type: "desktop" or "web"
        """
        if client_type not in ["desktop", "web"]:
            logger.error(f"Invalid Zoom client type: {client_type}")
            return
            
        # Clean up resources if changing client type
        if self.zoom_client_type != client_type and self.driver:
            self.close_browser()
            
        self.zoom_client_type = client_type
        logger.info(f"Zoom client type changed to {client_type}")
    
    def _is_server_environment(self) -> bool:
        """
        Detect if running in a server environment.
        
        Returns:
            Boolean indicating whether running in a server/CI environment
        """
        # Check common environment variables set in server/CI environments
        return any([
            os.environ.get('CI') == 'true',
            os.environ.get('REPLIT') == 'true',
            os.environ.get('GITHUB_ACTIONS') == 'true',
            os.environ.get('GITLAB_CI') == 'true',
            os.environ.get('TRAVIS') == 'true',
            os.environ.get('JENKINS_URL') is not None,
        ])