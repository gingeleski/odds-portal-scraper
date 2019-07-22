
# oddsporter

Comprehensive scraping utility for Odds Portal (oddsportal.com) results.

*Note this has now been released and is maintained in [**gingeleski/odds-portal-scraper**](https://github.com/gingeleski/odds-portal-scraper/tree/master/full_scraper).*

## Compatibility

This software has been tested to run successfully on the following sports/leagues:

- NBA (American basketball)
- NHL (American hockey)
- NFL (American football)
- AFL (Australian football)
- NRL (Australian rugby)

Other support may be possible by modifying `config/sports.json` - read on for more information.

## Setup

You should have Python 3.6 or later installed and on your path. This hasn't been tested with earlier versions of Python.

Before the scraper will work correctly, you'll need to put the [Chromium web driver](https://sites.google.com/a/chromium.org/chromedriver/) (chromedriver.exe) inside of the *chromedriver* directory. Download that and extract the file. This software expects an `.exe` so, if your binary's extension is something different, it's probably easiest to just rename it in there.

Google Chrome should also be installed, ideally at the equal version of the web driver.

Below instructions are for Windows Powershell. There will be some differences for OS X / MacOS, like in activating the virtual environment and using the web driver.

```
cd <this_project_root>

# Get into a new virtualenv
python -m venv venv
./venv/Scripts/activate

# Install the requirements
pip install -r requirements.txt

# Print out help for running the program
python op.py --help

# Run the program
python op.py

# Then eventually when you're done...
deactivate
```

## Running

By default, the program will scrape all available results for the history of what's specified in `config/sports.json`.

```
python op.py
```

As of this writing, the configured sports/leagues encompass the following:

- NBA (American basketball)
- NHL (American hockey)
- NFL (American football)
- AFL (Australian football)
- NRL (Australian rugby)

It may be possible to scrape other sports/leagues by adding them to the JSON file. This has not been explicitly tested but seems quite possible given the comprehensive nature of this software.

## Outputs

While the program runs, it will print out some log information to the console and also to a timestamped file under `logs/`.

After completion, see the directory `output/`, under which will be populated JSON files of the scraped results.

There will be one JSON file per sport/league - i.e. `NBA.json`

The specific subdirectories where things go are dictated in `config/sports.json` and you should note that folders of sports/leagues other than your current run are *not* modified or deleted.

## Known quirks / bugs

- Software crashes entirely if Internet is lost or disconnects
    - Exception handling for this hasn't been written into the logic
- Scraping multiple sports/leagues in a consecutive run can result in a crash
    - This was problematic enough that I wrote in that little sub-menu for you to pick a single sport to run on
    - Safety not guaranteed when running on all sports at once
- Some data accuracy loss if software is run without sufficient wait times ("too fast")
    - It's been observed that an inadequate wait time specified for Odds Portal pages causes...
        - The source URL fields of Game objects to be incorrect
        - Games towards the end of the season to disappear
            - Seemingly related to the first point as the scraper thinks it's farther along than it really is
    - The default 3 second wait time should be sufficient to avoid this
        - However this is ultimately dependent on factors like your hardware, network latency, etc.
- *Add further bugs/quirks under Issues*

## Disclaimer

*By cloning the source code or using the software, you have read and agree to all of the following...*

*This software has been intended for educational use only. You release the author(s) from any responsibility for how you use this software.*

*While it's possible to "cloak" a scraper to avoid detection by the target, none of those measures have been taken here, as of this writing. Perhaps this isn't the most obvious scraper in the world but it's loud enough to detect and actively block. Besides behavioral detection/blocking, one might also get blacklisted based on IP address or other identifiable markers.*

*The software is provided as-is. Odds Portal is a difficult website to scrape - thus the quirks/bugs disclosed earlier in this document.*

*It may be against Odds Portal's terms and conditions to scrape their website. You acknowledge this and, again, the author(s) are not responsible for how you use this.*
