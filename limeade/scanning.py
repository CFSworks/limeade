"""
In Limeade, "scanning" refers to the process of discovering modules that need
to be refreshed; that is, modules which have changed since their last (re)load.

By default, `sys.modules.values()` is scanned. A separate module list may be
provided instead.

For each module to be considered, Limeade checks if its loader has a
`check_newer(module)` method; if this function returns True, Limeade will add
the module to the results of the scan. However, in the majority of cases, the
module loader won't be Limeade-aware and won't implement this method. For the
typical Python built-in loaders, Limeade implements some helper functions for
answering this question without the assistance of the loader.
"""

import sys

__all__ = ['scan']


def scan(modules=None):
    """
    Scan all modules in `modules` (or in `sys.modules`) and return an iterable
    of modules believed to be refreshable.
    """

    if modules is None:
        modules = sys.modules.values()

    return filter(scan_one, modules)


def scan_one(module):
    """
    Scan the single `module` to see if it can be refreshed.
    """

    try:
        loader = module.__loader__
    except AttributeError:
        # Module lacks a loader; can't refresh it.
        return False

    if hasattr(loader, 'check_newer'):
        return loader.check_newer(module)

    # The loader won't cooperate with us. Do we know its type?
    helper = _helpers.get(type(loader))
    if helper:
        return helper(module)

    # No dice
    return False


# These are helper functions for various types of loader
_helpers = {}


def register_helper(loader_type):
    """
    Decorate a function to serve as a scan helper for loaders of a type.
    """

    def decorator(func):
        _helpers[loader_type] = func
        return func

    return decorator
