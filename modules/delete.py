"""
This module deletes temporary files before running program
"""

import os
from shutil import rmtree


def delete_temp_files():
    print("Checking that temp files have been deleted from previous scraper runs")
    payload_base_folder = "email_payload/"
    path = os.path.abspath(payload_base_folder)

    if os.path.exists(path):
        print("Deleting data payload folder...")
        try:
            rmtree(path)
            print("Successfully deleted the directory %s and all files inside" % payload_base_folder)
        except OSError:
            print("Deletion of the directory %s failed for some reason" % payload_base_folder)
    else:
        print("No email payload folder detected")