import os
import psutil
import time

from db_handler.db_handler import DBHandler

class ProcessesKiller:
    def __init__(self, db_handler: DBHandler, logger):
        self.db_handler = db_handler
        self.logger = logger

    def start(self, logger):
        while True:
            restrictions = self.db_handler.get_restrictions()
            kill_list = [restriction[2] for restriction in restrictions]
            self.logger.info(f"Kill list: {kill_list}")

            for proc in psutil.process_iter():
                try:
                    if proc.name() in kill_list:
                        restriction = None
                        for tmp_restriction in restrictions:
                            if tmp_restriction[2] == proc.name():
                                restriction = tmp_restriction
                        if restriction is None:
                            continue
                        
                        restriction_start_time = int(restriction[3])
                        restriction_end_time = int(restriction[4])
                        current_time = int(time.time())
                        current_time = int(time.strftime('%H', time.localtime(current_time)))
                        logger.info(f"Current time: {current_time}, restriction start time: {restriction_start_time}, restriction end time: {restriction_end_time}")
                        if current_time < restriction_start_time or current_time > restriction_end_time:
                            proc.kill()
                            self.logger.info(f"Killed {proc.name()}")
                        else:
                            self.logger.info(f"Process {proc.name()} is in restriction period")

                        # proc.kill()
                        # self.logger.info(f"Killed {proc.name()}")
                except psutil.NoSuchProcess:
                    pass
            time.sleep(4)