from termcolor import colored
from codes import file_helper as fh


def load_faiss_catalog_file():
    """
    Load the content of the faiss catalog.
    """
    return fh.open_pkl_file_rb(fh.get_faiss_catalog_path())


def print_formatted_info(info):
    """
    Print the information in a formatted manner.
    """
    for db_id, details in info.items():
        print(colored(f"Database ID: {db_id}", 'green'))
        print(f"  Location: {details['location']}")
        print(f"  Release: {details['release']}")
        print(f"  Type: {'Project' if details['type'] == 'project' else 'Project group'}")
        print(f"  Workitem Types: {', '.join(details['workitem_type'])}")
        print(f"  Last Updated: {details['last_update']}")
        print("-" * 45)


def display_file():
    """
    Display the content of the faiss catalog, which contains the information about the databases.
    """
    infos = load_faiss_catalog_file()
    print_formatted_info(infos)


def show_database():
    if fh.get_faiss_db_path().exists() and any(fh.get_faiss_db_path().iterdir()):
        display_file()
    else:
        print(colored("Your database seems empty.\nYou can create databases with 'py ./run_polarion.py' command.", "yellow"))


if __name__ == "__main__":
    fh.delete_uncatalogued_db()
    show_database()
