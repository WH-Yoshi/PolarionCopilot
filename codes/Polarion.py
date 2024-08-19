"""
Polarion.py
This file will be the main file for saving workitems in the databases, to make them usable by the Polarion Copilot
If installation of required libraries is not already done, go in the project folder from terminal :
    pip install -r requirements.txt
"""
import pickle
import random
import time
from pathlib import Path
from typing import Tuple

import requests.exceptions
from termcolor import colored

from WorkitemSaver import WorkitemSaver
from enhancer import Loader
from file_helper import check_update_file, check_db_folder
import file_helper as fh


def display_file(path: Path) -> None:
    """
    Display the content of the faiss file
    """
    update_dict = fh.open_pkl_file_rb(path)
    try:
        for i, (_, value) in enumerate(update_dict.items()):
            print(f"{colored(f'[{i + 1}]', 'green')} Database : {value['name']} "
                  f"({value['release'] if value['release'] is not None else 'All release'}) "
                  f"filled with {', '.join(value['workitem_type'])}")
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
        loader = Loader("Checking", "Database is empty, you can start saving some projects.", "green", 0.1).start()
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
    update_file_path = fh.get_faiss_data_path()

    print("\n|------Polarion Workitem Saver------|\n")

    if fh.get_cache_path().exists() and any(fh.get_cache_path().iterdir()):
        print("Cache files found, it contains workitems that need to be embedded.")
        do_save = ""
        while do_save not in ["y", "n"]:
            do_save = input(" \u21AA  Invalid input. Please enter 'y' or 'n: "
                            if do_save else " \u21AA  Do you want to embed them now ? [Y]es / [N]o : ").lower()
        if do_save == "y":
            display_file(fh.get_cache_data_path())
            cache_choice = ""
            while cache_choice not in [str(i) for i in
                                       range(1, len(fh.open_pkl_file_rb(fh.get_cache_data_path())) + 1)]:
                cache_choice = input(
                    " \u21AA  Invalid input, retry : "
                    if cache_choice else " \u21AA  Number input : ")

            dictio = fh.open_pkl_file_rb(fh.get_cache_data_path())
            db_id = list(dictio.keys())[int(cache_choice) - 1]
            details = dictio[db_id]

            location = details["name"]
            db_type = details["type"]
            workitem_type = details["workitem_type"]
            release_input = details["release"] if details["release"] is not None else ""

            with open(fh.get_cache_path() / f"{db_id}.pkl", "rb") as f:
                workitems = pickle.load(f)

            WorkitemSaver(location, db_type, workitem_type, release_input).create_vector_db(workitems)
            (fh.get_cache_path() / f"{db_id}.pkl").unlink()

    action, printable_actions = prepare_available_choices(action_available)
    while action not in [str(i) for i in range(1, len(action_available) + 1)]:
        action = input(
            "Invalid input. Please enter the right number: "
            if action else "Choose an action:\n" + printable_actions + " \u21AA  Input : ")

    print()
    if action == "1":  # Save
        locations_available = ["Group", "Project"]
        choice, printable_locations = prepare_available_choices(locations_available)
        while choice not in [str(i) for i in range(1, len(locations_available) + 1)]:
            choice = input(
                "Invalid input : "
                if choice else f"    {colored('Save', 'green')} from:\n"
                               + printable_locations + " \u21AA  Input : ")
        db_type = locations_available[int(choice) - 1].lower()
        print()
        if db_type == "group":
            location = ""
            while not location.strip():
                location = input(f" \u21AA  Type the {colored('group', 'green')} ID "
                                 f"(e.g. Therapy_Center_Spec, L2_System_Spec, ...): ")
        elif db_type == "project":
            location = ""
            while not location.strip():
                location = input(f" \u21AA  Type the {colored('project', 'green')} ID "
                                 f"(e.g. PT_L2_TSS_Subsystem, PT_L1_PTS_Subsystem, ...): ")
        else:
            raise ValueError(f"Invalid input. {choice}")

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
            " \u21AA  Type the number(s) of the workitem object(s) you want to save (example for req and sd: '1, 2'): ")
        workitem_type = workitem_type.split(",")
        workitem_type = [int(i) for i in workitem_type]
        workitem_type = [type_list[i - 1] for i in workitem_type if i in range(1, 4)]
        if not workitem_type:
            raise ValueError("Invalid input. Please enter at least one of the numbers 1, 2, 3")
        time = None
        db_id = None
    elif action == "2":  # Update
        print(f"Databases you can {colored('update', 'green')}:\n")
        display_file(fh.get_faiss_data_path())

        db_choice = ""
        while db_choice not in [str(i) for i in range(1, len(fh.open_pkl_file_rb(update_file_path)) + 1)]:
            db_choice = input(
                " \u21AA  Invalid input, retry : "
                if db_choice else " \u21AA  Number input : ")

        dictio = fh.open_pkl_file_rb(update_file_path)
        db_id = list(dictio.keys())[int(db_choice) - 1]
        details = dictio[db_id]
        location = details["name"]
        db_type = details["type"]
        workitem_type = details["workitem_type"]
        release_input = details["release"]
        time = details["last_update"]
    else:
        raise ValueError("Invalid input.")

    ws = WorkitemSaver(location, db_type, workitem_type, release_input, time, db_id)
    try:
        ws.caller()
    except requests.exceptions.ConnectionError:
        raise requests.exceptions.ConnectionError(
            "Connection error. Please check your ssh connection. Port 22027 and 22028 must be assigned")
