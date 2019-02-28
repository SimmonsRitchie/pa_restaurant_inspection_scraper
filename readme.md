## PA. RESTAURANT INSPECTION SCRAPER

This program scrapes county or city restaurant inspections from the Pa. Dept of Agriculture website and then emails a summary of violators and non-violators to a chosen email address


### Prerequisites

To run, you'll need python 3.6. You'll also need a copy of 'chromedriver', which is included in this repo.

### Configuration

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

### Authors

Daniel Simmons-Ritchie, reporter at the Patriot-News/PennLive.com
