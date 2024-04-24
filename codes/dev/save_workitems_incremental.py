"""
This code will save workitems incrementally in a database. To do so it saves a pkl file containing the last update date.
"""
import html
import os
import pickle
import re
import shutil
import sys
import certifi

import file_helper as fh
from save_workitems_release import get_polarion_instance, workitem_to_embed, printarrow, str_cleaner, \
    create_vector_db, get_workitems_from_project, get_workitems_from_group

from typing import List, Any, Dict

from dotenv import load_dotenv
from pprint import pprint
from datetime import datetime
from pathlib import Path

from langchain_community.embeddings import HuggingFaceHubEmbeddings
from langchain_community.vectorstores.faiss import FAISS

from polarion.document import Document
from polarion.project import Project
from polarion.polarion import Polarion
from polarion.workitem import Workitem

file_path = "../../data/.update_file.pkl"
dbs_folder_path = "../../faiss/"


def display_file():
    """
    Display the content of the update file
    """
    path = fh.get_update_path()
    update_dict = fh.open_pkl_file_rb(path)
    print("Content of the update file:")
    try:
        for i, (db, date) in enumerate(update_dict.items()):
            print(f"[{i + 1}] {db.split('%')[0].split('__')[0]} and {db.split('%')[0].split('__')[1]} : "
                  f"{date if date is not None else 'No date'}")
    except Exception as e:
        raise Exception(f"An error occurred while displaying the file: {e}")


def initial_checkup():
    """
    Save an update file if no folder exists in the faiss folder, update the file otherwise
    """
    abs_update_path = fh.get_update_path()
    dbs_path = fh.get_db_path()
    infos = fh.open_pkl_file_rb(abs_update_path)
    list_subfolders_with_paths = [f.name for f in os.scandir(dbs_path) if f.is_dir()]

    if not list_subfolders_with_paths and (not infos or infos == {}):
        print("No database saved for now. Start creating databases with the save_workitem_release.py script !")
        return
    elif list_subfolders_with_paths and (not infos or infos == {}):  # update happens with existing databases
        backup_abs_path = fh.get_backup_path()
        backup_content = fh.open_pkl_file_rb(backup_abs_path)
        if backup_content:
            shutil.copyfile(backup_abs_path, abs_update_path)
            copied_content = fh.open_pkl_file_rb(abs_update_path)
            for db in list_subfolders_with_paths:
                if db not in copied_content.keys():
                    copied_content[db] = None
                    print(f"Database '{db}' added, but has no date.")
            print("Update file updated with existing databases.")
            return
        else:
            for db in list_subfolders_with_paths:
                infos[db] = None
            with open(abs_update_path, 'wb') as f:
                pickle.dump(infos, f)
            with open(backup_abs_path, 'wb') as f:
                pickle.dump(infos, f)
            print(f"The update file has db names but no date. Might wanna re-run the save_workitems_release.py script "
                  f"for the following content:")
            for db in list_subfolders_with_paths:
                print(f" - {db.split('%')[0].split('__')[0]} and {db.split('%')[0].split('__')[1]}")
            return
    elif list_subfolders_with_paths and infos:  # update happens with existing databases if infos is not right
        keys_to_delete = [key for key in infos.keys() if key not in list_subfolders_with_paths]
        for key in keys_to_delete:
            del infos[key]
        if not all(elem in infos.keys() for elem in list_subfolders_with_paths):
            for db in list_subfolders_with_paths:
                if db not in infos.keys():
                    infos[db] = None
            with open(abs_update_path, 'wb') as f:
                pickle.dump(infos, f)
            printarrow("Update file updated with existing databases.")
            return
        else:
            with open(abs_update_path, 'wb') as f:
                pickle.dump(infos, f)
            return
    else:
        raise Exception("Unknown combination.")


def get_update_date(db_name: list[str]) -> dict[str, datetime]:
    """
    Get the last update date of a database from the db pkl file.
    :return: A datetime class object
    """
    if not isinstance(db_name, list):
        raise ValueError(f"The database parameter must be a list.")
    if len(db_name) == 0:
        raise ValueError(f"The database list must not be empty.")
    return_dict = {}
    try:
        with open(fh.get_update_path(), 'rb') as f:
            update_dict = pickle.load(f)
        for db in db_name:
            return_dict[db] = update_dict[db]
        return return_dict
    except FileNotFoundError:
        with open(fh.get_update_path(), 'wb') as f:
            pickle.dump({}, f)
        return {}
    except EOFError:
        with open(fh.get_update_path(), 'wb') as f:
            pickle.dump({}, f)
        return {}
    except pickle.UnpicklingError:
        raise pickle.UnpicklingError(f"File '{fh.get_update_path().name}' is corrupted")
    except KeyError:
        raise KeyError(f"Database '{db_name}' not found in '{fh.get_update_path().name}' file")
    except Exception as e:
        raise Exception(f"Unknown error : {e}")


