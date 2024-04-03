import os
import pickle

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


if __name__ == '__main__':
    polarion = get_polarion_instance()
    # name = 'Therapy_Center_Spec'
    # # name = 'L2_System_Spec'
    # project_group = ProjectGroup(polarion, name)
    #
    # # workitem = project_group.get_workitem_fullitem(query='id:XCU-1126')
    # project = get_project(polarion, 'PT_L1_Operating_Instructions')
    # workitem = get_one_workitem(polarion, project, 'OP-1201')
    # print(workitem.__dict__)
    # check_descriptions_in_pickle_file('.cache/cache_Therapy_Center_Spec__P235-R12.4.0.pkl')
    # verif = ProjectGroup(get_polarion_instance(), name)
    # if verif.name == name:
    #     print(verif)
    #     print("Project group exists")
