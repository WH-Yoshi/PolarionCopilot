# PolarionCopilot

PolarionCopilot is a combination of 2 main components for Windows:
- A Python script that can be used to retrieve Polarion work items to make them understandable by a LLM.
- A LLM that can be used to ask questions about the work items

## Installation

The installation is half automated, half manual. The automated part is the installation of each library, and specific changes dones to them.
The manual part is the installation of any required software.

### Required installation

1. Python version 3.11 (minimum) via this link: [Python for Windows](https://www.python.org/downloads/)
   - Make sure to check the box *"Add python.exe to PATH"* during the installation
2. Git to clone this repository via this link: [Git](https://git-scm.com/downloads)
   - You can click *Next* for each step.
3. **[Optional]** A new version of terminal to show you all this goodies going on in the scripts :)
   - You can use the new Windows Terminal via this link: [Windows Terminal](https://www.microsoft.com/en-us/p/windows-terminal/9n0dx20hk701)


### Activate and fill your environment

1. Define a location for the repository
   ```bash
   cd <DIRECTORY>
   ```
2. Create and activate a virtual environment
   ```bash
   py -m venv venv
   .\venv\Scripts\activate
   ```
   If you run into an error with execution policy, check your execution policy with:
   ```bash
    Get-ExecutionPolicy
    ```
   and remember its value if you want to go back later. Then, change it to:
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

### Use the Code

1. Run the desired script
    ```bash
    Launcher_polarion.cmd
    Launcher_copilot.cmd
    ```

2. Enjoy the ride!

# Made by WH-Yoshi
