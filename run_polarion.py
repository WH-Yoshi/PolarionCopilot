import os
import platform
import subprocess
from pathlib import Path
from termcolor import colored


def run_polarion():
    if platform.system() == 'Windows':
        script_path = str(Path(r'.\codes\launchers\Launcher_polarion.ps1').absolute())
        os.system(f'powershell -NoProfile -ExecutionPolicy Bypass -File {script_path}')
    elif platform.system() == 'Linux':
        subprocess.run(['bash', str(Path(r'./codes/launchers/Launcher_polarion.sh').absolute())], check=True)
    else:
        raise OSError('Unsupported OS yet')


if __name__ == '__main__':
    run_polarion()
