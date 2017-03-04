import os
import sqlite3

DB_FILENAME = 'oddsportal.db'

class DatabaseManager():
    def __init__(self, is_first_run):
        if is_first_run:
            try:
                os.remove(DB_FILENAME)
            except OSError:
                pass
        self.conn = sqlite3.connect(DB_FILENAME)
        self.cursor = self.conn.cursor()
        if is_first_run:
            self.cursor.execute('''DROP TABLE IF EXISTS matches''')
            self.cursor.execute('''CREATE TABLE matches
                                    (league text, area text,
                                    retrieved_from_url text, start_time text,
                                    end_time text, team1 text, team2 text,
                                    outcome text, team1_odds text,
                                    team2_odds text, draw_odds text)''')
            self.conn.commit()

    def add_soccer_match(self, league, retrieved_from_url, match):
        sql_str = "INSERT INTO matches VALUES ('"
        sql_str += league["league"] + "', '"
        sql_str += league["area"] + "', '"
        sql_str += retrieved_from_url + "', '"
        sql_str += match.get_start_time_string() + "', '"
        sql_str += match.get_end_time_string() + "', '"
        sql_str += match.get_team1_string() + "', '"
        sql_str += match.get_team2_string() + "', '"
        sql_str += match.get_outcome_string() + "', '"
        sql_str += str(match.get_team1_odds()) + "', '"
        sql_str += str(match.get_team2_odds()) + "', '"
        sql_str += str(match.get_draw_odds()) + "')"

        self.cursor.execute(sql_str)
        self.conn.commit()

    def __del__(self):
        self.conn.close()
