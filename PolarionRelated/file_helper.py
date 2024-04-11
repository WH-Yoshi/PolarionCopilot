import os
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any

from PolarionRelated.enhancer import printarrow

_db_folder_path = './faiss/'
_update_path = "./data/.update_file.pkl"
_backup_path = "./data/.backup.pkl"


def get_abs_backup_path() -> Path:
    """
    Get the absolute path of the backup file
    """
    try:
        return Path(_backup_path).absolute()
    except Exception as e:
        raise Exception(f"Error : {e}")


def get_abs_update_path() -> Path:
    """
    Get the absolute path of the update file
    """
    try:
        return Path(_update_path).absolute()
    except Exception as e:
        raise Exception(f"Error : {e}")


def get_abs_db_path() -> Path:
    """
    Get the absolute path of the databases folder
    """
    try:
        return Path(_db_folder_path).absolute()
    except Exception as e:
        raise Exception(f"Error : {e}")


def check_backup():
    try:
        abs_backup_path = get_abs_backup_path()
        if not abs_backup_path.exists():
            Path(_backup_path).touch()
    except Exception as e:
        raise Exception(f"Error while checking backup file: {e}")


def check_db_folder():
    try:
        abs_dbs_path = get_abs_db_path()
        if not abs_dbs_path.exists():
            os.mkdir(abs_dbs_path)
    except Exception as e:
        raise Exception(f"Error while checking database folder: {e}")


def check_update_file():
    try:
        abs_file_path = get_abs_update_path()
        if not abs_file_path.exists():
            with open(abs_file_path, 'wb') as f:
                pickle.dump({}, f)
    except Exception as e:
        raise Exception(f"Error while checking update file: {e}")


def db_to_update_file(db_name: str, time: str):
    """
    Add a database to the update file
    :param time: The time of the update
    :param db_name: The name of the database
    """
    if not isinstance(db_name, str):
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

    abs_path = get_abs_update_path()
    with open(abs_path, 'rb') as f:
        infos = pickle.load(f)
    infos[db_name] = time
    with open(abs_path, 'wb') as f:
        pickle.dump(infos, f)
    printarrow(f"Database '{db_name}' updated with current date : {infos[db_name]}.")


def open_pkl_file_rb(path: Path) -> Any:
    """
    Open the pkl file
    """
    if not isinstance(path, Path):
        raise ValueError(f"The path must be a Path object.")
    path = Path(path).absolute()
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        print(f"No file named '{path}' found in '{path.parent}' folder.")
    except EOFError:
        print(f"File '{path.name}' is empty")
    except pickle.UnpicklingError:
        print(f"File '{path.name}' is corrupted")
    except Exception as e:
        print(f"Unknown error : {e}")
