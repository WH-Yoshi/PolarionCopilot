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
   - For Windows, you can use the new Windows Terminal via this link: [Windows Terminal](https://www.microsoft.com/en-us/p/windows-terminal/9n0dx20hk701)
   - For Linux, you can use the ZSH shell by following this link: [ZSH](https://dev.to/yogeshdev/make-your-unix-terminal-beautiful-productive-c1d)

### Use the Repository

1. Open Terminal and Clone the repository
   ```bash
   cd <path to a prefered directory>
   ```
   ```bash
   git clone https://github.com/WH-Yoshi/PolarionCopilot.git
   cd PolarionCopilot
   ```
2. Run the desired script
   - For Windows :
    ```bash
    Launcher_polarion.cmd
    Launcher_copilot.cmd
    ```
   - For Linux :
    ```bash
    ./Launcher_polarion.sh
    ./Launcher_copilot.sh
    ```

3. Enjoy the ride!