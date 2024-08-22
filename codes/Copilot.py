"""
This script is used to create a gradio interface for the VLLM API. The API is used to interact with the VLLM model
"""
import os
import pickle
from pathlib import Path
from typing import List, Tuple

import gradio as gr
from dotenv import load_dotenv
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.documents import Document
from openai import OpenAI

import file_helper as fh

load_dotenv()

api_key = "EMPTY"
client = OpenAI(api_key=api_key, base_url=os.environ.get("openai_api"))
embeddings = HuggingFaceEndpointEmbeddings(model=os.environ.get("embedding_api"))
files = os.listdir(fh.get_faiss_path())
icon = Path(__file__).parent / "public" / "images" / "favicon.ico"
print("[CTRL] + Click on the link to open the interface in your browser.")


def faiss_loader(db_id: str) -> FAISS:
    """
    This function is used to load the faiss database
    :param db_id: The id of the database
    :return: The faiss database
    """
    db_path = str(fh.get_faiss_path() / db_id)
    try:
        db = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
    except Exception as e:
        raise Exception(f"Error while loading the database: {e}")
    return db


def document_search(message: str, db: FAISS, k: int, score: float) -> List[Tuple[Document, float]]:
    """
    This function is used to search for documents in the database
    :param message: the user input
    :param db: The faiss database
    :param k: The number of documents to return
    :param score: The score threshold
    :return: The documents found in the database
    """
    # instruction = "Given a user input, return the most similar documents from the database."
    # message = f"Instruct: {instruction}\nQuery: {message}"
    try:
        documents = db.similarity_search_with_score(query=message, k=k, score_threshold=score)
        print("Done")
    except Exception as e:
        raise Exception(f"Error while searching for documents: {e}")
    return documents


def history_format(history: list[list[str, str]]) -> list[dict[str, str]]:
    """
    This function is used to format the history in the OpenAI format
    :param history: The history of the conversation
    :return: The history in the OpenAI format
    """
    history_openai = []
    for human, assistant in history:
        history_openai.append({"role": "user", "content": human})
        history_openai.append({"role": "assistant", "content": assistant})
    return history_openai


def append_context_to_history(
        documents: List[Tuple[Document, float]] | None,
        history_openai_format: list,
        message: str,
        user_summary: str
) -> Tuple[list, str]:
    """
    This function is used to append the context to the history
    :param documents: The documents found in the database
    :param history_openai_format: The history in the OpenAI format
    :param message: The user input
    :param user_summary: The information about the user
    :return: The updated history and the system prompt in a tuple
    """
    if documents is not None and not isinstance(documents, list):
        raise Exception("The documents should be a list")
    system_prompt = ""
    if documents:
        for doc in documents:
            doc_content = doc[0].page_content
            doc_reference = doc[0].metadata["ibafullpuid"]
            doc_url = doc[0].metadata["url"]

            system_prompt += (
                f"{doc_content} {doc_reference} -- <b><a href='{doc_url}'>LINK</a></b>\n"
            )

        history_openai_format.append({
            "role":
                "user",
            "content":
                "You are a helpful assistant. The following CONTEXT might be useful for the question."
                "Consider it as knowledge and not provided information, use it to answer the question."
                "DO NOT display the links of the CONTEXT."
                "Only if the CONTEXT has nothing to do with the QUESTION or is EMPTY, provide the "
                "answer to the question without using the CONTEXT."
                "ABBREVIATION: PTS : Proton Therapy System, PBS : Pencil Beam Scanning, DS : Double Scattering, "
                "SIS : Single Scattering, US : Uniform Scanning"
                "Your might get a brief user presentation, I want you to use it to adapt to the user."
                "### User presentation :"
                f"{user_summary}"
                "### Context :"
                f"{system_prompt}"
                "### Question :"
                f"{message}"
        })
    else:
        history_openai_format.append({
            "role":
                "user",
            "content":
                "You are a helpful and appreciated assistant, answer the question naturally."
                "You might get a brief user presentation, I want you to use it to adapt to "
                "the user."
                "### User presentation : "
                f"{user_summary}"
                "### Question : "
                f"{message}"
        })
    return history_openai_format, system_prompt


