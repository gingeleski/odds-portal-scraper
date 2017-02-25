import sqlite3

class DatabaseManager():
    def __init__(self):
        # TODO delete db file if it already exists
        self.conn = sqlite3.connect('oddsportal.db')
        self.cursor = self.conn.cursor()
        # TODO create table and commit

    def __del__(self):
        self.conn.close()