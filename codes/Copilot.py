"""
This script is used to create a gradio interface for the VLLM API. The API is used to interact with the VLLM model
"""
import os
import pickle
from pathlib import Path
from typing import List, Tuple, Optional

import gradio as gr
import openai
from dotenv import load_dotenv
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.documents import Document
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
from openai import OpenAI
from termcolor import colored

import file_helper as fh

load_dotenv()

api_key = "EMPTY"
client = OpenAI(api_key=api_key, base_url=os.environ.get("openai_api"))
embeddings = HuggingFaceEndpointEmbeddings(model=os.environ.get("embedding_api"))
files = os.listdir(fh.get_faiss_db_path())
icon = Path(__file__).parent / "public" / "images" / "favicon.ico"
iba_logo = Path(__file__).parent / "public" / "images" / "iba.png"
glossary_path = Path(__file__).parent / "public" / "glossary" / "glossary.csv"
print()
print(colored("Copilot", "light_cyan"))
print("[CTRL] + Click on the link to open the interface in your browser.")


def faiss_db_loader(db_id: str) -> FAISS:
    """
    This function is used to load the faiss database
    :param db_id: The id of the database
    :return: The faiss database
    """
    db_path = str(fh.get_faiss_db_path() / db_id)
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
    try:
        documents = db.similarity_search_with_score(query=message, k=k, score_threshold=1)
    except Exception as e:
        raise Exception(f"Error while searching for documents: {e}")
    return documents


def history_format(history):
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
        documents: Optional[List[Tuple[Document, float]]],
        history_openai_format: list,
        message: str,
        prebuilt_context: str
) -> Tuple[list, str]:
    """
    This function is used to append the context to the history.

    @param documents: The documents found in the database
    @param history_openai_format: The history in the OpenAI format
    @param message: The user input
    @param prebuilt_context: The use case
    @return: The updated history and the system prompt in a tuple
    """
    glossary = fh.get_glossary(str(glossary_path))

    if documents is not None and not isinstance(documents, list):
        raise Exception("The documents should be a list")
    reference_prompt = ""
    if documents:
        for doc in documents:
            doc_content = doc[0].page_content
            doc_reference = doc[0].metadata["ibafullpuid"]
            doc_url = doc[0].metadata["url"]

            reference_prompt += (
                f" - {doc_content} {doc_reference} -- <b><a href='{doc_url}'>LINK</a></b>\n"
            )

        history_openai_format.append({
            "role":
                "user",
            "content":
                "You are a helpful assistant. The following CONTEXT might be useful for the question. "
                "Consider it as knowledge and not provided information, use it to answer the question. "
                "DO NOT display the links of the CONTEXT. "
                "Only if the CONTEXT has nothing to do with the QUESTION or is EMPTY, provide the "
                "answer to the question without using the CONTEXT. "
                f"ABBREVIATION: {glossary}"
                "Your might get a specific context, I want you to use it to adapt to the user. "
                "### Context :"
                f"{reference_prompt} "
                "### Question :"
                f"{message}"
        })
    else:
        if prebuilt_context != "no_use_case":
            if prebuilt_context == "test_case":
                prebuilt_context = """
                Your main goal is to write or modify test steps from a given requirement. 
                Here are some examples of the provided task.
                --- Start of example 
                Requirements to test 
                • The system shall prevent motion if pit is not secured 
                • The system shall prevent motion if motion enable button is not pressed 
                Test steps for the requirements 
                <table>
                <thead><tr><th>Step Number</th><th>Step Description</th><th>Expected Result</th></tr></thead>
                    <tbody>
                        <tr><td>1</td><td>Unsecure the pit</td><td>Motion enable = OFF</td></tr><tr><td>2</td>
                        <td>Press motion enable button</td><td>Motion enable = OFF</td></tr><tr><td>3</td>
                        <td>Stop pressing motion enable button</td><td>Motion enable = OFF</td></tr>
                        <tr><td>4</td><td>Secure the pit</td><td>Motion enable = OFF</td></tr>
                        <tr><td>5</td><td>Press motion enable button</td><td>Motion enable = ON</td></tr>
                        <tr><td>6</td><td>Stop pressing motion enable button</td><td>Motion enable = OFF</td></tr>
                    </tbody>
                </table>
                --- End of example 
                If the user asks you to write test steps from a requirement, you should provide the test steps with the same logic as the example.
                If the user asks you to modify the test steps, you should modify the test steps with the same logic as the example.
                If the users asks you to complete test steps DO NOT modify the provided test steps. DO NOT change the test steps order or provide MINIMUM 2 ways to do it.
                ALWAYS present your response in a table format with clear headers and neatly organized rows and columns. 
                Do not replicate the user's structured input directly, even if it looks like a table or structured text. 
                Instead, reformat all information into a new table with appropriate adjustments as needed.
                Ensure that:
                - Each step is listed clearly with step numbers.
                - The step description is concise and formatted uniformly.
                - Expected results are accurately represented in their own column.
                - Headers should be explicitly stated and aligned correctly. 
                Even if the user provides a structured answer, do not replicate it directly. Instead, format your response in a structured table with clear headers and neatly organized rows and columns.
                """
        history_openai_format.append({
            "role":
                "user",
            "content":
                "You are a helpful and appreciated assistant, answer the question naturally."
                "Your primary goal is to provide accurate and natural responses to the user's questions."
                "If a question is ambiguous, ask clarifying questions to better understand the user's needs."
                "*DO NOT make up information*; if you don't know the answer, it's okay to say so in a polite way."
                "When applicable, provide **examples** or **references** to support your answer."
                "### Specific context :"
                f"{prebuilt_context}"
                "### Question : "
                f"{message}"
        })
    return history_openai_format, reference_prompt


