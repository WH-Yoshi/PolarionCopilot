import os
import platform
import subprocess
from pathlib import Path


def run_copilot():
    if platform.system() == 'Windows':
        os.system('cmd /c "start /wait ' + str(Path(r'.\codes\launchers\Launcher_polarion.cmd').absolute()) + '"')
    elif platform.system() == 'Linux':
        subprocess.run(['bash', str(Path(r'./codes/launchers/Launcher_polarion.sh').absolute())], check=True)
    else:
        raise OSError('Unsupported OS yet')


if __name__ == '__main__':
    run_copilot()
