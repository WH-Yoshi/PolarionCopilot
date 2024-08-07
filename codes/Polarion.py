"""
Polarion.py
This file will be the main file for saving workitems in the databases, to make them usable by the Polarion Copilot
If installation of required libraries is not already done, go in the project folder from terminal :
    pip install -r requirements.txt
"""
import random
import time
from typing import Tuple

import requests.exceptions
from termcolor import colored

from WorkitemSaver import WorkitemSaver
from enhancer import Loader
from file_helper import check_update_file, check_db_folder
import file_helper as fh


def display_file():
    """
    Display the content of the update file
    """
    path = fh.get_update_path()
    update_dict = fh.open_pkl_file_rb(path)
    try:
        for i, (db, date) in enumerate(update_dict.items()):
            print(f"{colored(f'[{i + 1}]', 'green')} {db.split('%')[0].split('__')[0]} and "
                  f"{db.split('%')[0].split('__')[1]} : {date if date is not None else 'No date'}")
    except Exception as e:
        raise Exception(f"An error occurred while displaying the file: {e}")

def prepare_available_choices(action_available: list) -> tuple[str, str]:
    actions = ""
    for i, string in enumerate(action_available):
        actions += colored(f'[{i + 1}] ', 'green') + string + "\n"
    return "", actions


def preliminary_checks():
    print("---------Preliminary checks---------")
    if not check_db_folder() and not check_update_file():
        loader = Loader("Checking","Database is empty, you can start saving some projects.", "green", 0.1).start()
        time.sleep(random.uniform(1.5, 3))
        loader.stop()
        actions = ["Save"]
    elif check_db_folder() and not check_update_file():
        loader = Loader("Checking", "Update file has no records but database(s) exist(s)\n", "yellow", 0.1).start()
        time.sleep(random.uniform(1.5, 3))
        loader.stop()
        print("Recovering update file...")
        if fh.recover_update_file():
            print("Recover complete.")
        actions = ["Save", "Update"]
    else:
        loader = Loader("Checking", "All good.", "green", 0.1).start()
        time.sleep(random.uniform(1.5, 3))
        loader.stop()
        actions = ["Save", "Update"]
    return actions


if __name__ == "__main__":
    action_available = preliminary_checks()
    update_file_path = fh.get_update_path()

    print("\n|------Polarion Workitem Saver------|\n")

    if fh.get_cache_path().exists() and any(fh.get_cache_path().iterdir()):
        print("Cache files found, it contains workitems that need to be embedded.")
        choice = ""
        while choice not in ["y", "n"]:
            choice = input("Invalid input. Please enter 'y' or 'n: "
                           if choice else "Do you want to embed them now ? [Y]es / [N]o : ").lower()
        if choice == "y":
            fh.display_cache_file()

    choice, printable_actions = prepare_available_choices(action_available)
    while choice not in [str(i) for i in range(1, len(action_available) + 1)]:
        choice = input(
            "Invalid input. Please enter the right number: "
            if choice else "Choose an action:\n" + printable_actions + " \u21AA  Input : ")

    print()
    if choice == "1":  # Save
        locations_available = ["Group", "Project"]
        choice, printable_locations = prepare_available_choices(locations_available)
        while choice not in [str(i) for i in range(1, len(locations_available) + 1)]:
            choice = input(
                "Invalid input : "
                if choice else f"    {colored('Save', 'green')} from:\n"
                               + printable_locations + " \u21AA  Input : ")
        choice = locations_available[int(choice) - 1].lower()
        print()
        if choice == "group":
            project_or_group_id_input = ""
            while not project_or_group_id_input.strip():
                project_or_group_id_input = input(f" \u21AA  Type the {colored('group', 'green')} ID "
                                                  f"(e.g. Therapy_Center_Spec, L2_System_Spec, ...): ")
        elif choice == "project":
            project_or_group_id_input = ""
            while not project_or_group_id_input.strip():
                project_or_group_id_input = input(f" \u21AA  Type the {colored('project', 'green')} ID "
                                                  f"(e.g. PT_L2_TSS_Subsystem, PT_L1_TPS_Subsystem, ...): ")

        release_input = input(
            f" \u21AA  Type the IBA {colored('release', 'green')} ID "
            f"(e.g. AI-V2.4.0.0, P235-R12.4.0, ...) or [ENTER] for ALL : ") or None
        if release_input:
            release_input = release_input.strip()

        print()
        print(f"Choose one or multiple from the following workitem objects: ")
        print(f"{colored('[1]', 'green')} Requirements")
        print(f"{colored('[2]', 'green')} Safety decisions")
        print(f"{colored('[3]', 'green')} Risk analysis (Hazard and Failure mode)")
        type_list = ["requirement", "safetydecision", "hazard failuremode"]
        workitem_type = input(
            " \u21AA  Type the number(s) of the workitem object(s) you want to save (e.g. 1, 2, 3): ")
        workitem_type = workitem_type.split(",")
        workitem_type = [int(i) for i in workitem_type]
        workitem_type = [type_list[i - 1] for i in workitem_type if i in range(1, 4)]
        if not workitem_type:
            raise ValueError("Invalid input. Please enter at least one of the numbers 1, 2, 3")
        time = None
    elif choice == "2":
        print(f"\nDatabases you can {colored('update', 'green')}: ")
        display_file()
        db_choice = ""
        while db_choice not in [str(i) for i in range(1, len(fh.open_pkl_file_rb(update_file_path)) + 1)]:
            db_choice = input(
                "Invalid input : "
                if db_choice else " \u21AA  Number input : ")

        dictio = fh.open_pkl_file_rb(update_file_path)
        db = list(dictio.keys())[int(db_choice) - 1]
        time = dictio[db]
        project_or_group_id_input = db.split('%')[0].split('__')[0].replace('../faiss/', '')
        choice = db.split('%')[1]
        release_input = db.split('%')[0].split('__')[1]
        workitem_type = None
    ws = WorkitemSaver(project_or_group_id_input, choice, workitem_type, release_input, time)
    try:
        ws.caller()
    except requests.exceptions.ConnectionError:
        raise requests.exceptions.ConnectionError("Connection error. Please check your ssh connection. Port 22027 and 22028 must be assigned")