def save_last_update_date(db_choice) -> bool:  # MUST BE CALLED *AFTER* THE WORKITEMS HAVE BEEN SAVED IN DATABASE
    """
    Save the new update date of a database in the db pkl file
    :return: True if the file has been successfully updated, False otherwise
    :rtype: bool
    """
    now = datetime.now().strftime("%A %d %B %Y - %H:%M:%S")
    # if not abs_file_path.exists():
    #     printarrow(f"Adding date: [{now}] for {db_choice}")
    # else:
    #     last_update = get_update_date(db_choice)
    #     printarrow(f"Changing date: [{last_update}] to [{now}] for {db_choice}")

    input_content = "python"
    while input_content not in ['n', 'N', 'no', 'No', 'NO', 'y', 'Y', 'ye', 'Ye', 'YE', 'yes', 'Yes', 'YES', ""]:
        input_content = input(
            "Invalid input, try again: "
            if input_content != "python" else "Do you want to continue? (y/n): ")

    if input_content in ["n", "N", "no", "No", "NO"]:
        printarrow("Operation cancelled: Workitems not saved in database.")
        return False
    elif input_content in ["y", "Y", "ye", "Ye", "YE", "yes", "Yes", "YES", ""]:
        try:
            with open(abs_file_path, 'rb') as f:
                update_dict = pickle.load(f)
            with open(abs_file_path, 'wb') as f:
                update_dict[db_choice] = now
                pickle.dump(update_dict, f)
            printarrow(f"Content successfully modified to [{now}].")
            return True
        except FileNotFoundError:
            raise FileNotFoundError(f"No file named '{abs_file_path}' found in '{abs_file_path.parent}' folder.")
        except pickle.PicklingError:
            raise pickle.PicklingError(f"An error occurred while pickling the data into '{abs_file_path}' file.")
        except Exception as e:
            raise Exception(f"Unknown error: {e}")


def show_saved_db():
    """
    Show the saved databases
    """
    for i, db in enumerate(os.listdir('../../faiss')):
        print(f"[{i + 1}] {db}")


def workitem_caller(db: Dict[str, datetime]):
    """
    Call the workitem_to_embed function to save workitems in a database
    """
    client = get_polarion_instance()
    for db_name, date in db.items():
        directory = db_name.split('%')[1]
        name = db_name.split('%')[0].split('__')[0]
        release = db_name.split('%')[0].split('__')[1]
        date = date.strftime("%Y%m%d") if date is not None else None
        query = f"created:[{date} TO $today$] OR updated:[{date} TO $today$]" if date is not None else ""

        if directory == "project":
            project = client.getProject(name)
            workitems = get_workitems_from_project(
                client, project, release,
                additional_query=query
            )
        elif directory == "group":
            group = client.getProjectGroup(name)
            workitems = get_workitems_from_group(
                client, group, release,
                additional_query=query
            )
        else:
            raise ValueError(f"Unknown directory: {directory}")
        workitem_to_embed(workitems, db_name)
        ## TO CONTINUE MAYBE


def main(
        choice: str
):
    """
    Main function to save workitems incrementally in a database
    :param choice: The database choice (a number)
    """
    db = []
    if choice == "":
        db = os.listdir('../../faiss')
    else:
        db_str = os.listdir('../../faiss')[int(choice) - 1]
        db.append(db_str)
    db_date = get_update_date(db)
    pprint(db_date.keys())
    date = db_date[db[0]]
    print(date.strftime("%Y%m%d"))
    # workitem_caller(db_date)
    # element = db.split("%")[1]
    # get
    # save_last_update_date(db)


if __name__ == '__main__':
    fh.check_backup()
    fh.check_db_folder()
    fh.check_update_file()

    initial_checkup()

    display_file()
    print('\n')

    db_choice = "no input"
    valid_inputs = [str(i) for i in range(1, len(os.listdir('../../faiss')) + 1)] + [""]
    while db_choice not in valid_inputs:
        db_choice = input(
            "Please enter a valid number: "
            if db_choice else "Which database do you want to update? [number]: ")
    main(db_choice)
