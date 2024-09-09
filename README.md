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
1. Python (3.8+): [Python for Windows](https://www.python.org/downloads/)
   - Make sure to check the box *"Add python.exe to PATH"* during the installation
2. Git, if it isn't already installed, to clone this repository: [Git](https://git-scm.com/downloads)
   - You can click *Next* for each step.
3. **[Optional]** A good terminal to have a more user-friendly experience.
   - You can use the new Windows Terminal for exemple: [Windows Terminal](https://www.microsoft.com/en-us/p/windows-terminal/9n0dx20hk701)
#### Linux
1. Python (3.8+):
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
   python -m venv .venv
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
   sh install_polarioncopilot.sh
   ```

#### Before any further steps, you need to fill the environment variables in a .env file.
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
2. Get two VM with one GPU each
   1. 48GB VRAM, 8GB or RAM, 2CPUs and 50GB SSD
   2. 16GB VRAM, 8GB or RAM, 2CPUs and 30GB SSD
3. Select one of the available locations
4. Choose Ubuntu 22.04 as an operating system
5. Deploy
6. SSH into the machine :
   ```bash
   ssh -p xxxxx user@host -i ~/.ssh/id_rsa_tensordock
   ```
7. Run the two docker images :
   ```bash
   docker run -d --gpus all -v ~/.cache/huggingface:/root/.cache/huggingface --env "HUGGING_FACE_HUB_TOKEN=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" -p 8000:8000 --ipc=host vllm/vllm-openai:latest --model mistralai/Mistral-7B-Instruct-v0.3
   ```
   ```bash
   docker run -d --gpus all -p 8080:80 -v $PWD/data:/data --pull always ghcr.io/huggingface/text-embeddings-inference:86-1.5 --model-id dunzhang/stella_en_1.5B_v5 
   ```

### [Optional] Setup a Linux daemon for automatic containers start. 
**Warning:** You must have created the container by pulling the images on point 7.\
This step is optional but recommended to avoid having to restart the containers manually after a reboot.\
It will start all the containers that are stopped.

1. Create a new file in /etc/systemd/system/ :
   ```bash
   sudo nano /etc/systemd/system/containers.service
   ```
2. Fill the file with the following content :
   ```bash
   [Unit]
   Description=Starts all containers service
   After=network.target
   Requires=docker.service
   
   [Service]
   Type=oneshot
   ExecStart=/bin/sh -c '/usr/bin/docker start $(/usr/bin/docker ps -aq)'
   ExecStop=/bin/sh -c '/usr/bin/docker stop $(/usr/bin/docker ps -aq)'
   RemainAfterExit=true
   
3. Reload the daemon and enable the service to start at boot :
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable containers
   ```
   
Now you can restart the virtual machine without having to restart the containers manually.

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


###### Luca A. | 2024, Arnaud V. | 2024
