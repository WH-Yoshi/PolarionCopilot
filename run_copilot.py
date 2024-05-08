import os
import platform
import subprocess
from pathlib import Path


def run_copilot():
    print(Path(r'.\codes\launchers\Launcher_copilot.cmd').absolute())
    if platform.system() == 'Windows':
        os.system('cmd /c "start /wait ' + str(Path(r'.\codes\launchers\Launcher_copilot.cmd').absolute()) + '"')
    elif platform.system() == 'Linux':
        os.system('sh ' + str(Path(r'codes/launchers/Launcher_copilot.sh').absolute()))
    else:
        raise OSError('Unsupported OS')


if __name__ == '__main__':
    run_copilot()
