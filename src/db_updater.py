from libs.ServerAPI import ServerAPI
import time
import os
class DBUpdater:
    def __init__(self, db_repo, server_api, restriction_list_serializer, logger):
        self.logger = logger
        self.db_repo = db_repo
        self.server_api = server_api
        self.restriction_list_serializer = restriction_list_serializer

    def start(self):
        try:
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
        except Exception as e:
            self.logger.error("Error starting DBUpdater: %s", e)

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
                self.logger.error("known_processes.txt not found")
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
            new_restriction_list = self.server_api.agent_get_restrictions()
            if new_restriction_list:  # Check if the response is not empty
                new_restriction_list = self.restriction_list_serializer.deserialize(new_restriction_list)
                if new_restriction_list:
                    self.logger.info(f"Restrictions updated: {new_restriction_list}")
                    return new_restriction_list
            else:
                self.logger.info("No new restrictions found")
                return []    
        except Exception as e:
            self.logger.error("Error updating restrictions to server 1: %s", e)
            return []


    def update_restrictions(self, new_restriction_list):
        try:
            self.logger.info(f"Updating restrictions: {new_restriction_list}")
            for restriction in new_restriction_list:
                # check if restriction is already in the db and just update it but if not add it
                self.logger.info(f"single restriction: {restriction}")
                self.logger.info(f"Checking if restriction exists in the database...")
                try:
                    existing_restriction = self.db_repo.get_restriction(restriction.id)
                except Exception as e:
                    self.logger.error(f"Error getting restriction from database: {e}")
                    continue
                self.logger.info(f"Existing restriction: {existing_restriction}")
                if existing_restriction:
                    self.logger.info(f"Updating restriction: {restriction}")
                    self.db_repo.update_restriction(restriction)
                else:
                    self.logger.info(f"New restriction found: {restriction}")
                    self.db_repo.add_restriction(restriction)
            
            for restriction in self.db_repo.get_restrictions():
                restriction_id = restriction[0]
                if restriction_id not in [r.id for r in new_restriction_list]:
                    self.logger.info(f"Deleting restriction: {restriction}")
                    self.db_repo.delete_restriction(restriction_id)

        except Exception as e:
            self.logger.error("Error updating restrictions to server 2: %s", e)

                