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
from libs.ServerAPI.shared.SharedDTO import RestrictionListSerializer


class AppService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'WatchAgentService'
    _svc_display_name_ = 'WatchAgent'

import win32serviceutil
import win32security
import ntsecuritycon
import winerror
import win32api
import win32service
import win32event
import win32con
import threading
import logging
import os
import sys
import time
import win32process
import win32api
import ctypes
from ctypes import *

class AppService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'WatchAgentService'
    _svc_display_name_ = 'WatchAgent'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.is_alive = threading.Event()
        self.is_alive.set()
        log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'WatchAgentService.log')
        logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')  # Configure logging
        logging.info("\nService initialized -------------------------------")
        
        # Set security descriptor to restrict access
        self.set_service_security()

    def set_service_security(self):
        try:
            ntdll = WinDLL("ntdll.dll")
            ntdll.RtlSetProcessIsCritical(1,0,0)
            logging.info("Service security set")
        except Exception as e:
            logging.error("Error setting service security: %s", e)

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
        
        
        db_updater = DBUpdater(db_handler, serverapi, RestrictionListSerializer, logging)
        db_updater_thread = threading.Thread(target=db_updater.start)
        db_updater_thread.start()

        logging.info("DBUpdater initialized")

        processes_killer = ProcessesKiller(db_handler, logging)

        processes_killer_thread = threading.Thread(target=processes_killer.start)
        processes_killer_thread.start()

        logging.info("ProcessesKiller started")


        known_processes_update_thread = threading.Thread(target=Utils.update_known_processes)
        known_processes_update_thread.start()


        logging.info("Known processes update thread started")

        while self.is_alive.is_set():
            logging.info("ML is_authenticated: %s, is_connected: %s", serverapi.is_authenticated, serverapi.is_connected)
            if serverapi.is_connected and not serverapi.is_authenticated:
                Utils.login(serverapi, logging)
            if not serverapi.is_connected:
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
            if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'known_processes.txt')):
                with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'known_processes.txt'), 'w') as f:
                    f.write('')
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
                except Exception as e:
                    logging.error("Error updating known processes: %s", e)
            time.sleep(5)

    @staticmethod
    def check_connection(server_api, logger):
        try:
            response = "didn't get response"
            if(server_api.is_connected):
                response = server_api.ping()
                return True
            else:
                logger.info("Connecting to server...")
                response = server_api.connect()
                if (server_api.is_connected == False):
                    logger.error("Error connecting to server, response: %s", response)
                    return False
                response = server_api.ping()
                if response == "pong":
                    logger.info("Connected to server, response: %s", response)
                    Utils.login(server_api, logger)
                    return True
                else:
                    logger.error("Error connecting to server ping response: %s", response)
                    return False
        except Exception as e:
            logging.error("Error connecting to server: %s", e)
            return False
        
    @staticmethod
    def login(server_api, logger):
        try:
            auth_str = Utils.get_agent_id(server_api, logger)
            if auth_str:
                response = server_api.login_agent(auth_str)
                if "True" in str(response):
                    logger.info("Login successful")
                else:
                    logger.error("Login failed respond: %s", response)
            else:
                logger.error("Agent id not found")
        except Exception as e:
            logger.error("Error logging in: %s", e)

    @staticmethod
    def get_agent_id(server_api, logger):
        # Read the agent id from the file
        #check if the agent id exists
        agent_id = None
        if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agent_id.txt')):
            logger.info("Agent id not found, generating new agent id")
            Utils.set_agent_id(server_api, logger)
        else:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agent_id.txt'), "r") as file:
                agent_id = file.read().strip()
        logger.info(f"Agent id: {agent_id}")
        return agent_id
    
    @staticmethod
    def set_agent_id(server_api, logger):
        # Generate a new agent id
        mac_address = getmac.get_mac_address()
        agent_id = server_api.new_agent_request(mac_address)
        logger.info(f"Generated agent id: {agent_id} --")

        # Write the agent id to the 
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agent_id.txt'), "w") as file:
                file.write(agent_id[0])
        except Exception as e:
            logger.error("Error writing agent id to file: %s", e)
            return False
        


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AppService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AppService)
