import os
import pickle
import site
from datetime import datetime
from pathlib import Path
from pprint import pprint
from termcolor import colored


current_path = Path(__file__)

_db_folder_path = current_path.parent.parent / "faiss"
_data_path = current_path.parent.parent / "data"
_update_path = current_path.parent.parent / "data" / ".update_file.pkl"
_cache_path = current_path.parent.parent / ".cache"


def get_update_path() -> Path:
    """
    Returns ../folder/update_file absolute path
    """
    try:
        return Path(_update_path).absolute()
    except Exception as e:
        raise Exception(f"Error : {e}")


def get_db_path() -> Path:
    """
    Returns ../db_folder/ absolute path
    """
    try:
        return Path(_db_folder_path).absolute()
    except Exception as e:
        raise Exception(f"Error : {e}")


def get_cache_path() -> Path:
    """
    Returns ../cache_folder/ absolute path
    """
    try:
        return Path(_cache_path).absolute()
    except Exception as e:
        raise Exception(f"Error : {e}")


def check_db_folder():  # First to check
    try:
        abs_dbs_path = get_db_path()
        if abs_dbs_path.exists():
            dbs = os.listdir(abs_dbs_path)
            if dbs:
                return True
            return False
        else:
            os.mkdir(abs_dbs_path)
            return False
    except Exception as e:
        raise Exception(f"Error while checking database folder: {e}")


def check_update_file():  # second one
    try:
        abs_file_path = get_update_path()
        if abs_file_path.exists():
            infos = open_pkl_file_rb(abs_file_path)
            if not infos or infos == {}:
                return False
            return True
        else:
            if not Path(_data_path).exists():
                Path(_data_path).mkdir()
            with open(abs_file_path, 'wb') as f:
                pickle.dump({}, f)
            return False
    except Exception as e:
        raise Exception(f"Error while checking update file: {e}")


def db_to_update_file(db_name: Path, time: str):
    """
    Add a database to the update file
    :param time: The time of the update
    :param db_name: The name of the database
    """
    if not isinstance(db_name, Path):
        raise ValueError(f"The database name must be a string.")
    if not isinstance(time, str):
        raise ValueError(f"The time must be a string.")

    format_time = "%A %d %B %Y - %H:%M:%S"
    try:
        result = bool(datetime.strptime(time, format_time))
    except ValueError:
        result = False
    if not result:
        raise ValueError(f"The time format is incorrect.")

    abs_path = get_update_path()
    with open(abs_path, 'rb') as f:
        infos = pickle.load(f)
    infos[db_name.name] = time
    with open(abs_path, 'wb') as f:
        pickle.dump(infos, f)
    print(f"Database '{colored(db_name.name, 'green')}': last update date : {colored(infos[db_name.name], 'green')}.")


def open_pkl_file_rb(path: Path) -> dict[str, datetime | None] | None:
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
    faiss_subfolders = os.listdir(_db_folder_path)
    to_insert = {}
    for folder in faiss_subfolders:
        times = os.path.getctime(_db_folder_path / folder)
        times = datetime.fromtimestamp(times).strftime("%A %d %B %Y - %H:%M:%S")
        to_insert[folder] = times
    if not check_update_file():
        with open(_update_path, "wb") as f:
            pickle.dump(to_insert, f)
        return True
    return False


def display_pkl_file():
    infos = open_pkl_file_rb(get_update_path())
    pprint(infos)


if __name__ == '__main__':
    raise Exception("This file isn't intended to be run directly")
