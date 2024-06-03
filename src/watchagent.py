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
from screen_share import share_screen, run_task_with_task_scheduler, end_task_with_task_scheduler

from ctypes import *
import subprocess

TESTING = True

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
            if not TESTING:
                ntdll = WinDLL("ntdll.dll")
                ntdll.RtlSetProcessIsCritical(1,0,0)
            logging.info("Service security set")
        except Exception as e:
            logging.error("Error setting service security: %s", e)


    def main(self):
        logging.info("Starting main loop")

        # db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'watch_agent.db')
        # db_handler = DBHandler(db_path, logging)

        # logging.info("DBHandler initialized")

        try:
            serverapi = ServerAPI.ServerAPI()
        except Exception as e:
            logging.error("Error initializing ServerAPI: %s", e)
            return
        logging.info("ServerAPI initialized")
        
        
        # db_updater = DBUpdater(db_handler, serverapi, RestrictionListSerializer, logging)
        # db_updater_thread = threading.Thread(target=db_updater.start)
        # db_updater_thread.start()

        # logging.info("DBUpdater initialized")

        # processes_killer = ProcessesKiller(db_handler, logging)

        # processes_killer_thread = threading.Thread(target=processes_killer.start)
        # processes_killer_thread.start()

        # logging.info("ProcessesKiller started")


        # known_processes_update_thread = threading.Thread(target=Utils.update_known_processes)
        # known_processes_update_thread.start()

        while self.is_alive.is_set():
            logging.info("ML is_authenticated: %s, is_connected: %s", serverapi.is_authenticated, serverapi.is_connected)
            if serverapi.is_connected and not serverapi.is_authenticated:
                logging.info("Logging in")
                Utils.login(serverapi, logging)
                
            if not serverapi.is_connected:
                logging.info("check connection")
                Utils.check_connection(serverapi, logging)
            if serverapi.is_connected and serverapi.is_authenticated:
                logging.info("before serverapi status: is_connected: %s, is_authenticated: %s", serverapi.is_connected, serverapi.is_authenticated)
                share_screen(serverapi, logging)
                logging.info("after serverapi status: is_connected: %s, is_authenticated: %s", serverapi.is_connected, serverapi.is_authenticated)

            logging.info("Main loop running")


            time.sleep(3)




    def SvcStop(self):
        logging.info("Stopping service -------------------------------------------------\n")
        if TESTING:
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            self.is_alive.clear()
            self.is_alive.wait(10)  # Wait for the main loop to stop
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        logging.info("Starting service")
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        
        self.main()

class Utils:
    @staticmethod
    def is_system_process(proc):
        return False

    @staticmethod
    def update_known_processes():
        while True:
            known_processes_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'known_processes.txt')
            
            if not os.path.exists(known_processes_file):
                with open(known_processes_file, 'w') as f:
                    f.write('')
            
            with open(known_processes_file, 'r') as f:
                known_processes_list = f.read().splitlines()

            for proc in psutil.process_iter():
                try:
                    if not Utils.is_system_process(proc) and proc.name() not in known_processes_list:
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
                logger.info("Already connected to server, pinging server")
                response = server_api.ping()
                logger.info("Ping response: %s", response)
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