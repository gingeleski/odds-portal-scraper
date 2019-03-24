"""scraper.py

Odds Portal user predictions scraper

"""

from pyppeteer import launch

import asyncio
import os


# Constants related to emulating a "real user" in the browser
USER_AGENT_STRING = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
VIEWPORT_DICT = { 'width' : 1920 , 'height' : 1080 }


class Prediction():
    def __init__(self):
        self.sport = str()
        self.region = str()
        self.league = str()
        self.start_time = str()
        self.game_name = str()
        self.game_specifier = str()
        self.url = str()
        self.odds = ['','','']
        self.pick = -1

    def __repr__(self):
        return 'TODO'


async def main():
    # Set up headless browser and a page within it to work out of
    browser = await launch()
    page = await browser.newPage()
    page.setUserAgent(USER_AGENT_STRING)
    page.setViewport(VIEWPORT_DICT)
    # Read in Odds Portal username from environment variable ODDS_PORTAL_USERNAME
    try:
        username = os.environ['ODDS_PORTAL_USERNAME']
    except:
        raise RuntimeError('Could not read environment variable ODDS_PORTAL_USERNAME')
    # Read in Odds Portal password from environment variable ODDS_PORTAL_PASSWORD
    try:
        password = os.environ['ODDS_PORTAL_PASSWORD']
    except:
        raise RuntimeError('Could not read environment variable ODDS_PORTAL_PASSWORD')
    # Navigate to Odds Portal login page
    await page.goto('https://www.oddsportal.com/login/')
    # Get a selector for the username field by running some JavaScript
    username_selector = page.evaluate('TODO')
    # Get username field into focus then type into it
    page.click(username_selector)
    page.keyboard.type(username)
    # Get a selector for the password field by running some JavaScript
    password_selector = page.evaluate('TODO')
    # Get password field into focus then type into it
    page.click(password_selector)
    page.keyboard.type(password)
    # Get a selector for the submit button by running some JavaScript
    login_button_selector = page.evaluate('TODO')
    # Log in via that button then wait for redirect(s) to happen
    await asyncio.wait([
        page.click(login_button_selector),
        page.waitForNavigation(),
    ])
    # Use JavaScript to assert whether logout button is on page - otherwise assume error
    is_there_logout_button = page.evaluate('true')
    if False == is_there_logout_button:
        page.screenshot({ 'path' : 'assumed_error.png' })
        raise RuntimeError('Could not find logout button after login - see assumed_error.png !')
    # Get link to user profile
    my_profile_link = page.evaluate('https://www.oddsportal.com/profile/gingeleski/')
    # Navigate to personal profile now
    await page.goto(my_profile_link)
    # Get list of users we're following via JavaScript
    users_we_are_following = page.evaluate('["GGBet","OldTwinTowersFutbol"]')
    for user_we_are_following in users_we_are_following:
        link_to_users_predictions = 'https://www.oddsportal.com/profile/' + user_we_are_following + '/my-predictions/next/'
        this_output_folder = 'output/' + user_we_are_following
        await page.goto(link_to_users_predictions)
        this_users_predictions = []
        is_there_another_page = True
        page_count = 1
        while True == is_there_another_page:
            # Use JavaScript to determine if there are any predictions on the page
            are_there_predictions_on_page = page.evaluate('false')
            if True == are_there_predictions_on_page:
                html_for_page = page.content()
                # TODO scrape predictions off of page HTML
            # Save off image of this after checking if output directory exists
            if not os.path.exists(this_output_folder):
                os.makedirs(this_output_folder)
            page_image_filename = user_we_are_following + '_' + page_count + '.png'
            page.screenshot({ 'path' : this_output_folder + '/' + page_image_filename })
            # Use JavaScript to determine if there's another page
            is_there_another_page = page.evaluate('false')
            page_count += 1
    await browser.close()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
