import os
import platform
import subprocess
from pathlib import Path


def run_copilot():
    if platform.system() == 'Windows':
        script_path = str(Path(r'.\codes\launchers\Launcher_copilot.ps1').absolute())
        os.system(f'powershell -NoProfile -ExecutionPolicy Bypass -Command '
                  f'"Start-Process -Wait powershell -NoExit -ArgumentList '
                  f'\'-NoProfile -NoExit -ExecutionPolicy Bypass -File {script_path}\'"')
    elif platform.system() == 'Linux':
        subprocess.run(['bash', str(Path(r'./codes/launchers/Launcher_copilot.sh').absolute())], check=True)
    else:
        raise OSError('Unsupported OS yet')


if __name__ == '__main__':
    run_copilot()
