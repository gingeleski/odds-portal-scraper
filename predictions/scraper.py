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
        s = str()
        s += 'Sport: ' + self.sport
        s += 'Region: ' + self.region
        s += 'League: ' + self.league
        s += 'Start time: ' + self.start_time
        s += 'Game name: ' + self.game_name
        s += 'Game specifier: ' + self.game_specifier
        s += 'URL: ' + self.url
        s += 'Odds: ' + str(self.odds)
        s += 'Pick: ' + str(self.pick)
        return s


async def main():
    # Set up headless browser and a page within it to work out of
    browser = await launch()
    page = await browser.newPage()
    await page.setUserAgent(USER_AGENT_STRING)
    await page.setViewport(VIEWPORT_DICT)
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
    # Inject script onto the page so we can leverage jQuery to get unique selectors later on
    await page.evaluate('jQuery.fn.getPath=function(){for(var e,r=this;r.length;){var t=r[0],n=t.localName;if(!n)break;n=n.toLowerCase();var a=r.parent(),h=a.children(n);h.length>1&&(n+=":eq("+h.index(t)+")"),e=n+(e?">"+e:""),r=a}return e};')
    # Get a selector for the username field by running some JavaScript
    username_selector = await page.evaluate('if($(\'label:contains("sername")\').length<1){"ERROR"}else{var target_id=$(\'label:contains("sername")\').attr(\'for\');target_id}')
    if username_selector == 'ERROR':
        await page.screenshot({ 'path' : 'assumed_error.png' })
        raise RuntimeError('Encountered issue trying to find username field at login form - see assumed_error.png !')
    username_selector = 'input#' + username_selector 
    # Get username field into focus then type into it
    await page.waitForSelector(username_selector, {'timeout':5000})
    await page.click(username_selector)
    await page.keyboard.type(username)
    # Get a selector for the password field by running some JavaScript
    password_selector = await page.evaluate('if($(\'label:contains("assword")\').length<1){"ERROR"}else{var target_id=$(\'label:contains("assword")\').attr(\'for\');target_id}')
    if password_selector == 'ERROR':
        await page.screenshot({ 'path' : 'assumed_error.png' })
        raise RuntimeError('Encountered issue trying to find password field at login form - see assumed_error.png !')
    password_selector = 'input#' + password_selector
    # Get password field into focus then type into it
    await page.click(password_selector)
    await page.keyboard.type(password)
    # Get a selector for the submit button by running some JavaScript
    login_button_selector = await page.evaluate('if($(\'button:contains("ogin")\').length<2){"ERROR"}else{$(\'button:contains("ogin"):eq(1)\').getPath()}')
    if login_button_selector == 'ERROR':
        await page.screenshot({ 'path' : 'assumed_error.png' })
        raise RuntimeError('Encountered issue trying to find login button at login form - see assumed_error.png !')
    # Log in via that button then wait for redirect(s) to happen
    await asyncio.wait([
        await page.click(login_button_selector),
        await page.waitForNavigation(),
    ])
    # Use JavaScript to assert whether logout button is on page - otherwise assume error
    is_there_logout_button = await page.evaluate('if($(\'li#user-header-logout > a:contains("Logout")\').length<1){"ERROR"}')
    if is_there_logout_button == 'ERROR':
        await page.screenshot({ 'path' : 'assumed_error.png' })
        raise RuntimeError('Could not find logout button after login - see assumed_error.png !')
    # Get link to user profile with followed users showing
    my_username = await page.evaluate('$("div#user-header-r2 > ul > li#user-header-predictions > a").attr("href")')
    my_username = my_username.replace('/profile/','').replace('/my-predictions/','')
    my_profile_link = await page.evaluate('https://www.oddsportal.com/profile/' + my_username + '/#following')
    # Navigate to personal profile now
    await page.goto(my_profile_link)
    # Get list of users we're following via JavaScript
    users_we_are_following = await page.evaluate('$("div#profile-following > div > div.item > div.content > a.username").map(function(){return $(this).attr("title");}).get();')
    for user_we_are_following in users_we_are_following:
        link_to_users_predictions = 'https://www.oddsportal.com/profile/' + user_we_are_following + '/my-predictions/next/'
        this_output_folder = 'output/' + user_we_are_following
        await page.goto(link_to_users_predictions)
        this_users_predictions = []
        is_there_another_page = True
        page_count = 1
        while True == is_there_another_page:
            # Use JavaScript to determine if there are any predictions on the page
            are_there_predictions_on_page = await page.evaluate('$("li.last > strong > span").length>0')
            if True == are_there_predictions_on_page:
                # Get inner HTML of each prediction
                html_list_for_predictions = await page.evaluate('$("table.prediction-table#prediction-table-1 > tbody > tr[xeid]").map(function() { return $(this).html(); }).get();')
                this_users_predictions += html_list_for_predictions
            # Save off image of this after checking if output directory exists
            if not os.path.exists(this_output_folder):
                os.makedirs(this_output_folder)
            page_image_filename = user_we_are_following + '_' + page_count + '.png'
            await page.screenshot({ 'path' : this_output_folder + '/' + page_image_filename })
            # Use JavaScript to determine if there's another page
            is_there_another_page = await page.evaluate('false') # TODO
            page_count += 1
        for i, single_prediction in enumerate(this_users_predictions):
            with open(this_output_folder + '/' + user_we_are_following + '_' + str(i) + '.txt', 'w') as text_file:
                text_file.write(str(single_prediction))
    await browser.close()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
