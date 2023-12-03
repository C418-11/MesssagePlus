# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import os

from .Base import Config
from Lib.config.Progressbar import config_counter


@config_counter
class _Userdata(Config):
    def __init__(self):
        self.DEFAULT_FILES = {
            os.path.join(self.BASE_DIR, "userdata.json"): {
                "key": "userdata",
                "data": {
                    "uuid": None,
                    "uuid_base": 36,
                    "login_key": None,
                    "login_key_timeout": 0,
                    "email": None,
                    "password": None
                }
            }
        }

        super().__init__()

    @property
    def uuid(self) -> str:
        return self.userdata["uuid"]

    @property
    def uuid_base(self) -> int:
        return self.userdata["uuid_base"]

    @property
    def login_key(self) -> dict:
        return self.userdata["login_key"]

    @property
    def login_key_timeout(self) -> str:
        return self.userdata["login_key_timeout"]

    @property
    def email(self) -> str:
        return self.userdata["email"]

    @property
    def password(self) -> str:
        return self.userdata["password"]

    @property
    def BASE_DIR(self) -> str:
        return "./userdata/"


UserData = _Userdata()

__all__ = ("UserData",)
