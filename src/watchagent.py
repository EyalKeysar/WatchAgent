import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
from libs.ServerAPI.ServerAPI import ServerAPI
import getmac
import time
import psutil
import threading

class AppService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'WatchAgentService'
    _svc_display_name_ = 'WatchAgent'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.is_alive = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_alive = threading.Event()
        self.is_alive.set()

    def main(self):

        sys.stderr = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'WatchAgentServiceError.log'), 'a+')

        log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'WatchAgentService.log')
        while self.is_alive.is_set():
            with open(log_file_path, 'a') as f:
    
                # server_api = ServerAPI()
                # server_api.connect()
                # f.write("next step\n")
                # respond = server_api.new_agent_request(getmac.get_mac_address())
                # f.write(str(respond) + "\n")

                number = kill_chrome_processes()
                f.write("chrome closed = " + str(number) + "\n")

                current_time = f"H:{time.localtime().tm_hour} M:{time.localtime().tm_min} S:{time.localtime().tm_sec}"
                f.write("[" + current_time + "] LOG TIME\n")

            time.sleep(5)


    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_alive.clear()
        self.is_alive.wait()  # Wait for the main loop to stop
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AppService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AppService)


def kill_chrome_processes():
    for proc in psutil.process_iter():
        if proc.name() == "chrome.exe":
            proc.kill()