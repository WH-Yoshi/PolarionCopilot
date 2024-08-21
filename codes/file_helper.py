import os
import pickle
from datetime import datetime
from pathlib import Path
from pprint import pprint

from termcolor import colored

current_path = Path(__file__)

_faiss_path = current_path.parent.parent / "faiss"
_data_path = current_path.parent.parent / "data"
_cache_path = current_path.parent.parent / ".cache"
_cache_data_path = current_path.parent.parent / "data" / ".cache.pkl"
_faiss_data_path = current_path.parent.parent / "data" / ".faiss.pkl"


def get_faiss_data_path() -> Path:
    """
    Returns ../data/.faiss.pkl absolute path
    """
    try:
        get_faiss_path()
        update_path = Path(_faiss_data_path).absolute()
        if not update_path.exists():
            update_path.touch()
            with open(update_path, 'wb') as f:
                pickle.dump({}, f)
        return update_path
    except Exception as e:
        raise Exception(f"Error : {e}")


def get_cache_data_path() -> Path:
    """
    Returns ../data/.cache.pkl absolute path
    """
    try:
        get_cache_path()
        cache_path = Path(_cache_data_path).absolute()
        if not cache_path.exists():
            cache_path.touch()
            with open(cache_path, 'wb') as f:
                pickle.dump({}, f)
        return cache_path
    except Exception as e:
        raise Exception(f"Error : {e}")


def get_data_path() -> Path:
    """
    Returns ../data/ absolute path
    """
    try:
        data_path = Path(_data_path).absolute()
        if not data_path.exists():
            data_path.mkdir(parents=True)
        return data_path
    except Exception as e:
        raise Exception(f"Error : {e}")


def get_faiss_path() -> Path:
    """
    Returns ../faiss/ absolute path
    """
    try:
        db_path = Path(_faiss_path).absolute()
        if not db_path.exists():
            db_path.mkdir(parents=True)
        return db_path
    except Exception as e:
        raise Exception(f"Error : {e}")


def get_cache_path() -> Path:
    """
    Returns ../.cache/ absolute path
    """
    try:
        cache_path = Path(_cache_path).absolute()
        if not cache_path.exists():
            cache_path.mkdir(parents=True)
        return cache_path
    except Exception as e:
        raise Exception(f"Error : {e}")


def check_db_folder():  # First to check
    try:
        abs_dbs_path = get_faiss_path()
        dbs = os.listdir(abs_dbs_path)
        if dbs:
            return True
        return False
    except Exception as e:
        raise Exception(f"Error while checking database folder: {e}")


def check_update_file():  # second one
    try:
        abs_file_path = get_faiss_data_path()
        infos = open_pkl_file_rb(abs_file_path)
        if not infos or infos == {}:
            return False
        return True
    except Exception as e:
        raise Exception(f"Error while checking update file: {e}")


def db_to_update_file(db_id: str, pr_name: str, release: str, pr_type: str, wi_type: list[str], update_date: datetime):
    """
    Add a database to the update file
    :param db_id: The ID of the database
    :param pr_name: The name of the database
    :param release: The release of the database
    :param pr_type: The type of the database (project or group)
    :param wi_type: The type of workitems in the database
    :param update_date: The date of the last update
    """
    format_time = "%A %d %B %Y - %H:%M:%S"
    update_date = update_date.strftime(format_time)

    abs_update_path = get_faiss_data_path()
    with open(abs_update_path, 'rb') as f:
        infos = pickle.load(f)

    infos[db_id] = {
            "location": pr_name,
            "release": release if release else "All releases",
            "type": pr_type,
            "workitem_type": wi_type,
            "last_update": update_date
        }

    with open(abs_update_path, 'wb') as f:
        pickle.dump(infos, f)

    print(f"Database {colored(db_id, 'green')} updated : {colored(update_date, 'green')}.")


def delete_from_cache_file(db_id: str):
    """
    Delete a database from the cache file
    :param db_id: The ID of the database
    """
    abs_cache_path = get_cache_data_path()
    with open(abs_cache_path, 'rb') as f:
        infos = pickle.load(f)

    if db_id in infos:
        del infos[db_id]

    with open(abs_cache_path, 'wb') as f:
        pickle.dump(infos, f)


def open_pkl_file_rb(path: Path):
    """
    Open the pkl file
    """
    if not isinstance(path, Path):
        raise ValueError(f"The path must be a Path object.")
    path = path.absolute()
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"No file named '{path}' found in '{path.parent}' folder.")
    except EOFError:
        raise EOFError(f"File '{path.name}' is empty")
    except pickle.UnpicklingError:
        raise pickle.UnpicklingError(f"File '{path.name}' is corrupted")
    except Exception as e:
        raise Exception(f"Unknown error : {e}")


def recover_update_file():
    faiss_subfolders = os.listdir(_faiss_path)
    to_insert = {}
    for folder in faiss_subfolders:
        times = os.path.getctime(_faiss_path / folder)
        times = datetime.fromtimestamp(times).strftime("%A %d %B %Y - %H:%M:%S")
        to_insert[folder] = times
    if not check_update_file():
        with open(_faiss_data_path, "wb") as f:
            pickle.dump(to_insert, f)
        return True
    return False


def display_update_file():
    infos = open_pkl_file_rb(get_faiss_data_path())
    pprint(infos)


def display_cache_file():
    pprint("\n".join([item.stem for item in get_cache_path().iterdir()]))


if __name__ == '__main__':
    raise Exception("This file isn't intended to be run directly")
