# -*- coding: utf-8 -*-

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import os
import sys
from typing import Union, TextIO

from Lib.config.ConfigIO import IO
from Lib.config.Mixin.LogMixin import LogMixin
from Lib.database import logging as db_logging


class _DataBaseInjection:

    def __init__(self, parent: IO):
        super().__init__()
        self.parent = parent
        self.parent.DEFAULT_FILES.update({
            os.path.join(self.parent.BASE_DIR, "database.json"): {
                "key": "injection_login_database",
                "data": {
                    "server_name": "LoginDataBaseServer",
                    "addr": ("127.0.0.1", 11451),
                    "enable_builtin_db": True,
                    "log_file": "stdout",
                    "input_file": "stdin",
                    "disable_log": False,
                    "log_level": db_logging.NOTSET.name,
                    "debug_mode": True,
                    "listen": 10,
                    "username": "default",
                    "password": "default",
                    "path": {
                        "database_name": ".",
                        "store_name": "LoginData"
                    }
                }
            }
        })

        self._files_is_init = False

    @property
    def data(self) -> dict:
        return self.parent.injection_login_database

    server_name: str
    addr: tuple[str, int]
    enable_builtin_db: bool
    log_level: Union[int, str]
    debug_mode: bool
    listen: int
    disable_log: bool

    username: str
    password: str

    def _init_files(self):
        std_o = {"stdout": sys.stdout, "stderr": sys.stderr, "stdin": sys.stdin}

        for item in ["log_file", "input_file"]:
            if self.data[item] in std_o:
                self.data[item] = std_o[self.data[item]]

            else:
                self.data[item] = open(
                    self.data[item], mode='a', encoding=self._ENCODING, newline=self._NEW_LINE
                )

    @property
    def log_file(self) -> TextIO:
        if not self._files_is_init:
            self._init_files()
        return self.data["log_file"]

    @property
    def input_file(self) -> TextIO:
        if not self._files_is_init:
            self._init_files()
        return self.data["input_file"]

    @property
    def db_name(self) -> str:
        return self.data["path"]["database_name"]

    @property
    def store_name(self) -> str:
        return self.data["path"]["store_name"]

    def __getattribute__(self, item):
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            try:
                return self.data[item]
            except KeyError:
                pass
            raise


class _Login(IO, LogMixin):
    def __init__(self):
        self.DEFAULT_FILES = {
            os.path.join(self.BASE_DIR, "settings.json"): {
                "key": "settings",
                "data": {
                    "timeout": 5
                }
            }
        }

        self.DB = _DataBaseInjection(self)

        LogMixin.__init__(self)
        IO.__init__(self)

    @property
    def timeout(self):
        return self.settings["timeout"]

    @property
    def BASE_DIR(self):
        return "./Serv/Server/Login/"


Login = _Login()


class _Client(IO, LogMixin):
    def __init__(self):
        LogMixin.__init__(self)
        IO.__init__(self)

    @property
    def BASE_DIR(self):
        return "./Serv/Server/Client/"


ClientType = _Client()


class _ChatServer(IO, LogMixin):
    def __init__(self):
        LogMixin.__init__(self)
        IO.__init__(self)

    @property
    def BASE_DIR(self):
        return "./Serv/Server/ChatServer/"


ChatServerType = _ChatServer()


class _ClientPool(IO, LogMixin):
    def __init__(self):
        LogMixin.__init__(self)
        IO.__init__(self)

    @property
    def BASE_DIR(self):
        return "./Serv/Server/ClientPool/"


ClientPoolType = _ClientPool()


class _ChatServerPool(IO, LogMixin):
    def __init__(self):
        LogMixin.__init__(self)
        IO.__init__(self)

    @property
    def BASE_DIR(self):
        return "./Serv/Server/ChatServerPool/"


ChatServerPoolType = _ChatServerPool()

__all__ = ("Login", "ClientType", "ChatServerType", "ClientPoolType", "ChatServerPoolType")
