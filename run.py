#load misc modules
from datetime import datetime
import time

# Load my modules
from modules import date_control, email_gen, delete, clean, scraper
from config import config

"""
AUTHOR: Daniel Simmons-Ritchie

ABOUT: This program is designed to scrape Pa. restaurant inspections and send an email summarizing violators and non-violators.

OVERVIEW: Main program loop runs in 'main' function of Program.py.
Program conditions and desired counties/cities to scrape are set at the top of main.
The program flows as follows:

    - Delete old data from previous runs 
    - For every city/county scraped:
        - Scrape data
        - Clean and sort data
        - Save data to text file
    - Send email with text file

OPTIONS:

- At the top of main, a range of variables can be altered to change how the program runs.

"""


def main():
    ### SETTINGS
    run_headless = True # Select true to run in headless mode (no Chrome window will display as scraping occurs) or False for non-headless
    email_style = "list" # choose 'table' to send inspection data as table, choose 'list' to send as list to make it easier to copy and paste
    location_list = [("county","adams")] # set areas to be scraped as list of tuples: (county/city, name). Eg. ("city", "harrisburg") or ("county","dauphin").
    timeframe = ("sun_to_sat", 3) # This sets timeframe to scrape as tuple, options: 'sun_to_sat' or 'mon_to_sun'. Desired weeks back is any integer. Eg. ("sun_to_sat",2)

    ### DELETE EMAIL PAYLOAD FROM LAST RUN
    delete.delete_temp_files()

    ### GET PROGRAM START TIME FOR EMAIL PAYLOAD
    program_start_time = datetime.now()

    ### INITIALIZE CHROME DRIVER
    driver = scraper.initialize_chrome_driver(run_headless, config)

    ### SCRAPE LOOP
    for location in location_list:

        ### GET SCRAPE START TIME
        start_time = time.time()

        ### RESTAURANT INSPECTION DATA SCRAPE
        inspection_data = scraper.scrape_search_results(driver, location, timeframe)

        ### GET SCRAPE END TIME
        scrape_time = date_control.run_time_calculator(start_time)

        ### CHANGING ORDER OF INSPECTION DATA
        inspection_data = clean.inspection_data_sort_by_violator(inspection_data)

        ### CLEANING AND FORMATTING DATA
        inspection_data = clean.clean_data(inspection_data)

        ### GENERATE EMAIL PAYLOAD
        email_gen.email_payload(email_style, inspection_data, location, scrape_time)

    ### SEND EMAIL
    email_gen.email_send(config, program_start_time, timeframe)

    driver.quit()
    print("Program finished")



# Start main loop if running from program.py
if __name__ == '__main__':
    main()
