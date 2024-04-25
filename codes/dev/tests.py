from pathlib import Path, PureWindowsPath
from pprint import pprint

from openai import OpenAI


def vllm_openai_exemple():
    # Set OpenAI's API key and API base to use vLLM's API server.
    openai_api_key = "EMPTY"
    openai_api_base = "http://localhost:22028/v1"

    client = OpenAI(
        api_key=openai_api_key,
        base_url=openai_api_base,
    )

    chat_response = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        messages=[
            {"role": "user", "content": "Tell me a joke."},
        ]
    )
    print("Chat response:", chat_response)


def modify_file(file_pth, line_number, new_line):
    with open(file_pth, 'r') as file:
        lines = file.readlines()

    if 0 < line_number <= len(lines):
        lines[line_number - 1] = new_line + '\n'

        with open(file_pth, 'w') as file:
            file.writelines(lines)
        print("File updated successfully.")
    else:
        print("Invalid line number.")


if __name__ == '__main__':
    # vllm_openai_exemple()
    print(str(Path(__file__).parent.parent))
    file_path = PureWindowsPath(__file__).parent.parent.parent / 'codes' / 'site-packages-changes' / 'wrapt_certifi.py'
    cert_path = (Path(__file__).parent.parent.parent / 'certifi' / 'cacert.pem').as_posix().replace(r'/', r'\\')
    line_number_to_modify = 9
    new_line_content = f'    return "{cert_path}"'
    lines = modify_file(file_path, line_number_to_modify, new_line_content)

