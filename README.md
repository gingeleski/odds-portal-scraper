# Odds Portal Scraper
Sports odds and score scraper for Odds Portal.

## Setup
These instructions are for Windows Powershell. You'll need Visual C++ Build
Tools installed for the requirement of scrapy. There will be some differences
for OSX / MacOS, like how you activate the virtual environment.
```
# Get into a new virtualenv
virtualenv venv
.\venv\Scripts\activate.ps1

# Install the requirements
pip install -r requirements.txt

# Scrape!
scrapy runspider scrape.py
```
