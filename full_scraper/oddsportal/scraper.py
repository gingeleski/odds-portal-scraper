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

# TODO: sync this with DEBUG in op.py
DEBUG=True

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
        if not DEBUG:
            self.options.add_argument('headless')
            logger.info('Chrome browser opened in headless mode')
        self.driver = webdriver.Chrome('./chromedriver/chromedriver', chrome_options=self.options)
        
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

    def get_populate_odds_method(self, season):
        return self.default_populate_odds if season.bet_type is None else self.populate_odds_detailed
        
    def default_populate_odds(self, season, game, game_row):
        number_of_outcomes = season.possible_outcomes
        # Get the cells with odds - either 2 or 3 depending on number of possible outcomes
        individual_odds_links = game_row.find('td.odds-nowrp > a')
        if len(individual_odds_links) < 2:
            # Assume data corruption and skip to next row of tournament table
            raise RuntimeError('Data is corrupt.')
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

    def cssselect_one(self, el, selector):
        """Helper class to select the first result of lxml.cssselect"""
        try:
            return el.cssselect(selector)[0]
        except IndexError:
            return None
        
    def process_row(self, season, row):
        lines = row.cssselect('td.right')
        # Throws AttributeError if lines are not as expected.
        odds = [line.text for line in lines if line.text is not None]

        if not odds:
            # Odds will be empty for bookmaker odds rows, which have text nested inside a div that controls hover.
            # Throws AttributeError if lines are not as expected.
            odds = [line.find('div').text for line in lines]

        # Make sure that odds have been found for all outcomes, otherwise there is no guarantee the odds matched with the 
        # correct outcome.
        if len(odds) != season.possible_outcomes:
            raise ValueError
        
        try:
            return dict(list(zip(season.outcome_headers, odds)))
        except TypeError:
            # If season.outcome_headers is None, zip raises TypeError, not AttributeError.
            # No headers defined, so default to integer headers.
            return dict(list(zip([i for i in range(0, season.possible_outcomes)], odds)))  

    def scrape_odds_detailed(self, season, game_link, tc):
        """This method is using lxml objects."""
        game_odds = {}

        odds_sources = {s.lower() for s in season.odds_sources}

        # get the 2 rows from the footer table
        o = {'average': self.cssselect_one(tc, 'tr.aver'), 'highest': self.cssselect_one(tc, 'tr.highest')}
        for name, row in o.items():
            # If no odds_sources are specified, then try and get them all.
            if len(odds_sources) == 0 or name in odds_sources:
                try:
                    game_odds[name] = self.process_row(season, row)
                except (AttributeError, ValueError):
                    logger.warning(f'Some problem occurred parsing odds. Could not get odds from {row}. Link: {game_link}')
                    
        sportsbook_rows = tc.cssselect('tbody > tr.lo')
        
        for row in sportsbook_rows:
            try:
                book_link = self.cssselect_one(row, 'td > span.ico-bookmaker-detail > a').attrib['href']
                # book_link = s.cssselect('td > span.ico-bookmaker-detail > a')[0].attrib['href']
            except AttributeError:
                # row is None
                continue
            try:
                # Link is of the form '/bookmaker/pinnacle/link'.
                name = book_link.split('/')[2]
                if name in odds_sources:
                    try:
                        game_odds[name] = self.process_row(season, row)
                    except (AttributeError, ValueError):
                        logger.warning(f'Some problem occurred parsing odds. Could not get odds from {row}. Link: {game_link}')
            except IndexError:
                # The Link does not have the expected form.
                logger.warning(f'Some problem occurred parsing odds. Could not get odds from {row}. Link: {game_link}')
                continue
            
        return game_odds
    
    def open_rows(self, option_set):
        odds_table = self.driver.find_element_by_css_selector('div#odds-data-table')
        tcs = odds_table.find_elements_by_css_selector('div.table-container')
        # Iterate rows, clicking open matching rows
        for tc in tcs:
            try:
                tc_style = tc.get_attribute('style')

                # If table-container div has a style attribute, and its value is
                # 'display:none', then it is not visible, and it can be skipped.
                if 'display:none' in tc_style.replace(' ', ''):
                    continue

                # If table-container div has no style attribute, need to determine
                # whether it needs to be opened or not.
                # If it has a table element with class 'table-main', it is already
                # opened. Otherwise, open it if it is a target row.
                try:
                    tc.find_element_by_css_selector('table.table-main')
                    continue
                except NoSuchElementException:
                    pass

                a = tc.find_element_by_css_selector('a[onclick]')
                option = a.text.lower().strip()
                # If option_set is empty, then we want to open all rows.
                if len(option_set) == 0 or option in option_set:
                    a.click()

            except (AttributeError, NoSuchElementException):
                logger.warning(f'Some problem occurred parsing odds. Could not get odds from {tc}. Link: fooo')
            
    def populate_odds_detailed(self, season, game, game_row):
        # game_row parameter is not being used. Just matching signature with default.
        
        # save URL
        season_url = self.driver.current_url

        game_href = game_row.find('td.table-participant > a').attr.href
        game_link = f"{self.base_url}{game_href}#{season.bet_type}"
        if season.sub_bet_type is not None:
            game_link += f";{season.sub_bet_type}"
        try:
            self.go_to_link(game_link)
        except WebDriverException:
            logger.warning(f'Link is malformed. Could not get odds for game. Link: {game_link}')
            return

        # For some games, desired bet type not available. If so, URL will be different from expected URL.
        if self.driver.current_url != game_link:
            logger.warning(f'Odds for bet type combination not available for this game. Link: {game_link}')
            self.driver.get(season_url)
            return
           
        if season.bet_options is not None:
            self.open_rows({o.lower() for o in season.bet_options})
        
        # Freeze html after opening rows.
        pq = pyquery(self.get_html_source())

        odds_table = pq.find('div#odds-data-table')
        tcs = odds_table.find('div.table-container')

        # If bet_options is None then we should be in the only table container.
        if season.bet_options is None:
            try:
                game.odds = self.scrape_odds_detailed(season, game_link, tcs[0])
            except IndexError:
                logger.warning(f'Some problem occurred parsing odds. Could not get odds from {s}. Link: {game_link}')
                return
        # Otherwise, we need to go into each table row individually.
        else:
            # Create set of options for constant time access.
            option_set = {o.lower() for o in season.bet_options}
            # Use this to preserve case in output JSON.
            bet_options_lower = {opt.lower(): opt for opt in season.bet_options}

            # Each tc is an lxml object.
            for tc in tcs:
                try:
                    style = tc.get('style')

                    # Don't want any elements that aren't visible.
                    try:
                        if 'display:none' in style.replace(' ', ''):
                            continue
                    except AttributeError:
                        # Displayed elements do not have a style attribute.
                        pass
                    
                    try:
                        a = tc.cssselect('div > strong > a[onclick]')[0]
                    except IndexError:
                        # If there is no anchor tag for some reason, the table container is not formed as expected,
                        # so go to the next one.
                        continue
                    
                    option = a.text.lower().strip()
                    if len(option_set) == 0 or option in option_set:
                        game_odds = self.scrape_odds_detailed(season, game_link, tc)
                        try:
                            game.odds[bet_options_lower[option]] = game_odds
                        except KeyError:
                            game.odds[option] = game_odds
                            
                except NoSuchElementException:
                    pass

        # restore URL
        self.driver.get(season_url)

    def populate_games_into_season(self, season):
        """
        Params:
            season (Season) with urls but not games populated, to modify
        """
        populate_odds = self.get_populate_odds_method(season)

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

                    game_row = tournament_table.find('tbody > tr').eq(i)
                    try:
                        populate_odds(season, game, game_row)
                    except RuntimeError:
                        # If something happened we need to make sure it defaults to the correct URL.
                        if self.driver.current_url != url:
                            self.driver.get(url)
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
        