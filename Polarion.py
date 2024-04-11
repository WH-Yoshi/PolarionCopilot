"""
Main code that will maybe launch a GUI to select the database to save workitems in
"""
from PolarionRelated.WorkitemSaver import WorkitemSaver
from PolarionRelated.file_helper import check_update_file, check_db_folder, check_backup
from PolarionRelated import file_helper as fh


def display_file():
    """
    Display the content of the update file
    """
    path = fh.get_abs_update_path()
    update_dict = fh.open_pkl_file_rb(path)
    try:
        for i, (db, date) in enumerate(update_dict.items()):
            print(f"[{i + 1}] {db.split('%')[0].split('__')[0]} and {db.split('%')[0].split('__')[1]} : "
                  f"{date if date is not None else 'No date'}")
    except Exception as e:
        raise Exception(f"An error occurred while displaying the file: {e}")


if __name__ == "__main__":
    check_backup()
    check_db_folder()
    check_update_file()

    action_available = ["Update", "Save"]
    action_choice = ""
    while action_choice not in [str(i) for i in range(1, len(action_available) + 1)]:
        action_choice = input(
            "Invalid input. Please enter either '1' or '2': "
            if action_choice else "Choose an action:\n[1] Update\n[2] Save\n")

    if action_choice == "1":
        print("Which database do you want to update ?")
        display_file()
        db_choice = ""
        while db_choice not in [str(i) for i in range(1, len(fh.open_pkl_file_rb(fh.get_abs_update_path())) + 1)]:
            db_choice = input(
                "Invalid input : "
                if db_choice else "Enter the number of the database you want to update: ")

    else:
        type_choice = ""
        while type_choice not in ["project", "group"]:
            type_choice = input(
                "Invalid input. Please enter either 'project' or 'group': "
                if type_choice else "Do you want to save workitems from a project or a project group ? (project / "
                                    "group): ")

        if type_choice == "group":
            project_or_group_id_input = input("Project group ID (e.g. Therapy_Center_Spec, L2_System_Spec, ...): ")
        else:
            project_or_group_id_input = input("Project ID (e.g. PT_L2_TSS_Subsystem, PT_User_Requirements, ...): ")

        # Release examples: "P235-R12.3.0", "P235-R12.4.0", "AI-V2.4.0.0", etc...
        release_input = input("Release (e.g. AI-V2.4.0.0, P235-R12.4.0, ...): ") or None

    ws = WorkitemSaver(project_or_group_id_input, type_choice, release_input)
