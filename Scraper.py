from bs4 import BeautifulSoup
import re
from selenium import webdriver
from SoccerMatch import SoccerMatch

# TODO class Scraper():

def is_soccer_match_or_date(tag):
    if tag.name != "tr":
        return False
    if "center" in tag["class"] and "nob-border" in tag["class"]:
        return True
    if "deactivate" in tag["class"] and tag.has_attr("xeid"):
        return True
    return False

def is_date(tag):
    return "center" in tag["class"] and "nob-border" in tag["class"]

def get_date(tag):
    return tag.find(class_="datet").string

def get_time(tag):
    return tag.find(class_="datet").string

def get_participants(tag):
    parsed_strings = tag.find(class_="table-participant").text.split(" - ")
    participants = []
    participants.append(parsed_strings[0])
    participants.append(parsed_strings[-1])
    return participants

def get_scores(tag):
    score_str = tag.find(class_="table-score").string
    non_decimal = re.compile(r"[^\d]+")
    score_str = non_decimal.sub(" ", score_str)
    scores = [int(s) for s in score_str.split()]
    return scores

def get_odds(tag):
    odds_cells = tag.find_all(class_="odds-nowrp")
    odds = []
    for cell in odds_cells:
        odds.append(cell.text)
    return odds

if __name__ == "__main__":
    browser = webdriver.Chrome("./chromedriver/chromedriver.exe")
    browser.get("http://www.oddsportal.com/soccer/europe/euro/results/")
    tournament_tbl = browser.find_element_by_id("tournamentTable")
    tournament_tbl_html = tournament_tbl.get_attribute("innerHTML")
    tournament_tbl_soup = BeautifulSoup(tournament_tbl_html, "html.parser")
    significant_rows = tournament_tbl_soup(is_soccer_match_or_date)
    current_date_str = None
    for row in significant_rows:
        if is_date(row) is True:
            current_date_str = get_date(row)
        else:  # is a soccer match
            this_match = SoccerMatch()
            game_datetime_str = current_date_str + " " + get_time(row)
            this_match.set_start(game_datetime_str)
            participants = get_participants(row)
            this_match.set_teams(participants)
            scores = get_scores(row)
            this_match.set_outcome_from_scores(scores)
            odds = get_odds(row)
            this_match.set_odds(odds)
    browser.close()