def predict(
        message: str,
        history,
        db_id: str,
        k: int,
        user_summary: str
) -> str:
    """
    This function is used to predict the response of the VLLM model.

    @param message: The user inputs
    @param history: The history of the conversation
    @param db_id: The chosen database
    @param k: The number of documents to retrieve
    @param user_summary: The information about the user
    @return: The response of the VLLM model
    """
    if message:
        if db_id == "no_database":
            documents = None
        else:
            db = faiss_db_loader(db_id)
            documents = document_search(message, db, k)


        history_openai_format = history_format(history)
        messages, references = append_context_to_history(documents, history_openai_format, message, user_summary)

        try:
            response = client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.3",
                messages=messages,
                temperature=0.5,
                stream=True,
            )
        except openai.AuthenticationError:
            raise Exception("You didn't create and/or fill your .env file...")
        except Exception as e:
            raise Exception(e)

        partial_message = ""
        try:
            if documents:
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        partial_message = partial_message + chunk.choices[0].delta.content
                        yield partial_message
                yield partial_message + "\n\n<i><b>References:</b></i>\n" + references
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
    else:
        gr.Warning("Please enter a message.")
        yield "Oops! I'd love to help, but I need information to assist you better."

def update_visibility(selected_dropdown: str, gradio_value: str):
    if selected_dropdown == gradio_value:
        return gr.update(visible=False)
    else:
        return gr.update(visible=True)


CSS = fh.get_css(Path(__file__).parent / "public" / "styles" / "gradio.css")

textbox = gr.Textbox(
    lines=2,
    max_lines=20,
    placeholder="Enter your message here...",
    scale=7,
    label="Message",
    max_length=2000,
)

submit_btn = gr.Button(
    elem_id="submit",
    value="Send",
)

use_case_choices = [("No use case","no_use_case"), ("Test case [generation & modification]","test_case")]

# Choices over the database
choices1 = [("No database", "no_database")]
with open(fh.get_faiss_catalog_path(), "rb") as f:
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
        title="VLLM Polarion Copilot [BETA]",
) as demo:
    with gr.Column():
        with gr.Row(equal_height=False, elem_id="row1"):
            with gr.Column(scale=3):
                header = gr.HTML(
                    elem_id="gradio_header",
                    value=f"""
                        <div id="gradio_header">
                            <img id="logo" src="file/{iba_logo}" alt="IBA Logo">
                            <h1>Welcome to Polarion Copilot! [BETA]</h1>
                        </div>
                    """
                )
                selected_context = gr.Dropdown(
                    choices=use_case_choices,
                    value="No use case",
                    multiselect=False,
                    label="Prebuilt context",
                    info="Here are some pre made contexts to help you test the chatbot.",
                    show_label=True,
                    interactive=True,
                    elem_id="dropdown_context",
                    scale=3,
                    allow_custom_value=True
                )
                documentation = gr.HTML(
                    elem_id="left_container",
                    value="""
                        Copilot user documentation.
                        <p>Feel free to download the user documentation.</p>
                        <a href="https://gitlab.sw.goiba.net/req-test-tools/polarion-copilot/copilot-proto/-/raw/move-to-server/Doc-PolarionCopilot.pdf?ref_type=heads&inline=false">User Documentation</a>
                    """
                )
                issues = gr.HTML(
                    elem_id="left_container",
                    value="""
                        Found a bug or an issue? Let us know!
                        <p>Feel free to report any issue or bug you find in the chatbot.</p>
                        <a href="https://gitlab.sw.goiba.net/req-test-tools/polarion-copilot/copilot-proto/-/issues">Report</a>
                    """
                )
            with gr.Column(scale=8):
                with gr.Row(equal_height=True):
                    dropdown1 = gr.Dropdown(
                        choices=choices1,
                        value="no_database",
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
                        value=10,
                        multiselect=False,
                        label="Number of workitems",
                        info="Start with a larger value and then decrease it if the response is inconvenient.",
                        show_label=True,
                        interactive=True,
                        elem_id="dropdown_k",
                        scale=3,
                        visible=False
                    )
                gr.ChatInterface(
                    fn=predict,  # Function to call when the user sends a message (Submit)
                    textbox=textbox,  # Where the user input is
                    additional_inputs=[dropdown1, dropdown2, selected_context],
                    fill_height=True,
                    submit_btn=submit_btn
                )

    dropdown1.change(fn=update_visibility, inputs=[dropdown1, gr.State("no_database")], outputs=dropdown2)

if __name__ == '__main__':
    demo.launch(favicon_path=icon.__str__(), show_error=True, allowed_paths=["."])
