from bs4 import BeautifulSoup
from DbManager import DatabaseManager
import json
import re
from selenium import webdriver
from SoccerMatch import SoccerMatch

class Scraper():
    def __init__(self, league_json, initialize_db):
        self.browser = webdriver.Chrome("./chromedriver/chromedriver.exe")
        self.league = self.parse_json(league_json)
        self.db_manager = DatabaseManager(initialize_db)

    def parse_json(self, json_str):
        return json.loads(json_str)

    def scrape_all_urls(self):
        for url in self.league["urls"]:
            self.scrape_url(url)
        self.browser.close()

    def scrape_url(self, url):
        self.browser.get(url)
        tournament_tbl = self.browser.find_element_by_id("tournamentTable")
        tournament_tbl_html = tournament_tbl.get_attribute("innerHTML")
        tournament_tbl_soup = BeautifulSoup(tournament_tbl_html, "html.parser")
        significant_rows = tournament_tbl_soup(self.is_soccer_match_or_date)
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

    def is_soccer_match_or_date(self, tag):
        if tag.name != "tr":
            return False
        if "center" in tag["class"] and "nob-border" in tag["class"]:
            return True
        if "deactivate" in tag["class"] and tag.has_attr("xeid"):
            return True
        return False

    def is_date(self, tag):
        return "center" in tag["class"] and "nob-border" in tag["class"]

    def is_date_string_supported(self, date_string):
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
        this_date = tag.find(class_="datet").string
        if "Today" in this_date:
            return "Today"
        elif this_date.endswith(" - Play Offs"):
            this_date = this_date[:-12]
        return this_date

    def get_time(self, tag):
        return tag.find(class_="datet").string

    def get_participants(self, tag):
        parsed_strings = tag.find(class_="table-participant").text.split(" - ")
        participants = []
        participants.append(parsed_strings[0])
        participants.append(parsed_strings[-1])
        return participants

    def get_scores(self, tag):
        score_str = tag.find(class_="table-score").string
        if self.is_invalid_game_from_score_string(score_str):
            return [-1,-1]
        non_decimal = re.compile(r"[^\d]+")
        score_str = non_decimal.sub(" ", score_str)
        scores = [int(s) for s in score_str.split()]
        return scores

    def get_odds(self, tag):
        odds_cells = tag.find_all(class_="odds-nowrp")
        odds = []
        for cell in odds_cells:
            odds.append(cell.text)
        return odds

    def is_invalid_game_from_score_string(self, score_str):
        if score_str == "postp.":
            return True
        elif score_str == "canc.":
            return True
        return False
