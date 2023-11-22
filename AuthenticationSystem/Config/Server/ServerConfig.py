# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import os.path
from typing import override

from Lib.config.ConfigIO import IO
from Lib.config.Progressbar import config_counter


@config_counter
class _Server(IO):
    def __init__(self):
        self.DEFAULT_FILES = {
            os.path.join(self.BASE_DIR, "config.json"): {
                "key": "settings",
                "data": {
                    "address": ("127.0.0.1", 32767),
                    "max_connections": 10,
                }
            }
        }
        super().__init__()

    @property
    def address(self) -> tuple[str, int]:
        return self.settings["address"]

    @property
    def max_connections(self) -> int:
        return self.settings["max_connections"]

    @property
    @override
    def BASE_DIR(self) -> str:
        return "./Server/"


Server = _Server()

__all__ = ("Server",)
