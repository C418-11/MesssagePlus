# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"


from Lib.config.ConfigIO import IO
from Lib.config.Mixin.LogMixin import LogMixin


class Server(IO, LogMixin):

    def __init__(self):
        LogMixin.__init__(self)
        IO.__init__(self)

    @property
    def BASE_DIR(self):
        return "./Web/Server/"


ServerType = Server()

__all__ = ("ServerType",)
