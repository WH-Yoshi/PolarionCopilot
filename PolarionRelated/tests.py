import html
import os
import pickle
import re

from dotenv import load_dotenv
from polarion.polarion import Polarion
from polarion.project import Project
from polarion.project_groups import ProjectGroup
from polarion.workitem import Workitem
from zeep.exceptions import Fault

base_url = 'https://polarion.goiba.net/polarion'
load_dotenv()


def get_polarion_instance() -> Polarion:
    """
    Get a Polarion instance with the user's credentials or a token
    :return: A Polarion instance
    """
    print("Getting Polarion instance...")
    try:
        client = Polarion(base_url, 'aixyf', password=None, token=os.environ.get("polarion_token"))
    except Exception as e:
        raise Exception(f"Error while getting the Polarion instance: {e}")
    return client


def get_project(polarion: Polarion, project_id) -> Project:
    """
    Get a project from Polarion
    :param polarion: The Polarion instance
    :param project_id: The id of the project
    :return: The project
    """
    print(f"Getting project {project_id}...")
    try:
        project = polarion.getProject(project_id)
    except Exception as e:
        raise Exception(f"Error while getting the project: {e}")
    return project


def get_one_workitem(polarion: Polarion, project, workitem_id) -> Workitem:
    """
    Get a workitem from Polarion
    :param polarion: The Polarion instance
    :param project: The project of the workitem
    :param workitem_id: The id of the workitem
    :return: The workitem
    """
    print(f"Getting workitem {workitem_id}...")
    service = polarion.getService('Tracker')
    try:
        workitem = service.getWorkItemByIdsWithFields(
            project.id, workitem_id,
            ['id', 'description', 'project', 'linkedWorkItems', 'customFields.ibaFullPuid',])

        workitem_obj = Workitem(polarion, project, workitem.id, field_list=['id', 'description', 'project', 'linkedWorkItems', 'customFields.ibaFullPuid',])
        linked_workitems_description = []
        if workitem_obj.description is not None:
            for w in workitem_obj.getLinkedItemWithFields(['id', 'description', 'customFields.ibaFullPuid', 'type']):
                if w.type['id'] == "requirement" or w.type['id'] == "safetydecision":
                    for field in w.customFields['Custom']:
                        if field['value'] == "(cont'd)":
                            linked_workitems_description.append(w.description.content)
    except Fault as e:
        if 'com.polarion.alm.ws.WebserviceException' in str(e):
            raise Exception("One of the key passed in the field_list is not valid, "
                            "to know the available keys you can either: "
                            "\n- use the method getAllowedCustomKeys() on a Workitem object"
                            "\n- use the method getCustomFieldKeys(workitem SubterraURI) on the service object")
    except Exception as e:
        raise Exception(e)
    return workitem_obj


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


# if __name__ == '__main__':
#     polarion = get_polarion_instance()
#     name = 'Therapy_Center_Spec'
#     # # name = 'L2_System_Spec'
#     project_group = ProjectGroup(polarion, name)
#     #
#     workitem = project_group.get_workitem_with_fields(query='id:PMS-1307')
#     print('\n' + workitem[0].description.content)
#     print('\n')
#     print(str_cleaner(workitem[0].description.content))
#     # project = get_project(polarion, 'PT_L1_Operating_Instructions')
#     # workitem = get_one_workitem(polarion, project, 'OP-1201')
#     # print(workitem.__dict__)
#     # check_descriptions_in_pickle_file('.cache/cache_Therapy_Center_Spec__P235-R12.4.0.pkl')
#     # verif = ProjectGroup(get_polarion_instance(), name)
#     # if verif.name == name:
#     #     print(verif)
#     #     print("Project group exists")
import gradio as gr


def predict(message, history, choice=""):
    return "Hello " + choice

if __name__ == '__main__':
    # doesn't work
    examples = [
        "Hi",
        "Good morning",
    ]
    # works
    # examples = [
    #     ["Hi"],
    #     ["Good morning"],
    # ]
    chatbot = gr.Chatbot()
    textbox = gr.Textbox()

    with gr.Blocks() as demo:

        gr.ChatInterface(
            fn=predict,
            chatbot=chatbot,
            textbox=textbox,
            examples=examples,
        )

    demo.launch()
