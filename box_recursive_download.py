#!/usr/bin/env python3

import os
import sys
from boxsdk import Client, OAuth2
from boxsdk.object.collaboration import CollaborationRole
from pathlib import Path


# usage example
# box_recursive_download.py box <box_folder_id> <box_developer_token>

folder = "./" + sys.argv[1]
box_folder_id = sys.argv[2]
developer_token = sys.argv[3]

# Oauth setup, get client id and secret from box app in developer console
oauth = OAuth2(
  client_id='',
  client_secret='',
  access_token=developer_token,
)

client = Client(oauth)


box_root_folder = box_folder_id
os_root_folder = folder

# item logs all items that have finished downloading so the script can pick up from where it left off
item_log = "./upload_progress.log"
error_log = "./upload_errors.log"

working_directory = os.getcwd()
item_log_path = working_directory + "/" + item_log
error_log_path = working_directory + "/" + error_log

# pulls all items logged into an array
item_log_path_object = Path(item_log_path)

if item_log_path_object.exists():
    item_log_lines = [line.rstrip('\n') for line in open(item_log_path)]
else:
    item_log_lines = ""

error_log = open(item_log_path, "a+")
item_log = open(item_log_path, "a+")

os.chdir(os_root_folder)

# returns true if file was logged
def is_logged(item_path):

    for item in item_log_lines:
        if item == item_path:
            return True

    return False

# This function downloads all files and creates all directories within a given directory.
# Its called recursively in the event that sub directories are present.
def download_folder(folder):

    # api call to list all content of the provided box directory
    folder_items = client.folder(folder_id=folder).get_items()

    # every item within the list of items box returns
    for item in folder_items:

        item_type = item.type.lower()
        item_name = item.name
        item_id = item.id
        item_full_path = os.getcwd() + "/" + item_name

        # nothing is done in the event that an item is logged
        if not is_logged(item_full_path):

            if item_type == "folder":

                # directory is created and then script moves its current working directory to the newly created one
                path_object = Path(item_full_path)

                if not path_object.exists():
                    os.mkdir(item_name, 0o777)
                    os.chdir(item_name)

                # this function is called recursively for the new directory
                download_folder(item_id)

                # folder is marked to prevent the script from traversing it later
                item_log.write(item_full_path)
                item_log.write('\n')

                # when finished, current working directory goes back to the parent directory
                os.chdir("..")

            # all other types box returns are files
            else:

		# file is written to the local filesystem here
                with open(item_name, 'wb') as open_file:
                    try:
                        client.file(item_id).download_to(open_file)
                        print("downloaded: " + item_full_path)

                        # marked so script doesn't acidently try to download it again
                        item_log.write(item_full_path)
                        item_log.write('\n')
                    except:
                        error_log.write(item_full_path)
                        error_log.write('\n')
                        print("Error: " + item_full_path)

                open_file.close()
 

download_folder(box_root_folder)

item_log.close()
error_log.close()
