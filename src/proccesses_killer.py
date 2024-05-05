import os
import psutil
import time

from db_handler.db_handler import DBHandler

class ProcessesKiller:
    def __init__(self, db_handler: DBHandler, logger):
        self.db_handler = db_handler
        self.logger = logger

    def start(self):
        while True:
            kill_list = self.db_handler.get_restrictions()
            kill_list = [restriction[2] for restriction in kill_list]
            self.logger.info(f"Kill list: {kill_list}")

            for proc in psutil.process_iter():
                try:
                    if proc.name() in kill_list:
                        proc.kill()
                        self.logger.info(f"Killed {proc.name()}")
                except psutil.NoSuchProcess:
                    pass
            time.sleep(4)