import enum
import operator
from typing import *
import typing
import builtins
from itertools import islice
from functools import partial, partialmethod, wraps

# TODO: Write docs
#       Cleanup code.

__all__ = (
    'first',
    'nth',
    'last',
    'passalong',
    'passnth',
    'returns',
    'returnTrue',
    'returnFalse',
    'returnNone',
    'ne',
    'eq',
    'lt',
    'le',
    'gt',
    'ge',
    'is_',
    'is_not',
    'not_none',
    'is_none',
    'present',
    'absent',
    'invertdict',
    'strjoin',
    'do',
    'filterfalse',
    'filternone',
    'count',
    'istype',
    'instanceof',
    'filtertype',
    'revrange',
    'yieldinstead',
    'calltransform',
    'callstack',
    'callstackfn',
)

def first(seq: Iterable, filter=None) -> Any | None:
    for value in seq:
        if not callable(filter) or filter(value):
            return value
    return None

def nth(n: int, seq: Iterable) -> Any | None:
    # Try the obvious first.
    try:
        return seq[n]
    except: pass
    # Old fashioned way.
    for i, value in enumerate(seq):
        if i == n:
            return value
    return None

def last(seq: Sequence) -> Any | None:
    try:
        return seq[-1]
    except IndexError:
        return None
    except TypeError:
        for result in seq: pass
        return result

def passalong(value):
    """Returns the value that was passed to it.
    
    This is useful for situations where a map function is required, but no mapping is needed.
    """
    return value

def passnth(key: int | str = 0, default: Optional[Any] = None):
    match key:
        case int(index):
            def passnth(*args, **kwargs):
                return args[index] if index < len(args) and len(args) + index >= 0 else default
            return passnth
        case str(name):
            def passnth(*args, **kwargs):
                return kwargs.get(name, default)
            return passnth
        case _:
            raise TypeError(key)

def returns(*values)->Callable[..., Any]:
    def returns(*args, **kwargs):
        return values
    return returns

def returnTrue(*args, **kwargs): return True

def returnFalse(*args, **kwargs): return False

def returnNone(*args, **kwargs): return None

def ne(value):
    """Creates a function that checks if value is not equal to parameter."""
    return partial(operator.ne, value)

def eq(value):
    """Creates a function that checks if value is equal to parameter."""
    return partial(operator.eq, value)

def lt(value):
    """Creates a function that checks if value is less than parameter."""
    return partial(operator.lt, value)

def le(value):
    """Creates a function that checks if value is less than or equal to parameter."""
    return partial(operator.le, value)

def gt(value):
    """Creates a function that checks if value is greater than parameter."""
    return partial(operator.gt, value)

def ge(value):
    """Creates a function that checks if value is greater than or equal to parameter."""
    return partial(operator.ge, value)

def is_(value):
    """Creates a function that checks if value is parameter."""
    return partial(operator.is_, value)

def is_not(value):
    """Creates a function that checks if value is not parameter."""
    return partial(operator.is_not, value)

def not_none(value):
    return value is not None

def is_none(value):
    return value is None

class present:
    """Creates a function that checks if a value is present in collection."""
    __slots__ = ('collection',)

    def __init__(self, collection: Container):
        self.collection = collection
    
    def __call__(self, value)->bool:
        return value in self.collection

class absent:
    """Creates a function that checks if a value is absent from collection."""
    __slots__ = ('collection',)

    def __init__(self, collection: Container):
        self.collection = collection
    
    def __call__(self, value)->bool:
        return value not in self.collection

def invertdict(d : dict)->dict:
    """Returns a version of the passed dictionary that has the keys and values swapped."""
    return {v : k for k, v in d.items()}

@overload
def strjoin(seq: Sequence[str])->str:...
@overload
def strjoin(seq: Sequence[str], joiner: str = '')->str:...
def strjoin(seq: Sequence[str], joiner: str = '')->str:
    return joiner.join(seq)

def do(action: Callable, seq: Iterable):
    """Do `action(item)` for every `item` in `seq`."""
    for item in seq:
        action(item)

def filterfalse(seq: Iterable):
    """Filter elements that evaluate to True. Remove all elements that evaluate to False."""
    yield from filter(bool, seq)

