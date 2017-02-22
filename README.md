# Odds Portal Scraper
Sports odds and score scraper for Odds Portal.

## Setup
These instructions are for Windows Powershell. There will be some differences
for OSX / MacOS, like how you activate the virtual environment. Before the
scraper will work correctly, you'll need to put the [Chromium web driver](https://sites.google.com/a/chromium.org/chromedriver/)
(chromedriver.exe) inside of the *chromedriver* directory.
```
# Get into a new virtualenv
virtualenv venv
.\venv\Scripts\activate.ps1

# Install the requirements
pip install -r requirements.txt

# Scrape!
python scrape.py

# Then eventually when you're done...
deactivate
```