def predict(
        message: str,
        history: list[list[str, str]],
        db_id: str,
        k: int,
        score: float,
        user_summary: str
) -> str:
    """
    This function is used to predict the response of the VLLM model
    :param message: The user input
    :param history: The history of the conversation
    :param db_id: The chosen database
    :param k: The number of documents to retrieve
    :param score: The score threshold
    :param user_summary: The information about the user
    :return: The response of the VLLM model
    """
    if db_id == "General":
        documents = None
    else:
        db = faiss_loader(db_id)
        documents = document_search(message, db, k, score)

    history_openai_format = history_format(history)
    messages, system_prompt = append_context_to_history(documents, history_openai_format, message, user_summary)

    response = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=messages,
        temperature=0.5,
        stream=True,
    )

    partial_message = ""
    try:
        if documents:
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    partial_message = partial_message + chunk.choices[0].delta.content
                    yield partial_message + "\n\n<i><b>References:</b></i>\n" + system_prompt
        else:
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    partial_message = partial_message + chunk.choices[0].delta.content
                    yield partial_message
    except AttributeError:
        yield "Sorry, the response object does not have the expected structure."
    except TypeError:
        yield "Sorry, the documents object is not iterable."
    except Exception as e:
        yield f"Sorry, an unexpected error occurred: {str(e)}"


if __name__ == '__main__':
    CSS = """#row1 {flex-grow: 1; align-items: unset;}
    .form {height: fit-content;}
    footer {display: none !important;}"""

    textbox = gr.Textbox(
        lines=2,
        max_lines=20,
        placeholder="Enter your message here...",
        scale=7,
        label="Message",
    )

    # Choices over the database
    choices1 = [("No database", "General")]
    with open(fh.get_faiss_data_path(), "rb") as f:
        databases = pickle.load(f)
    for file in files:
        file = str(file)
        db_location = databases[file]["location"]
        db_release = databases[file]["release"]
        db_type = databases[file]["type"]
        db_wi_type = databases[file]["workitem_type"]
        db_wi_type = ", ".join(db_wi_type)
        choices1.append((f"{'Group' if db_type == 'group' else 'Project'}: {db_location} - {db_release} ({db_wi_type})",
                         str(file)))
    # Choices over the number of workitems to retrieve
    choices2 = [n + 1 for n in range(20)]

    # Choices over the precision of the search
    choices3 = [n / 20.0 for n in range(1, 21)]

    with gr.Blocks(
            fill_height=True,
            css=CSS,
            theme=gr.themes.Base(
                primary_hue="green",
                spacing_size="sm",
                radius_size="sm",
                font=[gr.themes.GoogleFont("Montserrat", weights=(500, 700))]),
            title="VLLM Copilot Polarion",
    ) as demo:
        with gr.Row(
                equal_height=False,
                elem_id="row1"
        ):
            yourself = gr.Textbox(
                lines=5,
                max_lines=10,
                placeholder="Tell me more about you and why you are here...",
                scale=2,
                elem_id="yourself",
            )
            with gr.Column(scale=7):
                with gr.Row(equal_height=True):
                    dropdown1 = gr.Dropdown(
                        choices=choices1,
                        value="General",
                        multiselect=False,
                        label="Feeding the chatbot",
                        info="If a database is selected, similarity search will be performed into it before the response is generated.",
                        show_label=True,
                        interactive=True,
                        elem_id="dropdown_release",
                        scale=5
                    )
                    dropdown2 = gr.Dropdown(
                        choices=choices2,
                        value=7,
                        multiselect=False,
                        label="Number of workitems",
                        info="Start with a larger value and then decrease it if the response is inconvenient.",
                        show_label=True,
                        interactive=True,
                        elem_id="dropdown_k",
                        scale=3
                    )
                    dropdown3 = gr.Dropdown(
                        choices=choices3,
                        value=0.4,
                        multiselect=False,
                        label="Precision",
                        info="Lower values increase the precision of the search by demanding a closer match.",
                        show_label=True,
                        interactive=True,
                        elem_id="dropdown_precision",
                        scale=3
                    )
                gr.ChatInterface(
                    fn=predict,
                    textbox=textbox,
                    additional_inputs=[dropdown1, dropdown2, dropdown3, yourself],
                    fill_height=True,
                )

    demo.launch(favicon_path=icon.__str__(),
                ssl_verify=False,
                ssl_keyfile="C:\\Users\\AIXYF\\Certfiles\\key.pem",
                ssl_certfile="C:\\Users\\AIXYF\\Certfiles\\cert.pem")
