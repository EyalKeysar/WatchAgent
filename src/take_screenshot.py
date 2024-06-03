import os
import sys
from PIL import ImageGrab
import logging
import time

TIME_INTERVAL = 0.3

def take_screenshot():
    try:
        screenshot = ImageGrab.grab()
        screenshot.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screenshot.png'))
    except Exception as e:
        logging.error("Error taking screenshot: %s", e)

if __name__ == "__main__":
    logging.basicConfig(filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'take_screenshot.log'), level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    logging.info("Starting take_screenshot")
    while True:
        logging.basicConfig(filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'take_screenshot.log'), level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
        try:
            take_screenshot()
        except Exception as e:
            logging.error("Error taking screenshot: %s", e)

        time.sleep(TIME_INTERVAL)
