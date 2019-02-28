### This module is for cleaning the data after it's scraped, before it's converted to slideshow

import pandas as pd
import re
from datetime import datetime
from collections import namedtuple
import inflect

#My modules
from modules import date_control

SortedInspectionData = namedtuple("InspectionData", ('restaurant', 'address', 'date','inspection_type','compliance', 'violator','violation'))
CleanedInspectionData = namedtuple("InspectionData", ('restaurant', 'address', 'date','inspection_type', 'compliance','violator','violation'))



def inspection_data_sort_by_violator(InspectionData):
    print("Changing order of inspection data so that restaurants with violations are first")

    print("Convert named tuples to dictionary")
    InspectionDict = InspectionData._asdict()

    print("Convert dictionary into Pandas dataframe")
    pd.set_option('display.max_colwidth', -1)
    df = pd.DataFrame.from_dict(InspectionDict)
    df = df[['restaurant', 'address', 'date', 'inspection_type', 'compliance','violator', 'violation']]

    # Converting date field into datetime format so it can be sorted
    df['date'] = pd.to_datetime(df['date'])

    # Sorting columns by whether there was a violation, date, and restaurant name
    sorted_data = df.sort_values(['violator', 'date', 'restaurant'], ascending=[False, False, True])

    print("Convert pandas dataframe back to dictionary")
    InspectionDict = sorted_data.to_dict('list')

    print(InspectionDict)
    print("Convert dictionary back to named tuple")
    return SortedInspectionData(
        InspectionDict.get("restaurant"),
        InspectionDict.get("address"),
        InspectionDict.get("date"),
        InspectionDict.get("inspection_type"),
        InspectionDict.get("compliance"),
        InspectionDict.get("violator"),
        InspectionDict.get("violation")
    )



