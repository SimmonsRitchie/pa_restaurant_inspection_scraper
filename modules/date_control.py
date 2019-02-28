"""
This modules hosts a number of important  time-related functions needed by other modules in this program

That primarily includes:
-- determining the dates of inspections to be scraped
-- formating dates for headlines, text


"""

from datetime import datetime, timedelta
import time

def date_range(timeframe):
    start = start_date(timeframe)
    end = end_date(timeframe)

    # If the month of the start date and end date is the same then format like 'Aug 5-11', else format like July 29-Aug 5
    if start.strftime('%b') == end.strftime('%b'):
        date_for_headline = start.strftime('%b ') + start.strftime('%d').lstrip('0') + "-" + end.strftime('%d').lstrip('0')
    else:
        date_for_headline = start.strftime('%b ') + start.strftime('%d').lstrip('0') + "-" + end.strftime('%b ') + end.strftime('%d').lstrip('0')

    date_for_headline = ap_formatting_for_months(date_for_headline)
    return date_for_headline


def start_date(timeframe):
    # Parsing timeframe tuple
    desired_day_range = timeframe[0]
    weeks = timeframe[1]

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


def end_date(timeframe):
    # Parsing timeframe tuple
    desired_day_range = timeframe[0]
    weeks = timeframe[1]


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


def ap_formatting_for_months(date):
    # Shortening month names
    date = date.replace('Mar', 'March').replace('Jul.', 'July').replace('Jun.', 'June')
    # Add periods after certain month names
    date = date.replace('Jan','Jan.').replace('Feb','Feb.').replace('Aug','Aug.').replace('Sep','Sept.').replace('Oct','Oct.').replace('Nov','Nov.').replace('Dec','Dec.')
    return date


def run_time_calculator(start_time):
    elapsed_time = time.time() - start_time
    elapsed_minutes, elapsed_seconds = divmod(int(elapsed_time), 60)
    elapsed_time_formatted = "{} min {} seconds".format(elapsed_minutes,elapsed_seconds)
    return elapsed_time_formatted