"""Execute morethon."""

import argparse
from pathlib import Path

from .grammar import UqParser


class StartAction(argparse.Action):
    """Start Action."""

    def __call__(self, *args): ...


parser = argparse.ArgumentParser(description="morethon")
parser.add_argument("file", nargs="?", help="read from script file")
parser.add_argument(".", nargs=0, action=StartAction, help="read from std input")

namespace = vars(parser.parse_args())
if namespace["file"]:
    UqParser().exec(Path(namespace["file"]).read_text("utf-8"))
else:
    print("not implemented yet")
