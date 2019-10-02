Limeade
=======

.. image:: https://github.com/CFSworks/limeade/blob/master/.github/readme/logo.png?raw=true
   :align: center

.. pypi section follows

::

    pip install limeade


Live module editing and development enhancement supporting hot reloading for
Python 3.4+.

|Travis| |Coverage| |PyPI| |PyPI Downloads|

Usage
-----

Equip your app with the ability to call ``limeade.refresh()`` on
command (e.g. via hotkey) and invoke after making edits to your source files!

.. image:: https://github.com/CFSworks/limeade/blob/master/.github/readme/demo.gif?raw=true

Features
--------

- **Speeds up development**: Don't restart your app, refresh your Python code!
- **Automatic**: Just call to ``limeade.refresh()``; Limeade does the rest!
- **Thorough**: Updates your classes/functions even if instantiated/referenced!
- **Object reuse**: Mutable objects are modified in-place; doesn't break **is**!
- **Good source of vitamin A**

Caveats
-------

Limeade is still experimental. I would be deeply appreciative if you could use
it and find ways in which it breaks!

The API is not yet stable. I will keep ``limeade.refresh()`` working, but
that is the extent of the public API for the time being.

Some things which it cannot (even theoretically) handle are:

- **Closures**: These aren't defined at module reload time; even so, it's unsafe
  to mutate code within instantiated closures. Closures will be updated the
  next time they are instantiated.
- **Changes in metaclass**: A class can be mutated if its type (metaclass) isn't
  changing, but Python does not permit changing the type of an existing class.
- **Threads**: This is not incompatible with threading, but note that threads
  may observe the program in an inconsistent state if they're running during a
  refresh operation. Make sure your threads are out of harm's way!
- **Changes to __init__ functions**: While the ``__init__`` change is handled
  normally just like any other function, a common pitfall to watch for is that
  the ``__init__`` function only runs when an instance is first created - as
  so, if any code added in the refresh depends on extra code added to
  ``__init__``, it may fail for classes which are already instantiated. An
  automatic update facility may be added in the future.

Some things which it may handle in the future:

- **Renaming functions/classes**: Currently, old and new definitions are matched
  via the qualified name. Heuristics can be used to match definitions when they
  are under different names, but this is not yet done.
- **Changes in __slots__ attribute**: New slot descriptors cannot be created;
  however, Limeade could invent its own descriptors for new slots and insert
  those. They wouldn't be as efficient but they would get the job done.
  Descriptors for deleted slots can be cached in case the slot is brought back
  in a future mutation.
- **Changes in base classes**: Initial experiments show that Python is much more
  picky about this one would expect.
- **Automatic rollback**: In case of refresh/mutate failure, it would be great
  to rollback everything to the state it was in before, so that the running app
  isn't left in a half-updated state.

Comparison
----------

The idea of merely reloading modules in Python is not a new one. What sets
Limeade apart is that it attempts to update extant classes (and their
instances) and functions. Here are some other approaches and how Limeade
differs:

- **importlib.reload()**: This simply re-executes the module in the same module
  namespace. The definitions of classes and functions are overwritten, but the
  classes and functions themselves are not updated. Because the module
  namespace is reused, a reload can be detected by first checking if certain
  names already exist. Note that Limeade uses the ``importlib.reload()`` call
  itself, so the same namespace reuse occurs at the module level.

- **IPython's autoreload extension**: This is a much more similar approach to
  Limeade from a theoretical standpoint. There are practical differences,
  however: The autoreload extension contains imports that pull in IPython,
  while Limeade is intended to function standalone. IPython is intended for
  interactive use, while Limeade may be useful in hotpatching daemons and other
  long-running standalone Python programs. Limeade also aspires to integrate
  well with custom loaders and user logic.

License
-------

All code licensed under 3-clause BSD.

Logo licensed under CC-BY-SA 4.0 with attribution to Elizabeth Reedy.

.. |Travis| image:: https://img.shields.io/travis/CFSworks/limeade
   :alt: Travis (.org)
.. |Coverage| image:: https://img.shields.io/codecov/c/github/CFSworks/limeade
   :alt: Codecov
.. |PyPI| image:: https://img.shields.io/pypi/v/limeade
   :alt: PyPI
.. |PyPI Downloads| image:: https://img.shields.io/pypi/dm/limeade
   :alt: PyPI - Downloads
