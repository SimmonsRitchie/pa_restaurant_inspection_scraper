"""
This module automatically sends an email with information about scraper data
"""


#load misc modules
from datetime import datetime
import os
import pandas as pd

#load email modules
import smtplib
from email.mime.text import MIMEText

# Load my modules
from modules import date_control


def email_payload(email_style, inspection_data, location, scrape_time):
    # This function saves inspection data as 'payload parcels' and adds to text file so it can be emailed later
    print("Creating text file for email payload...")

    # formatting named tuple into reader-friendly output
    area = get_area_name_formatted(location)

    if email_style == "table":
        payload_parcel = convert_data_into_table_format(inspection_data, scrape_time, area)
    elif email_style == "list":
        payload_parcel = convert_data_into_list_format(inspection_data, scrape_time, area)

    email_payload_path = email_payload_path_generator()
    email_save_for_payload(email_payload_path, payload_parcel)


def get_area_name_formatted(location):
    # Extracting area from location tuple and adding 'county' if descriptor is a county
    if location[0].capitalize() == "County":
        area = "{} County".format(location[1].capitalize())
    else:
        area = location[1].capitalize()
    return area


def convert_data_into_list_format(inspection_data, scrape_time, area):
    # Formatting text for email in list format
    print("Converting inspection data into list format...")

    # Formatting area header for HTML
    area_header = '<font size="5"><b>{0}</b></font><br>'.format(area)

    # Formatting scrape details for HTML
    scrape_details = "<b>Inspections:</b> {}, <b>Scrape time:</b> {}<br>".format(len(inspection_data.restaurant), scrape_time)

    # Formatting inspection data as list
    list_of_inspection_data = ""
    for x, value in enumerate(inspection_data.restaurant):
        violation_text_with_br_tags = inspection_data.violation[x].replace('\n','<br />')

        inspection = """
        <p>{0}<br />
        {1}<br />
        <b>Date:</b> {2}<br />
        <b>Type:</b> {3}<br />
        <b>Compliance:</b> {4}<br />
        <b>Violations:</b> <br />
        {5}</p>
        <p></p>
        """.format(inspection_data.restaurant[x], inspection_data.address[x], inspection_data.date[x],
                   inspection_data.inspection_type[x], inspection_data.compliance[x], violation_text_with_br_tags)
        list_of_inspection_data = list_of_inspection_data + inspection

    # Putting all the HTML elements together into payload parcel
    # If no inspection data then simply say 'no restaurant inspections' found
    if inspection_data.restaurant:
        payload_parcel = "<p>" + area_header + '<font size="3" color="red">' + scrape_details + "</font></p>" + list_of_inspection_data + "<p></p>"
    else:
        payload_parcel = area_header + "<p>No restaurant inspections found</p>"

    return payload_parcel


def convert_data_into_table_format(inspection_data, scrape_time, area):
    # This creates a table of inspection data so it looks pretty for email

    # First loading named tuples into dictionary to load into pandas dataframe
    print("Creating dictionary from inspection data")

    inspection_dict = {
        "Name": inspection_data.restaurant,
        "Address": inspection_data.address,
        "Date": inspection_data.date,
        "Type": inspection_data.inspection_type,
        "Compliance": inspection_data.compliance,
        "Violations": inspection_data.violation,
    }

    # Converting dictionaries into Pandas dataframe
    print("Turning saved data on {} inspections into Pandas dataframe".format(area))
    pd.set_option('display.max_colwidth', -1)
    df = pd.DataFrame.from_dict(inspection_dict)
    df = df[["Name", "Address", "Date", "Type", "Compliance","Violations"]]

    # Formatting text for email
    print("Converting pandas dataframe to HTML")
    html = df.to_html(index=False) # Converts dataframe to HTML
    area_header = "<br><p style='font-size:20px'><b>{0}</b><br>".format(area)
    if inspection_data.restaurant:
        scrape_details = "Inspections: {}, Scrape time: {}<br>".format(
            len(inspection_data.restaurant), scrape_time)
        payload_parcel = "<tr><td>" + area_header + scrape_details + "</p></td></tr>" + "<tr><td>" + html + "</td></tr>"
    else:
        payload_parcel = "<tr><td>" + area_header + "<p>No restaurant inspections found</p><br></td></tr>"
    return payload_parcel


def email_save_for_payload(email_payload_path, new_area):
    # Saving email payload to text file, creating text file if none exists
    print("Saving payload parcel as text file for email payload...")
    if os.path.exists(email_payload_path):
        with open(email_payload_path, "a") as fin:
            print("Existing text file found: Adding parcel")
            fin.write(new_area)
            print("Dataframe added")
    else:
        with open(email_payload_path, "w") as fout:
            print("Creating email payload text file")
            fout.write(new_area)
            print("File created")


def email_payload_path_generator():
    # This function creates the filename and path for text files for email

    base_folder = "email_payload/"

    # Checking whether base folder directory exists and, if doesn't exist, creating it
    check_directory_exists(base_folder)

    # Getting today's date for filename
    today = datetime.now()
    today = today.strftime('%m%d%Y')

    email_filename = "email_{}.txt".format(today)
    email_payload_path = os.path.join(base_folder,email_filename)
    return email_payload_path


def check_directory_exists(base_folder):
    directory = os.path.dirname(base_folder)
    if not os.path.exists(directory):
        os.makedirs(directory)


def email_send(config, program_start_time, timeframe):
    print("Sending email...")

    range = date_control.date_range(timeframe)
    program_start_time = program_start_time.strftime("%I:%M%p on %B %d, %Y")

    intro_text = "The following restaurant inpections were scraped for {}.".format(range)


    #Table_top and table_bottom create a big table that nests the tables from email payload
    #This was used after encountering weird issues where tables overlapped in email
    table_top = '<table border="0">'
    intro_text_with_html = "<tr><td><p style='font-size:20px'>{}</p>".format(intro_text)
    email_payload_path = email_payload_path_generator()
    outro = "<tr><td>See errors in this email? Contact simmons-ritchie@pennlive.com</tr></td>"
    table_bottom = "</table>"

    with open(email_payload_path, "r") as fin:
        email_payload = fin.read()

    msg_content = table_top + intro_text_with_html + email_payload + outro + table_bottom
    message = MIMEText(msg_content, 'html')

    recipients = config["destination"]

    subject = "Restaurant inspections - {}".format(range)
    fromaddr = "dsr.newsalert@gmail.com"
    message['From'] = 'NewsAlert <dsr.newsalert@gmail.com>'
    message['To'] = ", ".join(recipients)
    message['Subject'] = subject

    msg_full = message.as_string()

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(config["email"]["username"], config["email"]["pass"])
    server.sendmail(fromaddr, recipients, msg_full)
    server.quit()
    print("Email sent!")
    return