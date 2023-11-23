# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

from typing import override

from ..Base import Config
from Lib.config.Mixin.LogMixin import LogMixin
from Lib.config.Progressbar import config_counter


@config_counter
class _Server(Config, LogMixin):

    def __init__(self):
        LogMixin.__init__(self)
        Config.__init__(self)

    @property
    @override
    def BASE_DIR(self):
        return "./Web/"


ServerType = _Server()

__all__ = ("ServerType",)
