import html
import os
import pickle
import re
import shutil
import sys
from typing import List, Any

import certifi

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

load_dotenv()
print(certifi.where())

api_url = "http://localhost:22027"
base_url = 'https://polarion.goiba.net/polarion'
file_name = 'last_update_date.pkl'


def get_polarion_instance() -> Polarion:
    """
    Get a Polarion instance with the user's credentials or a token
    :return: A Polarion instance
    """
    return Polarion(base_url, 'aixyf', password=None, token=os.environ.get("polarion_token"))


def get_project(cl: Polarion, project_id: str = "PT_L2_TSS_Subsystem") -> Project:
    """
    Get a project from the Polarion instance
    :param cl: The Polarion instance
    :type cl: Polarion
    :param project_id: A string representing the project's id
    :type project_id: str
    :return: A project object
    """
    project_from_id = cl.getProject(project_id)
    return project_from_id


def get_last_update_date(file: str) -> datetime | None:
    """
    Get the last update date from a pkl file.
    Should be a datetime.date() object
    :param file: The file containing the last update date
    :type file: str
    :return: A datetime object
    """
    try:
        with open(file, 'rb') as f:
            last_update_date = pickle.load(f)
            return last_update_date
    except FileNotFoundError:
        print(f"No file named '{file}' found in '{Path().absolute()}' folder.")
    except EOFError:
        print(f"File '{file}' is empty")
        return None
    except pickle.UnpicklingError:
        print(f"File '{file}' is corrupted")
    except Exception as e:
        print(f"An error occurred: {e}")


def save_last_update_date(file: str) -> bool:  # MUST BE CALLED *AFTER* THE WORKITEMS HAVE BEEN SAVED IN DATABASE
    """
    Save the new update date in a pkl file
    :param file: The file containing the last update date
    :type file: str
    :return: True if the file has been successfully updated, False otherwise
    :rtype: bool
    """
    if not Path(file).exists():
        print(f"Intializing update date file:\n"
              f" \u21AA  Creating 'last_update_date.pkl' file with following content: '{datetime.now().date()}'")
    else:
        last_update = get_last_update_date(file)
        print(f"Changing update date:\n"
              f" \u21AA  Deleting '{file}' file following content: '{last_update}' for '{datetime.now().date()}'")

    valid_input = False
    while not valid_input:
        input_content = input("Do you want to continue? (y/n): ")
        if input_content in ['n', 'N', 'no', 'No', 'NO']:
            print("\tOperation cancelled: Workitems not saved in database.")
            return False
        elif input_content in ['y', 'Y', 'ye', 'Ye', 'YE', 'yes', 'Yes', 'YES']:
            try:
                with open(file, 'wb') as f:
                    pickle.dump(datetime.now().date(), f)
                print(f"\tFile '{file}' content successfully modified with: {get_last_update_date(file)}")
                return True
            except FileNotFoundError:
                print(f"\tNo file named '{file}' found in '{Path().absolute()}' folder.")
                return False
            except pickle.PicklingError:
                print(f"\tAn error occurred while pickling the data into '{file}' file.")
                return False
            except Exception as e:
                print(f"\tAn error occurred: {e}")
                return False
        else:
            print("\tInvalid input.")


def get_updated_workitems(project: Project, updated_since: datetime = None) -> list[Workitem] | None:
    """
    Get all workitems updated since the last update
    :param project: A Polarion project
    :param updated_since: A datetime.date() object representing the last update date
    :return: A list of workitems
    """
    if updated_since is None:
        query = 'type:(requirement safetydecision) AND NOT created:20240312'
        print("Getting all workitems since update date is not available.")
    else:
        if not isinstance(project, Project):
            raise TypeError("The project parameter must be a Polarion object")
        if not isinstance(updated_since, datetime):
            raise TypeError("The updated_since parameter must be a datetime object")

        query = f'type:(requirement safetydecision) updated:[{updated_since.strftime("%Y%m%d")} TO 30000000]'
        print("Getting workitems updated since:", updated_since.strftime("%Y%m%d"))

    workitem_list = project.searchWorkitemFullItem(query)
    return workitem_list if save_last_update_date(file_name) else None


def workitem_to_embed(workitems: list[Workitem]) -> list[list[list[str | Any] | Any]]:
    """
    Create a list of workitems with their metadatas, to embed in the database
    :param workitems: A list of Polarion workitems
    :return: A list of workitems with their metadatas
    """
    new_workitems = []

    for workitem in workitems:
        try:
            workitem.children = doc.getChildren(workitem)
            if workitem.children is not None or workitem.children != []:
                for child in workitem.children:
                    workitem.description.content += "\n" + child.description.content
        except Exception as e:
            print(e)
            pass

    for workitem in workitems:
        try:
            parent = doc.getParent(workitem)
            print(workitem.id)
        except IndexError as e:
            new_workitems.append(workitem)
            pass
        except AttributeError as e:
            pass

    livedoc_url = f'/#/project/{project.id}/workitem?id='
    workitems_to_embed = [[workitem.description.content, [item['value'], base_url + livedoc_url + workitem.id]]
                          for workitem in new_workitems for item in
                          workitem.customFields.Custom if item['key'] == 'ibaFullPuid']

    return workitems_to_embed


