"""IPython widget stuff.
"""

from ipywidgets import *
from IPython.core.display_functions import display
import ipywidgets

from typing import *
from typing_extensions import *

from collections import UserDict
from ..includer import Includer

__all__ = (includer := Includer())

_auto_display: bool = False

_widget_factory = dict(
    button = lambda *args, **kwargs: button(*args, display=None, **kwargs),
)

class Factory(UserDict):
    """This class is meant to be used in cases where you want a dictionary of factories (callables that return Non-None values)."""
    __getattr__ = UserDict.__getitem__
    def register(self, name_or_callable: str | Callable[..., Any], callback: Callable[..., Any] = None):
        match (name_or_callable, callback):
            case (target, None) if callable(target) and hasattr(target, '__name__'):
                self.data[target.__name__] = target
                return target
            case (str(name), None) if name.isidentifier():
                def _inner(target):
                    self.data[name] = target
                    return target
                return _inner
            case (str(name), callback) if name.isidentifier() and callable(callback):
                self.data[name] = callback
            case (arg0, arg1):
                raise Exception("You used this function wrong. I'm not sure in what way and I'm too lazy to think about the ways you could have done it wrong, so this is the error you get.")

_widget_factory = Factory()

@_widget_factory.register
class output(Output):
    pass

@_widget_factory.register
class button(Button):
    """A special button class that can be used as a decorator to 
    register callbacks."""
    def __init__(self, text: str = ..., on_click: Callable[[Button], Any] = ..., display = display, **kwargs):
        if text is not ...:
            kwargs['description'] = str(text)
        super().__init__(**kwargs)
        if on_click is not ...:
            self.on_click(on_click)
        if _auto_display and callable(display):
            display(self)

    def __call__(self, *args, **kwargs):
        """This does not invoke the button!
        Instead, this allows you to use the button as a decorator to register callbacks.
        """
        if len(args) == 1 and not kwargs:
            target = args[0]
            self.on_click(target)
            return target
        else:
            def decorator(target):
                def click_fn(button):
                    return target(button, *args, **kwargs)
                self.on_click(click_fn)
                return target
            return decorator

class hbox(HBox):
    def button(self, text: str, on_click: Callable[[Button], Any] = ..., **kwargs):
        btn = button(text, on_click, display=None, **kwargs)
        new_children = (*self.children, btn)
        return btn
    def __getattr__(self, name):
        if (factory := _widget_factory.get(name, None)):
            return factory
        else:
            raise AttributeError()