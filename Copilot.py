"""
This script is used to create a gradio interface for the VLLM API. The API is used to interact with the VLLM model
"""
import os
import gradio as gr
from langchain_community.embeddings import HuggingFaceHubEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from openai import OpenAI

api_key = "EMPTY"
openai_api_base = "http://localhost:22028/v1"
client = OpenAI(api_key=api_key, base_url=openai_api_base)
embeddings = HuggingFaceHubEmbeddings(model="http://localhost:22027")
files = os.listdir("./faiss")


def history_format(history: list):
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


def faiss_loader(release):
    """
    This function is used to load the faiss database
    :param release: The release of the database
    :return: The faiss database
    """
    if not isinstance(release, str):
        raise Exception("The release should be a string")

    db_path = f"./faiss/{release}"
    try:
        db = FAISS.load_local(db_path, embeddings)
    except Exception as e:
        raise Exception(f"Error while loading the database: {e}")
    return db


def document_search(message, db):
    """
    This function is used to search for documents in the database
    :param message: the user input
    :param db: The faiss database
    :return: The documents found in the database
    """
    if not isinstance(message, str):
        raise Exception("The message should be a string")

    try:
        documents = db.similarity_search_with_score(query=message, k=5, score_threshold=0.8)
    except Exception as e:
        raise Exception(f"Error while searching for documents: {e}")
    return documents


def append_context_to_history(documents, history_openai_format, system_prompt, message):
    """
    This function is used to append the context to the history
    :param documents: The documents found in the database
    :param history_openai_format: The history in the OpenAI format
    :param system_prompt: The system prompt
    :param message: The user input
    :return: The history in the OpenAI format with the context appended
    """
    if not isinstance(history_openai_format, list):
        raise Exception("The history should be a list of dictionaries")
    if not isinstance(system_prompt, str):
        raise Exception("The system prompt should be a string")
    if not isinstance(message, str):
        raise Exception("The message should be a string")
    if not isinstance(documents, list):
        raise Exception("The documents should be a list")
    if documents:
        for doc in documents:
            doc_content = doc[0].page_content
            doc_reference = doc[0].metadata["ibapuid"]
            doc_url = doc[0].metadata["url"]

            system_prompt += (
                f"{doc_content} {doc_reference} <a href='{doc_url}'>LINK</a>\n\n"
            )

        history_openai_format.append(
            {
                "role": "user",
                "content": "Primarily, use the following pieces of information to answer the user’s question. If the "
                           "context does not provide information, you can use your knowledge:\nContext :"
                           + system_prompt
                           + "Question :"
                           + message,
            }
        )
    else:
        history_openai_format.append(
            {"role": "user", "content": "Question :" + message}
        )
    return history_openai_format


def predict(
        message: str,
        history: list,
        release: str
) -> str:
    """
    This function is used to predict the response of the VLLM model
    :param message: gr.ChatInterface input
    :param history: gr.ChatInterface input
    :param release: A release to filter the searches in the database
    :return: The response of the VLLM model
    """

    history_openai_format = history_format(history)
    system_prompt = ""

    db = faiss_loader(release)
    documents = document_search(message, db)

    response = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        messages=append_context_to_history(documents, history_openai_format, system_prompt, message),
        temperature=1,
        stream=True,
    )

    partial_message = ""
    try:
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                partial_message = partial_message + chunk.choices[0].delta.content
                yield partial_message
    except Exception:
        yield "Sorry, I am unable to provide an answer at the moment."
    finally:
        if documents:
            yield partial_message + "\n\n<i><b>References:</b></i>\n" + system_prompt


CSS = """
.contain { display: flex; flex-direction: column; }
.gradio-container { height: 100vh !important; }
#component-0 { height: 100%; }
#chatbot { flex-grow: 1; overflow: auto;}
"""

examples = [
    ["What action should the TSS take in the event of wiring failures detected on the output signal ‘ACU service "
     "mode allowed’?"],
    ["What is the height of the Mount Everest?"],
]
chatbot = gr.Chatbot(
        elem_id="chatbot",
    )
textbox = gr.Textbox(
        lines=2,
        max_lines=5,
        placeholder="Enter your message here...",
        scale=7
    )
choices = [(file, file) for file in files]
choices.insert(0, ("General", "General"))

with gr.Blocks(fill_height=True, css=CSS, theme=gr.themes.Base()) as demo:
    dropdown = gr.Dropdown(
        choices=choices,
        value="General",
        multiselect=False,
        label="Release",
        info="You can specify a release in live, to filter the searches in the database.",
        show_label=True,
        interactive=True,
        elem_id="dropdown_release"
    )

    gr.ChatInterface(
        fn=predict,
        chatbot=chatbot,
        textbox=textbox,
        additional_inputs=dropdown,
        css=CSS,
        fill_height=True
    )

demo.launch()
