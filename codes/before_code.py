import os
import shutil
import site
import sys
from pathlib import Path

import polarion
import subprocess
from termcolor import colored

from enhancer import Loader, arrow

site_package_path = Path(__file__).parent / "site-packages-changes"
polarion_location = Path(polarion.__file__)


def check_packages():
    loader = Loader("Checking packages... ", colored("Packages up to date.", "green"), timeout=0.05).start()
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], stdout=subprocess.DEVNULL)
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

print_instructions()
