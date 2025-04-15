import logging
import pyautogui
from zoom_automation import ZoomAutomation
import time

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

def wait_for_button(image_path, timeout=10, confidence=0.7):
    """Helper function to wait for and find a button"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            button = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if button:
                return button
        except Exception:
            pass
        time.sleep(0.5)
    return None

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
            
            # Real meeting ID
            test_meeting_id = "84795972782"
            
            # Step 3: Wait for and enter meeting ID
            logging.info("Step 3: Waiting for meeting ID input box...")
            time.sleep(2)  # Wait for input box to be fully ready
            
            # Verify meeting ID input box is visible
            meeting_id_box = wait_for_button('assets/images/zoom_meeting_id_dialog_box.png')
            if meeting_id_box:
                logging.info("Found meeting ID input box")
                pyautogui.click(pyautogui.center(meeting_id_box))
                time.sleep(1)
                
                # Type meeting ID
                logging.info("Entering meeting ID...")
                pyautogui.write(test_meeting_id)
                time.sleep(1)
                
                # Press Enter after entering meeting ID
                logging.info("Pressing Enter after ID entry...")
                pyautogui.press('enter')
                time.sleep(2)  # Wait for the join button to appear
                
                # Click join button after entering ID
                logging.info("Step 4: Looking for secondary join button...")
                secondary_join = wait_for_button('assets/images/zoom_secondary_join_button.png', timeout=5)
                
                if secondary_join:
                    logging.info("Found secondary join button, clicking...")
                    button_center = pyautogui.center(secondary_join)
                    pyautogui.moveTo(button_center, duration=0.5)
                    pyautogui.click(button_center)
                    logging.info("Successfully clicked secondary join button")
                    time.sleep(2)  # Wait for any potential password prompt
                else:
                    # Try alternative method - press Enter again
                    logging.info("Secondary join button not found, trying Enter key...")
                    pyautogui.press('enter')
                    time.sleep(2)
            else:
                logging.error("Could not find meeting ID input box")
        else:
            logging.error("Failed to click initial join button")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
    finally:
        logging.info("Test completed")

if __name__ == "__main__":
    test_zoom_automation()