def filternone(seq: Iterable):
    """Filter out elements that are None."""
    yield from filter(not_none, seq)

@overload
def count(seq: Iterable)->int:...
@overload
def count(seq: Iterable, filter: Callable)->int:...
def count(seq: Iterable, filter=None)->int:
    if callable(filter):
        return sum((1 for _ in builtins.filter(filter, seq)))
    else:
        if hasattr(seq, '__len__'):
            return len(seq)
        else:
            return sum((1 for _ in seq))

def istype(type: Type):
    def istype(value)->bool:
        return builtins.type(value) == type
    return istype

def instanceof(type: Type):
    def instanceof(value)->bool:
        return isinstance(value, type)
    return instanceof

def filtertype(_type: Type, seq: Iterable, subtypes: bool = False):
    pass

@overload
def revrange(end: SupportsIndex,/)->range:...
@overload
def revrange(start: SupportsIndex, end: SupportsIndex,/)->range:...
@overload
def revrange(start: SupportsIndex, end: SupportsIndex, step: SupportsIndex,/)->range:...
def revrange(start: SupportsIndex, end: SupportsIndex = ..., step: SupportsIndex = ...)->range:
    pass

def yieldinstead(iterable: Iterable[Any], value: Any = None):
    yield from (value for _ in iterable)

def calltransform(callback: Callable[..., Any], transformer: Callable[..., Tuple[Tuple[Any], Dict[str, Any]]])->Callable[..., Any]:
    """Creates a function that transforms the arguments passed to it before calling the provided callback."""
    @wraps(callback)
    def _callback(*args, **kwargs):
        args, kwargs = transformer(*args, **kwargs)
        return callback(*args, *kwargs)
    return _callback

@overload
def callstack(iterable: Iterable[Callable[...,Any]|Any])->Callable[[Any], Any]:...
@overload
def callstack(*stack)->Callable[[Any], Any]:...
def callstack(iterable_or_callable, *stack)->Callable[[Any], Any]:
    if callable(iterable_or_callable):
        stack = (iterable_or_callable, *stack)
    elif isinstance(iterable_or_callable, Iterable) and not stack:
        stack = iterable_or_callable
    def callstack(*args, **kwargs):
        for mapper in stack:
            match mapper:
                case (tuple(nargs), dict(nkwargs)):
                    args = (*args, *nargs)
                    kwargs = {**kwargs, **nkwargs}
                case (tuple(nargs)):
                    args = (*args, *nargs)
                case (dict(nkwargs)):
                    kwargs = {**kwargs, **nkwargs}
                case call if callable(call):
                    match call(*args, **kwargs):
                        case (tuple(args), dict(kwargs)):pass
                        case (tuple(args)): kwargs = {}
                        case (dict(kwargs)): args = ()
                        case None:
                            args = (None,)
                            kwargs = {}
                        case other:
                            args = (other,)
                            kwargs = {}
                case other:
                    args = (*args, other)
        return args if args else None
    return callstack

def callstackfn(callback: Callable[..., Any], pass_kwargs: bool = False)->Callable[...,tuple]:
    """Transforms a regular callback into a callstack function.

    This will make a function that returns the result of the callback inside of a tuple.
    This function is what you might want to use when creating a callstack filter that returns
    a tuple, but you don't want to wrap that tuple inside of a tuple. I know that might sound a
    bit confusing, so let me show you an example of where this is handy:
    
    ```
    def vec2(x, y):
        return float(x), float(y)
    def get_pos():
        return 3, 14
    def multiply_vec(vec):
        return vec[0]*vec[1]
    
    transformer = callstack(get_pos, callstackfn(vec2), multiply_vec)
    ```

    Args:
        callback (Callable[..., Any]): The regular callback that you would like to transform.
        pass_kwargs (bool): Determines if this should pass along the kwargs given to the function.

    Returns:
        Callable[...,tuple]: The transformed callback.
    """
    def callstackfn(*args, **kwargs):
        result = callback(*args, **kwargs)
        return (result,) if not pass_kwargs else (result, kwargs)
    return callstackfn