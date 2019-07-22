"""
crawler.py

Logic for the overall Odds Portal scraping utility focused on crawling

"""


from .models import Season
from pyquery import PyQuery as pyquery
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException

import logging
import time


logger = logging.getLogger(__name__)


class Crawler(object):
    """
    A class to crawl links from oddsportal.com website.
    Makes use of Selenium and BeautifulSoup modules.
    """
    WAIT_TIME = 3  # max waiting time for a page to load
    
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
            # If no Login button, page not found
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

    def get_seasons_for_league(self, main_league_results_url):
        """
        Params:
            (str) main_league_results_url e.g. https://www.oddsportal.com/hockey/usa/nhl/results/

        Returns:
            (list) urls to each season for given league
        """
        seasons = []
        logger.info('Getting all seasons for league via %s', main_league_results_url)
        if not self.go_to_link(main_league_results_url):
            logger.error('League results URL loaded unsuccessfully %s', main_league_results_url)
            # Going to send back empty list so this is not processed further
            return seasons
        html_source = self.get_html_source()
        html_querying = pyquery(html_source)
        season_links = html_querying.find('div.main-menu2.main-menu-gray > ul.main-filter > li > span > strong > a')
        logger.info('Extracted links to %d seasons', len(season_links))
        for season_link in season_links:
            this_season = Season(season_link.text)
            # Start the Season's list of URLs with just the root one
            this_season_url = self.base_url + season_link.attrib['href']
            this_season.urls.append(this_season_url)
            seasons.append(this_season)
        return seasons
    
    def fill_in_season_pagination_links(self, season):
        """
        Params:
            (Season) object with just one entry in its urls field, to be modified
        """
        first_url_in_season = season.urls[0]
        self.go_to_link(first_url_in_season)
        html_source = self.get_html_source()
        html_querying = pyquery(html_source)
        # Check if the page says "No data available"
        no_data_div = html_querying.find('div.message-info > ul > li > div.cms')
        if no_data_div != None and no_data_div.text() == 'No data available':
            # Yes, found "No data available"
            logger.warning('Found "No data available", skipping %s', first_url_in_season)
            return
        # Just need to locate the final pagination tag
        pagination_links = html_querying.find('div#pagination > a')
        # It's possible, however, there is no pagination...
        if len(pagination_links) <= 1:
            return
        last_page_number = -1
        last_page_url = None
        for link in reversed(pagination_links):
            span = link.find('span')
            if span != None and span.text != None and '»|' in span.text:
                # This is the last link because it has these two characters in it...
                last_page_number = int(link.attrib['x-page'])
                last_page_url = first_url_in_season + link.attrib['href']
                break
        # If the last page number was set, the page format must've changed - RuntimeError
        if last_page_number == -1:
            logger.error('Could not locate final page URL from %s', first_url_in_season)
            raise RuntimeError('Could not locate final page URL from %s', first_url_in_season)
        for i in range(2,last_page_number):
            this_url = last_page_url.replace('page/' + str(last_page_number), 'page/' + str(i))
            season.urls.append(this_url)
        season.urls.append(last_page_url)
