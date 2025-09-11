# coding=utf-8
# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
NO_DEFAULT = object()


def yield_dicts_and_owners(obj):
    """
    Yield (mapping, owner) pairs for attribute resolution, bypassing the descriptor protocol.

    Yields:
        (dict, owner): For the instance (if it has a __dict__) and then for each class in the
        method resolution order (__mro__), if the class has a __dict__.

    Parameters:
        obj: The object whose attribute resolution order to traverse.

    Notes:
        - The instance's __dict__ (if present) is yielded first, then
          each class's __dict__ and the class itself.
        - If an object or class does not have a __dict__, it is skipped.
    """
    if hasattr(obj, '__dict__'):
        yield obj.__dict__, obj

    cls = type(obj)
    for base in cls.__mro__:
        if hasattr(base, '__dict__'):
            yield base.__dict__, base


def raw_hasattr(obj, attr):
    """
    Determine if an attribute name exists in an instance or class __dict__, bypassing descriptors.

    Args:
        obj: The object to check.
        attr (str): The name of the attribute.

    Returns:
        bool: True if the attribute exists as a key in the instance or class __dict__, False otherwise.

    Notes:
        - Ignores the descriptor protocol. Only literal presence as a key matters.
    """
    for __dict__, _ in yield_dicts_and_owners(obj):
        if attr in __dict__:
            return True
    else:
        return False


def raw_getattr(obj, attr, default=NO_DEFAULT):
    """
    Get an attribute's raw value from instance or class __dict__, ignoring descriptors.

    Args:
        obj: The object to examine.
        attr (str): The name of the attribute.
        default: (optional) Value to return if not found. If not provided, raises AttributeError.

    Returns:
        The value directly from the instance or class dict (not resolving descriptors).

    Notes:
        - For slots, returns the member descriptor object.
        - For methods or properties, returns unbound function or descriptor, not the resolved value.
    """
    for __dict__, _ in yield_dicts_and_owners(obj):
        if attr in __dict__:
            return __dict__[attr]
    else:
        if default is NO_DEFAULT:
            raise AttributeError('%r object has no attribute %r' % (type(obj).__name__, attr))
        else:
            return default


def raw_delattr(obj, attr):
    """
    Delete a named attribute key from instance or class __dict__, ignoring descriptors.

    Args:
        obj: The object to mutate.
        attr (str): The attribute name.

    Notes:
        - Physically deletes the key from the first __dict__ in resolution order where it is found.
    """
    for __dict__, _ in yield_dicts_and_owners(obj):
        if attr in __dict__:
            del __dict__[attr]
            return
    else:
        raise AttributeError('%r object has no attribute %r' % (type(obj).__name__, attr))


def raw_setattr(obj, attr, value, add_to_instance=True):
    """
    Set an attribute in an instance's or class' __dict__, ignoring descriptors.

    Args:
        obj: The object to mutate.
        attr (str): The attribute name.
        value: The new value to assign.
        add_to_instance (bool): If True (default), set directly on instance __dict__.
                                If False, only set in the first dict where the key is
                                already present (such as on the class).
    """
    if add_to_instance:
        obj.__dict__[attr] = value
    else:
        for __dict__, _ in yield_dicts_and_owners(obj):
            if attr in __dict__:
                __dict__[attr] = value
                return
        else:
            raise AttributeError('%r object has no attribute %r' % (type(obj).__name__, attr))
