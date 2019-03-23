"""
Manager class to handle database interactions.
"""

import os
import sqlite3

DB_FILENAME = "oddsportal.db"

class DatabaseManager():

    def __init__(self, is_first_run):
        """
        Constructor.

        Args:
            is_first_run (bool): Is this the first DatabaseManager
                created in this run?
        """

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
                                    retrieved_from_url text, start_time integer,
                                    end_time integer, team1 text, team2 text,
                                    outcome text, team1_odds real,
                                    team2_odds real, draw_odds real)''')
            self.conn.commit()

    def add_soccer_match(self, league, retrieved_from_url, match):
        """
        Insert a soccer match entry into the database.

        Args:
            league (dict): The dict result from parsing a league.json file.

            retrieved_from_url (str): URL this match was retrieved from.

            match (object): The SoccerMatch to insert into the database.
        """

        sql_str = "INSERT INTO matches VALUES ('"
        sql_str += league["league"] + "', '"
        sql_str += league["area"] + "', '"
        sql_str += retrieved_from_url + "', "
        sql_str += str(match.get_start_time_unix_int()) + ", "
        sql_str += str(match.get_end_time_unix_int()) + ", '"
        sql_str += match.get_team1_string() + "', '"
        sql_str += match.get_team2_string() + "', '"
        sql_str += match.get_outcome_string() + "', '"
        sql_str += str(match.get_team1_odds()) + "', '"
        sql_str += str(match.get_team2_odds()) + "', '"
        sql_str += str(match.get_draw_odds()) + "')"

        self.cursor.execute(sql_str)
        self.conn.commit()

    def __del__(self):
        """
        Destructor.
        """

        self.conn.close()
