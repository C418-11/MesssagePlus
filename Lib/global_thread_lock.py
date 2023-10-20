# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"


import threading


OutputLock = threading.RLock()


class ProcessLock:
    def __init__(self, lock_name: str):
        """Lock names: log"""
        self.lock_name = lock_name.lower()
        self.locks = {
            "Log".lower(): OutputLock,
        }

    def __call__(self, func):
        if isinstance(func, staticmethod):
            # 如果被装饰的对象是静态方法，则需要调用__func__来获取方法对象
            func = func.__func__
        if isinstance(func, classmethod):
            # 如果被装饰的对象是类方法，则需要调用__func__来获取方法对象
            func = func.__func__

        def wrapper(*args, **kwargs):
            lock = self.locks.get(self.lock_name, None)
            if lock is None:
                # 如果找不到lock_name，则提示当前存在的lock_name
                existing_lock_names = ', '.join(list(self.locks.keys()))
                raise ValueError(
                    f"Invalid lock name: {self.lock_name}. Current existing lock names: {existing_lock_names}"
                )

            lock.acquire()
            try:
                return func(*args, **kwargs)
            finally:
                lock.release()
        return wrapper


__all__ = ("OutputLock", "ProcessLock")
