"""
This script is used to create a gradio interface for the VLLM API. The API is used to interact with the VLLM model
"""
import os
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
files = os.listdir(fh.get_db_path())
icon = Path(__file__).parent / "public" / "images" / "favicon.ico"
print("[CTRL] + Click on the link to open the interface in your browser.")


def history_format(history: list[list[str, str]]) -> list[dict[str, str]]:
    """
    This function is used to format the history in the OpenAI format
    :param history: The history of the conversation
    :return: The history in the OpenAI format
    """
    if not isinstance(history, list):
        raise Exception("The history should be a list of tuples")

    history_openai = []
    for human, assistant in history:
        history_openai.append({"role": "user", "content": human})
        history_openai.append({"role": "assistant", "content": assistant})
    return history_openai


def faiss_loader(release: str) -> FAISS:
    """
    This function is used to load the faiss database
    :param release: The release of the database
    :return: The faiss database
    """
    if not isinstance(release, str):
        raise Exception("The release should be a string")

    db_path = str(fh.get_db_path() / release)
    try:
        db = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
    except Exception as e:
        raise Exception(f"Error while loading the database: {e}")
    return db


def document_search(message: str, db: FAISS, k: int) -> List[Tuple[Document, float]]:
    """
    This function is used to search for documents in the database
    :param message: the user input
    :param db: The faiss database
    :param k: The number of documents to return
    :return: The documents found in the database
    """
    if not isinstance(message, str):
        raise Exception("The message should be a string")

    try:
        documents = db.similarity_search_with_score(query=message, k=5, score_threshold=0.35)
    except Exception as e:
        raise Exception(f"Error while searching for documents: {e}")
    return documents


def append_context_to_history(
        documents: List[Tuple[Document, float]] | None,
        history_openai_format: list,
        message: str
) -> Tuple[list, str]:
    """
    This function is used to append the context to the history
    :param documents: The documents found in the database
    :param history_openai_format: The history in the OpenAI format
    :param message: The user input
    :return: The updated history and the system prompt in a tuple
    """
    if not isinstance(history_openai_format, list):
        raise Exception("The history should be a list of dictionaries")
    if not isinstance(message, str):
        raise Exception("The message should be a string")
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

        history_openai_format.append(
            {
                "role": "user",
                "content": f"""You are a helpful assistant. If the context provide sufficient information,
                 use it to answer the question (don't display links). 
                 if the context has nothing to do with the subject, answer naturally.
                ### Context :
                {system_prompt}
                ### Question :
                {message}"""
            }
        )
    else:
        history_openai_format.append(
            {"role": "user", "content": f"Question : {message}"}
        )
    return history_openai_format, system_prompt


def predict(
        message: str,
        history: list[list[str, str]],
        release: str,
        k: int
) -> str:
    """
    This function is used to predict the response of the VLLM model
    :param message: gr.ChatInterface input
    :param history: gr.ChatInterface input
    :param release: Two additional inputs, the release and the number of documents
    :param k: Two additional inputs, the release and the number of documents
    :return: The response of the VLLM model
    """
    if not isinstance(message, str):
        raise Exception("The message should be a string")
    if not isinstance(history, list):
        raise Exception("The history should be a list")
    if not isinstance(release, str):
        raise Exception("The release should be a string")
    if not isinstance(k, int):
        raise Exception("The number of documents should be an integer")

    if release == "General":
        documents = None
    else:
        db = faiss_loader(release)
        documents = document_search(message, db, k)

    history_openai_format = history_format(history)
    messages, system_prompt = append_context_to_history(documents, history_openai_format, message)

    response = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.2",
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
    CSS = """
    .contain { display: flex; flex-direction: column; }
    .gradio-container { height: 100vh !important; }
    #component-0 { height: 100%; }
    #chatbot { flex-grow: 1; overflow: auto; cursor: default}
    a { cursor: pointer}
    p { cursor: text}
    .border-none.svelte-vomtxz { cursor: pointer}
    """

    examples = [
        ["What is the height of the Mount Everest?", "General"],
    ]
    chatbot = gr.Chatbot(
        elem_id="chatbot",
    )
    textbox = gr.Textbox(
        lines=2,
        max_lines=5,
        placeholder="Enter your message here...",
        scale=7,
        label="Message",
    )
    choices1 = [(f"{file.split('%')[0].split('__')[0]} + {file.split('%')[0].split('__')[1] if not None else ''}", file)
                for file in files]
    choices1.insert(0, ("Unfed Chat Bot", "General"))

    choices2 = [n + 1 for n in range(10)]

    with gr.Blocks(
            fill_height=True,
            css=CSS,
            theme=gr.themes.Base(
                primary_hue="green",
                spacing_size="sm",
                radius_size="sm",
                font=[gr.themes.GoogleFont("Barlow", weights=(500, 700))]),
            title="VLLM Copilot Polarion",
    ) as demo:
        with gr.Row():
            dropdown1 = gr.Dropdown(
                choices=choices1,
                value="General",
                multiselect=False,
                label="Release",
                info="You can specify a release that will act as a filter during the feeding of the chatbot.",
                show_label=True,
                interactive=True,
                elem_id="dropdown_release",
                scale=7
            )
            dropdown2 = gr.Dropdown(
                choices=choices2,
                value=5,
                multiselect=False,
                label="Number of documents",
                info="You can specify the number of documents to retrieve.",
                show_label=True,
                interactive=True,
                elem_id="dropdown_k",
                scale=2
            )

        gr.ChatInterface(
            fn=predict,
            chatbot=chatbot,
            textbox=textbox,
            additional_inputs=[dropdown1, dropdown2],
            css=CSS,
            fill_height=True,
        )

    demo.launch(favicon_path=icon.__str__())
