import os
import platform
from pathlib import Path


def run_copilot():
    if platform.system() == 'Windows':
        os.system('cmd /c "start /wait ' + str(Path(r'.\codes\launchers\Launcher_polarion.cmd').absolute()) + '"')
    else:
        raise OSError('Unsupported OS yet')


if __name__ == '__main__':
    run_copilot()
