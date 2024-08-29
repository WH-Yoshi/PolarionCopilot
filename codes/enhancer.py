from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep

from termcolor import colored


def arrow(content: str, start: str | None = '', end: str | None = ''):
    return f"{start} \u21AA  {content}{end}"


def printarrow(content: str, start: str | None = '', end: str | None = ''):
    print(arrow(content, start, end))


class Loader:
    def __init__(self, desc="Loading...", end="Done!", exit_color="white", timeout=0.1):
        """
        A loader-like context manager

        Args:
            desc (str, optional): The loader's description. Defaults to "Loading...".
            end (str, optional): Final print. Defaults to "Done!".
            timeout (float, optional): Sleep time between prints. Defaults to 0.1.
        """
        self.desc = desc
        self.end = end
        self.timeout = timeout
        self.exit_color = exit_color

        self._thread = Thread(target=self._animate, daemon=True)
        self.steps = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
        # self.steps = ['|', '/', '--', '\\']
        self.done = False

    def start(self):
        self._thread.start()
        return self

    def _animate(self):
        for c in cycle(self.steps):
            if self.done:
                break
            print(f"\r{self.desc}  {c}", flush=True, end="")
            sleep(self.timeout)

    def __enter__(self):
        self.start()

    def stop(self, print_exit=True):
        self.done = True
        cols = get_terminal_size((80, 20)).columns
        if print_exit:
            print("\r" + " " * cols, end="", flush=True)
            print(f"\r{colored(self.end, self.exit_color)}", flush=True)
        else:
            print("\r" + " " * cols, end="", flush=True)
            print("\n")

    def __exit__(self, exc_type, exc_value, tb):
        # handle exceptions with those variables ^
        self.stop()


if __name__ == '__main__':
    raise Exception("This script is not meant to be run directly.")