def get_workitem(p: Project, name: str) -> Workitem:
    return p.getWorkitem(name)


def lprint(data):
    pprint(data)


def get_document(project) -> Document:
    return project.getDocuments()[1]


def str_cleaner(text: str) -> str:
    """
    Clean a string from HTML tags and other characters
    :param text: The string to clean
    :type text: str
    :return: The cleaned string
    :rtype: str
    """
    if not isinstance(text, str):
        raise TypeError("The text must be a string")
    # Convert HTML entities (like &amp;) into their corresponding characters (like &)
    text = html.unescape(text)
    # if a </ul> is at the end of the string, remove it
    text = re.sub(r'</?ul>$', '', text)
    # if a </ul> is at the end of the string, remove it
    text = re.sub(r'<li>$', '', text)
    # replace <li> or </li> with a ',' character
    text = re.sub(r'</li>', ',', text)
    # replace <li> or </li> with a newline character
    text = re.sub(r'</?li>', ' ', text)
    # Remove tab characters
    text = text.replace("\t", "")
    # Remove newline characters
    text = text.replace("\n", "")
    # Remove carriage return characters
    text = text.replace("\r", "")
    # Remove leading whitespace characters
    text = text.lstrip()
    # Use a regular expression to remove any HTML tags in the text
    text = re.sub('<.*?>', '', text)
    # Replace sequences of more than one space with a single space
    text = re.sub(' +', ' ', text)
    # Remove any whitespace after a dot if it's not followed by something that is not a whitespace
    text = re.sub(r'(?<=\.)\s*(?!.)', '', text)
    # Make sure there is a space after a period if it's followed by any capital character
    text = re.sub(r'(?<=\.)\s*(?=[A-Z])', ' ', text)
    # Remove any spaces that occur immediately before a period
    text = re.sub(r'\s+(?=\.)', '', text)
    # Remove any spaces that occur immediately after an opening parenthesis
    text = re.sub(r'\(\s+', '(', text)
    # Verify that there will always be a space after a closing parenthesis if there is no period after it
    text = re.sub(r'\)\s+(?![a-z,A-Z])', ')', text)
    # Remove any spaces that occur immediately before a comma
    text = re.sub(r'\s+,', ',', text)
    # Add a space after a closing parenthesis if it's followed by any capital character
    text = re.sub(r'\)(?=[a-z,A-Z])', ') ', text)
    return text


def create_vector_db(data: List[str], db_path: Path | str):
    """
    Create a vector database from a list of strings
    :param data: The list of strings
    :type data: List[str]
    :param db_path: The path to the database
    :type db_path: str
    """
    if not isinstance(data, list):
        raise TypeError("The data must be a list")
    if not isinstance(db_path, str):
        raise TypeError("The db_path must be a string")

    if os.path.exists(db_path):
        shutil.rmtree(db_path)

    db_path_abs = Path(db_path).absolute()
    embeddings = HuggingFaceHubEmbeddings(model=api_url)

    descriptions = [description for description, _ in data]
    metadatas = [{"reference": reference[0], "url": reference[1]} for _, reference in data]

    batch_size = 32
    texts = [descriptions[i:i + batch_size] for i in range(0, len(descriptions), batch_size)]
    metadatas = [metadatas[i:i + batch_size] for i in range(0, len(metadatas), batch_size)]

    faiss = FAISS.from_texts(texts=texts[0], metadatas=metadatas[0], embedding=embeddings)
    for i, text in enumerate(texts[1:], start=1):
        faiss.add_texts(texts=text, metadatas=metadatas[i])

    faiss.save_local(str(db_path_abs))


if __name__ == '__main__':
    client = get_polarion_instance()  # To modify: use a python unique token or a user's credentials
    project = get_project(client)  # To modify: after discussion of which project to include in DB. Return project[]

    doc = get_document(project)  # Will be deleted depending on demand
    workitems = get_workitems(doc, ['requirement', 'safetydecision'])
    workitem_to_embed = workitem_to_embed(workitems)
    lprint(workitem_to_embed)

    # Vector db related
    # filtered_list = file_loader('../data/polarion_xml_fetch.pkl')
    # create_vector_db(filtered_list, '../faiss/polarion-tei')
