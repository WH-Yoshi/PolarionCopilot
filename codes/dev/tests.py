import os
import polarion
from pathlib import Path

path = Path(polarion.__file__)
bs4_codes = os.listdir(path.parent)
print(bs4_codes)
