"""
"Refreshing" is a supreme version of reloading. In particular, it allows
special hooks to be applied as the reloading happens, and it works well with
batches of modules.

The latter point is important: suppose there are two modules, x and y, and x
contains a `from y import ...`, then it's important to make sure x gets the
reloaded version of y. A naive `importlib.reload()` loop will not suffice here.

To that end, we leverage the existing Python import machinery to resolve these
dependencies: simply grab the batch of modules to be refreshed off of
`sys.modules` and reimport them one at a time. The actual imports will occur in
the order they're necessary, and we can use a special import hook to turn these
into a reload instead of a reimport.
"""

import builtins
import sys
import importlib

from .scanning import scan
from .mutating import ClassHook, mutate_functions

__all__ = ['refresh']


def refresh(batch=None, *, mutate=True):
    """
    Refresh `batch` (or None to scan) of modules.
    """

    if batch is None:
        batch = scan()

    modules = {mod.__name__: mod for mod in batch}

    # Sanity-check __name__
    assert all(sys.modules[name] is mod for name, mod in modules.items())

    # Pull all modules down to force Python to refind them
    for name in modules:
        del sys.modules[name]

    with ImportHook(modules, mutate):
        for name in modules:
            __import__(name)


class ImportHook:
    """
    This hooks the import machinery to reload modules from a dict. It serves as
    a context manager, so `with ImportHook(...):` works.
    """

    def __init__(self, modules, mutate):
        self.modules = dict(modules)

        self.mutate = mutate

    def __import_hook(self, fullname, *args):
        module = self.modules.get(fullname)
        if module is None:
            # This isn't a module that interests us
            return self._old_import(fullname, *args)

        sys.modules[module.__name__] = module
        del self.modules[module.__name__]

        if self.mutate:
            old_ns = dict(module.__dict__)

            classes = [x for x in old_ns.values()
                       if type(x) is type
                       and getattr(x, '__module__', None) == module.__name__]

            with ClassHook(classes):
                importlib.reload(module)

            mutate_functions(old_ns, module.__dict__)

        else:
            importlib.reload(module)

        return module

    # Context manager
    def __enter__(self):
        self._old_import, builtins.__import__ = \
            (builtins.__import__, self.__import_hook)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._old_import, builtins.__import__ = None, self._old_import
