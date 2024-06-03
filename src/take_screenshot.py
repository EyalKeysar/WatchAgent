import os
import sys
from PIL import ImageGrab
import logging
import time

def take_screenshot():
    try:
        screenshot = ImageGrab.grab()
        screenshot.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screenshot.png'))
    except Exception as e:
        logging.error("Error taking screenshot: %s", e)

if __name__ == "__main__":
    # use logging to log the start
    while True:
        logging.basicConfig(filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'take_screenshot.log'), level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
        take_screenshot()
        time.sleep(0.1)