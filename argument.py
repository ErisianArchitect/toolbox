"""I got annoyed having to write match statements and isinstance everywhere.

This module is meant to allow you to create generic functions.

Example of what I want, but may change after implementation:
```python

@generic
def gopher():...

@gopher.overload
def _(a: int, b: int, c: Optional[Any] = None):
    print(f'int int: {a}, {b}, {c or "<none>"}')

@gopher.overload
def _(a: Tuple[int, int], c: Optional[Any] = None):
    print(f'(int, int): {a}, {c or "<none>"}')

gopher(1, 2)
gopher(3, 4, 'Test')
gopher((5, 6))
gopher((7, 8), 'Fnord')
```
"""