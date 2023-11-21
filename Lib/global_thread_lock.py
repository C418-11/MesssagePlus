# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import threading

OutputLock = threading.RLock()


class ProcessLock:
    Locks = {
        "Log".lower(): OutputLock,
    }

    def __init__(self, lock_name: str):
        """Lock names: log"""

        lock_name = lock_name.lower()

        lock = self.Locks.get(lock_name, None)
        if lock is None:
            # 如果找不到lock_name，则提示当前存在的lock_name
            existing_lock_names = ', '.join(list(self.Locks.keys()))
            raise ValueError(
                f"Invalid lock name: {lock_name}. Current existing lock names: {existing_lock_names}"
            )

        self.lock = lock

    def __call__(self, func):
        if isinstance(func, staticmethod):
            func = func.__func__
        if isinstance(func, classmethod):
            func = func.__func__

        def wrapper(*args, **kwargs):
            self.lock.acquire()
            try:
                return func(*args, **kwargs)
            finally:
                self.lock.release()

        return wrapper


__all__ = ("OutputLock", "ProcessLock")
