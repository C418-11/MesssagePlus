# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"


from Lib.config.ConfigIO import IO
from abc import ABC


class Config(IO, ABC):
    _BASE_PATH = "./configs/Authentication/UserClient/"


__all__ = ("Config",)
