from PIL import ImageGrab
import pickle
import pyautogui
import time
from PIL import Image
import os
import sys
from datetime import datetime, timedelta
from win32com.client import Dispatch
import logging

def share_screen(server_api, logger):
    # load truncated images
    Image.MAX_IMAGE_PIXELS = None

    if server_api.is_connected and server_api.is_authenticated:
        try:
            logger.info("Sharing screen")
            screenshot = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screenshot.png'))
            screenshot.thumbnail((800, 600))
            screenshot_bytes = pickle.dumps(screenshot)
            logger.info("Sending screen shot to server")
            server_api.set_frame("screen", screenshot_bytes)
            logger.info("Screen shared")

        except Exception as e:
            logger.error("Error sharing screen: %s", e)
            
    else:
        logger.error("Not connected/auth to server")


def run_task_with_task_scheduler(script_path):
    current_time = datetime.now()
    start_time = current_time + timedelta(minutes=1)
    start_time_str = start_time.strftime('%H:%M')

    # Get the full path to the Python executable
    python_executable = sys.executable

    # Create a VBScript to run the Python script in a hidden window
    vbscript_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run_hidden.vbs')
    with open(vbscript_path, 'w') as f:
        f.write(f'CreateObject("Wscript.Shell").Run """{python_executable}"" ""{script_path}""", 0, True')
    command = f'schtasks /Create /F /SC ONCE /TN "WatchTestTask" /TR "{vbscript_path}" /ST {start_time_str} /RU "{os.getlogin()}" /IT'
    result = os.system(command)
    return result

def end_task_with_task_scheduler():
    command = 'schtasks /End /TN "WatchTestTask"'
    result = os.system(command)

    # Define the command to kill the Python process
    command = 'taskkill /IM python.exe /F'
    result = os.system(command)
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        pass
    else:
        if sys.argv[1] == "stop":
            end_task_with_task_scheduler()
        elif sys.argv[1] == "start":
            run_task_with_task_scheduler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'take_screenshot.py'))
        else:
            pass
