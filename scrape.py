from bs4 import BeautifulSoup
from selenium import webdriver

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

if __name__ == "__main__":
    browser = webdriver.Chrome("./chromedriver/chromedriver.exe")
    browser.get("http://www.oddsportal.com/soccer/europe/euro/results/")
    tournament_tbl = browser.find_element_by_id("tournamentTable")
    tournament_tbl_html = tournament_tbl.get_attribute("innerHTML")
    tournament_tbl_soup = BeautifulSoup(tournament_tbl_html, "html.parser")
    significant_rows = tournament_tbl_soup(is_soccer_match_or_date)
    current_date = None
    for row in significant_rows:
        if is_date(row) is True:
            current_date = get_date(row)
            print(current_date)
        else:  # is a soccer match
            # TODO
            print("<game>")
    browser.close()