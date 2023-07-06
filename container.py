"""
Additional collections.
"""

from typing import *
from typing_extensions import Self
from collections import (
    defaultdict,
    ChainMap,
    UserDict,
)
from collections.abc import MutableMapping, Mapping
from .modutil import Includer

__all__ = (include := Includer())

@include
class attrdict(dict):
    """A dictionary subtype that allows access through attributes.
    ```py
    >>> letter_fruit = attrdict()
    >>> letter_fruit.a = 'Apple'
    >>> letter_fruit.b = 'Banana'
    >>> letter_fruit.c = 'Cherry'
    >>> letter_fruit
    {'a': 'Apple', 'b': 'Banana', 'c': 'Cherry'}
    >>> del letter_fruit.c
    >>> letter_fruit.b
    'Banana'
    >>> letter_fruit
    {'a': 'Apple', 'b': 'Banana'}
    ```
    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

@include
class attruserdict(UserDict):
    """A UserDict subtype that allows acces through attributes."""
    __getattr__ = UserDict.__getitem__
    __setattr__ = UserDict.__setitem__
    __delattr__ = UserDict.__delitem__

@include
class attrdefaultdict(defaultdict):
    """Similar to attrdict, but allows a factory method.
    """
    __getattr__ = defaultdict.__getitem__
    __setattr__ = defaultdict.__setitem__
    __delitem__ = defaultdict.__delitem__

@include
class attrchainmap(ChainMap):
    """A ChainMap subtype that allows access through attributes.
    """
    __getattr__ = ChainMap.__getitem__
    __setattr__ = ChainMap.__setitem__
    __delitem__ = ChainMap.__delitem__

@include
class attrmappingproxy:
    """Similar to AttrDict, but is useful when you already have a mapping.
    """
    __slots__ = ('________ATTRMAPPINGPROXY_MAPPING',)
    ________ATTRMAPPINGPROXY_MAPPING: MutableMapping

    def __init__(self, mapping: MutableMapping):
        self.________ATTRMAPPINGPROXY_MAPPING = mapping
    
    def __getattr__(self, name: str):
        return self.________ATTRMAPPINGPROXY_MAPPING.__getitem__(name)
    
    def __setattr__(self, name: str, value):
        self.________ATTRMAPPINGPROXY_MAPPING.__setitem__(name, value)
    
    def __delattr__(self, name: str):
        self.________ATTRMAPPINGPROXY_MAPPING.__delitem__(name)