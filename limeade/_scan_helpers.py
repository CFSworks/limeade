"""
This file implements some helper functions for allowing Limeade to scan modules
loaded with Python's builtin loaders.
"""

import importlib

from .scanning import register_helper

__all__ = []


@register_helper(importlib.machinery.SourceFileLoader)
def _source_file_helper(module):
    """
    Determine if a module, loaded from a source file via SourceFileLoader, has
    had its file modified since loading.
    """

    assert type(module.__loader__) is importlib.machinery.SourceFileLoader
    loader = module.__loader__

    try:
        path = module.__file__
    except AttributeError:
        return False

    try:
        stat = loader.path_stats(path)
    except OSError:
        return False

    if getattr(module, '__cached__', None):
        # There may be a .pyc - see if it's older than the .py?
        try:
            pyc_stat = loader.path_stats(module.__cached__)
        except OSError:
            pass
        else:
            if stat.get('mtime', 0) > pyc_stat.get('mtime', 0):
                return True

    # We can't conclude it's outdated; maybe more checks will come soon
    return False
