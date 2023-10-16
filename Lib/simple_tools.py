# -*- coding: utf-8 -*-
import weakref
from threading import Thread


def Disable(class_func):
    def wrapper(*_, **__):
        def func():
            path = class_func.__qualname__.split('.')
            raise AttributeError(f"AttributeError: type object '{path[-2]}' has no attribute '{path[-1]}' "
                                 f"(Disabled Class Func)")

        return func()

    return wrapper


class ThreadPool:
    def __init__(self):
        self._pool = weakref.WeakValueDictionary()

    def add(self, thread: Thread, uuid=None):
        """
         If uuid is None it will be hash(thread)
         """
        if uuid is None:
            uuid = hash(thread)
        self._pool[uuid] = thread

    def remove(self, uuid):
        del self._pool[uuid]


__all__ = ("Disable", "ThreadPool")
