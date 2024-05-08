import os
import platform
import subprocess
import site
import shutil
import time

import polarion
from enhancer import Loader
from pathlib import Path

site_package_path = Path(__file__).parent.parent / "codes" / "site-packages-changes"
certifi_path = Path(__file__).parent.parent / "certifi" / "cacert.pem"
line_number_to_modify = 9
polarion_location = Path(polarion.__file__)


def modify_file(file_pth, line_number, new_line):
    with open(file_pth, 'r') as file:
        lines = file.readlines()

    if 0 < line_number <= len(lines):
        lines[line_number - 1] = new_line + '\n'

        with open(file_pth, 'w') as file:
            file.writelines(lines)
        return True
    else:
        return False


def os_identification():
    if platform.system() == 'Windows':
        cert_path = Path(__file__).parent.parent / 'certifi' / 'cacert.pem'
        cert_path = cert_path.as_posix().replace(r'/', r'\\')
    elif platform.system() == 'Linux':
        cert_path = Path(__file__).parent.parent / 'certifi' / 'cacert.pem'
    else:
        raise OSError('Unsupported OS')
    return f'    return "{cert_path}"'


def check_packages():
    new_line_content = os_identification()
    loader = Loader("Checking the necessary packages... ", "All good.").start()
    time.sleep(1)
    installed_codes = os.listdir(polarion_location.parent)
    required_code = "project_groups.py"
    if required_code not in installed_codes:
        modify_file(site_package_path / 'wrapt_certifi.py', line_number_to_modify, new_line_content)
        for path in site.getsitepackages():
            path = Path(site.__file__).parent / "site-packages" / path
            if "site-packages" in str(path):
                if platform.system() == 'Windows':
                    shutil.copy(site_package_path / "wrapt_certifi.py", path / "certifi_win32" / "wrapt_certifi.py")
                elif platform.system() == 'Linux':
                    shutil.copy(certifi_path, "/etc/ssl/certs/")
                    os.system("sudo update-ca-certificates")
                    print("Certificates updated.")
                for file in os.listdir(site_package_path / "polarion"):
                    shutil.copy(site_package_path / "polarion" / file, path / "polarion" / file)
        loader.stop()
        print("Packages installed.")
        return
    else:
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
    print("     \u21AA Note : Automation of this process is possible but not implemented.")


print_instructions()
input("\nPress Enter to run the script.")
