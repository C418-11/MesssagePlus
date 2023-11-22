# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import os.path
from typing import override

from Lib.config.ConfigIO import IO
from Lib.config.Progressbar import config_counter


@config_counter
class _Verification(IO):
    def __init__(self):
        self.DEFAULT_FILES = {
            os.path.join(self.BASE_DIR, "verification.json"): {
                "key": "settings",
                "data": {
                    "smtp_addr": ("smtp.163.com", 25),
                    "api_user": None,
                    "api_password": None
                }
            }
        }
        super().__init__()

    @property
    def smtpAddr(self) -> tuple[str, int]:
        return self.settings["smtp_addr"]

    @property
    def userEmail(self) -> str:
        return self.settings["api_user"].lower()

    @property
    def userPassword(self) -> str:
        return self.settings["api_password"]

    @property
    @override
    def BASE_DIR(self) -> str:
        return "./Server/API/"


Verification = _Verification()

__all__ = ("Verification", )
