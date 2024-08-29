import os
import platform
import shutil
import site
import time
import random
from pathlib import Path

import polarion

from enhancer import Loader

site_package_path = Path(__file__).parent / "site-packages-changes"
polarion_location = Path(polarion.__file__)

def check_packages():
    loader = Loader("Checking packages... ", "All good.").start()
    installed_codes = os.listdir(polarion_location.parent)
    required_code = "project_groups.py"
    if required_code not in installed_codes:
        for path in site.getsitepackages():
            path = Path(site.__file__).parent / "site-packages" / path
            if "site-packages" in str(path):
                for file in os.listdir(site_package_path / "polarion"):
                    shutil.copy(site_package_path / "polarion" / file, path / "polarion" / file)
        time.sleep(random.uniform(0.8, 1.5))
        loader.stop()
        print("Packages installed.")
        return
    else:
        time.sleep(random.uniform(0.5, 1.0))
        loader.stop()
        print("Packages already installed.")
        return

def print_instructions():
    print("Instructions for setting up and running Polarion.py:")

    print("\n1. Installing the necessary packages:")
    check_packages()

    print("\n2. Run the Cloud GPU:")
    print("   - Open your browser and navigate to the following link: https://marketplace.tensordock.com/deploy")
    print("   - Follow the instruction made by Luca Abs for the deployment of the cloud GPU via TensorDock.")
    print("     \u21AA Note : Automation of this process can be but is not implemented.")


print_instructions()
input("\nPress Enter to run the script.")
