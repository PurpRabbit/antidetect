import os

from ui.settings import STYLES_DIR


def load_style_sheet(filename: str) -> str:
    with open(os.path.join(STYLES_DIR, filename)) as fp:
        style = fp.read()
    return style
