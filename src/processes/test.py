import pygetwindow as gw
import time

while True:
    time.sleep(2)
    active_window = gw.getActiveWindow()
    if active_window:
        print("Active Window Title:", active_window.title)
    else:
        print("No active window found.")
