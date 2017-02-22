from selenium import webdriver

if __name__ == "__main__":
    browser = webdriver.Chrome("./chromedriver/chromedriver.exe")
    browser.get("http://www.oddsportal.com/soccer/england/premier-league-2015-2016/results/")
    tournament_table = browser.find_element_by_id("tournamentTable")
    # TODO parse WebObject tournament_table
    browser.close()