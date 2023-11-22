import operator
from typing import *
import builtins
from functools import partial, wraps
from .modutil import Includer

__all__ = Includer()

@__all__
def first(seq: Iterable, filter=None) -> Any | None:
    for value in seq:
        if not callable(filter) or filter(value):
            return value
    return None

@__all__
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

@__all__
def last(seq: Sequence) -> Any | None:
    try:
        return seq[-1]
    except IndexError:
        return None
    except TypeError:
        for result in seq: pass
        return result

@__all__
def passalong(value):
    """Returns the value that was passed to it.
    
    This is useful for situations where a map function is required, but no mapping is needed.
    """
    return value

@__all__
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

@__all__
def returns(*values)->Callable[..., Any]:
    def returns(*args, **kwargs):
        return values
    return returns

@__all__
def returnTrue(*args, **kwargs): return True

@__all__
def returnFalse(*args, **kwargs): return False

@__all__
def returnNone(*args, **kwargs): return None

@__all__
def ne(value):
    """Creates a function that checks if value is not equal to parameter."""
    return partial(operator.ne, value)

@__all__
def eq(value):
    """Creates a function that checks if value is equal to parameter."""
    return partial(operator.eq, value)

@__all__
def lt(value):
    """Creates a function that checks if value is less than parameter."""
    return partial(operator.lt, value)

@__all__
def le(value):
    """Creates a function that checks if value is less than or equal to parameter."""
    return partial(operator.le, value)

@__all__
def gt(value):
    """Creates a function that checks if value is greater than parameter."""
    return partial(operator.gt, value)

@__all__
def ge(value):
    """Creates a function that checks if value is greater than or equal to parameter."""
    return partial(operator.ge, value)

@__all__
def is_(value):
    """Creates a function that checks if value is parameter."""
    return partial(operator.is_, value)

@__all__
def is_not(value):
    """Creates a function that checks if value is not parameter."""
    return partial(operator.is_not, value)

@__all__
def not_none(value):
    return value is not None

@__all__
def is_none(value):
    return value is None

@__all__
class present:
    """Creates a function that checks if a value is present in collection."""
    __slots__ = ('collection',)

    def __init__(self, collection: Container):
        self.collection = collection
    
    def __call__(self, value)->bool:
        return value in self.collection

@__all__
class absent:
    """Creates a function that checks if a value is absent from collection."""
    __slots__ = ('collection',)

    def __init__(self, collection: Container):
        self.collection = collection
    
    def __call__(self, value)->bool:
        return value not in self.collection

@__all__
def invertdict(d : dict)->dict:
    """Returns a version of the passed dictionary that has the keys and values swapped."""
    return {v : k for k, v in d.items()}

@__all__
def prefixargs(fn: Callable[...,Any], *prefix_args, **prefix_kwargs):
    """Creates a function that prefixes the supplied arguments
    to the arguments passed to the callback."""
    @wraps(fn)
    def wrapped(*args, **kwargs):
        return fn(*(*prefix_args, *args), **{**prefix_kwargs, **kwargs})
    return wrapped

@__all__
def appendargs(fn: Callable[..., Any], *post_args, **post_kwargs):
    """Creates function that appends the supplied arguments
    to the arguments passed to the callback."""
    @wraps(fn)
    def wrapped(*args, **kwargs):
        return fn(*(*args, *post_args), **{**kwargs, **post_kwargs})
    return wrapped

@__all__
def callwith(*args, **kwargs):
    """Creates a function that accepts a function as its argument
    and calls that function with the supplied args and kwargs."""
    def callwith(callback):
        return callback(*args, **kwargs)
    return callwith

@__all__
def matchall(*predicates):
    def matchall(*args, **kwargs)->bool:
        return all(map(callwith(*args, **kwargs), predicates))
    return matchall

@__all__
def matchany(*predicates):
    def matchany(*args, **kwargs)->bool:
        return any(map(callwith(*args, **kwargs), predicates))
    return matchany

@overload
def strjoin(seq: Sequence[str])->str:...
@overload
def strjoin(seq: Sequence[str], joiner: str = '')->str:...
@__all__
def strjoin(seq: Sequence[str], joiner: str = '')->str:
    return joiner.join(seq)

@__all__
def surroundedwith(start: str, end: str, __start: SupportsIndex = None, __end: SupportsIndex = None)->Callable[[str],bool]:
    return matchall(startswith(start, __start, __end), endswith(end, __start, __end))

@__all__
def startswith(start: str, __start: SupportsIndex = None, __end: SupportsIndex = None)->Callable[[str],bool]:
    # def startswith(s: str)->bool:
    #     return s.startswith(start, __start, __end)
    # return startswith
    return appendargs(str.startswith, start, __start, __end)

@__all__
def endswith(end: str, __start: SupportsIndex = None, __end: SupportsIndex = None)->Callable[[str], bool]:
    # def endswith(s: str)->bool:
    #     return s.endswith(end, __start, __end)
    # return endswith
    return appendargs(str.endswith, end, __start, __end)

@__all__
def do(action: Callable, seq: Iterable, unpack: bool = True):
    """Do `action(item)` for every `item` in `seq`."""
    for item in seq:
        if isinstance(item, tuple) and unpack:
            action(*item)
        else:
            action(item)

@__all__
def filterfalse(seq: Iterable):
    """Filter elements that evaluate to True. Remove all elements that evaluate to False."""
    yield from filter(bool, seq)

