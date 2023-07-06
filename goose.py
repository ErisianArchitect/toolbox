from typing import *
from typing_extensions import *
from .modutil import Includer, modulereloader
from datetime import datetime

__all__ = Includer()

import sys

reload = modulereloader(__name__)

@__all__
def bumpy():
    print("Hello, world!")

@__all__
def dixon():
    print("The quick brown fox jumps over the lazy dog.")

@__all__
def excluded():
    print("This should be exluded.")

print(f"Loaded {__name__} {datetime.now().strftime('%H:%M:%S %p')}")