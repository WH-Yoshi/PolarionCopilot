import os
import shutil
import site
from pathlib import Path

import polarion
from termcolor import colored

from enhancer import Loader, arrow

site_package_path = Path(__file__).parent / "site-packages-changes"
polarion_location = Path(polarion.__file__)


def check_packages():
    loader = Loader("Checking packages... ", colored("Packages up to date.", "green")).start()
    for path in site.getsitepackages():
        path = Path(site.__file__).parent / "site-packages" / path
        if "site-packages" in str(path):
            for file in os.listdir(site_package_path / "polarion"):
                shutil.copy(site_package_path / "polarion" / file, path / "polarion" / file)
    loader.stop()
    return


def print_instructions():
    print(colored("\nInstructions:", "light_cyan"))

    print("1. Installing the necessary packages:")
    check_packages()

    print("\n2. Run the Embedding Machine if it does not already:")
    print("   Follow these instruction for the deployment of the cloud GPU via TensorDock.")
    print(arrow("https://gitlab.sw.goiba.net/req-test-tools/polarion-copilot/copilot-proto#polarioncopilot", start="  "))


print_instructions()
input("\nPress Enter to run the script.")