@__all__
def filternone(seq: Iterable):
    """Filter out elements that are None."""
    yield from filter(not_none, seq)

@overload
def count(seq: Iterable)->int:...
@overload
def count(seq: Iterable, filter: Callable)->int:...
@__all__
def count(seq: Iterable, filter=None)->int:
    if callable(filter):
        return sum((1 for _ in builtins.filter(filter, seq)))
    else:
        if hasattr(seq, '__len__'):
            return len(seq)
        else:
            return sum((1 for _ in seq))

@__all__
def istype(type: Type):
    def istype(value)->bool:
        return builtins.type(value) == type
    return istype

@__all__
def instanceof(type: Type):
    def instanceof(value)->bool:
        return isinstance(value, type)
    return instanceof

@__all__
def filtertype(_type: Type, seq: Iterable):
    yield from (value for value in seq if isinstance(value, _type))

@overload
def revrange(end: SupportsIndex,/)->range:...
@overload
def revrange(start: SupportsIndex, end: SupportsIndex,/)->range:...
@overload
def revrange(start: SupportsIndex, end: SupportsIndex, step: SupportsIndex,/)->range:...
@__all__
def revrange(start: SupportsIndex, end: SupportsIndex = ..., step: SupportsIndex = ...)->range:
    return range(start, end-1, -step)

@__all__
def yieldinstead(iterable: Iterable[Any], value: Any = None):
    yield from (value for _ in iterable)

@__all__
def yieldforever(value: Any = None):
    while True:
        yield value

@__all__
def yieldcall(callback: Callable[..., Any], *args, **kwargs):
    while True:
        yield callback(*args, **kwargs)

@__all__
def next_or(it, default: Any = None):
    try:
        return next(it)
    except StopIteration:
        return default

@__all__
def repeatforever(callback: Callable[..., Any], *args, **kwargs):
    for _ in yieldcall(callback, *args, **kwargs):...

@__all__
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
@__all__
def callstack(iterable_or_callable, *stack)->Callable[[Any], Any]:
    """Calls each function along the callstack with the result of the previous.

    This function is a bit complicated, so it would be easier to read the code, but I'll
    give a couple examples. First, a simple one, then a complicated one.
    
    ```
    def vec2(x, y):
        return float(x), float(y)
    def get_pos():
        return 3, 14
    def multiply_vec(x, y):
        return x*y
    
    transformer = callstack(get_pos, vec2, multiply_vec)
    print(transformer())
    ```
    """
    if callable(iterable_or_callable):
        stack = (iterable_or_callable, *stack)
    elif isinstance(iterable_or_callable, Iterable) and not stack:
        stack = iterable_or_callable
    else:
        raise TypeError("Supplied incorrect values or something, idk.")
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

@__all__
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

@__all__
def call_or(maybe_fn, *args, **kwargs):
    """If maybe_fn is a callable, call it with the given args and return the result, otherwise return maybe_fn."""
    if callable(maybe_fn):
        return maybe_fn(*args, **kwargs)
    return maybe_fn

R = TypeVar('R')

@__all__
@overload
def conditional(predicate: Callable[...,bool]):
    """A decorator for a function that is only callable if predicate is `True`.

    Args:
        predicate (Callable[...,bool]): The conditional predicate.
    """
@overload
def conditional(predicate: Callable[...,bool], takes_args: bool = True):
    """A decorator for a function that is only callable if predicate is `True`.

    Args:
        predicate (Callable[...,bool]): The conditional predicate. (Will take the arguments)
        takes_args (bool, optional): Determines if the arguments are passed to the predicate. Defaults to True.
    """
@overload
def conditional(predicate: Callable[...,bool], target: Callable[...,R])->Callable[..., R]:
    """Create a conditional function for the target callable.

    Args:
        predicate (Callable[...,bool]): The conditional predicate. (Will take the arguments)
        target (Callable[...,Any]): The target callable.
    """
@overload
def conditional(predicate: Callable[...,bool], target: Callable[...,R], takes_args: bool = True)->Callable[..., R]:...
def conditional(predicate: Callable[...,bool], first = True, takes_args = True):
    """Creates a function that is only called if a predicate is met."""
    match (first, takes_args):
        case (bool(takes_args), _):
            def decorator(target):
                @wraps(target)
                def conditional(*args, **kwargs):
                    if takes_args:
                        active = predicate(*args, **kwargs)
                    else:
                        active = predicate()
                    if active:
                        return target(*args, **kwargs)
                return conditional
            return decorator
        case (target, bool(takes_args)) if callable(target):
            @wraps(target)
            def conditional(*args, **kwargs):
                if takes_args:
                    active = predicate(*args, **kwargs)
                else:
                    active = predicate()
                if active:
                    return target(*args, **kwargs)
            return conditional
        case _:
            raise ValueError('Invalid arguments.')

# @__all__
# def replace_decorator(name_or_obj: str | object, name: str = None):
#     match (name_or_obj, name):
#         case (str(name), None):
#             if not name.isidentifier():
#                 raise NameError(f'Name was not a valid identifier: {name!r}')
#             def _wrapped(self, target):
#                 setattr(self, name, target)
#             _wrapped.__name__ = name
#             return _wrapped
#         case (object(), str(name)):
#             if not name.isidentifier():
#                 raise NameError(f'Name was not a valid identifier: {name!r}')
#             return partial(setattr, name_or_obj, name)
#         case _:
#             raise Exception("TODO!")