"""
Object to save Workitems from given PROJECTS in a corresponding database.
"""
import html
import os
import pickle
import re
import sys
import uuid
from datetime import datetime
from typing import Any, List, Optional, Union, Tuple

from dotenv import load_dotenv
from langchain_community.vectorstores.faiss import FAISS
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
from polarion.polarion import Polarion
from polarion.workitem import Workitem
from termcolor import colored

import file_helper as fh
import risk_analysis_helper as ra
from enhancer import printarrow, Loader

load_dotenv()


def modify_value_in_list_of_dicts(list_of_dicts, value_to_find, new_value):
    for dictionary in list_of_dicts:
        if dictionary['key'] == value_to_find:
            try:
                dictionary['value']['content'] = new_value
                break
            except TypeError:
                new_dict = {'key': value_to_find, 'value': new_value}
                list_of_dicts.append(new_dict)


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
    # Make sure a white space is after a dot
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


class WorkitemSaver:
    """
    This class is used as a Workitem Saver.
    It saves work items from a given project or project group in a database.
    After instantiating the class, you can call the caller method to start the process like so :
    WorkitemSaver.caller()
    :param location: A string representing the project or project group polarion ID
    :param location_type: A string representing the type between 'project' or 'group'
    :param workitem_type: A list of strings representing the workitem types
    :param release: [Optional] A string representing the release for filtering purposes
    :param last_update_date: [Optional] A string representing the time of the last update
    :param db_id: [Optional] A string representing the database id
    """
    db_folder_name = fh.get_faiss_db_path()

    def __init__(
            self,
            location: str,
            location_type: str,
            workitem_type: List[str],
            release: Optional[str] = "",
            last_update_date: Optional[datetime] = None,
            db_id: Optional[str] = None
    ):
        self.location_id = location
        self.location_type = location_type
        self.release = release
        self.polarion_url = os.environ.get("polarion_url")
        self.embedding_api = os.environ.get("embedding_api")
        self.update_file_path = fh.get_faiss_catalog_path()
        self.now = datetime.now()
        self.client = self.get_polarion_instance()
        self.date = last_update_date
        self.workitem_type = workitem_type
        self.db_id = db_id

    def get_polarion_instance(self) -> Polarion:
        """
        Get a Polarion instance with the user's credentials or a token
        :return: A Polarion instance
        """
        loader = Loader("Connecting to polarion ", colored("Connected.","green"), timeout=0.05).start()
        try:
            client = Polarion(
                self.polarion_url,
                user=os.environ.get("polarion_user"),
                password=os.environ.get("polarion_password") if os.environ.get("polarion_password") else None,
                token=os.environ.get("polarion_token") if os.environ.get("polarion_token") else None,
                verify_certificate=str(fh.path_to_certs())
            )
        except Exception as e:
            loader.stop(print_exit=False)
            if "Could not find a suitable TLS CA certificate bundle" in str(e):
                raise Exception(f"Unable to get the Polarion instance. Could not find a suitable TLS CA certificate bundle.\n{colored('Please make sure that the certificates are in the certifi folder.', 'yellow')}")
            if "Could not log in to Polarion for user" in str(e):
                raise Exception(f"Unable to get the Polarion instance.\nPossible error: {colored('The user credentials might be wrong', 'yellow')}\nReal error: {colored(e, 'red')}\n")
            raise Exception(f"Unable to get the Polarion instance.\nPossible error: {colored('The .env file might not be created and/or filled correctly.', 'yellow')}\nReal error: {colored(e, 'red')}\n")
        loader.stop()
        return client

    def check_release(self, release: str) -> Workitem:
        """
        Check if the release exists in the PTS_Config project
        :param release: A string representing the ID of the release
        :return: Should return a unique workitem associated to the release
        """
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
            elif match[0] is None:
                raise ValueError(f"Release '{release}' has a None value.")
            else:
                print(f'Found release "{colored(release, "green")}" with id: {match[0].id}.')
                return match[0]
        except Exception as e:
            raise Exception(f"Error while searching for the release: {e}")

    def define_query(self, additional_query: Optional[str] = "") -> str:
        """
        Define the query to get workitems from a project or a project group
        :param additional_query: [Optional] A string representing an additional query
        :return: A string representing the query
        """
        if not isinstance(additional_query, str) and additional_query is not None:
            raise TypeError("The additional_query parameter must be a string")

        if self.release and self.release != "None":
            release_id = self.check_release(self.release)
            query = f"""type:({' '.join(self.workitem_type)}) AND NOT ibaFullPuid:("(cont'd)") AND ibaApplicableConfiguration.KEY:("{release_id.id}") AND status:approved"""
        else:
            query = f"""type:({' '.join(self.workitem_type)}) AND NOT ibaFullPuid:("(cont'd)") AND status:approved"""
        query += f" AND {additional_query}" if additional_query else ""
        return query

    def get_workitems_from_group(
            self,
            project_group_id: str,
            additional_query: Optional[str] = ""
    ) -> List[Workitem]:
        """
        Get a list of workitems (requirement and safety decisions) from the given Group
        :param additional_query: [Optional] A string representing an additional query
        :param project_group_id: A string representing the project group id
        :return: A list of workitem objects
        """
        query = self.define_query(additional_query)
        project_group = self.client.getProjectGroup(project_group_id)

        try:
            print(f"Getting {colored('workitems', 'green')} from groups... might take a long time")
            workitems = project_group.getWorkitemsWithFields(
                query=query, field_list=["customFields.ibaFullPuid", "customFields.ibaHazardousSituation",
                                         "customFields.ibaInitiatingEvent", "customFields.ibaHarm",
                                         "customFields.ibaRAFailureMode", "customFields.ibaRACause",
                                         "customFields.ibaRAEffects", "description", "id",
                                         "linkedWorkItemsDerived", "project", "status", "type"]
            )
            return workitems
        except Exception as e:
            raise Exception(f"Error while getting the workitems:\n\n{e}")

    def get_workitems_from_project(
            self,
            project_id: str,
            additional_query: Optional[str] = ""
    ) -> List[Workitem]:
        """
        Get workitems with a query from a project
        :param additional_query: [Optional] A string representing an additional query
        :param project_id: A string representing the project id
        :return: A list of workitems
        """
        if not isinstance(project_id, str):
            raise TypeError("The project parameter must be a Polarion project object")

        query = self.define_query(additional_query)
        project = self.client.getProject(project_id)

        try:
            print(f"Getting {colored('workitems', 'green')} from project... might take a while for big queries.")
            workitem_list = project.searchWorkitemFullItem(
                query=query, field_list=["customFields.ibaFullPuid", "customFields.ibaHazardousSituation",
                                         "customFields.ibaInitiatingEvent", "customFields.ibaHarm",
                                         "customFields.ibaRAFailureMode", "customFields.ibaRACause",
                                         "customFields.ibaRAEffects", "description", "id",
                                         "linkedWorkItemsDerived", "project", "status", "type"]
            )
            return workitem_list
        except Exception as e:
            raise Exception(f"Error while getting the workitems:\n\n{e}")

    def merge_workitem_children_descriptions(
            self,
            full_workitems_list: List[Workitem],
    ) -> List[Workitem]:
        """
        Get the children of a workitem and merge their description with the parent workitem
        :param full_workitems_list: A list of workitems
        :return: A list of parent workitems with the children's description merged
        """
        if not isinstance(full_workitems_list, list):
            raise TypeError("The full_workitems_list parameter must be a list")
        if not full_workitems_list:
            raise ValueError(f"The full_workitems_list list must not be empty, this means that there is no workitem "
                             f"of type {', '.join(self.workitem_type)} in the project or project group.")

        print(f"\nGetting {colored('children', 'green')}... might take a while accordingly")
        merged_workitems = []
        for i, workitem in enumerate(full_workitems_list):
            sent = (' \u21AA  Loading workitems children: ' + str(i + 1) + ' of ' + str(len(full_workitems_list)))
            sys.stdout.write('\r' + sent)
            if workitem.type['id'] in ["safetydecision", "requirement"]:  # We append the child description to the parent one
                try:
                    if workitem.description is not None and workitem.description != "" and workitem.linkedWorkItemsDerived is not None:
                        for w_child in workitem.linkedWorkItemsDerived['LinkedWorkItem']:
                            if w_child.role['id'] == "parent":
                                link_w = Workitem(self.client, workitem.project, uri=w_child.workItemURI,
                                                  field_list=["id", "description", "customFields.ibaFullPuid"])
                                if "cont'd" in ra.get_iba_full_puid_value(link_w.customFields):
                                    workitem.description.content += (", " + link_w.description.content)
                            else:
                                continue
                        merged_workitems.append(workitem)
                except AttributeError as e:
                    print()
                    raise AttributeError(e)
                except Exception as e:
                    if "Workitem not retrieved from Polarion" in str(e):
                        print(f"\nWorkitem {colored(workitem.id, 'red')} not retrieved from Polarion")
                    else:
                        print()
                        raise Exception(e)
            elif workitem.type['id'] == "hazard":  # We separate children and parents
                try:
                    if workitem.linkedWorkItemsDerived is not None:
                        parent_hazardous_situation = ra.get_hazardous_situation_value(workitem.customFields)
                        parent_initiating_event = ra.get_initiating_event_value(workitem.customFields)
                        parent_harm = ra.get_harm_value(workitem.customFields)
                        for w_child in workitem.linkedWorkItemsDerived['LinkedWorkItem']:
                            if w_child.role['id'] == "parent":
                                link_w = Workitem(self.client, workitem.project, uri=w_child.workItemURI,
                                                  field_list=["id", "project", "type", "customFields.ibaFullPuid",
                                                              "customFields.ibaHazardousSituation",
                                                              "customFields.ibaInitiatingEvent",
                                                              "customFields.ibaHarm"])
                                if "cont'd" in ra.get_iba_full_puid_value(link_w.customFields):
                                    if ra.get_hazardous_situation_value(link_w.customFields) != parent_hazardous_situation:
                                        modify_value_in_list_of_dicts(link_w.customFields['Custom'],
                                                                      'ibaHazardousSituation',
                                                                      parent_hazardous_situation)
                                    if ra.get_initiating_event_value(link_w.customFields) is None:
                                        modify_value_in_list_of_dicts(link_w.customFields['Custom'],
                                                                      'ibaHazardousSituation',
                                                                      parent_initiating_event)
                                    if ra.get_harm_value(link_w.customFields) is None:
                                        modify_value_in_list_of_dicts(link_w.customFields['Custom'],
                                                                      'ibaHazardousSituation',
                                                                      parent_harm)
                                    merged_workitems.append(link_w)
                            else:
                                continue
                except AttributeError as e:
                    print()
                    raise AttributeError(e)
                except Exception as e:
                    if "Workitem not retrieved from Polarion" in str(e):
                        print(f"\nWorkitem {colored(workitem.id, 'red')} not retrieved from Polarion")
                    else:
                        print()
                        raise Exception(e)
            elif workitem.type['id'] == "failuremode":  # We separate children and parents
                try:
                    if workitem.linkedWorkItemsDerived is not None:
                        parent_failure_mode = ra.get_ra_failure_mode_value(workitem.customFields)
                        parent_cause = ra.get_ra_cause_value(workitem.customFields)
                        parent_effects = ra.get_ra_effects_value(workitem.customFields)
                        for w_child in workitem.linkedWorkItemsDerived['LinkedWorkItem']:
                            if w_child.role['id'] == "parent":
                                link_w = Workitem(self.client, workitem.project, uri=w_child.workItemURI,
                                                  field_list=["id", "project.id", "type", "customFields.ibaFullPuid",
                                                              "customFields.ibaRAFailureMode",
                                                              "customFields.ibaRACause", "customFields.ibaRAEffects"])
                                if "cont'd" in ra.get_iba_full_puid_value(link_w.customFields):
                                    if ra.get_ra_failure_mode_value(link_w.customFields) != parent_failure_mode:
                                        modify_value_in_list_of_dicts(link_w.customFields['Custom'], 'ibaRAFailureMode',
                                                                      parent_failure_mode)
                                    if ra.get_ra_cause_value(link_w.customFields) is None:
                                        modify_value_in_list_of_dicts(link_w.customFields['Custom'], 'ibaRACause',
                                                                      parent_cause)
                                    if ra.get_ra_effects_value(link_w.customFields) is None:
                                        modify_value_in_list_of_dicts(link_w.customFields['Custom'], 'ibaRAEffects',
                                                                      parent_effects)
                                    merged_workitems.append(link_w)
                            else:
                                continue
                except AttributeError as e:
                    print()
                    raise AttributeError(e)
                except Exception as e:
                    if "Workitem not retrieved from Polarion" in str(e):
                        print(f"\nWorkitem {colored(workitem.id, 'red')} not retrieved from Polarion")
                    else:
                        print()
                        raise Exception(e)
        print()
        return merged_workitems

    def format_workitem(
            self,
            merged_workitems: List[Workitem]
    ) -> List[Tuple[str, Tuple[Any, Union[str, Any]]]]:
        workitems_to_embed = []
        for workitem in merged_workitems:
            if workitem.type['id'] in ["safetydecision", "requirement"]:
                try:
                    workitems_to_embed.extend(
                        [
                            (str_cleaner(workitem.description.content),
                             (item['value'],
                              self.polarion_url + f'/#/project/{workitem.project.id}/workitem?id=' + workitem.id))
                            for item in workitem.customFields.Custom
                            if item['key'] == 'ibaFullPuid'
                        ]
                    )
                except Exception as e:
                    print(f"An error occurred while processing workitem {workitem.id}: {e}")
            elif workitem.type['id'] == "hazard":
                try:
                    for item in workitem.customFields['Custom']:
                        if item['key'] == 'ibaFullPuid':
                            ibaHS = ("[Risk analysis] Hazardous situation: " +
                                     str(ra.get_hazardous_situation_value(workitem.customFields)))
                            ibaIE = ("Initiating event: " +
                                     str(ra.get_initiating_event_value(workitem.customFields)))
                            ibaHarm = "Harm :" + str(ra.get_harm_value(workitem.customFields))
                            description = str_cleaner(ibaHS + ". " + ibaIE + ". " + ibaHarm)
                            puid = item['value']
                            url = self.polarion_url + f'/#/project/{workitem.project.id}/workitem?id=' + workitem.id
                            workitems_to_embed.append((description, (puid, url)))
                except StopIteration:
                    print(f"Skipping workitem {workitem.id} due to missing required keys.")
                except Exception as e:
                    raise Exception(f"An error occurred while processing workitem {workitem.id}: {e}")
            elif workitem.type['id'] == "failuremode":
                try:
                    for item in workitem.customFields.Custom:
                        if item['key'] == 'ibaFullPuid':
                            ibaFM = ("[Risk analysis] Failure mode: " +
                                     str(ra.get_ra_failure_mode_value(workitem.customFields)))
                            ibaC = "Cause: " + str(ra.get_ra_cause_value(workitem.customFields))
                            ibaE = "Effects: " + str(ra.get_ra_effects_value(workitem.customFields))
                            description = str_cleaner(ibaFM + ". " + ibaC + ". " + ibaE)
                            puid = item['value']
                            url = self.polarion_url + f'/#/project/{workitem.project.id}/workitem?id=' + workitem.id
                            workitems_to_embed.append((description, (puid, url)))
                except StopIteration:
                    print(f"Skipping workitem {workitem.id} due to missing required keys.")
                except Exception as e:
                    raise Exception(f"An error occurred while processing workitem {workitem.id}: {e}")
        return workitems_to_embed

    def create_vector_db(self, data: List[Tuple[Any, Tuple[Any, Union[str, Any]]]]):
        """
        Create a vector database from a list of workitems
        :param data: A list of tuples containing the workitem description and the workitem references
        """

        if not data:
            raise Exception("This error comes because the function received a empty list. This means that there are no "
                            "workitems with the IBAApplicabilityConfiguration field set to the release you provided in "
                            "that particular project or project group.")

        embeddings = HuggingFaceEndpointEmbeddings(model=self.embedding_api, model_kwargs={"truncate": True})

        descriptions = []
        metadatas = []
        for description, reference in data:
            if description != "":
                chunks = [description[i:i + 1000] for i in range(0, len(description), 1000)]
                descriptions.extend(chunks)
                metadatas.extend([{"ibafullpuid": reference[0], "url": reference[1]}] * len(chunks))
            else:
                print('it does happen')

        batch_size = 32
        texts = [descriptions[i:i + batch_size] for i in range(0, len(descriptions), batch_size)]
        metadatas = [metadatas[i:i + batch_size] for i in range(0, len(metadatas), batch_size)]
        if self.db_id:
            path = str(fh.get_faiss_db_path() / self.db_id)
            faiss = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
            loader = Loader("Precessing embeddings...", "That should be it! Try those with the Copilot",
                            timeout=0.05).start()
            for i, text in enumerate(texts):
                faiss.add_texts(text, metadatas[i])
            loader.stop()
            faiss.save_local(path)
        else:
            faiss = FAISS.from_texts(texts=texts[0], metadatas=metadatas[0], embedding=embeddings)
            loader = Loader("Precessing embeddings...", "That should be it! Try those with the Copilot",
                            timeout=0.05).start()
            for i, text in enumerate(texts[1:], start=1):
                faiss.add_texts(texts=text, metadatas=metadatas[i])
            loader.stop()
            self.db_id = uuid.uuid4().hex
            faiss.save_local(str(fh.get_faiss_db_path() / self.db_id))
        fh.db_to_faiss_catalog(self.db_id, self.location_id, self.release, self.location_type, self.workitem_type, self.now)

    def caller(self) -> None:
        workitems = []
        if self.date:  # When updating a DB
            try:
                result = self.date.strftime("%Y%m%d")
                add_query = f"updated:[{result} TO 30000000] created:[{result} TO 30000000]"
            except Exception as e:
                print(
                    f"Please report this error to this github https://github.com/WH-Yoshi/PolarionCopilot/issues : {e}")
                print("This error comes from the date parameter. "
                      "Update can still happen but will take longer as it will recreate a new db.")
                input("Press Enter to continue...")
                add_query = ""
            if self.location_type == "group":
                workitems = self.get_workitems_from_group(self.location_id, add_query)
            elif self.location_type == "project":
                workitems = self.get_workitems_from_project(self.location_id, add_query)
            if not workitems:
                printarrow(colored("The database is already up to date!", 'green'))
                sys.exit(0)
            merged_workitems = self.merge_workitem_children_descriptions(workitems)
            formatted_list_workitems = self.format_workitem(merged_workitems)

            if add_query:
                self.create_vector_db(formatted_list_workitems)
            else:
                self.create_vector_db(formatted_list_workitems)

        else:  # When saving a new DB
            if self.location_type == "group":
                workitems = self.get_workitems_from_group(self.location_id)
            elif self.location_type == "project":
                workitems = self.get_workitems_from_project(self.location_id)
            merged_workitems = self.merge_workitem_children_descriptions(workitems)
            formatted_list_workitems = self.format_workitem(merged_workitems)

            uid = uuid.uuid4().hex
            try:
                with open(fh.get_cache_catalog_path(), "rb") as f:
                    infos = pickle.load(f)
                infos_to_dump = {
                    "location": self.location_id,
                    "release": self.release,
                    "type": self.location_type,
                    "workitem_type": self.workitem_type,
                    "last_update": None
                }
                infos[uid] = infos_to_dump
                with open(fh.get_cache_catalog_path(), "wb") as f:
                    pickle.dump(infos, f)

                with open(fh.get_cache_path() / f"{uid}.pkl", "wb") as f:
                    pickle.dump(formatted_list_workitems, f)
            except Exception as e:
                print(f"An error occurred while saving the cache file: {e}")

            try:
                self.create_vector_db(formatted_list_workitems)
                (fh.get_cache_path() / f"{uid}.pkl").unlink()
                fh.delete_from_cache_file(uid)
            except Exception as e:
                if "Failed to establish a new connection" and "22027" in str(e):
                    print(colored("This happens because the 22027 port is not open to communication. "
                                  "A SSH tunnel has to be opened to the distant server.\n"
                                  "Find instructions here: https://gitlab.sw.goiba.net/req-test-tools/polarion-copilot/copilot-proto#tensordock-virtual-machine", 'red'),
                          colored("\nA cache file has been created, try again after enabling the SSH tunnel.", 'yellow'))
                else:
                    raise Exception(f"Some error occurred: {e}")


if __name__ == '__main__':
    raise Exception("This module is not intended to be run directly. Run Polarion.py instead")
