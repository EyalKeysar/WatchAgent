import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import getmac
import time
import psutil
import threading
from consts import *

class AppService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'WatchAgentService'
    _svc_display_name_ = 'WatchAgent'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.is_alive = threading.Event()
        self.is_alive.set()

    def first_run(self):
        # Perform first run initialization here
        # For example, create a registry entry to start the service automatically
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "WatchAgentService", 0, winreg.REG_SZ, sys.executable + " " + os.path.abspath(__file__))
            winreg.CloseKey(key)
        except Exception as e:
            print("Error setting autostart:", e)

    def main(self):
        sys.stderr = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'WatchAgentServiceError.log'), 'a+')
        log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'WatchAgentService.log')

        kill_list = ["Dolphin.exe", "dosbox", "chrome.exe"]
        
        while self.is_alive.is_set():
            with open(log_file_path, 'a') as f:
                number = kill_by_list(kill_list)
                update_known_processes()

                f.write(f"Killed {number} processes\n")
                current_time = f"H:{time.localtime().tm_hour} M:{time.localtime().tm_min} S:{time.localtime().tm_sec}"
                f.write("[" + current_time + "] LOG TIME\n\n")

            time.sleep(TIME_INTERVAL)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_alive.clear()
        self.is_alive.wait(10)  # Wait for the main loop to stop
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.first_run()  # Call first_run() before starting the main loop
        self.main()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AppService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AppService)

def kill_by_list(kill_list):
    number = 0
    for proc in psutil.process_iter():
        try:
            if proc.name() in kill_list:
                proc.kill()
                number += 1
        except psutil.NoSuchProcess:
            pass

    return number

def update_known_processes():
    known_processes_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'known_processes.txt')
    known_processes_list = []
    with open(known_processes_file, 'r') as f:
        known_processes_list = f.read().splitlines()

    for proc in psutil.process_iter():
        try:
            if proc.name() not in known_processes_list:
                with open(known_processes_file, 'a') as f:
                    f.write(proc.name() + '\n')
        except psutil.NoSuchProcess:
            pass
