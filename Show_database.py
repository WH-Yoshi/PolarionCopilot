from termcolor import colored

from codes import file_helper as fh


def display_file():
    """
    Display the content of the update file, which represent the last update of each active database
    """
    infos = fh.open_pkl_file_rb(fh.get_update_path())
    for i, (db, date) in enumerate(infos.items()):
        print(f"{colored(f'[{i + 1}]', 'green')} {db.split('%')[0].split('__')[0]} and "
              f"{db.split('%')[0].split('__')[1]} {colored(':', 'green')} "
              f"{date if date is not None else 'No date'}")


if __name__ == '__main__':
    if fh.get_db_path().exists():
        display_file()
    else:
        print(colored('Your database seems empty.', 'yellow'))
        print(colored("You can create databases with 'py ./run_polarion.py' command.", 'yellow'))
