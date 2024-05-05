from libs.ServerAPI import ServerAPI
import time
import os
class DBUpdater:
    def __init__(self, db_repo, server_api, logger):
        self.logger = logger
        self.db_repo = db_repo
        self.server_api = server_api

    def start(self):
        self.logger.info("DBUpdater initialized --")
        while True:
            self.logger.info("DBUpdater is running")
            try:
                if(self.server_api.is_authenticated and self.server_api.is_connected):
                    self.logger.info("Updating known processes")
                    self.update_known_processes()
                    self.update_restrictions(self.get_update_restrictions())
                else:
                    self.logger.info("is_authenticated: %s, is_connected: %s", self.server_api.is_authenticated, self.server_api.is_connected)
            except Exception as e:
                self.logger.error("Error in DBUpdater: %s", e)
            time.sleep(5)

    def update_known_processes(self):
        try:
            known_programs = self.get_known_processes()
            self.server_api.update_known_programs(known_programs)
            self.logger.info(f"Known processes updated to server {known_programs}")
        except Exception as e:
            self.logger.error("Error updating known processes to server: %s", e)

    def get_known_processes(self):
        try:
            known_processes_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'known_processes.txt')
            known_processes_list = []
            if not os.path.exists(known_processes_file):
                return known_processes_list
            with open(known_processes_file, 'r') as f:
                known_processes_list = f.read().splitlines()
            self.logger.info(f"Known processes: {known_processes_list}")
            return known_processes_list       
        except Exception as e:
            self.logger.error("Error getting known processes: %s", e)
            return []
    
    def get_update_restrictions(self):
        try:
            new_restriction_list = self.server_api.update_restrictions()
        except Exception as e:
            self.logger.error("Error updating restrictions to server: %s", e)




    def update_restrictions(self, new_restriction_list):
        try:
            for restriction in new_restriction_list:
                # check if restriction is already in the db and just update it but if not add it
                if self.db_repo.get_restriction(restriction.id):
                    self.db_repo.update_restriction(restriction)
                else:
                    self.db_repo.add_restriction(restriction)

        except Exception as e:
            self.logger.error("Error updating restrictions to server: %s", e)

                