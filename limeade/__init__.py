"""
Limeade is a live module editing-and-development enhancement for Python 3.4+.

This package implements what is essentially an ultra-aggressive version of
`importlib.reload()` - here called `limeade.refresh()` - which:
    1. Scans for outdated modules so you don't have to specify them yourself.
    2. Reloads them all in batch, allowing cross-module dependencies to work
       themselves out naturally.
    3. Takes advantage of the intrinsic mutability of class types and functions
       in order to make your edits take effect immediately.
"""

# Make sure these are registered
from . import _scan_helpers

from .refreshing import refresh
from .scanning import scan

__all__ = ['refresh', 'scan']

__author__ = 'Sam Edwards <CFSworks@gmail.com>'
__version__ = '0.1.0'
