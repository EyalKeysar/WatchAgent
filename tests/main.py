import time
from gui import AppGUI

def main():
    app_gui = AppGUI()
    while True:
        app_gui.show_processes()

if __name__ == '__main__':
    main()
