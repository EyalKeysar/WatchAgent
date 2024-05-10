from PIL import ImageGrab
import pickle
import pyautogui
import time
from PIL import Image
def share_screen(server_api, logger):
    while True:
        time.sleep(0.5)
        if server_api.is_connected and server_api.is_authenticated:
            try:
                logger.info("Sharing screen")
                # screenshot = ImageGrab.grab()
                # screenshot = pyautogui.screenshot()
                
                # static image for testing "./test.jpg"
                screenshot = Image.open("C:/Dev/WatchAgent/src/test.jpg")
                logger.info("Screenshot taken")
                serialized_screenshot = pickle.dumps(screenshot)
                server_api.set_stream_frame(serialized_screenshot)
            except Exception as e:
                logger.error("Error sharing screen: %s", e)
                continue
        
        else:
            logger.error("Not connected/auth to server")
            time.sleep(5)
            continue