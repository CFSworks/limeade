"""
"Mutating" is the fun part: Being able to reload modules is nice and all, but
what makes Limeade special is that it can redefine functions which are already
registered as callbacks and modify classes which already have some instances
running around.

Mutating takes advantage of the mutability of Python class types and function
objects in order to change their behavior without having to replace them. This
is fantastic because it doesn't even break `is`! If a function is currently
being called while mutation redefines its code, this is fine too. The
redefinition only affects subsequent calls to the function.

To mutate classes, we hook the `builtins.__build_class__` function, which is
invoked by the `class ...:` statement under the hood. Our hook finds the old
definition of the class and mutates it, then returns the mutated version.

To mutate functions, more finesse is required. If the function is part of a
class, the class mutator takes care of it. If the function is loose in the
namespace of the module, we resolve it when the refreshing code gives us a
before-and-after comparison to mutate.
"""

import builtins
import types

__all__ = ['ClassHook', 'mutate_functions', 'mutate_class']


def mutate_functions(old_ns, new_ns):
    """
    Given two namespaces (dicts), look for matching functions and mutate the
    old functions to match the new ones.

    The old function object is placed in new_ns, overwriting the new function.
    """

    # TODO: Identify by more than just __qualname__ in case of name change

    def func_filter(x):
        return isinstance(x, types.FunctionType)

    old_funcs = {}
    for f in filter(func_filter, old_ns.values()):
        old_funcs[f.__qualname__] = f

    for f in tuple(filter(func_filter, new_ns.values())):
        old_f = old_funcs.get(f.__qualname__)

        if old_f is None:
            # There is no old function; let the new one take precedence
            continue

        if f.__closure__ or old_f.__closure__:
            # Not safe to do this to closures
            continue

        old_f.__code__ = f.__code__
        new_ns[f.__qualname__] = old_f


def mutate_class(cls, new_ns, new_bases):
    """
    Mutate a given class (`cls`) with the new namespace and bases.
    """

    # TODO: Bases not handled yet.

    mutate_functions(cls.__dict__, new_ns)

    for k, v in new_ns.items():
        setattr(cls, k, v)


class ClassHook:
    """
    This is a context manager (use it with `with`) that hooks the
    `builtins.__build_class__` function to cause classes to be mutated rather
    than redefined.

    It needs a list/tuple of old classes to consider for mutation. The mutation
    system picks the most similar class to mutate, falling back to redefinition
    if none are sufficiently similar.
    """

    __old_build_class = None
    __active = []

    def __init__(self, old_classes):
        self.old_classes = old_classes

    def __mutate(self, ns, bases):
        """
        Attempt to find a class to mutate and mutate it.

        Returns the original class, or None if nothing suitable was found.
        """

        # TODO: Identify by more than just __qualname__ in case of name change
        for cls in self.old_classes:
            if cls.__qualname__ == ns.get('__qualname__'):
                mutate_class(cls, ns, bases)

                return cls

    # Context manager stuff
    def __enter__(self):
        if not self.__active:
            self.__hook()

        self.__active.insert(0, self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__active.remove(self)

        if not self.__active:
            self.__unhook()

    # __build_class__ hook below

    @classmethod
    def __try_mutate(cls, func, name, bases, kwargs):
        if func.__closure__:
            # Not safe to mutate closure-classes
            return

        metaclass = kwargs.get('metaclass')
        if metaclass is not None or (bases and type(bases[0]) is not type):
            # TODO: Support metaclasses
            return
        else:
            metaclass = type

        ns = metaclass.__prepare__(name, bases, **kwargs)

        exec(func.__code__, func.__globals__, ns)

        for instance in cls.__active:
            obj = instance.__mutate(ns, bases)
            if obj:
                return obj

    @classmethod
    def __build_class(cls, func, name, *bases, **kwargs):
        obj = cls.__try_mutate(func, name, bases, kwargs)
        if obj:
            return obj

        return cls.__old_build_class(func, name, *bases, **kwargs)

    @classmethod
    def __hook(cls):
        assert cls.__old_build_class is None

        builtins.__build_class__, cls.__old_build_class = \
            (cls.__build_class, builtins.__build_class__)

    @classmethod
    def __unhook(cls):
        assert builtins.__build_class__ == cls.__build_class

        builtins.__build_class__, cls.__old_build_class = \
            (cls.__old_build_class, None)
