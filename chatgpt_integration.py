"""
ChatGPT Integration Module for the Automated Zoom Poll Generator.
Uses Selenium to automate browser interactions with ChatGPT.
"""

import time
import re
import logging
from typing import Dict, Optional, Tuple
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementNotInteractableException
)

from logger import get_logger
from config import CHATGPT_URL, CHATGPT_PROMPT, WAIT_SHORT, WAIT_MEDIUM, WAIT_LONG

logger = get_logger()


class ChatGPTIntegration:
    """
    Handles integration with ChatGPT using Selenium browser automation.
    """
    
    def __init__(self):
        """Initialize the ChatGPT integration module."""
        self.driver = None
        self.is_logged_in = False
        logger.info("ChatGPT integration module initialized")
        
        # Ensure chromedriver is installed and up to date
        try:
            chromedriver_autoinstaller.install()
            logger.info("ChromeDriver installed/updated successfully")
        except Exception as e:
            logger.error(f"Error installing ChromeDriver: {str(e)}")
    
    def initialize_browser(self):
        """Initialize the Chrome browser with Selenium WebDriver."""
        logger.info("Initializing Chrome browser")
        
        try:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome browser initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Chrome browser: {str(e)}")
            return False
    
    def login_to_chatgpt(self, credentials: Dict[str, str]) -> bool:
        """
        Log in to ChatGPT using provided credentials.
        
        Args:
            credentials: Dict containing 'email' and 'password' keys
            
        Returns:
            Boolean indicating whether login was successful
        """
        if not self.driver:
            if not self.initialize_browser():
                return False
        
        logger.info("Attempting to log in to ChatGPT")
        
        try:
            # Navigate to ChatGPT
            self.driver.get(CHATGPT_URL)
            time.sleep(WAIT_MEDIUM)
            
            # Check if already logged in
            if self._check_if_already_logged_in():
                logger.info("Already logged in to ChatGPT")
                self.is_logged_in = True
                return True
            
            # Click "Log in" button if present
            try:
                login_button = WebDriverWait(self.driver, WAIT_MEDIUM).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log in')]"))
                )
                login_button.click()
                time.sleep(WAIT_SHORT)
            except TimeoutException:
                logger.info("No login button found, may already be on login page")
            
            # Enter email
            try:
                email_field = WebDriverWait(self.driver, WAIT_MEDIUM).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                email_field.clear()
                email_field.send_keys(credentials['email'])
                email_field.send_keys(Keys.RETURN)
                time.sleep(WAIT_SHORT)
            except TimeoutException:
                logger.warning("Email field not found - login flow may have changed")
                return False
            
            # Enter password
            try:
                password_field = WebDriverWait(self.driver, WAIT_MEDIUM).until(
                    EC.presence_of_element_located((By.ID, "password"))
                )
                password_field.clear()
                password_field.send_keys(credentials['password'])
                password_field.send_keys(Keys.RETURN)
                time.sleep(WAIT_MEDIUM)
            except TimeoutException:
                logger.warning("Password field not found - login flow may have changed")
                return False
            
            # Wait for login to complete and verify
            try:
                WebDriverWait(self.driver, WAIT_LONG).until(
                    EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Send a message' or @placeholder='Message ChatGPT…']"))
                )
                logger.info("Successfully logged in to ChatGPT")
                self.is_logged_in = True
                return True
            except TimeoutException:
                logger.error("Failed to log in to ChatGPT - could not find chat input")
                return False
                
        except Exception as e:
            logger.error(f"Error during ChatGPT login: {str(e)}")
            return False
    
    def generate_poll_with_chatgpt(self, transcript: str) -> Optional[Dict[str, str]]:
        """
        Generate a poll using ChatGPT by submitting the transcript and prompt.
        
        Args:
            transcript: The meeting transcript text
            
        Returns:
            Dict containing 'question' and 'options' keys, or None if generation fails
        """
        if not self.driver or not self.is_logged_in:
            logger.error("Browser not initialized or not logged in to ChatGPT")
            return None
        
        logger.info("Generating poll with ChatGPT")
        
        try:
            # Create the full prompt with transcript
            full_prompt = f"{CHATGPT_PROMPT}\n\n{transcript}"
            
            # Find and clear the chat input field
            chat_input = WebDriverWait(self.driver, WAIT_MEDIUM).until(
                EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Send a message' or @placeholder='Message ChatGPT…']"))
            )
            chat_input.clear()
            
            # Enter the prompt
            chat_input.send_keys(full_prompt)
            time.sleep(WAIT_SHORT)
            
            # Send the message (hit Enter)
            chat_input.send_keys(Keys.RETURN)
            
            # Wait for response to be generated
            logger.info("Waiting for ChatGPT to generate response...")
            
            # Wait for the loading spinner to disappear or timeout
            try:
                WebDriverWait(self.driver, WAIT_LONG).until_not(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'result-streaming')]"))
                )
            except TimeoutException:
                logger.info("Loading indicator not found or timed out")
            
            # Give a little extra time for the response to fully appear
            time.sleep(WAIT_MEDIUM)
            
            # Get the latest response from ChatGPT
            response_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'markdown')]")
            
            if not response_elements:
                logger.error("Could not find ChatGPT response element")
                return None
                
            # Get the latest response (last element)
            response_text = response_elements[-1].text
            
            if not response_text:
                logger.error("Empty response from ChatGPT")
                return None
                
            # Parse the response to extract question and options
            poll_data = self._parse_chatgpt_response(response_text)
            
            if poll_data:
                logger.info("Successfully generated and parsed poll from ChatGPT")
                return poll_data
            else:
                logger.error("Failed to parse poll data from ChatGPT response")
                logger.debug(f"Raw response: {response_text}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating poll with ChatGPT: {str(e)}")
            return None
    
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
                self.is_logged_in = False
    
    def _check_if_already_logged_in(self) -> bool:
        """
        Check if already logged in to ChatGPT.
        
        Returns:
            Boolean indicating whether already logged in
        """
        try:
            # Check if chat input field is present (indicates logged in state)
            chat_input = self.driver.find_elements(By.XPATH, "//textarea[@placeholder='Send a message' or @placeholder='Message ChatGPT…']")
            return len(chat_input) > 0
        except Exception:
            return False
    
    def _parse_chatgpt_response(self, response_text: str) -> Optional[Dict[str, str]]:
        """
        Parse the ChatGPT response to extract question and options.
        
        Args:
            response_text: Raw text response from ChatGPT
            
        Returns:
            Dict containing 'question' and 'options' list, or None if parsing fails
        """
        try:
            # Extract question using regex
            question_match = re.search(r"Question:?\s*(.+?)(?:\n|$)", response_text)
            if not question_match:
                logger.error("Could not find question in ChatGPT response")
                return None
                
            question = question_match.group(1).strip()
            
            # Extract options using regex
            option_matches = re.findall(r"Option\s*\d+:?\s*(.+?)(?:\n|$)", response_text)
            
            if len(option_matches) < 2:
                # Try alternative format (A, B, C, D)
                option_matches = re.findall(r"[A-D][.):]\s*(.+?)(?:\n|$)", response_text)
            
            if len(option_matches) < 2:
                logger.error(f"Not enough options found in ChatGPT response (found {len(option_matches)})")
                return None
                
            # Limit to 4 options
            options = option_matches[:4]
            
            return {
                "question": question,
                "options": options
            }
            
        except Exception as e:
            logger.error(f"Error parsing ChatGPT response: {str(e)}")
            return None
