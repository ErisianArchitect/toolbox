"""A module for creating an IPython storyboard.

What's a storyboard? Use your imagination. I will give you the tools.
"""

from typing import *
from typing_extensions import *

from ipywidgets import *
from ..includer import Includer

__all__ = Includer()

def button(text: str, on_click: Callable[...,Any] = ..., display: bool = True, button_kwargs: dict = {}, *args, **kwargs):
    btn = Button(description=text, **button_kwargs)
    if on_click is ...:
        def decorator(target):
            if args or kwargs:
                def new_target(button):
                    return target(button, *args, **kwargs)
                btn.on_click(new_target)
            
            btn.on_click(target)
            return btn
        return decorator
    elif on_click is not None:
        btn.on_click(on_click)
    Button()

class DeletableCallback:
    """Does it ever make sense to have a callback that does something
    when it is deleted? Probably not. But it does for my use case."""
    __slots__ = ('callback', 'on_delete')
    def __init__(self, callback, on_delete):
        self.callback = callback
        self.on_delete = on_delete
    def __call__(self, *args, **kwargs):
        return self.callback(*args, **kwargs)
    def __del__(self):
        self.on_delete()

class ButtonBarButton(Button):
    def __init__(self, text: str, on_click: Callable[[Button],Any] = None, *args, **kwargs):
        super().__init__(description=text, *args, **kwargs)
        if on_click:
            super().on_click(on_click)

class ButtonBar(Output):
    __slots__ = ('buttons')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buttons = dict()
    
    def redisplay(self):
        self.clear_output(wait=True)
        
    
    def remove_button(self, text: str):
        self.buttons.pop(text, None)
    
    def button(self, text: str, *args, **kwargs):
        if (btn := self.buttons.get(text)):
            btn._click_handlers.callbacks.clear()
        else:
            btn = Button(description = text)
            self.buttons[text] = btn
        def inner(target):
            def click_target(button: Button):
                target(button = button, *args, **kwargs)
            def _remove():
                btn.on_click(click_target, remove=True)
            if hasattr(target, 'remove'):
                # TODO!
                ...
            target.remove = _remove
            btn.on_click(target, *args, **kwargs)
        return inner

branches = ButtonBar()

@branches.branch('Some text.')
def first_branch(self, button):
    