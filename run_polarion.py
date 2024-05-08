import os
import platform
from pathlib import Path


def run_copilot():
    if platform.system() == 'Windows':
        os.system('cmd /c "start /wait ' + str(Path(r'.\codes\launchers\Launcher_polarion.cmd').absolute()) + '"')
    elif platform.system() == 'Linux':
        os.system('sh ' + str(Path(r'codes/launchers/Launcher_polarion.sh').absolute()))
    else:
        raise OSError('Unsupported OS')


if __name__ == '__main__':
    run_copilot()
