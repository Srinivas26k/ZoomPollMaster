"""
Configuration settings for the Automated Zoom Poll Generator.
"""

import os
from pathlib import Path

# Application settings
APP_NAME = "Automated Zoom Poll Generator"
APP_VERSION = "1.0.0"

# Deployment mode - set to True to enable web interface, False for desktop app
WEB_MODE = True

# Zoom client type - "desktop" or "web"
DEFAULT_ZOOM_CLIENT = "desktop"

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

# Web URLs
CHATGPT_URL = "https://chat.openai.com/"
ZOOM_WEB_URL = "https://zoom.us/wc/"

# Selenium WebDriver
CHROME_DRIVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chromedriver")

# Default window sizes
DEFAULT_WINDOW_WIDTH = 1280
DEFAULT_WINDOW_HEIGHT = 800

# Credential security
CREDENTIAL_TIMEOUT = 30 * 60  # 30 minutes in seconds before credentials are cleared from memory

# Web server settings
SERVER_HOST = '0.0.0.0'
SERVER_PORT = int(os.environ.get("PORT", 5000))
DEBUG_MODE = True

# Web interface endpoints
LOGIN_ENDPOINT = '/login'
CHATGPT_SETUP_ENDPOINT = '/chatgpt_setup'
DASHBOARD_ENDPOINT = '/'

# Zoom web client DOM elements (for Web Client automation)
ZOOM_WEB_MEETING_ID_INPUT = "//input[@id='join-confno']"
ZOOM_WEB_MEETING_PASSWORD_INPUT = "//input[@id='join-pwd']"
ZOOM_WEB_JOIN_BUTTON = "//button[contains(text(), 'Join')]"

# Default file paths for UI automation image recognition
IMAGE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
POLL_BUTTON_IMAGE = os.path.join(IMAGE_FOLDER, "poll_button.png")
TRANSCRIPT_BUTTON_IMAGE = os.path.join(IMAGE_FOLDER, "transcript_button.png")
LAUNCH_POLL_IMAGE = os.path.join(IMAGE_FOLDER, "launch_poll.png")

# Create image folder if it doesn't exist
if not os.path.exists(IMAGE_FOLDER):
    try:
        os.makedirs(IMAGE_FOLDER)
    except OSError:
        pass