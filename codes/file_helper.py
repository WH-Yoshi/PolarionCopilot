import os
import pickle
from datetime import datetime
from pathlib import Path
import pandas as pd
from pprint import pprint

from termcolor import colored

current_path = Path(__file__)

_faiss_db_path = current_path.parent.parent / "faiss_databases"
_catalog_path = current_path.parent.parent / "catalog"
_cache_path = current_path.parent.parent / ".cache"
_cache_catalog_path = current_path.parent.parent / "catalog" / ".cache.pkl"
_faiss_catalog_path = current_path.parent.parent / "catalog" / ".faiss_db.pkl"


def get_faiss_catalog_path() -> Path:
    """
    Returns /catalog/.faiss_db.pkl absolute path
    """
    try:
        get_catalog_path()
        update_path = Path(_faiss_catalog_path).absolute()
        if not update_path.exists():
            update_path.touch()
            with open(update_path, 'wb') as f:
                pickle.dump({}, f)
        return update_path
    except Exception as e:
        raise Exception(f"Error : {e}")



def get_cache_catalog_path() -> Path:
    """
    Returns /catalog/.cache.pkl absolute path
    """
    try:
        get_cache_path()
        cache_path = Path(_cache_catalog_path).absolute()
        if not cache_path.exists():
            cache_path.touch()
            with open(cache_path, 'wb') as f:
                pickle.dump({}, f)
        return cache_path
    except Exception as e:
        raise Exception(f"Error : {e}")


def get_catalog_path() -> Path:
    """
    Returns /catalog/ absolute path
    """
    try:
        data_path = Path(_catalog_path).absolute()
        if not data_path.exists():
            data_path.mkdir(parents=True)
        return data_path
    except Exception as e:
        raise Exception(f"Error : {e}")


def get_faiss_db_path() -> Path:
    """
    Returns /faiss_databases/ absolute path
    """
    try:
        db_path = Path(_faiss_db_path).absolute()
        if not db_path.exists():
            db_path.mkdir(parents=True)
        return db_path
    except Exception as e:
        raise Exception(f"Error : {e}")


def get_cache_path() -> Path:
    """
    Returns /.cache/ absolute path
    """
    try:
        cache_path = Path(_cache_path).absolute()
        if not cache_path.exists():
            cache_path.mkdir(parents=True)
        return cache_path
    except Exception as e:
        raise Exception(f"Error : {e}")


def faiss_db_filled():
    """
    Check if the /faiss_databases/ folder is empty or not
    Returns:
        True if the folder is not empty, False otherwise
    """
    try:
        dbs = os.listdir(get_faiss_db_path())
        if dbs:
            return True
        return False
    except Exception as e:
        raise Exception(f"Error while checking database folder: {e}")


def faiss_catalog_filled():
    """
    Check if the faiss catalog file is empty or not
    Returns:
        True if the file is not empty, False otherwise
    """
    try:
        infos = open_pkl_file_rb(get_faiss_catalog_path())
        if not infos or infos == {}:
            return False
        return True
    except Exception as e:
        raise Exception(f"Error while checking update file: {e}")


def db_to_faiss_catalog(db_id: str, pr_name: str, release: str, pr_type: str, wi_type: list[str], update_date: datetime):
    """
    Add a database to the faiss catalog.

    :param db_id: The ID of the database
    :param pr_name: The name of the database
    :param release: The release of the database
    :param pr_type: The type of the database (project or group)
    :param wi_type: The type of workitems in the database
    :param update_date: The date of the last update
    """
    abs_update_path = get_faiss_catalog_path()
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
    abs_cache_path = get_cache_catalog_path()
    with open(abs_cache_path, 'rb') as f:
        infos = pickle.load(f)

    del infos[db_id]

    with open(abs_cache_path, 'wb') as f:
        pickle.dump(infos, f)


def open_pkl_file_rb(path: Path):
    """
    Open the pkl file in read binary mode
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


def delete_uncatalogued_db():
    """
    Delete all the databases that aren't followed by the catalog
    """
    try:
        dbs = os.listdir(get_faiss_db_path())
        catalog = open_pkl_file_rb(get_faiss_catalog_path())
        for db in dbs:
            if db not in catalog.keys():
                db_path = get_faiss_db_path() / db
                os.remove(db_path)
                print(f"Uncatalogued database {colored(db, 'red')} deleted.")
    except Exception as e:
        raise Exception(f"Error while deleting databases: {e}")


def delete_all_databases():
    """
    Delete all the databases
    """
    try:
        dbs = os.listdir(get_faiss_db_path())
        for db in dbs:
            db_path = get_faiss_db_path() / db
            os.remove(db_path)
    except Exception as e:
        raise Exception(f"Error while deleting databases: {e}")


def path_to_certs() -> Path:
    """
    Returns the path to the certificates
    """
    try:
        cert_path = current_path.parent.parent / 'certifi' / 'ca-certificates.crt'
        return cert_path
    except Exception as e:
        raise Exception(f"Error : {e}")


def get_glossary(path: str | Path) -> dict:
    """
    Read the glossary file and return it as a dictionary
    """
    try:
        df = pd.read_csv(path, on_bad_lines='skip', header=None, delimiter=';')
        glossary_dict = dict(zip(df[0], df[1]))
        return glossary_dict
    except Exception as e:
        raise Exception(f"Error while reading glossary file: {e}")


def get_css(path: str | Path) -> str:
    """
    Read the css file and return the content as a string
    """
    try:
        with open(path, 'r') as css_file:
            css_content = css_file.read()
        return css_content
    except Exception as e:
        raise Exception(f"Error while reading css file: {e}")


if __name__ == '__main__':
    raise Exception("This file isn't intended to be run directly")
