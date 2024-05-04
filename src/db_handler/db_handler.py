import sqlite3
from ..libs.ServerAPI.shared.SharedDTO import Restriction, TimeLimit, ChildData
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
INSERT INTO restrictions (program_name, start_time, end_time, allowed_time, time_span, usage_time) VALUES (?, ?, ?, ?, ?, ?)
"""

class DBHandler:
    def __init__(self, path):
        self.conn = sqlite3.connect(f"{path}")
        self.cursor = self.conn.cursor()

        self.cursor.execute(CREATE_RESTRICTIONS_TABLE)
        self.cursor.execute(CREATE_TIMELIMIT_TABLE)
        self.conn.commit()

    def add_restriction(self, restriction: Restriction):
        self.cursor.execute(ADD_RESTRICTION, 
                            (restriction.program_name, restriction.start_time, restriction.end_time, restriction.allowed_time, restriction.time_span, restriction.usage_time))
        self.conn.commit()

    def get_restrictions(self):
        self.cursor.execute("SELECT * FROM restrictions")
        return self.cursor.fetchall()
    
    def delete_restriction(self, id):
        self.cursor.execute("DELETE FROM restrictions WHERE id=?", (id,))
        self.conn.commit()

    

    def __del__(self):
        self.conn.close()