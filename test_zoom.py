import logging
import pyautogui
from zoom_automation import ZoomAutomation
import time

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

def test_zoom_automation():
    try:
        # Initialize ZoomAutomation with desktop client
        zoom = ZoomAutomation(client_type="desktop")
        logging.info("Step 1: Opening Zoom application...")
        zoom.open_zoom_app()
        time.sleep(3)  # Wait for Zoom to fully load
        logging.info("Successfully opened Zoom")

        # Step 2: Click join button and handle meeting ID input
        logging.info("Step 2: Clicking join button...")
        if zoom.click_join_meeting():
            logging.info("Successfully clicked join button")
            
            # Test meeting ID
            test_meeting_id = "88646363911"
            test_passcode = "password123"
            
            # Type meeting ID
            logging.info("Step 3: Entering meeting ID...")
            time.sleep(1)  # Wait for input box to be ready
            pyautogui.write(test_meeting_id)
            pyautogui.press('enter')
            time.sleep(2)  # Wait for passcode screen
            
            # Type passcode
            logging.info("Step 4: Entering passcode...")
            pyautogui.write(test_passcode)
            pyautogui.press('enter')
            
            logging.info("Test completed with meeting ID and passcode entry")
        else:
            logging.error("Failed to click join button")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
    finally:
        logging.info("Test completed")

if __name__ == "__main__":
    test_zoom_automation()