def clean_data(InspectionData):
    print("Cleaning and reformatting data")
    new_date_list = []
    new_restaurant_list = []
    new_address_list = []
    new_violation_list = []

    # Converting restaurant name into uppercase
    print("FORMATTING restaurant name")
    for restaurant in InspectionData.restaurant:
        print("Old: {}".format(restaurant))
        restaurant = restaurant.upper()
        print("New: {}".format(restaurant))
        new_restaurant_list.append(restaurant)


    # Converting dates from timestamp format into better looking format
    print("FORMATTING date")
    for date in InspectionData.date:
        print("Old: {}".format(date))
        date = datetime.strftime(date, '%b ') + datetime.strftime(date,'%d, ').lstrip('0') + datetime.strftime(date,'%Y')
        # Using AP date formatting
        date = date_control.ap_formatting_for_months(date)
        print("New: {}".format(date))
        new_date_list.append(date)


    print("FORMATTING address")
    for address in InspectionData.address:
        # Using regex to remove zip and state code
        try:
            print("Old: {}".format(address))
            pattern = re.compile(r'(.*)(,\s\D{2}.?\s\d{5})', re.DOTALL)
            strip_address = pattern.search(address)
            strip_address = strip_address.group(1)
            new_address = strip_address
        except:
            print("ERROR: Something went wrong when attempting to strip zipcode and state code")
            new_address = address

        # Formatting to AP Style and adding comma before city name
        new_address = new_address.replace(" Dr. ", " Drive, ")
        new_address = new_address.replace(" Dr ", " Drive, ")
        new_address = new_address.replace(" Dr, ", " Drive, ")
        new_address = new_address.replace(" Dr., ", " Drive, ")
        new_address = new_address.replace(" St ", " St., ")
        new_address = new_address.replace(" St. ", " St., ")
        new_address = new_address.replace(" St, ", " St., ")
        new_address = new_address.replace(" Street ", " St., ")
        new_address = new_address.replace(" Rd. ", " Road, ")
        new_address = new_address.replace(" Rd., ", " Road, ")
        new_address = new_address.replace(" Rd, ", " Road, ")
        new_address = new_address.replace(" Rd ", " Road, ")
        new_address = new_address.replace(" Pike ", " Pike, ")
        new_address = new_address.replace(" Ave ", " Ave., ")
        new_address = new_address.replace(" Ct ", " Ct, ")
        new_address = new_address.replace(" Ct. ", " Ct., ")
        new_address = new_address.replace(" Court ", " Ct, ")
        new_address = new_address.replace(" Blvd ", " Blvd., ")
        new_address = new_address.replace(" Boulevard ", " Blvd., ")
        new_address = new_address.replace(" Bldg ", " Bldg, ")
        new_address = new_address.replace(" Ctr ", " Ctr, ")
        new_address = new_address.replace(" Cir ", " Cir, ")
        new_address = new_address.replace(" Apt ", " Apt, ")
        new_address = new_address.replace(" Hts ", " Hts, ")
        new_address = new_address.replace(" Hwy ", " Hwy, ")
        new_address = new_address.replace(" Is ", " Is, ")
        new_address = new_address.replace(" Jct ", " Jct, ")
        new_address = new_address.replace(" Ln ", " Lane, ")
        new_address = new_address.replace(" Mt ", " Mt, ")
        new_address = new_address.replace(" Pky ", " Pky, ")
        new_address = new_address.replace(" Pkwy ", " Pkwy, ")
        new_address = new_address.replace(" Pl ", " Pl, ")
        new_address = new_address.replace(" Tpke ", " Tpke, ")

        print("New: {}".format(new_address))
        print("")
        new_address_list.append(new_address)

    print("FORMATTING violations")
    for violation in InspectionData.violation:
        print("Old: {}".format(violation))

        # Checking if any large violation words are all in uppercase or
        # whether text is all in lowercase. if so, changing all of violation text to sentence case
        violation = convert_to_sentence_case(violation)

        # If any dumb jargon words are detected, change those to plain speech.
        violation = violation.replace(" Cos.", " Corrected on-site.")
        violation = violation.replace(". (corrected)",". (Corrected)")
        violation = violation.replace("°f", "F")
        violation = violation.replace("°F", "F")
        violation = violation.replace("baine marie","bain-marie")
        violation = violation.replace("Baine marie","Bain-marie")
        violation = violation.replace("bain marie","bain-marie")
        violation = violation.replace("Bain marie","Bain-marie")
        violation = violation.replace("time temperature controlled for safety","time/temperature-controlled-for-safety")
        violation = violation.replace("Time temperature controlled for safety","Time/temperature-controlled-for-safety")
        violation = violation.replace("person in charge","person-in-charge")
        violation = violation.replace("Person in charge","Person-in-charge")
        violation = violation.replace("ready to eat","ready-to-eat")
        violation = violation.replace("Ready to eat","Ready-to-eat")
        violation = violation.replace(" tcs"," TCS")
        violation = violation.replace(" Tcs"," TCS")
        violation = violation.replace(" (tcs)"," (TCS)")
        violation = violation.replace("old food residue","old-food residue")
        violation = violation.replace("warewashing","ware-washing")
        violation = violation.replace("Warewashing","Ware-washing")
        violation = violation.replace("walk in","walk-in")
        violation = violation.replace("Walk in","Walk-in")
        violation = violation.replace("shatter proof","shatterproof")
        violation = violation.replace("single use","single-use")
        violation = violation.replace("self serve","self-serve")
        violation = violation.replace("handwash","hand-wash")
        violation = violation.replace("Handwash","Hand-wash")
        violation = violation.replace("haccp","HACCP")
        violation = violation.replace("Haccp","HACCP")
        violation = violation.replace("shoot","chute")
        violation = violation.replace("Shoot","Chute")
        violation = violation.replace(" & ", " and ")

        # If there are any numbers in the violation text then turn those into words
        violation = convert_numbers_in_violation_text_to_words(violation)

        print("New: {}".format(violation))

        new_violation_list.append(violation)

    return CleanedInspectionData(new_restaurant_list,
                                 new_address_list,
                                 new_date_list,
                                 InspectionData.inspection_type,
                                 InspectionData.compliance,
                                 InspectionData.violator,
                                 new_violation_list)


