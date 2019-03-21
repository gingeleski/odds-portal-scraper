# Odds Portal Scraper
Sports odds and score scraper for Odds Portal.

## Current Support
Soccer only.

See the directory *./leagues/soccer* for how the input JSON is formatted. In this way you specify what you want to scrape.

## Setup
These instructions are for Windows Powershell. There will be some differences for OS X / MacOS, like in activating the virtual environment and using the web driver.

Before the scraper will work correctly, you'll need to put the [Chromium web driver](https://sites.google.com/a/chromium.org/chromedriver/) (chromedriver.exe) inside of the *chromedriver* directory. You may also need to update the path to `chromedriver` in the script.

```
# Get into a new virtualenv
virtualenv venv
.\venv\Scripts\activate.ps1

# Install the requirements
pip install -r requirements.txt

# Scrape and populate the database
python run.py

# Then eventually when you're done...
deactivate
```
Then you have your SQLite .db file to analyze how you wish.
