"""scraper.py

Odds Portal user predictions scraper

"""

from pyppeteer import launch

import asyncio
import os

# Constants related to emulating a "real user" in the browser
USER_AGENT_STRING = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
VIEWPORT_DICT = { 'width' : 1920 , 'height' : 1080 }


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
    # Log in via that button
    page.click(login_button_selector)
    # Wait for post-login redirect(s) to happen
    # TODO
    # Make sure everything looks right here, otherwise warn login might've been bad
    # TODO
    # Navigate to personal profile now
    # TODO

    # TODO continue from here

    page.content()
    await browser.close()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
