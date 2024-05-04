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
import logging  # Add logging module import

from consts import *
from proccesses_killer import ProcessesKiller
from db_handler.db_handler import DBHandler
from db_updater import DBUpdater
from libs.ServerAPI import ServerAPI


class AppService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'WatchAgentService'
    _svc_display_name_ = 'WatchAgent'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.is_alive = threading.Event()
        self.is_alive.set()
        log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'WatchAgentService.log')
        logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')  # Configure logging
        logging.info("\nService initialized -------------------------------------------------")
        

    def first_run(self):
        
        # Perform first run initialization here
        # For example, create a registry entry to start the service automatically
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "WatchAgentService", 0, winreg.REG_SZ, sys.executable + " " + os.path.abspath(__file__))
            winreg.CloseKey(key)
        except Exception as e:
            logging.error("Error setting autostart: %s", e)  # Log the error


    def main(self):
        logging.info("Starting main loop")

        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'watch_agent.db')
        db_handler = DBHandler(db_path, logging)

        logging.info("DBHandler initialized")

        try:
            serverapi = ServerAPI.ServerAPI()
        except Exception as e:
            logging.error("Error initializing ServerAPI: %s", e)
            return
        logging.info("ServerAPI initialized")
        Utils.check_connection(serverapi, logging)
        # db_updater = DBUpdater(db_handler, serverapi, logging)

        logging.info("DBUpdater initialized")

        processes_killer = ProcessesKiller(db_handler, logging)

        processes_killer_thread = threading.Thread(target=processes_killer.start)
        processes_killer_thread.start()

        logging.info("ProcessesKiller started")


        known_processes_update_thread = threading.Thread(target=Utils.update_known_processes)
        known_processes_update_thread.start()


        logging.info("Known processes update thread started")

        while self.is_alive.is_set():
            Utils.check_connection(serverapi, logging)

            time.sleep(3)



    def SvcStop(self):
        logging.info("Stopping service -------------------------------------------------\n")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_alive.clear()
        self.is_alive.wait(10)  # Wait for the main loop to stop
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        logging.info("Starting service")
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.first_run()  # Call first_run() before starting the main loop
        self.main()

class Utils:
    @staticmethod
    def update_known_processes():
        while True:
            known_processes_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'known_processes.txt')
            known_processes_list = []
            with open(known_processes_file, 'r') as f:
                known_processes_list = f.read().splitlines()

            for proc in psutil.process_iter():
                try:
                    if proc.name() not in known_processes_list:
                        logging.info(f"New process found: {proc.name()}")
                        with open(known_processes_file, 'a') as f:
                            f.write(proc.name() + '\n')
                except psutil.NoSuchProcess:
                    pass
            time.sleep(5)

    @staticmethod
    def check_connection(server_api, logger):
        logger.info("Checking connection to server")
        try:
            if(server_api.is_connected):
                logger.info("Already connected to server, getting info...")
                response = server_api.ping()
            else:
                logger.info("Connecting to server...")
                server_api.connect()
                response = server_api.ping()
            if server_api.is_connected and response == "pong":
                logging.info("Connected to server, response: %s", response)
                return True
            else:
                logging.error("Error connecting to server")
                return False
        except Exception as e:
            logging.error("Error connecting to server: %s", e)
            return False

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AppService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AppService)
