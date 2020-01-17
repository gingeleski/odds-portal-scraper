
# Odds Portal user predictions scraper

Gets all future predictions from users you follow, saving them off into `output/`.

## Setup

This was developed and tested with Python 3.6 so compatibility with other versions is not assured.

It's recommended you set up a virtual environment to contain this project, included below. These are Powershell instructions and may need adjustment for other shells.

```powershell
cd predictions

# Sets up virtual environment in a directory named 'venv'
python -m venv venv

# Activate the virtual env
./venv/scripts/activate.ps1

# Install requirements/dependencies
pip install -r requirements.txt
```

Finally, set your OddsPortal username and password as environment variables `ODDS_PORTAL_USERNAME` and `ODDS_PORTAL_PASSWORD`, respectively. ([**See this for help**](https://www.twilio.com/blog/2017/01/how-to-set-environment-variables.html))

Now you're set up. Note the virtual environment is still active, a good state for us to get into running this.

Note that pyppeteer will download an executable for Chrome the first time it runs. This project depends on headless Chrome.

## Usage

```powershell
# Run the scraper
python scraper.py

# When you're finally done, make sure to deactivate the virtual env!
deactivate
```

You should see at least one directory now in `output/`. Output directories from this scraper are named with Unix-style times.

Contents in those are text files and pictures with self-explanatory file names.

## More detail on what it does

In chronological order...

- Reads your Odds Portal username from environment variable `ODDS_PORTAL_USERNAME`
- Reads your Odds Portal password from environment variable `ODDS_PORTAL_PASSWORD`
- Logs into Odds Portal as you
- Navigates to your personal user profile
    - Scrape all the users you follow
- *Terminate here if you don't follow any users*
- Make a new directory in `output/` named as the current Unix-style time
- For each user you follow...
    - Navigate to their future predictions initial page
    - *Continue to next user right now if there are no future predictions out*
    - For each page of this user's future predictions...
        - Save a screenshot off of this page as `{theirusername}_###.png`
        - For each prediction on the page...
            - Get pertinent HTML snippet
            - Write this HTML out to `{theirusername}_###.txt`
