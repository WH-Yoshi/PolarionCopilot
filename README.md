# PolarionCopilot

PolarionCopilot is a combination of 2 main components for Windows:
- A Python script that can be used to retrieve Polarion work items to make them understandable by a LLM.
- A LLM that can be used to ask questions about the work items

## Installation

The installation is half automated, half manual. The automated part is the installation of each library, and specific changes dones to them.
The manual part is the installation of any required software.

### Required installation

1. Python, minimum version 3.11: [Python for Windows](https://www.python.org/downloads/)
   - Make sure to check the box *"Add python.exe to PATH"* during the installation
2. Git, to clone this repository: [Git](https://git-scm.com/downloads)
   - You can click *Next* for each step.
3. **[Optional]** A good terminal to show you all this goodies going on in the scripts :)
   - You can use the new Windows Terminal for exemple: [Windows Terminal](https://www.microsoft.com/en-us/p/windows-terminal/9n0dx20hk701)

### Activate and fill your environment *(Important steps)*
Using a virtual environment is a good practice to avoid conflicts between libraries and versions. And also to keep your main Python installation clean.
#### Windows
1. Find a suitable location for the repository
   ```bash
   cd <DIRECTORY>
   ```
2. Create and activate the virtual environment
   ```bash
   py -m venv .venv
   .\.venv\Scripts\activate
   ```
   If you run into an error with execution policy, check your own execution policy with:
   ```bash
    Get-ExecutionPolicy
   ```
   remember it if you want to put it back later. Then, change it to RemoteSigned and try to activate the environment again:
   ```bash
    Set-ExecutionPolicy RemoteSigned
   ```
3. Clone the repository
   ```bash
   git clone https://github.com/WH-Yoshi/PolarionCopilot.git
   cd PolarionCopilot
   ```
4. Install the required libraries
   ```bash
   pip install -r requirements.txt
   ```
#### Linux (Not supported yet)

#### Before any further steps, you need to fill the environment variables in the .env file.
1. Fill the .env file with the following content, each value must be between quotes "":
   ```bash
   base_url=<URL> # The URL of your Polarion server (e.g. https://polarion.example.com/polarion)
   embedding_api=<URL> # The URL of your embedding API
   openai_api=<URL> # The URL of your OpenAI like API (has to finish with "/v1")
   polarion_user=<USERNAME> # The username to access the Polarion server
   polarion_token=<TOKEN> # The user token to access the Polarion server
   ```
   Replace `<URL>`, `<USERNAME>`, and `<TOKEN>` with your own values.
   .env file contains sensitive information, make sure to not share it.


### Tensordock virtual machine

1. Open [TensorDock](https://dashboard.tensordock.com/deploy)
2. Get a GPU with at least 48Gb of VRAM
3. 1GPU, 8Gb of RAM, 2CPU and 30Gb SSD
4. Select one of the available locations
5. Choose Ubuntu as operating system
6. Put a password and a machine name
7. Deploy
8. SSH into the machine :
   ```bash
   ssh -p xxxxx user@host -L 22027:localhost:8080 -L 22028:localhost:8000
   ```
9. Run the two docker images :
   ```bash
   docker run -d --gpus all -v ~/.cache/huggingface:/root/.cache/huggingface --env "HUGGING_FACE_HUB_TOKEN=<secret>" -p 8000:8000 --ipc=host vllm/vllm-openai:latest --model mistralai/Mistral-7B-Instruct-v0.2 --max-model-len 2048
   ```
   ```bash
   docker run -d --gpus all -p 8080:80 -v $PWD/data:/data --pull always ghcr.io/huggingface/text-embeddings-inference:1.2 --model-id intfloat/multilingual-e5-large-instruct
   ```
When the two images are booted up, you can proceed.

### Use the Code
1. Run the desired script
   ```bash
   python run_copilot.py
   python run_polarion.py
   ```
2. Enjoy the ride!
