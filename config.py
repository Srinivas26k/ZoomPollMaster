"""
Configuration settings for the Automated Zoom Poll Generator.
"""

import os
from pathlib import Path

# Application settings
APP_NAME = "Automated Zoom Poll Generator"
APP_VERSION = "1.0.0"

# Logging settings
LOG_FOLDER = Path.home() / "ZoomPollGenerator_Logs"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"  # Can be DEBUG, INFO, WARNING, ERROR, CRITICAL

# Scheduler settings
TRANSCRIPT_CAPTURE_INTERVAL = 10 * 60  # 10 minutes in seconds
POLL_POSTING_INTERVAL = 15 * 60  # 15 minutes in seconds

# UI Automation
# Wait times (in seconds)
WAIT_SHORT = 1
WAIT_MEDIUM = 3
WAIT_LONG = 10

# ChatGPT Prompt
CHATGPT_PROMPT = """Based on the transcript below, generate one poll question with four engaging answer options. 
Format your response as follows:
Question: [Your question here]
Option 1: [First option]
Option 2: [Second option]
Option 3: [Third option]
Option 4: [Fourth option]

Here's the transcript:
"""

# Selenium WebDriver
CHROME_DRIVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chromedriver")
CHATGPT_URL = "https://chat.openai.com/"

# Default window sizes
DEFAULT_WINDOW_WIDTH = 1280
DEFAULT_WINDOW_HEIGHT = 800

# Credential security
CREDENTIAL_TIMEOUT = 30 * 60  # 30 minutes in seconds before credentials are cleared from memory
