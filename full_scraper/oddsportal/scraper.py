"""
scraper.py

Logic for the overall Odds Portal scraping utility focused on scraping

"""


from .models import Game
from .models import Season
from pyquery import PyQuery as pyquery
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import datetime
import logging
import os
import re
import time


logger = logging.getLogger(__name__)


class Scraper(object):
    """
    A class to scrape/parse match results from oddsportal.com website.
    Makes use of Selenium and BeautifulSoup modules.
    """
    
    def __init__(self, wait_on_page_load=3):
        """
        Constructor
        """
        self.base_url = 'https://www.oddsportal.com'
        self.wait_on_page_load = wait_on_page_load
        if wait_on_page_load == None:
            self.wait_on_page_load = 3
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')
        self.driver = webdriver.Chrome('./chromedriver/chromedriver', chrome_options=self.options)
        logger.info('Chrome browser opened in headless mode')
        
        # exception when no driver created
        
    def go_to_link(self,link):
        """
        returns True if no error
        False whe page not found
        """
        self.driver.get(link)
        try:
            # if no Login button -> page not found
            self.driver.find_element_by_css_selector('.button-dark')
        except NoSuchElementException:
            logger.warning('Problem with link, could not find Login button - %s', link)
            return False
        # Workaround for ajax page loading issue
        time.sleep(self.wait_on_page_load)
        return True
        
    def get_html_source(self):
        return self.driver.page_source
    
    def close_browser(self):
        time.sleep(5)
        try:
            self.driver.quit()
            logger.info('Browser closed')
        except WebDriverException:
            logger.warning('WebDriverException on closing browser - maybe closed?')

    def populate_games_into_season(self, season):
        """
        Params:
            season (Season) with urls but not games populated, to modify
        """
        for url in season.urls:
            self.go_to_link(url)
            html_source = self.get_html_source()
            html_querying = pyquery(html_source)
            # Check if the page says "No data available"
            no_data_div = html_querying.find('div.message-info > ul > li > div.cms')
            if no_data_div != None and no_data_div.text() == 'No data available':
                # Yes, found "No data available"
                logger.warning('Found "No data available", skipping %s', url)
                continue
            retrieval_time_for_reference = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            tournament_table = html_querying.find('div#tournamentTable > table#tournamentTable')
            table_rows = tournament_table.find('tbody > tr')
            num_table_rows = len(table_rows)
            for i in range(0,num_table_rows):
                try:
                    # Finding the table cell with game time and assessing if its blank tells us if this is a game data row
                    time_cell = tournament_table.find('tbody > tr').eq(i).find('td.table-time')
                    if 0 == len(str(time_cell).strip()):
                        # This row of the table does not contain game/match data
                        continue
                    game = Game()
                    # Need to get the actual HtmlElement out of the PyQuery object that time_cell currently is
                    time_cell = time_cell[0]
                    for key, value in time_cell.attrib.items():
                        if key == 'class':
                            time_cell_classes = value.split(' ')
                            for time_cell_class in time_cell_classes:
                                if 0 == len(time_cell_class) or time_cell_class[0] != 't':
                                    continue
                                if time_cell_class[1] == '0' or time_cell_class[1] == '1' or time_cell_class[2] == '2':
                                    unix_time = int(time_cell_class.split('-')[0].replace('t',''))
                                    game.game_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(unix_time))
                                    break
                            break
                    # If time still isn't set at this point, then assume corrupt data and skip the row
                    if 0 == len(game.game_datetime):
                        continue
                    # Set some of the other Game fields that are easy to fill in
                    game.retrieval_datetime = retrieval_time_for_reference
                    game.retrieval_url = url
                    game.num_possible_outcomes = season.possible_outcomes
                    number_of_outcomes = season.possible_outcomes
                    # Now get the table cell - the link within it, actually - with participants
                    participants_link = tournament_table.find('tbody > tr').eq(i).find('td.table-participant > a')
                    participants = participants_link.text().split(' - ')
                    game.team_home = participants[0]
                    game.team_away = participants[1]
                    game.game_url = self.base_url + participants_link[0].attrib['href']
                    # Now get the table cell with overall score
                    overall_score_cell = tournament_table.find('tbody > tr').eq(i).find('td.table-score')
                    overall_score_string = overall_score_cell.text()
                    # Perform crude sanitization against various things appended to scores, like " OT"
                    overall_score_string = overall_score_string.split()[0]
                    # Home team/participant is always listed first in Odds Portal's scores
                    if ':' in overall_score_string:
                        game.score_home = int(overall_score_string.split(':')[0])
                        game.score_away = int(overall_score_string.split(':')[1])
                    elif '-' in overall_score_string:
                        game.score_home = int(overall_score_string.split('-')[0])
                        game.score_away = int(overall_score_string.split('-')[1])
                    else:
                        logger.warning('Could not split score string - delimiter unknown')
                        raise RuntimeError('Could not split score string - delimiter unknown')
                    # Based on the score we can infer the outcome, as follows...
                    if game.score_home > game.score_away:
                        game.outcome = 'HOME'
                    elif game.score_home < game.score_away:
                        game.outcome = 'AWAY'
                    else:
                        game.outcome = 'DRAW'
                    # Finally, get the cells with odds - either 2 or 3 depending on number of possible outcomes
                    individual_odds_links = tournament_table.find('tbody > tr').eq(i).find('td.odds-nowrp > a')
                    if len(individual_odds_links) < 2:
                        # Assume data corruption and skip to next row of tournament table
                        continue
                    elif number_of_outcomes != 2 and number_of_outcomes != 3:
                        raise RuntimeError('Unsupported number of outcomes specified - ' + str(number_of_outcomes))
                    for x, individual_odds_link in enumerate(individual_odds_links):
                        if 2 == number_of_outcomes:
                            if x == 0:
                                # home team odds
                                game.odds_home = individual_odds_link.text
                            else:
                                # away team odds - x must be 1
                                game.odds_away = individual_odds_link.text
                        elif 3 == number_of_outcomes:
                            if x == 0:
                                # home team odds
                                game.odds_home = individual_odds_link.text
                            elif x == 1:
                                # draw/tie odds
                                game.odds_draw = individual_odds_link.text
                            else:
                                # away team odds - x must be 2
                                game.odds_away = individual_odds_link.text
                    # And then, at this point, let's mark draw odds as None/null if only 2 outcomes
                    if number_of_outcomes == 2:
                        game.odds_draw = None
                    season.add_game(game)
                except Exception as e:
                    logger.warning('Skipping row, encountered exception - data format not as expected')
                    continue


if __name__ == '__main__':
    s = Scraper()
    s.go_to_link('https://www.oddsportal.com/basketball/usa/nba/results/#/page/27/')
    s.close_browser()
        