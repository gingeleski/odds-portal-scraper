import os
import sqlite3

DB_FILENAME = 'oddsportal.db'

class DatabaseManager():
    def __init__(self):
        try:
            os.remove(DB_FILENAME)
        except OSError:
            pass
        self.conn = sqlite3.connect(DB_FILENAME)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''DROP TABLE IF EXISTS matches''')
        self.cursor.execute('''CREATE TABLE matches
                                (area text, retrieved_from_url text,
                                start_time text, end_time text, team1 text,
                                team2 text, outcome text, team1_odds text,
                                team2_odds text, draw_odds text)''')
        self.conn.commit()

    def __del__(self):
        self.conn.close()

my_db = DatabaseManager()