from typing import *
from functools import partial, wraps
import inspect
from inspect import signature, Parameter as param, Signature
from .fp import first, replace_decorator
from .modutil import Includer

__all__ = (include := Includer())

# TODO: Update the decorator to add a `.replace(value)` function to
#       the wrapper allowing the decorator to replace the decorated value.
@include
def decorator(target):
    """Turns `target` into a decorator.
    
    `target` must be a callable that has a signature such as:
    ```
    @decorator
    def example_decorator(target, *args, **kwargs):
        ...
    ```
    or
    ```
    @decorator
    def example_decorator(target):
        ...
    ```
    This decorator can then be used like so:
    ```
    @example_decorator(*args, **kwargs)
    def example_function():
        ...
    ```
    or
    ```
    @example_decorator
    def example_function():
        ...
    ```
    """
    if not callable(target):
        raise TypeError(type(target))
    sig = inspect.signature(target)
    params = sig.parameters
    # Check if there is only one parameter, meaning that it is a bare decorator.
    if len(params) == 1 and first(params.values()).kind != param.VAR_KEYWORD:
        @wraps(target)
        def _wrapped(decorator_target):
            # Call the target function, and if a result is returned, that is the replacement.
            # If None is returned, no replacement occurs.
            if (result := target(decorator_target)) is not None:
                return result
            else:
                return decorator_target
        return _wrapped
    else:
        @wraps(target)
        def _wrapped(*args, **kwargs):
            def inner(decorator_target):
                # Call the target function, and if a result is returned, that is the replacement.
                # If None is returned, no replacement occurs.
                if (result := target(decorator_target, *args, **kwargs)) is not None:
                    return result
                else:
                    return decorator_target
            return inner
        return _wrapped

@include
class params:
    __slots__ = ('args', 'kwargs')
    @overload
    def __init__(self):...
    @overload
    def __init__(self, *args):...
    @overload
    def __init__(self, *args, **kwargs):...
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    def invoke(self, fn: Callable):
        return fn(*self.args, **self.kwargs)

@include
class Alias:
    __slots__ = ('target', 'args', 'kwargs')
    @overload
    def __init__(self, target):...
    @overload
    def __init__(self, target, params: params):...
    @overload
    def __init__(self, target, *args):...
    @overload
    def __init__(self, target, *args, **kwargs):...
    def __init__(self, target, _params: params = ..., *args, **kwargs):
        self.target = target
        match (_params, args, kwargs):
            case (alt, (), {}) if isinstance(alt, params):
                self.args = alt.args
                self.kwargs = alt.kwargs
            case (Ellipsis, _, _):
                self.args = args
                self.kwargs = kwargs
            case (something, args, kwargs):
                self.args = (something, *args)
                self.kwargs = kwargs
    @overload
    def __call__(self, *args):...
    @overload
    def __call__(self, *args, **kwargs):...
    def __call__(self, *args, **kwargs):
        return self.target(*(*self.args, *args), **{**self.kwargs, **kwargs})

@decorator
@include
def alias(target, *names, **partials):
    """Apply aliases to target.
    
    Example:
    ```py
    @alias(
        'short',
        short_partial = params(extra='Hello, world!')
    )
    def this_is_a_long_name(value,extra=...):
        print(value)
        if extra is not ...:
            print(extra)
    ```
    """
    import inspect
    plocals = inspect.currentframe().f_back.f_back.f_locals
    for name in names:
        name: str
        if isinstance(name, str) and name.isidentifier():
            plocals[name] = target
    for k, v in partials.items():
        match v:
            case (tuple(args), dict(kwargs)):
                v = params(*args, **kwargs)
            case tuple(args):
                v = params(*args)
            case dict(kwargs):
                v = params(**kwargs)
        plocals[k] = Alias(target, v)

@decorator
@include
def attr(target, **kwargs):
    """Apply attributes to the decorated object."""
    for k, v in kwargs.items():
        setattr(target, k, v)

def __new__singleton__(cls, *args, **kwargs):
    """If you are trying to call this function, you are probably doing something wrong.
    
    This function is meant to be plugged into a class's `__new__`
    Example:
    ```
    class Singleton:
        __new__ = __new__singleton__
    ```
    """
    if not hasattr(cls, '___singleton_instance'):
        cls.___singleton_instance = super(cls, cls).__new__(cls)
    return cls.___singleton_instance

@decorator
@include
def singleton(cls):
    """When used as a decorator for a class, turns class into a singleton."""
    setattr(cls, '__new__', __new__singleton__)

R = TypeVar("R")

@include
def evaluate(target: Callable[[], R]) -> R:
    """This decorator is used to replace a function with the value that it returns.
    
    The function must require no arguments.
    
    Example:
    ```
    @evaluate
    def text()->str:
        pieces = ['the', 'quick', 'brown', 'fox', 'jumps', 'over', 'the', 'lazy', 'dog']
        return ' '.join(pieces)

    print(text)
    ```
    """
    return target()

@include
class lookup:
    """The lookup class can be used to create a getter and optional setter for key lookup.
    
    This is easier to explain with an example.
    Let's say you want to have the following functionality:
    ```
    value = index[key]
    ```
    But you do not want to go through the trouble of creating a new class for it.
    The usual way would be to create a new class, then create an instance of that
    class, then you would have your `__getitem__` and `__setitem__`.
    This class circumvents that redundancy and allows you to simply create one
    or two functions.
    Here is an example in usage:
    ```
    items = [('one', 1), ('two', 2), ('three', 3), ('four', 4), ('five', 5)]

    def finditem(key):
        for item in items:
            if item[0] == key:
                return item
        return None
    
    table = lookup(finditem)
    print(table['one'])
    print(table['five'])
    ```
    If you don't mind your function getting replaced with an instance of `lookup`,
    you can also use `lookup` as a decorator.
    ```
    _items = {'a':1,'b':2,'c':3}
    @lookup
    def items(key: str)->int | None:
        return _items.get(key, None)
    
    print(items['a'])
    ```
    """
    __slots__ = ('getter','setter')
    def __init__(self, getter: Callable, setter: Callable = ...):
        self.getter = getter
        self.setter = setter if callable(setter) else self._assign_setter
    
    def _assign_setter(self, setter: Callable):
        self.setter = setter
        return setter
    
    def __getitem__(self, key):
        try:
            return self.getter(key)
        except:
            return None
    
    def __setitem__(self, key, value):
        if callable(self.setter):
            self.setter(key, value)
    
    def __call__(self, *args, **kwargs):
        return self.getter(*args, **kwargs)
    
    def __sub__(self, other):
        return self.getter(other)

@include
class attrgetter:
    """Allows for the quick creation of a `__getattr__` interface.

    Example:
    ```
    >>> @attrgetter
    >>> def docs(name: str)->str:
    >>>     return f'www.example.com/docs/{name}/'
    >>> 
    >>> docs.example
    'www.example.com/docs/example/'
    ```
    """
    getter: Callable[[str], Any]

    def __init__(self, getter: Callable | dict):
        if callable(getter):
            self.getter = getter
        elif isinstance(getter, dict):
            self.getter = getter.__getitem__
    
    def __getattr__(self, name: str)->Any:
        return self.getter(name)