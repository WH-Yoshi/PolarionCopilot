from pathlib import Path

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


if __name__ == '__main__':
    # vllm_openai_exemple()
    print(str(Path(__file__).parent.parent))
