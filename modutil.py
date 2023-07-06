"""Utilities for Modules."""

from typing import *
from typing_extensions import *

import sys
import importlib

from types import ModuleType

def _passalong(arg):
    return arg

def _include_map_err(target):
    if isinstance(target, str):
        return target
    elif hasattr(target, '__name__'):
        return target.__name__
    else:
        raise IncludeError(target)

class IncludeError(Exception):
    def __init__(self, obj):
        super().__init__(f'Target does not have "__name__" attribute (Type: {type(obj)})')

class Includer(list):
    """A list subtype that is used to include items in your module into `__all__`.
    
    You would set `__all__` to an Includer, then you can use `__all__`
    as a decorator on all the items you would like to include.
    
    ```python
    __all__ = Includer()
    
    @__all__
    def this_will_be_included():
        print('The quick brown fox jumps over the lazy dog.')
    ```
    Optionally, you can also utilize the Walrus operator to create an
    alias so you don't need to type `__all__`.
    (This is just a recommendation, not a necessity)
    
    ```python
    __all__ = (include = := Includer())
    
    @include
    def this_will_be_included():
        print('The quick brown fox jumps over the lazy dog.')
    ```
    
    Note:
        It's important to understand that this class will not know
        if your function's `__name__` attribute is different from
        how it appears to your code. If another decorator renames
        your item, the includer will try to include based on
        the name of the item that is decorated. It will not
        know the name of the item given in the code.
        If you are using an `Includer` as a decorator, you can use
        the optional `alias` parameter to apply an alias.
        
        ```python
        __all__ = Includer()
        
        def rename_decorator(target):
            def _wrapper(*args, **kwargs):
                return target(*args, **kwargs)
            return _wrapper
        
        @__all__(alias='some_target')
        def some_target():
            print('Hello, world!')
        ```
    """
    @overload
    def __init__(self, targets: Iterable[str | Any]):...
    @overload
    def __init__(self, *targets: Iterable[str | Any]):...
    @overload
    def __init__(self, targets: Iterable[str | Any],*, include_globals: bool = False, exclude: Iterable[str | Any] = ...):...
    @overload
    def __init__(self, *targets: Iterable[str | Any], include_globals: bool = False, exclude: Iterable[str | Any] = ...):...
    def __init__(self, *targets, exclude: Iterable[str | Any] = (), include_globals: bool = False):
        super().__init__()
        if isinstance(exclude, Iterable):
            exclude = set(map(_include_map_err, exclude))
        else:
            exclude = set()
        if (
            len(targets) == 1 
            and not isinstance(targets[0], str)
            and isinstance(targets[0], Iterable)
        ):
            targets = targets[0]
        if include_globals:
            for k in globals().keys():
                if k not in exclude:
                    super().append(k)
        for target in map(_include_map_err, targets):
            if target not in exclude:
                self.append(target)
    
    def remove(self, target: str | Any):
        if isinstance(target, str):
            super().remove(target)
        elif hasattr(target, "__name__"):
            super().remove(target.__name__)
        else:
            raise IncludeError(target)
    
    def append(self, target: str | Any):
        if isinstance(target, str):
            super().append(target)
        elif hasattr(target, "__name__"):
            super().append(target.__name__)
            return target
        else:
            raise IncludeError(target)
    
    def extend(self, __iterable):
        super().extend(map(_include_map_err, __iterable))
    
    def include(self, *targets):
        for target in targets:
            self.append(target)
    
    @overload
    def __call__(self, alias: str = ...):...
    @overload
    def __call__(self, target):...
    def __call__(self, target = None,*, alias: str = None):
        match (target, alias):
            case (None, str(name)):
                self.append(name)
                return _passalong
            case (str(name), None):
                self.append(name)
                return _passalong
            case (target, None):
                self.append(target)
                return target

__all__ = (include := Includer('Includer, IncludeError'))

@include
def modulereloader(module, returns_module: bool = False):
    """Creates a function that reloads a module and optionally returns the reloaded modules.
    
    `module`: Can be either a module or a module name. If it is a module name,
        This will search `sys.modules` for the module name and raise a `KeyError`
        if it is not found.
    
    Raises:
        `KeyError`
    """
    if isinstance(module, str):
        try:
            module = sys.modules[module]
        except:
            raise KeyError(f'Module not found: {module}')
    def reloader():
        nonlocal module
        module = importlib.reload(module)
        if returns_module:
            return module
    return reloader