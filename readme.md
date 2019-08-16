## PA. RESTAURANT INSPECTION SCRAPER

This program scrapes county or city restaurant inspections from the Pa. Dept of Agriculture website and then emails a summary of violators and non-violators to a chosen email address

### Prerequisites

To run you will need: 

- Python 3.6+

- Google Chrome installed and located in your applications folder.

- Chromedriver. Here's a guide for [installing on Mac](http://jonathansoma.com/lede/foundations-2017/classes/more-scraping/selenium/) (pretty easy) and 
here's a guide for [installing on Ubuntu 16.04 or 18.04](https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/) (a little trickier but not too bad).

- In order for the program to send emails with the scraped data, you'll 
need a gmail account. The program will log into this account to do the actual sending. You'll likely need to make sure that your gmail settings allow "less secure app access". You can find this under gmail's security settings. If you don't feel comfortable adjusting this setting on your personal gmail address, I suggest creating a new one. 


### Config

In order for the program to send you an email with summarized info, you'll need a gmail account. This account does the actual sending. You'll likely need to make sure that your gmail settings allow "Less secure app access". You can find this under security settings.

If you don't feel comfortable adjusting this setting on your personal gmail address, I suggest creating a new one. 

When you have decided on what gmail address to use. Create a file called config.py at the root of the program directory and add a dictionary called 'config':

Where indicated in caps, replace with your own values, preserving the quotation marks. You can enter as few or as many destination email addresses as you like:

    config = {
        "email": {
            'username': 'ENTER_YOUR_GMAIL_ADDRESS',
            'pass': 'ENTER_YOUR_PASSWORD'
        },
        "destination": [
            "ENTER_EMAIL_ADDRESS1",
            "ENTER_EMAIL_ADDRESS2",
            "ENTER_EMAIL_ADDRESS3",
        ],
         "chrome_driver_path": "FULL_PATH_TO_CHROME_DRIVER",
    }

Once you've created that file, you can then adjust settings at the top of main() in program.py. You can specify specific counties/cities you would like to scrape.

### Install & run

1) In the terminal, clone this repo:

    `git clone https://github.com/SimmonsRitchie/pa_restaurant_inspection_scraper.git`

2) cd into project folder:

    `cd court_docket_scraper`

3) Install dependencies:

    `pip install -r requirements.txt`

4) Run:

    `python run.py`
