# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import functools
from abc import ABC


class MixinClassNotInitError(Exception):
    def __str__(self):
        return "Called mixin cls 's func before it init"


def MixinFlagChecker(flag: str, cls_func):
    @functools.wraps(cls_func)
    def wrapper(self, *args, **kwargs):
        try:
            object.__getattribute__(self, flag)
        except AttributeError:
            pass
        else:
            if object.__getattribute__(self, flag) is True:
                return cls_func(self, *args, **kwargs)
        raise MixinClassNotInitError

    return wrapper


class ConfigIoLike(ABC):
    DEFAULT_FILES: dict
    BASE_DIR: str
    _ENCODING: str
    _READ_SIZE: int
    _NEW_LINE: str
    _INDENT: int
    _BASE_PATH: str


__all__ = ("MixinClassNotInitError", "MixinFlagChecker", "ConfigIoLike")
