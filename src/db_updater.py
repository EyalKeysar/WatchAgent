from libs.ServerAPI import ServerAPI
import time
import os
class DBUpdater:
    def __init__(self, db_repo, server_api, logger):
        self.logger = logger
        self.db_repo = db_repo
        self.server_api = server_api

    def start(self):
        while True:
            self.update_known_processes()
            self.update_restrictions()
            time.sleep(5)

    def update_known_processes(self):
        try:
            self.server_api.update_known_processes(self.get_known_processes())
        except Exception as e:
            self.logger.error("Error updating known processes to server: %s", e)

    def get_known_processes(self):
        known_processes_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'known_processes.txt')
        known_processes_list = []
        with open(known_processes_file, 'r') as f:
            known_processes_list = f.read().splitlines()
        return known_processes_list       
    
    def get_update_restrictions(self):
        try:
            new_restriction_list = self.server_api.update_restrictions()
        except Exception as e:
            self.logger.error("Error updating restrictions to server: %s", e)

    def update_restrictions(self, new_restriction_list):
        for restriction in new_restriction_list:
            # check if restriction is already in the db and just update it but if not add it
            if self.db_repo.get_restriction(restriction.id):
                self.db_repo.update_restriction(restriction)
            else:
                self.db_repo.add_restriction(restriction)

                