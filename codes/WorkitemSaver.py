"""
Save Workitems from a given RELEASE (e.g. R12.3, R12.4, AI-V2.4.0.0, etc.) in a corresponding database.
R13.3 will have a different database than R12.4, for example.
"""
import html
import os
import pickle
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceHubEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from polarion.polarion import Polarion
from polarion.workitem import Workitem
from termcolor import colored

import file_helper as fh
from enhancer import printarrow, Loader, arrow

load_dotenv()


class WorkitemSaver:
    """
    This class is used as a Workitem Saver. It saves workitems from a given project or project group in a database.
    After instantiating the class, you can call the caller method to start the process like so :
    WorkitemSaver.caller()
    :param saver_id: A string representing the project or project group id
    :param type_chosen: A string representing the choice between 'project' or 'group'
    :param release: [Optional] A string representing the release
    """
    db_folder_name = fh.get_db_path()

    def __init__(self, saver_id: str, type_chosen: str, release: str | None = "", time: str | None = None):
        self.id = saver_id
        self.type_chosen = type_chosen
        self.release = release
        self.base_url = os.environ.get("base_url")
        self.embedding_api = os.environ.get("embedding_api")
        self.save_path = ""
        self.update_file_path = fh.get_update_path()
        self.now = ""
        self.client = self.get_polarion_instance()
        self.time = time

    def get_polarion_instance(self) -> Polarion:
        """
        Get a Polarion instance with the user's credentials or a token
        :return: A Polarion instance
        """
        loader = Loader("Getting the Polarion instance... ", arrow("Done !"), timeout=0.1).start()
        try:
            client = Polarion(
                self.base_url,
                user=os.environ.get("polarion_user"),
                password=None,
                token=os.environ.get("polarion_token")
            )
        except Exception as e:
            raise Exception(f"Error while getting the Polarion instance. Did you create .env file ? : {e}")
        loader.stop()
        return client

    def check_release(self, release: str) -> list[Workitem] | None:
        """
        Check if the release exists in the PTS_Config project
        :param release: A string representing the name of the release
        :return: Should return only one workitem associated to the release
        """
        if not isinstance(release, str):
            raise TypeError("The release parameter must be a string")

        print(f"Checking if {colored('release', 'green')} exists...")
        try:
            pts_config = self.client.getProject("PTS_Config")
            query = f'title:"{release}"'
            match = pts_config.searchWorkitemFullItem(query, field_list=['id'])
            if not match:
                raise ValueError(
                    f"Release '{release}' not found in PTS_Config project. Make sure it's the exact title.")
            elif len(match) > 1:
                raise ValueError(f"Multiple releases found with the title '{release}'...")
            else:
                printarrow(f'Found release "{colored(release,"green")}" with id: {match[0].id}.', start="\n")
                return match
        except Exception as e:
            raise Exception(f"Error while searching for the release: {e}")

    def define_query(
            self,
            additional_query: str | None = ""
    ) -> str:
        """
        Define the query to get workitems from a project or a project group
        :param additional_query: [Optional] A string representing an additional query
        :return: A string representing the query
        """
        if not isinstance(additional_query, str) and additional_query is not None:
            raise TypeError("The additional_query parameter must be a string")

        if self.release and self.release != "None":
            match = self.check_release(self.release)
            query = f"""type:("requirement" "safetydecision") AND NOT ibaFullPuid:("(cont'd)") AND 
            ibaApplicableConfiguration.KEY:("{match[0].id}")"""
            self.save_path = WorkitemSaver.db_folder_name / f'{match[0].id}__{self.release}%project'
        else:
            query = """type:("requirement" "safetydecision") AND NOT ibaFullPuid:("(cont'd)")"""
        query += f" AND {additional_query}" if additional_query else ""
        return query

    def get_workitems_from_group(
            self,
            project_group_id: str,
            additional_query: str | None = ""
    ) -> list[Workitem]:
        """
        Get a list of workitems (requirement and safety decisions) from the given Group
        :param additional_query: [Optional] A string representing an additional query
        :param project_group_id: A string representing the project group id
        :return: A list of project objects
        """
        if not isinstance(project_group_id, str):
            raise TypeError("The group_name parameter must be a Project Group object")

        self.now = datetime.now().strftime("%A %d %B %Y - %H:%M:%S")
        query = self.define_query(additional_query)
        project_group = self.client.getProjectGroup(project_group_id)

        try:
            print(f"Getting {colored('workitems','green')} from groups... might take a long time")
            workitems = project_group.get_workitem_with_fields(query=query,
                                                               field_list=['id', 'description', 'project',
                                                                           'linkedWorkItems',
                                                                           'customFields.ibaFullPuid'])
            return workitems
        except Exception as e:
            raise Exception(f"Error while getting the workitems: {e}")

    def get_workitems_from_project(
            self,
            project_id: str,
            additional_query: str | None = ""
    ) -> list[Workitem]:
        """
        Get workitems with a query from a project
        :param additional_query: [Optional] A string representing an additional query
        :param project_id: A string representing the project id
        :return: A list of workitems
        """
        if not isinstance(project_id, str):
            raise TypeError("The project parameter must be a Polarion project object")

        self.now = datetime.now().strftime("%A %d %B %Y - %H:%M:%S")
        query = self.define_query(additional_query)
        project = self.client.getProject(project_id)

        try:
            print(f"Getting {colored('workitems','green')} from project... might take a while for big queries.")
            workitem_list = project.searchWorkitemFullItem(query=query,
                                                           field_list=['id', 'description', 'project',
                                                                       'linkedWorkItems', 'customFields.ibaFullPuid'])
            return workitem_list
        except Exception as e:
            raise Exception(f"Error while getting the workitems: {e}")

    def workitem_to_embed(
            self,
            full_workitems_list: list[Workitem],
    ) -> list[Workitem]:
        """
        Get linked workitems from every workitems in the list and add them to the parent description.
        Create a list of workitems and their metadatas ready to embed
        :param full_workitems_list: A list of workitems
        :return: A tuple of workitems with their metadatas
        """
        if not isinstance(full_workitems_list, list):
            raise TypeError("The full_workitems_list parameter must be a list")
        if not full_workitems_list:
            raise ValueError("The full_workitems_list list must not be empty, this means that there is no workitem"
                             "of type 'requirement' or 'safetydecision' in the project or project group.")

        merged_workitems = []

        print(f"\nGetting {colored('children','green')}... might take a while accordingly")
        for i, workitem in enumerate(full_workitems_list):
            sent = (' \u21AA  Loading workitems children: ' + str(i + 1) + ' of ' + str(len(full_workitems_list)))
            sys.stdout.write('\r' + sent)
            try:
                linked_workitems_description = []
                if workitem.description is not None and workitem.description != "" and \
                        workitem.customFields['Custom'][0]['value'] != "(cont'd)":
                    for w in workitem.getLinkedItemWithFields(
                            ['id', 'description', 'customFields.ibaFullPuid', 'type']):
                        if w.type['id'] in ["safetydecision", "requirement"]:
                            for field in w.customFields['Custom']:
                                if field['value'] == "(cont'd)":
                                    linked_workitems_description.append(w.description.content)
                    for description in linked_workitems_description:
                        if description and workitem.description is not None:
                            workitem.description.content += f', {description}'
                    merged_workitems.append(workitem)
            except AttributeError as e:
                raise AttributeError(e)
            except Exception as e:
                if "Workitem not retrieved from Polarion" in str(e):
                    print(f"\nWorkitem {colored(workitem.id,'red')} not retrieved from Polarion")
                else:
                    raise Exception(e)
        return merged_workitems

    def format_workitem(
            self,
            merged_workitems: list[Workitem]
    ) -> list[tuple[str, tuple[Any, str | Any]]]:
        try:
            workitems_to_embed = [
                (
                    self.str_cleaner(workitem.description.content),
                    (item['value'], self.base_url + f'/#/project/{workitem.project.id}/workitem?id=' + workitem.id),
                )
                for workitem in merged_workitems for item in
                workitem.customFields.Custom if item['key'] == 'ibaFullPuid'
            ]
            return workitems_to_embed
        except Exception as e:
            raise e

    def str_cleaner(self, text: str) -> str:
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
        # if a </li> is at the end of the string, remove it
        text = re.sub(r'<li>$', '', text)
        # replace <li> or </li> with a ',' character
        text = re.sub(r'</li>', ',', text)
        # replace <li> or </li> with a newline character
        text = re.sub(r'</?li>', ' ', text)
        # Replace <br> tags with a newline character
        text = re.sub(r'(?<!:)<br/>', ". ", text)
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
        # Make sure a white space is after a dot if it's not a dot of end of sentence
        text = re.sub(r'\.(?=\S)', '. ', text)
        # Remove any whitespace after a dot if it's not followed by something that is not a whitespace
        text = re.sub(r'(?<=\.)\s*(?!.)', '', text)
        # Make sure there is a space after a dot if it's followed by any capital character
        text = re.sub(r'(?<=\.)\s*(?=[A-Z])', ' ', text)
        # Remove any spaces that occur immediately before a dot
        text = re.sub(r'\s+(?=\.)', '', text)
        # Remove any spaces that occur immediately after an opening parenthesis
        text = re.sub(r'\(\s+', '(', text)
        # Verify that there will always be a space after a closing parenthesis if there is no dot after it
        text = re.sub(r'\)\s+(?![a-z,A-Z])', ')', text)
        # Remove any spaces that occur immediately before a comma
        text = re.sub(r'\s+,', ',', text)
        # Add a space after a comma if it's not followed by a whitespace
        text = re.sub(r',(?!\s)', ', ', text)
        # Remove a comma if it's at the end of the string
        text = re.sub(r'\.,\s*$', '.', text)
        # Add a space after a closing parenthesis if it's followed by any capital character
        text = re.sub(r'\)(?=[a-zA-Z])', ') ', text)
        # Add whitespace after a double dot if it's not followed by a whitespace
        text = re.sub(r':(?=\S)', ': ', text)
        return text

    def create_vector_db(
            self,
            data: list[tuple[Any, tuple[Any, str | Any]]],
            db_path: Path,
            from_existent: bool | None = None
    ):
        if not isinstance(data, list):
            raise TypeError("The data must be a list")
        if not isinstance(db_path, Path):
            raise TypeError("The db_path must be a Path object")
        if not data:
            raise Exception("This error comes because the function received a empty list. This means that there are no "
                            "workitems with the IBAApplicabilityConfiguration field set to the release you provided in "
                            "that particular project or project group.")

        if os.path.exists(db_path) and not from_existent:
            deleted = False
            while not deleted:
                user_input = input(f"The path '{db_path}' already exists. Press [Enter] to delete it and continue.")
                if user_input == "":
                    deleted = True
                    shutil.rmtree(db_path)
                else:
                    print("Exiting...")
                    sys.exit(0)

        absolute_db_path = db_path.absolute()
        embeddings = HuggingFaceHubEmbeddings(model=self.embedding_api, model_kwargs={"truncate": True})

        descriptions = []
        metadatas = []
        for description, reference in data:
            if description != "":
                chunks = [description[i:i + 1000] for i in range(0, len(description), 1000)]
                descriptions.extend(chunks)
                metadatas.extend([{"ibafullpuid": reference[0], "url": reference[1]}] * len(chunks))

        batch_size = 32
        texts = [descriptions[i:i + batch_size] for i in range(0, len(descriptions), batch_size)]
        metadatas = [metadatas[i:i + batch_size] for i in range(0, len(metadatas), batch_size)]
        if from_existent:
            faiss = FAISS.load_local(str(absolute_db_path), embeddings, allow_dangerous_deserialization=True)
            loader = Loader("Precessing embeddings...", "That was fast!", timeout=0.1).start()
            for i, text in enumerate(texts):
                faiss.add_texts(text, metadatas[i])
        else:
            faiss = FAISS.from_texts(texts=texts[0], metadatas=metadatas[0], embedding=embeddings)
            loader = Loader("Precessing embeddings...", "That was fast!", timeout=0.1).start()
            for i, text in enumerate(texts[1:], start=1):
                faiss.add_texts(texts=text, metadatas=metadatas[i])
        loader.stop()

        faiss.save_local(str(absolute_db_path))
        fh.db_to_update_file(db_path, self.now)

    def caller(self) -> None:
        cache_path = fh.get_cache_path()
        cache_path = cache_path / f"cache_{self.id}__{self.release}%{self.type_chosen}.pkl"
        if not cache_path.exists():
            cache_path.parent.mkdir(parents=True, exist_ok=True)
        workitems = []

        if self.time:  # When updating a DB
            format_time = "%A %d %B %Y - %H:%M:%S"
            try:
                result = datetime.strptime(self.time, format_time)
                result = result.strftime("%Y%m%d")
                add_query = f"updated:[{result} TO 30000000] created:[{result} TO 30000000]"
            except ValueError as e:
                raise ValueError(f"The format is not good: {e}")
            if self.type_chosen == "group":
                workitems = self.get_workitems_from_group(self.id, add_query)
            elif self.type_chosen == "project":
                workitems = self.get_workitems_from_project(self.id, add_query)
            if not workitems:
                print(colored(" \u21AA  The database is already up to date!", 'green'))
                sys.exit(0)
            merged_workitems = self.workitem_to_embed(workitems)
            formatted_list_workitems = self.format_workitem(merged_workitems)
            self.save_path = WorkitemSaver.db_folder_name / f"{self.id}__{self.release}%{self.type_chosen}"
            self.create_vector_db(formatted_list_workitems, self.save_path, from_existent=True)

        else:  # When saving a new DB
            print("Checking .cache")
            if os.path.exists(cache_path):
                with open(cache_path, 'rb') as f:
                    formatted_list_workitems = pickle.load(f)
                    self.save_path = WorkitemSaver.db_folder_name / f'{self.id}__{self.release}%{self.type_chosen}'
                    printarrow(".cache loaded")
                file_time = os.path.getctime(cache_path)
                self.now = datetime.fromtimestamp(file_time).strftime("%A %d %B %Y - %H:%M:%S")
            else:
                printarrow(".cache empty")
                if self.type_chosen == "group":
                    workitems = self.get_workitems_from_group(self.id)
                elif self.type_chosen == "project":
                    workitems = self.get_workitems_from_project(self.id)
                else:
                    raise ValueError("The choice parameter must be either 'project' or 'group'")
                merged_workitems = self.workitem_to_embed(workitems)
                formatted_list_workitems = self.format_workitem(merged_workitems)
                with open(cache_path, 'wb') as f:
                    pickle.dump(formatted_list_workitems, f)
                    print("\nCache saved")
                    self.save_path = WorkitemSaver.db_folder_name / f'{self.id}__{self.release}%{self.type_chosen}'

            self.create_vector_db(formatted_list_workitems, self.save_path)

        if os.path.exists(cache_path):
            os.remove(cache_path)


if __name__ == '__main__':
    raise Exception("This module is not intended to be run directly. Run Polarion.py instead")
