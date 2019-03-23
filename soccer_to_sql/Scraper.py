"""
Soccer match results scraping object.
"""

from bs4 import BeautifulSoup
from DbManager import DatabaseManager
import json
import re
import time
from selenium import webdriver
from SoccerMatch import SoccerMatch

class Scraper():

    def __init__(self, league_json, initialize_db):
        """
        Constructor. Launch the web driver browser, initialize the league
        field by parsing the representative JSON file, and connect to the
        database manager.

        Args:
            league_json (str): JSON string of the league to associate with the
                Scraper.
            initialize_db (bool): Should the database be initialized?
        """

        self.browser = webdriver.Chrome("./chromedriver/chromedriver")
        self.league = self.parse_json(league_json)
        self.db_manager = DatabaseManager(initialize_db)

    def parse_json(self, json_str):
        """
        Parse a JSON string into a dict.

        Args:
            json_str (str): JSON string to parse.

        Returns:
            (dict)
        """

        return json.loads(json_str)

    def scrape_all_urls(self, do_verbose_output=False):
        """
        Call the scrape method on every URL in this Scraper's league field, in
        order, then close the browser.

        Args:
            do_verbose_output (bool): True/false do verbose output.
        """

        if do_verbose_output is True:
            output_str = "Start scraping " + self.league["league"] + " of "
            output_str += self.league["area"] + "..."
            print(output_str)

        for url in self.league["urls"]:
            # loop through all pages in that season
            page = 1
            while self.scrape_url("#/page/".join((url, "{}/".format(page)))):
                if do_verbose_output:
                    print("Scraped page", page)
                page += 1

            if do_verbose_output:
                print("Finished season")


        self.browser.close()

        if do_verbose_output is True:
            print("Done scraping this league.")

    def scrape_url(self, url):
        """
        Scrape the data for every match on a given URL and insert each into the
        database.

        Args:
            url (str): URL to scrape data from.

        Returns:
            Whether data existed for that season.
        """

        self.browser.get(url)

        # waiting for table to load
        # needed or else the data won't be complete
        delay = 5 # seconds
        time.sleep(delay)

        tournament_tbl = self.browser.find_element_by_id("tournamentTable")
        tournament_tbl_html = tournament_tbl.get_attribute("innerHTML")
        tournament_tbl_soup = BeautifulSoup(tournament_tbl_html, "html.parser")
        try:
            significant_rows = tournament_tbl_soup(self.is_soccer_match_or_date)
        except:
            return False

        current_date_str = None
        for row in significant_rows:
            if self.is_date(row) is True:
                current_date_str = self.get_date(row)
            elif self.is_date_string_supported(current_date_str) == False:
                # not presently supported
                continue
            else:  # is a soccer match
                this_match = SoccerMatch()
                game_datetime_str = current_date_str + " " + self.get_time(row)
                this_match.set_start(game_datetime_str)
                participants = self.get_participants(row)
                this_match.set_teams(participants)
                scores = self.get_scores(row)
                this_match.set_outcome_from_scores(scores)
                odds = self.get_odds(row)
                this_match.set_odds(odds)
                self.db_manager.add_soccer_match(self.league, url, this_match)

        return True

    def is_soccer_match_or_date(self, tag):
        """
        Determine whether a provided HTML tag is a row for a soccer match or
        date.

        Args:
            tag (obj): HTML tag object from BeautifulSoup.

        Returns:
            (bool)
        """

        if tag.name != "tr":
            return False
        if "center" in tag["class"] and "nob-border" in tag["class"]:
            return True
        if "deactivate" in tag["class"] and tag.has_attr("xeid"):
            return True
        return False

    def is_date(self, tag):
        """
        Determine whether a provided HTML tag is a row for a date.

        Args:
            tag (obj): HTML tag object from BeautifulSoup.

        Returns:
            (bool)
        """

        return "center" in tag["class"] and "nob-border" in tag["class"]

    def is_date_string_supported(self, date_string):
        """
        Determine whether a given date string is currently supported by this
        software's parsing capabilities.

        Args:
            date_string (str): Date string to assess.

        Returns:
            (bool)
        """

        if date_string is None:
            return False
        elif "Today" in date_string:
            return False
        elif "Yesterday" in date_string:
            return False
        elif "Qualification" in date_string:
            return False
        elif "Promotion" in date_string:
            return False
        return True

    def get_date(self, tag):
        """
        Extract the date from an HTML tag for a date row.

        Args:
            tag (obj): HTML tag object from BeautifulSoup.

        Returns:
            (str) Extracted date string.
        """

        this_date = tag.find(class_="datet").string
        if "Today" in this_date:
            return "Today"
        elif this_date.endswith(" - Play Offs"):
            this_date = this_date[:-12]
        return this_date

    def get_time(self, tag):
        """
        Extract the time from an HTML tag for a soccer match row.

        Args:
            tag (obj): HTML tag object from BeautifulSoup.

        Returns:
            (str) Extracted time.
        """

        return tag.find(class_="datet").string

    def get_participants(self, tag):
        """
        Extract the match's participants from an HTML tag for a soccer match
        row.

        Args:
            tag (obj): HTML tag object from BeautifulSoup.

        Returns:
            (list of str) Extracted match participants.
        """

        parsed_strings = tag.find(class_="table-participant").text.split(" - ")
        participants = []
        participants.append(parsed_strings[0])
        participants.append(parsed_strings[-1])
        return participants

    def get_scores(self, tag):
        """
        Extract the scores for each team from an HTML tag for a soccer match
        row.

        Args:
            tag (obj): HTML tag object from BeautifulSoup.

        Returns:
            (list of str) Extracted match scores.
        """

        score_str = tag.find(class_="table-score").string
        if self.is_invalid_game_from_score_string(score_str):
            return [-1,-1]
        non_decimal = re.compile(r"[^\d]+")
        score_str = non_decimal.sub(" ", score_str)
        scores = [int(s) for s in score_str.split()]
        return scores

    def get_odds(self, tag):
        """
        Extract the betting odds for a match from an HTML tag for a soccer
        match row.

        Args:
            tag (obj): HTML tag object from BeautifulSoup.

        Returns:
            (list of str) Extracted match odds.
        """

        odds_cells = tag.find_all(class_="odds-nowrp")
        odds = []
        for cell in odds_cells:
            odds.append(cell.text)
        return odds

    def is_invalid_game_from_score_string(self, score_str):
        """
        Assess, from the score string extracted from a soccer match row,
        whether a game actually paid out one of the bet outcomes.

        Args:
            score_str (str): Score string to assess.

        Returns:
            (bool)
        """

        if score_str == "postp.":
            return True
        elif score_str == "canc.":
            return True
        return False
