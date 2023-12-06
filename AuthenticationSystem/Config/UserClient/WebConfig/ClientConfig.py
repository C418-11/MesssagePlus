# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import os.path
from typing import override

from Lib.config.Mixin.LogMixin import LogMixin
from Lib.config.Progressbar import config_counter
from ..Base import Config


@config_counter
class _Client(Config, LogMixin):
    def __init__(self):
        self.DEFAULT_FILES = {
            os.path.join(self.BASE_DIR, "AuthenticationServer.json"): {
                "key": "server",
                "data": {
                    "address": ("127.0.0.1", 32767),
                }
            },
            os.path.join(self.BASE_DIR, "login.json"): {
                "key": "login",
                "data": {
                    "login_timeout": 10
                }
            }
        }
        LogMixin.__init__(self)
        Config.__init__(self)

    @property
    def address(self) -> tuple[str, int]:
        return self.server["address"]

    @property
    def login_timeout(self) -> int:
        return self.login["login_timeout"]

    @property
    @override
    def BASE_DIR(self) -> str:
        return "./WebConfig/"


Client = _Client()

__all__ = ("Client",)
