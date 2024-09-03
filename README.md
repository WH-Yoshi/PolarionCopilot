# PolarionCopilot

PolarionCopilot is a combination of two main codes:
- A Polarion workitem retrieval script.
- A Copilot script to use the workitems.

## Installation

The installation is half-manual, half-automated.\
The manual part is the installation of the required software.\
The automated part is the installation of each library, and specific changes done to them.

### Required installations
#### Windows
1. Python, any version is good: [Python for Windows](https://www.python.org/downloads/)
   - Make sure to check the box *"Add python.exe to PATH"* during the installation
2. Git, if it isn't already installed, to clone this repository: [Git](https://git-scm.com/downloads)
   - You can click *Next* for each step.
3. **[Optional]** A good terminal to have a more user-friendly experience.
   - You can use the new Windows Terminal for exemple: [Windows Terminal](https://www.microsoft.com/en-us/p/windows-terminal/9n0dx20hk701)
#### Linux
1. Python, any version is good: 
   ```bash
   sudo apt-get install python3 python3-venv
   ```
2. Git, if it isn't already installed, to clone this repository: 
   ```bash
   sudo apt-get install git
   ```
### Activate and fill your environment *(Important steps)*
Using a virtual environment is a good practice to avoid conflicts between libraries and versions.\
Also to keep your main Python installation clean.
#### Windows
1. Find a suitable location for the repository
   ```batsh
   cd \your\directory\
   ```
2. Create and activate the virtual environment
   ```batsh
   py -m venv .venv
   .\.venv\Scripts\activate
   ```
   If you run into an error with execution policy, check your own execution policy with:
   ```batsh
    Get-ExecutionPolicy
   ```
   remember it if you want to put it back later. Then, change it to RemoteSigned and try to activate the environment again:
   ```batsh
    Set-ExecutionPolicy RemoteSigned
   ```
3. Clone the repository
   ```batsh
   git clone https://github.com/WH-Yoshi/PolarionCopilot.git
   cd PolarionCopilot
   ```
4. Install the required libraries
   ```batsh
   pip install -r requirements.txt
   ```
#### Linux 
1. Find a suitable location for the repository
   ```bash
   cd /your/directory/
   ```
2. Create and activate the virtual environment
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
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

#### Before any further steps, you need to fill the environment variables in the .env file.
Create and fill the .env file with the following content, each value must be between quotes "":
   ```
   base_url=<URL> # The URL of your Polarion server (e.g. https://polarion.example.com/polarion)
   embedding_api=<URL> # The URL of your embedding API
   openai_api=<URL> # The URL of your OpenAI like API (has to finish with "/v1")
   polarion_user=<USERNAME> # The username to access the Polarion server
   polarion_password=<PASSWORD> # The password to access the Polarion server [Not recommended]
   polarion_token=<TOKEN> # The user token to access the Polarion server
   ```
   Replace `<URL>`, `<USERNAME>`, and `<TOKEN>`(or `<PASSWORD>`) with your own values.
   The '.env' file contains sensitive information, make sure to not share it.


### Tensordock virtual machine

1. Open [TensorDock](https://dashboard.tensordock.com/deploy)
2. Get two GPU with at least 48Gb of VRAM
3. 2GPUs, 8Gb of RAM, 2CPU and 80Gb SSD
4. Select one of the available locations
5. Choose Ubuntu 22.04 as an operating system
6. Put a secure password and a machine name
7. Deploy
8. SSH into the machine :
   ```bash
   ssh -p xxxxx user@host -L 22027:localhost:8080 -L 22028:localhost:8000
   ```
9. Run the two docker images :
   ```bash
   docker run -d --gpus '"device=0"' -v ~/.cache/huggingface:/root/.cache/huggingface --env "HUGGING_FACE_HUB_TOKEN=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" -p 8000:8000 --ipc=host vllm/vllm-openai:latest --model mistralai/Mistral-7B-Instruct-v0.3
   ```
   ```bash
   docker run -d --gpus '"device=1"' -p 8080:80 -v $PWD/data:/data --pull always ghcr.io/huggingface/text-embeddings-inference:86-1.5 --model-id dunzhang/stella_en_1.5B_v5 
   ```
When the two images are booted up, you can proceed.

### Use the Code
1. Run the desired script in the main directory:
   #### Windows
      ```batsh
      python run_polarion.py
      python run_copilot.py
      ```
   #### Linux
      ```bash
      python3 run_polarion.py
      python3 run_copilot.py
      ```
2. Enjoy the ride!
