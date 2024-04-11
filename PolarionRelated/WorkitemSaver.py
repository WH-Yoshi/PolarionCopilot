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
from polarion.project import Project
from polarion.project_groups import ProjectGroup
from polarion.workitem import Workitem

from PolarionRelated import file_helper as fh
from PolarionRelated import enhancer as en

load_dotenv()


class WorkitemSaver:
    def __init__(self, id: str, type_chosen: str, release: str | None = None):
        self.id = id
        self.type_chosen = type_chosen
        self.release = release
        self.api_url = os.environ.get("api_url")
        self.base_url = os.environ.get("base_url")
        self.db_folder_name = '../faiss/'
        self.save_path = ""
        self.update_file_path = "../data/.update_file.pkl"
        self.now = ""
        self.client = self.get_polarion_instance()

        self.main()

    def get_polarion_instance(self) -> Polarion:
        """
        Get a Polarion instance with the user's credentials or a token
        :return: A Polarion instance
        """
        print("Getting Polarion instance...")
        try:
            client = Polarion(self.base_url, 'aixyf', password=None, token=os.environ.get("polarion_token"))
        except Exception as e:
            raise Exception(f"Error while getting the Polarion instance: {e}")
        return client

    def check_release(self, release: str) -> list[Workitem] | None:
        """
        Check if the release exists in the PTS_Config project
        :param release: A string representing the name of the release
        :return: Should return only one workitem associated to the release
        """
        if not isinstance(release, str):
            raise TypeError("The release parameter must be a string")

        print("Checking if release exists...")
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
                en.printarrow(f'Found release "{release}" with id: {match[0].id}.', start="\n")
                return match
        except Exception as e:
            raise Exception(f"Error while searching for the release: {e}")

    def define_query(
            self,
            release: str | None = None,
            additional_query: str | None = ""
    ) -> str:
        """
        Define the query to get workitems from a project or a project group
        :param release: [Optional] A string representing the release
        :param additional_query: [Optional] A string representing an additional query
        :return: A string representing the query
        """
        if not isinstance(release, str) and release is not None:
            raise TypeError("The release parameter must be a string")
        if not isinstance(additional_query, str) and additional_query is not None:
            raise TypeError("The additional_query parameter must be a string")

        if release:
            match = self.check_release(release)
            query = f"""type:("requirement" "safetydecision") AND NOT ibaFullPuid:("(cont'd)") AND 
            ibaApplicableConfiguration.KEY:("{match[0].id}")"""
            self.save_path = self.db_folder_name + f'{match[0].id}__{release}%project'
        else:
            query = """type:("requirement" "safetydecision") AND NOT ibaFullPuid:("(cont'd)")"""
        query += f" AND {additional_query}" if additional_query else ""
        return query

    def get_workitems_from_group(
            self,
            project_group_id: str,
            release: str | None = None,
            additional_query: str | None = ""
    ) -> list[Project]:
        """
        Get a list of workitems (requirement and safety decisions) from the given Group
        :param additional_query: [Optional] A string representing an additional query
        :param project_group_id: A string representing the project group id
        :param release:  [Optional] A string representing the release
        :return: A list of project objects
        """
        if not isinstance(project_group_id, str):
            raise TypeError("The group_name parameter must be a Project Group object")

        self.now = datetime.now().strftime("%A %d %B %Y - %H:%M:%S")
        query = self.define_query(release, additional_query)
        project_group = self.client.getProjectGroup(project_group_id)

        try:
            print("Getting workitems from groups... might take a long time")
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
            release: str | None = None,
            additional_query: str | None = ""
    ) -> list[Workitem]:
        """
        Get workitems with a query from a project
        :param additional_query: [Optional] A string representing an additional query
        :param project_id: A string representing the project id
        :param release: [Optional] A string representing the release
        :return: A list of workitems
        """
        if not isinstance(project_id, str):
            raise TypeError("The project parameter must be a Polarion project object")

        self.now = datetime.now().strftime("%A %d %B %Y - %H:%M:%S")
        query = self.define_query(release, additional_query)
        project = self.client.getProject(project_id)

        try:
            print("Getting workitems... might take a while for big queries.")
            workitem_list = project.searchWorkitemFullItem(query=query,
                                                           field_list=['id', 'description', 'project',
                                                                       'linkedWorkItems', 'customFields.ibaFullPuid'])
            return workitem_list
        except Exception as e:
            raise Exception(f"Error while getting the workitems: {e}")

    def workitem_to_embed(
            self,
            full_workitems_list: list[Workitem],
            release: str | None = None
    ) -> list[Workitem]:
        """
        Get linked workitems from every workitems in the list and add them to the parent description.
        Create a list of workitems and their metadatas ready to embed
        :param full_workitems_list: A list of workitems
        :param release: [Optional] A string representing the release
        :return: A tuple of workitems with their metadatas
        """
        if not isinstance(full_workitems_list, list):
            raise TypeError("The full_workitems_list parameter must be a list")
        if not full_workitems_list:
            raise ValueError("The full_workitems_list list must not be empty")
        if not isinstance(release, str) and release is not None:
            raise TypeError("The release parameter must be a string")

        merged_workitems = []

        print("Getting children... might take a while accordingly")
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
                    print(f"\nWorkitem {workitem.id} not retrieved from Polarion")
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
            db_path: Path | str
    ):
        if not isinstance(data, list):
            raise TypeError("The data must be a list")
        if not isinstance(db_path, str):
            raise TypeError("The db_path must be a string")
        if not data:
            raise Exception("This error comes because the function received a empty list. This means that there are no "
                            "workitems with the IBAApplicabilityConfiguration field set to the release you provided in "
                            "that particular project or project group.")

        if os.path.exists(db_path):
            deleted = False
            while not deleted:
                user_input = input(f"The path '{db_path}' already exists. Press [Enter] to delete it and continue.")
                if user_input == "":
                    deleted = True
                    shutil.rmtree(db_path)
                else:
                    print("Exiting...")
                    sys.exit(0)

        absolute_db_path = Path(db_path).absolute()
        embeddings = HuggingFaceHubEmbeddings(model=self.api_url, model_kwargs={"truncate": True})

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

        faiss = FAISS.from_texts(texts=texts[0], metadatas=metadatas[0], embedding=embeddings)
        for i, text in enumerate(texts[1:], start=1):
            faiss.add_texts(texts=text, metadatas=metadatas[i])

        faiss.save_local(str(absolute_db_path))
        fh.db_to_update_file(db_path, self.now)

    def caller(
            self,
            choice_id: str,
            type_chosen: str,
            release: str | None = None,
    ) -> None:
        print("Checking .cache")
        if os.path.exists(f'.cache/cache_{choice_id}__{release}%{type_chosen}.pkl'):
            with open(f'.cache/cache_{choice_id}__{release}%{type_chosen}.pkl', 'rb') as f:
                formatted_list_workitems = pickle.load(f)
                self.db_folder_name += f'{choice_id}__{release}%{type_chosen}'
                en.printarrow(".cache loaded")
        else:
            en.printarrow(".cache empty")
            if type_chosen == "group":
                workitems = self.get_workitems_from_group(choice_id, release)
                en.printarrow("Done !", start="\n")
            elif type_chosen == "project":
                workitems = self.get_workitems_from_project(choice_id, release)
                en.printarrow("Done !", start="\n")
            else:
                raise ValueError("The choice parameter must be either 'project' or 'group'")

            merged_workitems = self.workitem_to_embed(workitems, release)
            formatted_list_workitems = self.format_workitem(merged_workitems)
            en.printarrow("Done !", start="\n")
            with open(f'.cache/cache_{choice_id}__{release}%{type_chosen}.pkl', 'wb') as f:
                pickle.dump(formatted_list_workitems, f)
                en.printarrow("Cache saved")
                self.db_folder_name += f'{choice_id}__{release}%{type_chosen}'

        if release:
            self.create_vector_db(formatted_list_workitems, self.db_folder_name)
        else:
            self.create_vector_db(formatted_list_workitems, self.db_folder_name)

        if os.path.exists(f'.cache/cache_{choice_id}__{release}%{type_chosen}.pkl'):
            os.remove(f'.cache/cache_{choice_id}__{release}%{type_chosen}.pkl')
        print("Finished !")


