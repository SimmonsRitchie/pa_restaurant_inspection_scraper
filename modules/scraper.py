#Load selenium modules
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

#load misc modules
from datetime import datetime, timedelta
from collections import namedtuple
import string




# load PDF miner imports
# From PDFInterpreter import both PDFResourceManager and PDFPageInterpreter
# Import this to raise exception whenever text extraction from PDF is not allowed

#load email modules

#load my modules
from modules import date_control

#This module handles scrape of Pa. restaurant inspections

InspectionData = namedtuple("InspectionData", ('restaurant', 'address', 'date','inspection_type', 'compliance', 'violator', 'violation'))
SlideshowData = namedtuple("SlideshowData", ('inspection_id', 'headline'))

def scrape_search_results(driver, location, timeframe):

    # Dept of Ag restaurant inspection URL for search
    url = "https://www.pafoodsafety.state.pa.us/web/inspection/publicinspectionsearch.aspx"

    # Setting date range for search
    startdate = date_control.start_date(timeframe).strftime('%m/%d/%Y')
    enddate = date_control.end_date(timeframe).strftime('%m/%d/%Y')

    # Parsing location tuples
    descriptor = location[0].capitalize()
    area = location[1].capitalize()
    print("Beginning search for inspections in {}...".format(area))

    # Opening webpage
    print("Opening inspection website")
    driver.get(url)

    # selecting start date
    print("Entering start date: {}".format(startdate))
    css_startdate = '#MainContent_dteInspectionBeginDate_txtDate'
    input_startdate = driver.find_element_by_css_selector(css_startdate)
    input_startdate.clear()
    input_startdate.send_keys(str(startdate))

    # selecting end date
    print("Entering end date: {}".format(enddate))
    css_enddate = '#MainContent_dteInspectionEndDate_txtDate'
    input_enddate = driver.find_element_by_css_selector(css_enddate)
    input_enddate.clear()
    input_enddate.send_keys(str(enddate))

    if descriptor == "County":
        # selecting county
        print("Entering county: {}".format(area))
        css_county = '#MainContent_wucStateCountiesFS_ddlCounty'
        input_county = Select(driver.find_element_by_css_selector(css_county))
        input_county.select_by_visible_text(area)
    elif descriptor == "City":
        # selecting city
        print("Entering city: {}".format(area))
        css_city = '#MainContent_txtCity'
        input_city = driver.find_element_by_css_selector(css_city)
        input_city.clear()
        input_city.send_keys(area)

    # Submit form
    print("Submitting form")
    css_submit = '#MainContent_btnSearch'
    driver.find_element_by_css_selector(css_submit).click()

    # Explicit wait - load search results
    css_results_table = "#MainContent_pnlResults"
    WebDriverWait(driver,120).until(EC.presence_of_element_located((By.CSS_SELECTOR,css_results_table)))
    # id_results_table = "MainContent_gvInspections"
    # WebDriverWait(driver,120).until(EC.presence_of_element_located((By.ID,id_results_table)))

    # Creating lists to store info from search results
    restaurant_list = []
    address_list = []
    date_list = []
    inspection_type_list = []
    compliance_list = []
    violator_list = []
    violation_list = []


    # Checking if there are any results, if not, then close program
    print("Checking if there are any search results")
    try:
        css_results_box = "#MainContent_gvInspections_gvInspections > tbody > tr:nth-child(2) > td"
        results_box_contents = driver.find_element_by_css_selector(css_results_box)
        results_box_contents = results_box_contents.text
        if "There are no records to display" in results_box_contents:
            print("No records detected")
            print("Terminating scraper")
            return InspectionData(restaurant_list, address_list, date_list, inspection_type_list, violator_list, violation_list)
    except:
        print("Search results detected")

    page_search_loop = True

    # Beginning page search loop and setting counter to 1
    print("Beginning page search loop")
    count_of_violators = 0
    count_of_nonviolators = 0
    page_search_counter = 1
    page_search_loop = True
    while page_search_loop is True:

        if page_search_counter > 1:
            try:
                print("Waiting for 'switching pages' popup appear")
                WebDriverWait(driver, 60).until(EC.text_to_be_present_in_element((By.ID,"theBody"), "Switching Pages"))
                print("'Switching pages' popup appeared'")
                print("Wait for 'switching pages' popup to disappear")
                WebDriverWait(driver, 60).until_not(EC.text_to_be_present_in_element((By.ID,"theBody"), "Switching Pages"))
                print("'Switching pages' popup disappeared - page {} loaded".format(page_search_counter))
            except:
                print("Something went awry while waiting for 'switching pages' popup to appear")
                print("Assuming new page has succesfully loaded...")

        print("Searching page {}".format(page_search_counter))
        row_count = 1

        # Beginning row search loop and settin counter to 1
        print("Beginning row search loop")
        search_row_loop = True
        while search_row_loop is True:
            try:
                # Checking whether row has violation text in selector
                css_violation = "#MainContent_gvInspections_lnkViolations_" + str(row_count - 1)
                violation_found = driver.find_element_by_css_selector(css_violation)

                print("Searching page {}, row {}".format(page_search_counter, row_count))

                # If violations found then scrape row data
                if violation_found.text:
                    # Noting status as violator in InspectionData named tuple
                    violator = "Yes"
                    violator_list.append(violator)

                    # Adding to violator counter
                    count_of_violators += 1

                    print("\n/\/\/\ FOUND: VIOLATOR ({}) /\/\/\ ".format(count_of_violators))

                    #scraping restaurant name and address
                    css_name_address_phone = "#MainContent_gvInspections > tbody:nth-child(1) > tr:nth-child(" + str(row_count + 1) + ") > td:nth-child(1)"
                    name_address_phone = driver.find_element_by_css_selector(css_name_address_phone)
                    parts = name_address_phone.text.split("\n")
                    restaurant_name = string.capwords(parts[0])
                    restaurant_address = string.capwords(parts[1])
                    restaurant_list.append(restaurant_name)
                    address_list.append(restaurant_address)
                    print("Restaurant: {}".format(restaurant_name))
                    print("Address: {}".format(restaurant_address))

                    # scraping inspection date
                    css_inspection_date = "#MainContent_gvInspections > tbody:nth-child(1) > tr:nth-child(" + str(row_count + 1) + ") > td:nth-child(2)"
                    inspection_date = driver.find_element_by_css_selector(css_inspection_date)
                    inspection_date = inspection_date.text
                    date_list.append(inspection_date)
                    print("Inspection date: {}".format(inspection_date))

                    # scraping inspection type
                    css_inspection_type = "#MainContent_gvInspections > tbody:nth-child(1) > tr:nth-child(" + str(row_count + 1) + ") > td:nth-child(3)"
                    inspection_type = driver.find_element_by_css_selector(css_inspection_type)
                    inspection_type = inspection_type.text
                    inspection_type_list.append(inspection_type)
                    print("Inspection type: {}".format(inspection_type))

                    # scraping compliance status
                    css_compliance = "#MainContent_gvInspections > tbody:nth-child(1) > tr:nth-child(" + str(row_count + 1) + ") > td:nth-child(4)"

                    compliance = driver.find_element_by_css_selector(css_compliance)
                    compliance = compliance.text
                    compliance_list.append(compliance)
                    print("Compliance: {}".format(compliance))


                    # Opening violation pop up
                    driver.find_element_by_css_selector(css_violation).click()

                    # Explicit wait - load violation pop up
                    id_violation_box = "tbPublicInspectionMain"
                    WebDriverWait(driver, 120).until(EC.visibility_of_element_located((By.ID, id_violation_box)))

                    violations_search_loop = True
                    violation_counter = 0
                    violation_collection = ""
                    while violations_search_loop is True:
                        try:
                            css_violation_item = "#MainContent_wucPublicInspectionViolations_rptViolations_pnlComments_" + str(violation_counter)
                            violation_item = driver.find_element_by_css_selector(css_violation_item)
                            violation_collection = violation_collection + violation_item.text.strip("Inspector Comments")
                            violation_collection = violation_collection.lstrip().rstrip()
                            violation_counter += 1
                        except NoSuchElementException:
                            break

                    print(violation_collection)
                    print()
                    violation_list.append(violation_collection)

                    # Explicit wait - ensure exit button is loaded
                    css_exit = '#cboxClose'
                    WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_exit)))

                    # click exit button
                    driver.find_element_by_css_selector(css_exit).click()

                    # Explicit wait - ensure violation pop up is closed
                    id_violation_box = "tbPublicInspectionMain"
                    WebDriverWait(driver, 60).until_not(EC.visibility_of_element_located((By.ID, id_violation_box)))

                else:
                    # ELSE: This is a nonviolator. Note: A lot of this code is pretty sloppy and repeats much from the previous IF.
                    # At a later point I should consolidate this with the above.

                    # Noting status as nonviolator in InspectionData named tuple
                    violator = "No"
                    violator_list.append(violator)

                    # Adding empty string to violation list
                    violation = "None found"
                    violation_list.append(violation)

                    # Adding to violator counter
                    count_of_nonviolators += 1

                    print("\n/\/\/\ FOUND: NON-VIOLATOR ({}) /\/\/\ ".format(count_of_nonviolators))

                    #scraping restaurant name and address
                    css_name_address_phone = "#MainContent_gvInspections > tbody:nth-child(1) > tr:nth-child(" + str(row_count + 1) + ") > td:nth-child(1)"
                    name_address_phone = driver.find_element_by_css_selector(css_name_address_phone)
                    parts = name_address_phone.text.split("\n")
                    restaurant_name = string.capwords(parts[0])
                    restaurant_address = string.capwords(parts[1])
                    restaurant_list.append(restaurant_name)
                    address_list.append(restaurant_address)
                    print("Restaurant: {}".format(restaurant_name))
                    print("Address: {}".format(restaurant_address))

                    # scraping inspection date
                    css_inspection_date = "#MainContent_gvInspections > tbody:nth-child(1) > tr:nth-child(" + str(row_count + 1) + ") > td:nth-child(2)"
                    inspection_date = driver.find_element_by_css_selector(css_inspection_date)
                    inspection_date = inspection_date.text
                    date_list.append(inspection_date)
                    print("Inspection date: {}".format(inspection_date))

                    # scraping inspection type
                    css_inspection_type = "#MainContent_gvInspections > tbody:nth-child(1) > tr:nth-child(" + str(row_count + 1) + ") > td:nth-child(3)"
                    inspection_type = driver.find_element_by_css_selector(css_inspection_type)
                    inspection_type = inspection_type.text
                    inspection_type_list.append(inspection_type)
                    print("Inspection type: {}".format(inspection_type))

                    # scraping compliance status
                    css_compliance = "#MainContent_gvInspections > tbody:nth-child(1) > tr:nth-child(" + str(row_count + 1) + ") > td:nth-child(4)"
                    compliance = driver.find_element_by_css_selector(css_compliance)
                    compliance = compliance.text
                    compliance_list.append(compliance)
                    print("Compliance: {}".format(compliance))

                row_count += 1

            except NoSuchElementException:
                print("No more rows found")
                break

        #Going to next page and adding page to page counter
        page_search_counter += 1
        try:
            # Attempting to click next page if it exists
            print("Checking if there are more pages...")
            css_page = ".GridPager > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(" + str(page_search_counter) + ") > a:nth-child(1)"
            driver.find_element_by_css_selector(css_page).click()
            print("Another page found - going to next page")
        except NoSuchElementException:
            print("No further pages found")
            break

    #Returning list of lists with inspection data
    print("Scraping of {} inspections complete".format(area))
    print("Saving inspection data in InspectionData named tuple")
    return InspectionData(restaurant_list, address_list, date_list, inspection_type_list, compliance_list, violator_list, violation_list)


