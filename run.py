"""
Run the Odds Portal scraping suite, processing all the present soccer league
JSON files in lexicographical order.
"""

from os import listdir, sep
from os.path import isfile, join
from Scraper import Scraper

soccer_match_path = "." + sep + "leagues" + sep + "soccer"

initialize_db = True

for possible_file in listdir(soccer_match_path):
    if isfile(join(soccer_match_path, possible_file)):
        soccer_match_json_file = join(soccer_match_path, possible_file)
        with open(soccer_match_json_file, "r") as open_json_file:
            json_str = open_json_file.read().replace("\n", "")
            match_scraper = Scraper(json_str, initialize_db)
            match_scraper.scrape_all_urls(True)
            if initialize_db is True:
                initialize_db = False