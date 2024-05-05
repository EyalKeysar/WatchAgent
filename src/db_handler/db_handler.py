import sqlite3
import threading


CREATE_RESTRICTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS restrictions (
    id INTEGER PRIMARY KEY,
    child_id INTEGER NOT NULL,
    program_name TEXT NOT NULL,

    start_time INTEGER NOT NULL,
    end_time INTEGER NOT NULL,

    allowed_time INTEGER NOT NULL,
    time_span TEXT NOT NULL,
    usage_time FLOAT NOT NULL
);
"""
CREATE_TIMELIMIT_TABLE = """
CREATE TABLE IF NOT EXISTS timelimit (
    id INTEGER PRIMARY KEY,
    start_time INTEGER NOT NULL,
    end_time INTEGER NOT NULL,
    allowed_time INTEGER NOT NULL,
    time_span TEXT NOT NULL,
    usage_time FLOAT NOT NULL
);
"""
ADD_RESTRICTION = """
INSERT INTO restrictions (id, child_id, program_name, start_time, end_time, allowed_time, time_span, usage_time) VALUES (?, 0, ?, ?, ?, ?, ?, ?)
"""

class DBHandler:
    def __init__(self, path, logger):
        self.logger = logger
        self.conn = sqlite3.connect(f"{path}", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()

        self.cursor.execute(CREATE_RESTRICTIONS_TABLE)
        self.cursor.execute(CREATE_TIMELIMIT_TABLE)
        self.conn.commit()

    def add_restriction(self, restriction):
        self.logger.info("Acquiring lock for add_restriction")
        with self.lock:
            self.logger.info("Lock acquired for add_restriction")
            self.cursor.execute(ADD_RESTRICTION, 
                                (restriction.id, restriction.program_name, restriction.start_time, restriction.end_time, restriction.allowed_time, restriction.time_span, restriction.usage_time))
            self.conn.commit()
        self.logger.info("Lock released for add_restriction")

    def update_restriction(self, restriction):
        self.logger.info("Acquiring lock for update_restriction")
        with self.lock:
            self.logger.info("Lock acquired for update_restriction")
            update_query = """
            UPDATE restrictions 
            SET start_time=?, end_time=?, allowed_time=?, time_span=?, usage_time=?
            WHERE id=?
            """
            self.cursor.execute(update_query, 
                                (restriction.start_time, restriction.end_time, restriction.allowed_time, restriction.time_span, restriction.usage_time, restriction.id))
            self.conn.commit()
        self.logger.info("Lock released for update_restriction")

    def get_restrictions(self):
        self.logger.info("Acquiring lock for get_restrictions")
        with self.lock:
            self.logger.info("Lock acquired for get_restrictions")
            self.cursor.execute("SELECT * FROM restrictions")
            data = self.cursor.fetchall()
        self.logger.info("Lock released for get_restrictions")
        return data
    
    def get_restriction(self, restriction_id):
        self.logger.info("Acquiring lock for get_restriction")
        with self.lock:
            self.logger.info("Lock acquired for get_restriction")
            self.cursor.execute("SELECT * FROM restrictions WHERE id=?", (restriction_id,))
            data = self.cursor.fetchone()
        self.logger.info("Lock released for get_restriction")
        return data
    
    def delete_restriction(self, id):
        self.logger.info("Acquiring lock for delete_restriction")
        with self.lock:
            self.logger.info("Lock acquired for delete_restriction")
            self.cursor.execute("DELETE FROM restrictions WHERE id=?", (id,))
            self.conn.commit()
        self.logger.info("Lock released for delete_restriction")

    def modify_restriction(self, id, restriction):
        self.logger.info("Acquiring lock for modify_restriction")
        with self.lock:
            self.logger.info("Lock acquired for modify_restriction")
            update_query = """
            UPDATE restrictions 
            SET start_time=?, end_time=?, allowed_time=?, time_span=? 
            WHERE id=?
            """
            self.cursor.execute(update_query, 
                                (restriction.start_time, restriction.end_time, restriction.allowed_time, restriction.time_span, id))
            self.conn.commit()
        self.logger.info("Lock released for modify_restriction")

    def get_id_by_program_name(self, program_name):
        self.logger.info("Acquiring lock for get_id_by_program_name")
        with self.lock:
            self.logger.info("Lock acquired for get_id_by_program_name")
            self.cursor.execute("SELECT id FROM restrictions WHERE program_name=?", (program_name,))
            data = self.cursor.fetchone()
        self.logger.info("Lock released for get_id_by_program_name")
        return data

    def __del__(self):
        self.conn.close()