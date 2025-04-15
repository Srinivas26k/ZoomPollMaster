"""
ChatGPT Integration Module for the Automated Zoom Poll Generator.
Uses Selenium to automate browser interactions with ChatGPT.
"""

import os
import time
import json
import logging
from typing import Dict, Any, Optional, List

import chromedriver_autoinstaller
import selenium
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

# Configure logger
logger = logging.getLogger(__name__)

class ChatGPTIntegration:
    """
    Handles integration with ChatGPT using Selenium browser automation.
    Direct browser automation without using OpenAI API.
    """
    
    def __init__(self):
        """Initialize the ChatGPT integration module."""
        self.driver = None
        self.is_logged_in = False
        self.prompt_template = """Based on the transcript below from a Zoom meeting, generate one engaging poll question with exactly four answer options. Format your response as a JSON object with "question" and "options" keys, where "options" is a list of four answer choices. The poll should be relevant to the content discussed in the transcript and encourage participation.

Transcript:
{transcript}

Response format:
{
  "question": "Your poll question here?",
  "options": [
    "Option A",
    "Option B",
    "Option C",
    "Option D"
  ]
}
"""
        logger.info("ChatGPTIntegration initialized")
    
    def initialize_browser(self) -> bool:
        """
        Initialize the Chrome browser with Selenium WebDriver.
        
        Returns:
            Boolean indicating whether initialization was successful
        """
        logger.info("Initializing browser for ChatGPT interaction")
        
        try:
            # Auto-install ChromeDriver
            chromedriver_autoinstaller.install()
            
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-notifications")
            
            # Add headless option if in a server environment
            if self._is_server_environment():
                logger.info("Running in server environment, using headless mode")
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Initialize WebDriver
            self.driver = selenium.webdriver.Chrome(options=chrome_options)
            
            logger.info("Browser initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            self.driver = None
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
            logger.error("Browser not initialized - call initialize_browser() first")
            return False
        
        # Check if credentials are provided
        if not credentials or 'email' not in credentials or 'password' not in credentials:
            logger.error("Invalid credentials provided")
            return False
        
        logger.info("Attempting to log in to ChatGPT")
        
        try:
            # Check if already logged in
            if self._check_if_already_logged_in():
                logger.info("Already logged in to ChatGPT")
                self.is_logged_in = True
                return True
            
            # Navigate to ChatGPT login page
            self.driver.get("https://chat.openai.com/auth/login")
            
            # Wait for the login button to appear
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log in')]"))
            )
            
            # Click the login button
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Log in')]")
            login_button.click()
            
            # Wait for email input field
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            
            # Enter email
            email_input = self.driver.find_element(By.ID, "username")
            email_input.clear()
            email_input.send_keys(credentials['email'])
            email_input.send_keys(Keys.RETURN)
            
            # Wait for password input field
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            
            # Enter password
            password_input = self.driver.find_element(By.ID, "password")
            password_input.send_keys(credentials['password'])
            password_input.send_keys(Keys.RETURN)
            
            # Wait for ChatGPT interface to load
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".text-input"))
            )
            
            logger.info("Successfully logged in to ChatGPT")
            self.is_logged_in = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to log in to ChatGPT: {str(e)}")
            return False
    
    def generate_poll_with_chatgpt(self, transcript: str) -> Optional[Dict[str, Any]]:
        """
        Generate a poll using ChatGPT by submitting the transcript and prompt.
        
        Args:
            transcript: The meeting transcript text
            
        Returns:
            Dict containing 'question' and 'options' keys, or None if generation fails
        """
        if not self.driver:
            logger.error("Browser not initialized - call initialize_browser() first")
            return None
        
        if not self.is_logged_in:
            logger.error("Not logged in to ChatGPT - call login_to_chatgpt() first")
            return None
        
        logger.info("Generating poll with ChatGPT")
        
        try:
            # Prepare the prompt with the transcript
            prompt = self.prompt_template.format(transcript=transcript)
            
            # Navigate to ChatGPT if not already there
            if "chat.openai.com" not in self.driver.current_url:
                self.driver.get("https://chat.openai.com/")
                time.sleep(2)
            
            # Clear any existing conversation by starting a new chat
            try:
                new_chat_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'New chat')]")
                new_chat_button.click()
                time.sleep(1)
            except NoSuchElementException:
                logger.warning("Could not find 'New chat' button, continuing with current chat")
            
            # Find the input field
            input_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".text-input"))
            )
            
            # If the transcript is very long, split it into chunks
            chunks = self._chunk_text(prompt) if len(prompt) > 12000 else [prompt]
            
            # Send each chunk
            for i, chunk in enumerate(chunks):
                # Clear the input field
                input_box.clear()
                
                # Type the chunk
                input_box.send_keys(chunk)
                
                # If this is the last chunk, send it
                if i == len(chunks) - 1:
                    # Send the prompt
                    input_box.send_keys(Keys.CONTROL + Keys.RETURN)  # Use Ctrl+Enter to submit
                    
                    # Wait for response
                    logger.info("Waiting for ChatGPT response")
                    time.sleep(5)  # Initial wait
                    
                    # Wait for response to complete (check for the "Regenerate" button)
                    WebDriverWait(self.driver, 60).until(
                        EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Regenerate')]"))
                    )
                    
                    # Give a moment for the response to fully render
                    time.sleep(2)
                    
                    # Find and extract the response
                    response_elements = self.driver.find_elements(By.CSS_SELECTOR, ".markdown")
                    
                    if not response_elements:
                        logger.error("Could not find ChatGPT response")
                        return None
                    
                    # Get the last response (most recent)
                    response_text = response_elements[-1].text
                    
                    # Parse the response to extract the poll question and options
                    poll_data = self._parse_chatgpt_response(response_text)
                    
                    if poll_data:
                        logger.info(f"Successfully generated poll: {poll_data['question']}")
                        return poll_data
                    else:
                        logger.error("Failed to parse ChatGPT response")
                        return None
                else:
                    # For intermediate chunks, just send and wait briefly
                    input_box.send_keys(Keys.CONTROL + Keys.RETURN)
                    time.sleep(3)  # Wait for chunk to be processed
                    
                    # Clear the input field for the next chunk
                    input_box = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".text-input"))
                    )
            
            logger.error("No response generated")
            return None
            
        except Exception as e:
            logger.error(f"Error generating poll with ChatGPT: {str(e)}")
            return None
    
    def close_browser(self):
        """Close the browser and clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed successfully")
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
            # Navigate to ChatGPT
            self.driver.get("https://chat.openai.com/")
            
            # Wait a moment for the page to load
            time.sleep(3)
            
            # Check if we're on the login page or already in the chat interface
            if "auth/login" in self.driver.current_url:
                return False
            
            # Try to find elements that would indicate we're logged in
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".text-input"))
                )
                return True
            except TimeoutException:
                return False
                
        except Exception as e:
            logger.error(f"Error checking login status: {str(e)}")
            return False
    
    def _parse_chatgpt_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse the ChatGPT response to extract question and options.
        
        Args:
            response_text: Raw text response from ChatGPT
            
        Returns:
            Dict containing 'question' and 'options' list, or None if parsing fails
        """
        try:
            logger.info("Parsing ChatGPT response")
            
            # Try to extract JSON from the response
            # Look for text between ```json and ``` markers
            json_pattern = r'```(?:json)?\s*({[\s\S]*?})\s*```'
            import re
            json_matches = re.findall(json_pattern, response_text)
            
            if json_matches:
                # Use the first match
                json_str = json_matches[0]
                poll_data = json.loads(json_str)
                
                # Validate required keys
                if 'question' in poll_data and 'options' in poll_data:
                    # Ensure options is a list with at least 2 items
                    if isinstance(poll_data['options'], list) and len(poll_data['options']) >= 2:
                        return {
                            'question': poll_data['question'],
                            'options': poll_data['options']
                        }
            
            # If JSON extraction failed, try manual parsing
            logger.warning("JSON extraction failed, attempting manual parsing")
            
            # Look for lines that might be the question (ends with ?)
            lines = response_text.split('\n')
            question = None
            options = []
            
            for line in lines:
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # If we haven't found a question yet and this line ends with ?, it might be our question
                if not question and line.endswith('?'):
                    question = line
                
                # If line starts with a number and period (1., 2., etc.) or letter and period (A., B., etc.)
                # or dash/bullet point, it might be an option
                elif re.match(r'^(\d+\.|\w\.|-|\*)\s+', line):
                    # Extract the text after the marker
                    option_text = re.sub(r'^(\d+\.|\w\.|-|\*)\s+', '', line)
                    options.append(option_text)
            
            # If we found both a question and at least 2 options, return them
            if question and len(options) >= 2:
                return {
                    'question': question,
                    'options': options
                }
            
            logger.error("Failed to parse response manually")
            return None
            
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON in ChatGPT response")
            return None
        except Exception as e:
            logger.error(f"Error parsing ChatGPT response: {str(e)}")
            return None
    
    def _is_server_environment(self) -> bool:
        """
        Detect if running in a server environment.
        
        Returns:
            Boolean indicating whether running in a server/CI environment
        """
        # Check common environment variables that indicate a server environment
        server_env_vars = ['CI', 'JENKINS_URL', 'TRAVIS', 'CIRCLECI', 'GITHUB_ACTIONS', 'GITLAB_CI']
        for var in server_env_vars:
            if os.environ.get(var):
                return True
        
        # Check if DISPLAY is set (Linux GUI)
        if os.name == 'posix' and not os.environ.get('DISPLAY'):
            return True
        
        return False
    
    def _chunk_text(self, text, chunk_size=1000):
        """
        Split long text into manageable chunks.
        
        Args:
            text: The text to chunk
            chunk_size: Maximum size of each chunk
            
        Returns:
            List of text chunks
        """
        chunks = []
        current_chunk = ""
        
        # Split by lines to avoid breaking in the middle of a line
        lines = text.split('\n')
        
        for line in lines:
            # If adding this line would exceed chunk size and we already have content
            if len(current_chunk) + len(line) + 1 > chunk_size and current_chunk:
                chunks.append(current_chunk)
                current_chunk = line + '\n'
            else:
                current_chunk += line + '\n'
        
        # Add the last chunk if it has content
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks

# Helper function to create an instance
def create_chatgpt_integration() -> ChatGPTIntegration:
    """
    Create and return a ChatGPTIntegration instance.
    
    Returns:
        ChatGPTIntegration instance
    """
    return ChatGPTIntegration()