"""The Includer module is used for creating an includer for your
modules.

What is an includer? An includer is a special list type that you
can use in place of `__all__`. This special type allows you to
use it as a decorator for functions and classes.

Example:
```
some_global = "This is a global that will be includer."
def some_function():
    print('some_function()')
    
# Note that I include the name of 'some_global'
__all__ = Includer(
    'some_global',
    some_function
)

@__all__
def include_me():
    print('This function will also be included.')

```
"""

from typing import *
from typing_extensions import *

__all__ = ['Includer', 'IncludeError']

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
    @overload
    def __init__(self, targets: Iterable[str | Any]):...
    @overload
    def __init__(self, *targets: Iterable[str | Any]):...
    def __init__(self, *targets):
        super().__init__()
        if (
            len(targets) == 1 
            and not isinstance(targets[0], str)
            and isinstance(targets[0], Iterable)
        ):
            targets = targets[0]
        for target in targets:
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
    
    @overload
    def __call__(self, target):...
    @overload
    def __call__(self, *targets):...
    def __call__(self, *targets):
        for target in targets:
            self.append(target)
        if len(targets) == 1 and not isinstance(targets[0], str):
            return targets[0]