def initialize_chrome_driver(run_headless, config):
    # this directs selenium to initialize chrome in either normal or headless mode and tells it where to find chromedriver

    print("\nInitializing Chrome in local testing mode")
    options = webdriver.ChromeOptions()
    if run_headless:
        options.add_argument('-headless')
        options.add_argument('--no-sandbox')
    executable_path = config["chrome_driver_path"]
    driver = webdriver.Chrome(chrome_options=options,executable_path=executable_path)
    return driver



def date_range(desired_day_range, weeks):

    start = start_date(desired_day_range, weeks)
    end = end_date(desired_day_range, weeks)

    # If the month of the start date and end date is the same then format like 'Aug 5-11', else format like July 29-Aug 5
    if start.strftime('%b') == end.strftime('%b'):
        date_for_headline = start.strftime('%b ') + start.strftime('%d').lstrip('0') + "-" + end.strftime('%d').lstrip('0')
    else:
        date_for_headline = start.strftime('%b ') + start.strftime('%d').lstrip('0') + "-" + end.strftime('%b ') + end.strftime('%d').lstrip('0')

    # Shortening month names
    date_for_headline = date_for_headline.replace('Mar', 'March').replace('Jul', 'July').replace('Jun', 'June')
    return date_for_headline


def start_date(desired_day_range, weeks):

    # This sets days as integers. Sunday = 1, Saturday = 2, Friday = 3, etc.
    if desired_day_range == "sun_to_sat":
        desired_start_day = 1
    elif desired_day_range == "mon_to_sun":
        desired_start_day = 0

    # today's date
    today = datetime.today()

    # today converted into a number: Monday is 0 and Sunday is 6
    today_as_integer = today.weekday()

    # Calculating most recent Sunday by substracting today_as_integer from today's date
    # Adding 1 to today_as_integer to get most recent Sunday. 2= most recent Sat, 3= most recent Fri, etc
    subtraction_num = today_as_integer + desired_start_day
    most_recent_desired_start_day = today - timedelta(subtraction_num)

    # Calculating how many weeks back
    weeks_back = weeks * 7
    start_date = most_recent_desired_start_day - timedelta(weeks_back)

    # Date is returned in time format and needs to be formatted
    return start_date


def end_date(desired_day_range, weeks):

    # This sets days as integers. Sunday = 1, Saturday = 2, Friday = 3, etc.
    if desired_day_range == "sun_to_sat":
        desired_end_day = 2
    elif desired_day_range == "mon_to_sun":
        desired_end_day = 1

    # Because this is calculating end date, subtracting 1 week from weeks
    weeks = weeks - 1

    # today's date
    today = datetime.today()

    # today converted into a number: Monday is 0 and Sunday is 6
    today_as_integer = today.weekday()

    # Calculating most recent Sunday by substracting today_as_integer from today's date
    # Adding 1 to today_as_integer to get most recent Sunday. 2= most recent Sat, 3= most recent Fri, etc
    subtraction_num = today_as_integer + desired_end_day
    most_recent_desired_end_day = today - timedelta(subtraction_num)

    # Calculating how many weeks back
    days_as_weeks = weeks * 7
    end_date = most_recent_desired_end_day - timedelta(days_as_weeks)

    # Date is returned in time format and needs to be formatted
    return end_date