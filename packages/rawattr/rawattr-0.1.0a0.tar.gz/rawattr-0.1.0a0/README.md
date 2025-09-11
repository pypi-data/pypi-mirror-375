Low-level Python attribute access utilities that bypass the descriptor protocol.

## What is it?

`rawattr` provides utilities for exploring, getting, setting, and deleting attributes *exactly as they physically
appear* in the `__dict__` of Python objects and their classes - without triggering properties, methods, or any
descriptor logic. This makes it easy to introspect and manipulate attributes "raw", without Python's usual attribute
access rules.

- **No descriptor protocol:** No property, method binding, or magic getters/setters—just pure dict lookups.
- **Access class and instance dicts:** Traverse instance, then all classes in MRO (method resolution order).
- **Manipulate attributes on both instance and class-level, or just the instance.**

## Why?

Sometimes you want to see *what is actually* in the underlying attribute dicts, or manipulate attributes as stored, not
as interpreted by Python's attribute machinery.

- See the *actual* keys and values present (including methods and slot descriptors).
- Set or delete attributes without triggering custom logic.
- Useful for introspection tools, dynamic manipulation, advanced class/instance hacking, and more.

## Installation

```bash
pip install rawattr
```

## Usage

```python
# coding=utf-8
from rawattr import raw_getattr, raw_setattr, raw_hasattr, raw_delattr


class S(object):
    __slots__ = ('s',)


raw_getattr(S, 's')  # <member 's' of 'S' objects>
raw_getattr(S(), 's')  # <member 's' of 'S' objects>


class A(object):
    x = 42


class B(A):
    pass


b = B()
b.y = 100

raw_hasattr(b, 'x')  # True: sees A.x on the class
raw_hasattr(b, 'y')  # True

raw_getattr(b, 'x')  # 42: unbound, as stored in class __dict__
raw_getattr(b, 'y')  # 100

raw_setattr(b, 'y', 1000, add_to_instance=True)
raw_getattr(b, 'y')  # 1000

raw_delattr(b, 'y')  # Deletes b.y
raw_hasattr(b, 'y')  # False

# AttributeError: 'B' object has no attribute 'y'
try:
    raw_getattr(b, 'y')
except AttributeError:
    pass

# TypeError: 'dictproxy' object does not support item assignment (Python 2)
# TypeError: 'mappingproxy' object does not support item assignment (Python 3)
try:
    raw_setattr(b, 'x', 77, add_to_instance=False)
except TypeError:
    pass

# TypeError: 'dictproxy' object does not support item deletion (Python 2)
# TypeError: 'mappingproxy' object does not support item deletion (Python 3)
try:
    raw_delattr(b, 'x')
except TypeError:
    pass
```

## API Reference

### `yield_dicts_and_owners(obj)`

Yield pairs of `(dict, owner)` for the instance (`__dict__, obj`) and each class in its MRO (`class __dict__, class`),
if a `__dict__` exists.

### `raw_hasattr(obj, attr)`

True if `attr` is present as a key in either the instance or any of its class `__dict__`s (no descriptors).

### `raw_getattr(obj, attr, default=NO_DEFAULT)`

Fetches the raw value, or raises (or returns `default`), without triggering descriptors or attribute methods.

### `raw_setattr(obj, attr, value, add_to_instance=True)`

Sets an attribute—by default, adds to the instance's `__dict__`; if `add_to_instance=False`, only updates the attribute
in the first (instance/class) `__dict__` where it is present in-place.

### `raw_delattr(obj, attr)`

Deletes the key from the first (instance/class) `__dict__` where it is present.

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).