def convert_to_sentence_case(text):
    print("Checking whether text is in all lowecase or might be written in all uppercase")
    # This function is designed specifically to convert blocks of violation text into sentence case if needed

    # This regex checks whether any word in a violation has more than 4 uppercase characters
    pattern_uppercase_words = re.compile(r'[A-Z]{4,}',re.DOTALL)
    result = re.search(pattern_uppercase_words, text)

    # If a uppercase word is found or if all the text is lowercase then convert the text to sentence case.
    # To use capitalize method, certain punctuation marks are removed and then re-added
    if result or text.islower():
        print("Detected: Text is all lowercase or at least one word is in all caps")
        print("Converting text to sentence case")
        old_text_split_by_newlines = text.split("\n") # First splitting text by each line
        new_text = "" # Creating an empty string to dump each transformed line into
        for line in old_text_split_by_newlines:
            line = line.replace("--", "")  # Removing '--' because it messes with capitalize method
            line = '. '.join(i.capitalize() for i in line.split('. '))  # capitalize start of each sentence in line
            line = "--" + line  # Adding '--' back to start of line
            new_text = new_text + line + "\n"  # Adding newline back to each line
        new_text = new_text.rstrip()  # Remove trailing newline at end of text block
        return new_text
    else:
        print("None detected")
        return text


def numbers_to_words(number):
    if number < 10:
        p = inflect.engine()
        return p.number_to_words(number)
    else:
        return number


def convert_numbers_in_violation_text_to_words(text):
    print("Checking if single digit numbers are present in text...")

    # This regex uses negative lookahead and negative lookbehind.
    # If a '/', '.' or a single digit precedes or procedes a single digit then the match will be ignored.
    # this is done to prevent the regex from scooping up dates or multi-digit numbers, eg. the 3 and 2 in '32'.
    # And to prevent decimals
    pattern = re.compile(r'(?<![/\d\.])\d(?![/\d])', re.DOTALL)
    result = re.findall(pattern, text)

    if result:
        print("Numbers found: {}".format(result))
        print("Converting numbers to words")

    for single_digit in result:
        # Single digit number
        # print("Single digit: {}".format(single_digit))

        # Single digit number as word
        inflect_engine = inflect.engine()
        single_digit_as_word = inflect_engine.number_to_words(single_digit)
        # print("Number as word: {}".format(single_digit_as_word))

        # PATTERNS TO SEARCH
        # Exact match of single digit
        pattern = re.compile(r'(?<![/\d])' + re.escape(single_digit) + r'(?![/\d])', re.DOTALL)

        # Determine whether number as word needs to be capitalized because '. ' or '! ' or '? ' precedes the single digit using
        # positive lookbehind
        pattern_full_stop = re.compile(r'(?<=[\.?!]\s)' + re.escape(single_digit) + r'(?![/\d])', re.DOTALL)

        # Determine whether number as word needs to be capitalized because '--' precedes the single digit using
        # positive lookbehind
        pattern_dash = re.compile(r'(?<=--)' + re.escape(single_digit) + r'(?![/\d])', re.DOTALL)

        if re.search(pattern_full_stop, text):
            # print("{} is preceded by '. ' or '! ' or '? ' and therefore should be capitalized".format(single_digit))
            single_digit_as_word = single_digit_as_word.capitalize()
            text = re.sub(pattern_full_stop, single_digit_as_word, text)
        elif re.search(pattern_dash, text):
            # print("{} is preceded by '--' and therefore should be capitalized".format(single_digit))
            single_digit_as_word = single_digit_as_word.capitalize()
            text = re.sub(pattern_dash, single_digit_as_word, text)
        else:
            # print("{} is not preceded by '. ' or '--' and therefore doesn't need to be capitalized")
            text = re.sub(pattern, single_digit_as_word, text)

    # New version of string
    # print("NEW VERSION: {}".format(text))
    return text