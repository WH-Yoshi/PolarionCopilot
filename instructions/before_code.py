import os
import subprocess
import site
import shutil
from pathlib import Path

site_package_path = Path(__file__).parent.parent / "codes" / "site-packages-changes"


def print_instructions():
    print("Instructions for setting up and running Polarion.py:")

    print("\n1. Install necessary packages:")
    inputted = input("   \u21AA  Do you want to install the necessary packages? (y/n): ")
    if inputted.lower() == 'y':
        print("Installing packages...")
        subprocess.run(["start", "/wait", "cmd", "/k", "pip install -r requirements.txt"], shell=True)
        for path in site.getsitepackages():
            path = Path(site.__file__).parent / "site-packages" / path
            if "site-packages" in str(path):
                shutil.copy(site_package_path / "wrapt_certifi.py", path / "certifi_win32" / "wrapt_certifi.py")
                for file in os.listdir(site_package_path / "polarion"):
                    shutil.copy(site_package_path / "polarion" / file, path / "polarion" / file)
        print("Packages installed.")
    else:
        print("   Ensure all necessary packages are installed before running the script.")

    print("\n2. Run the Cloud GPU:")
    print("   - Open your browser and navigate to the following link: https://marketplace.tensordock.com/deploy")
    print("   - Follow the instruction made by Luca Abs for the deployment of the cloud GPU via TensorDock.")
    print("     \u21AA Note : Automation of this process is possible but not implemented.")


print_instructions()
input("\nPress Enter to run the script.")
