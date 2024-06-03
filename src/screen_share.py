from PIL import ImageGrab
import pickle
import pyautogui
import time
from PIL import Image
import os
import sys
from datetime import datetime, timedelta
from win32com.client import Dispatch

# def share_screen(server_api, logger):
#     # load truncated images
#     Image.MAX_IMAGE_PIXELS = None

#     if server_api.is_connected and server_api.is_authenticated:
#         try:
#             logger.info("Sharing screen")
#             # # imgae placeholder test.jpg
#             # screenshot = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.png'))
#             # # screenshot = ImageGrab.grab()
#             # screenshot.thumbnail((800, 600))
#             # screenshot_bytes = pickle.dumps(screenshot)
#             # logger.info("Sending screen shot to server")
#             # server_api.set_frame("screen", screenshot_bytes)
#             # logger.info("Screen shared")

#             # use windows task scheduler to take a screenshot because it currently not in window interactive session

#             script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'take_screenshot.py')
#             create_task(script_path)
#             logger.info("Task created to take screenshot")


#         except Exception as e:
#             logger.error("Error sharing screen: %s", e)
            
#     else:
#         logger.error("Not connected/auth to server")



def run_task_with_task_scheduler(script_path):
    # Get the current time
    current_time = datetime.now()

    # Add a minute to the current time
    start_time = current_time + timedelta(minutes=1)

    # Format the start time in 24-hour format
    start_time_str = start_time.strftime('%H:%M')

    # Get the full path to the Python executable
    python_executable = sys.executable

    # Create a VBScript to run the Python script in a hidden window
    vbscript_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run_hidden.vbs')
    with open(vbscript_path, 'w') as f:
        f.write(f'CreateObject("Wscript.Shell").Run "{python_executable} {script_path}", 0, True')

    # Define the command to create a task in Task Scheduler
    command = f'schtasks /Create /SC ONCE /TN "WatcchTestTask" /TR "{vbscript_path}" /ST {start_time_str} /RU "{os.getlogin()}" /IT'

    # Run the command
    result = os.system(command)

    # Return the result
    return result

if __name__ == "__main__":
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'take_screenshot.py')
    run_task_with_task_scheduler(script_path)