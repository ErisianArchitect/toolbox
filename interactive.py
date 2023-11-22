"""
Some useful stuff for when using an interactive interpreter.
"""
from typing import *
from typing_extensions import *
from .decorators import *

# System
import os, sys
from pathlib import Path
# Functools
from functools import (
    partial,
    partialmethod,
    cache,
    cached_property,
    lru_cache,
    reduce,
    wraps,
)
# Itertools
from itertools import *
# Handling imports
import importlib
# For handling text
import re, string
# For handling data
import json
# For mathematics
import math, numpy as np
# Threading
import threading
from threading import Thread
from time import sleep
# Time
from datetime import datetime, date, timedelta
now = datetime.now
utcnow = datetime.utcnow
def today(): return date((t := date.today()).year, t.month, t.day)

def date_from_today(days: int):
    return today() + timedelta(days = days)

tomorrow = partial(date_from_today, 1)
yesterday = partial(date_from_today, -1)
next_week = partial(date_from_today, 7)
last_week = partial(date_from_today, -7)
days_ago = lambda days: today() - timedelta(days = days)

# For handling web requests
try:
    import requests
except ImportError: pass
# For handline the clipboard
try:
    from pyperclip import paste, copy as _copy
    def copy(data: Any):
        _copy(str(data))
    
    def copyr(data: Any):
        _copy(repr(data))
except ImportError: pass

_prelude = list(filter(lambda key: not key.startswith('_'), globals().keys()))

from .modutil import Includer

__all__ = Includer(_prelude)

# Globals

startup_path = Path('.').resolve()

def inject_into_main(replace: bool = True):
    """This will attempt to inject stuff into the main module."""
    import __main__
    for name in __all__:
        if (
            replace 
            or not hasattr(name, __main__)
        ):
            setattr(name, __main__, globals()[name])