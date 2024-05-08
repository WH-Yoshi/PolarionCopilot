import platform
import subprocess


def run_copilot():
    if platform.system() == 'Windows':
        subprocess.call(['start', './codes/launchers/Launcher_polarion.cmd'])
    elif platform.system() == 'Linux':
        subprocess.call(['sh', './codes/launchers/Launcher_polarion.sh'])
    else:
        raise OSError('Unsupported OS')


if __name__ == '__main__':
    run_copilot()
