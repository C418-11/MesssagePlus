# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import os
from typing import Union
from typing import override

from Lib.config.ConfigIO import IO
from Lib.config.Mixin.LogMixin import LogMixin
from Lib.config.Progressbar import config_counter
from Lib.database import logging as db_logging


class Data:
    def __init__(self, data: dict):
        self._data = {}
        for d in data:
            if type(data[d]) is dict:
                self._data[d] = Data(data[d])
            else:
                self._data[d] = data[d]

    def __getattribute__(self, item):
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            pass
        return self._data[item]

    def __getitem__(self, item):
        return self._data[item]


class DataTypeAnnotation:
    class Server:
        name: str
        address: list

    class Userdata:
        username: str
        password: str

    class BuiltinDatabase:
        enable: bool
        log_file: str
        input_file: str
        enable_log: bool
        log_level: Union[str, int]
        enable_debug: bool
        max_connections: int

    class AutoInit:
        init_database: bool
        init_store: bool


class _DataBaseInjection:

    def __init__(self, parent: IO):
        super().__init__()
        self.parent = parent
        self.parent.DEFAULT_FILES.update({
            os.path.join(self.parent.BASE_DIR, "database.json"): {
                "key": "injection_login_database",
                "data": {
                    "Server": {
                        "name": "LoginDataBaseServer",
                        "address": ("127.0.0.1", 11451),
                    },
                    "Userdata": {
                        "username": "default",
                        "password": "default",
                    },
                    "BuiltinDatabase": {
                        "enable": True,
                        "log_file": "stderr",
                        "input_file": None,
                        "enable_log": True,
                        "log_level": db_logging.WARN.name,
                        "enable_debug": True,
                        "max_connections": 10,
                    },
                    "database_name": "LoginData",
                    "store_list": [
                        "Client",
                        "ChatServer"
                    ],
                    "AutoInit": {
                        "init_database": True,
                        "init_store": True
                    }
                }
            }
        })

        self._data = None

    @property
    def data(self) -> Data:
        if self._data is None:
            self._data = Data(self.parent.injection_login_database)
        return self._data

    Server: DataTypeAnnotation.Server
    Userdata: DataTypeAnnotation.Userdata
    BuiltinDatabase: DataTypeAnnotation.BuiltinDatabase

    database_name: str
    store_list: list

    AutoInit: DataTypeAnnotation.AutoInit

    def __getattribute__(self, item):
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            try:
                return self.data[item]
            except KeyError:
                pass
            raise

    def __getitem__(self, item):
        return self.__getattribute__(item)


@config_counter
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
    @override
    def BASE_DIR(self):
        return "./Server/Serv/Login/"


Login = _Login()


@config_counter
class _Client(IO, LogMixin):
    def __init__(self):
        LogMixin.__init__(self)
        IO.__init__(self)

    @property
    @override
    def BASE_DIR(self):
        return "./Server/Serv/Client/"


ClientType = _Client()


@config_counter
class _ChatServer(IO, LogMixin):
    def __init__(self):
        LogMixin.__init__(self)
        IO.__init__(self)

    @property
    @override
    def BASE_DIR(self):
        return "./Server/Serv/ChatServer/"


ChatServerType = _ChatServer()


@config_counter
class _ClientPool(IO, LogMixin):
    def __init__(self):
        LogMixin.__init__(self)
        IO.__init__(self)

    @property
    @override
    def BASE_DIR(self):
        return "./Server/Serv/ClientServicePool/"


ClientPoolType = _ClientPool()


@config_counter
class _ChatServerPool(IO, LogMixin):
    def __init__(self):
        LogMixin.__init__(self)
        IO.__init__(self)

    @property
    @override
    def BASE_DIR(self):
        return "./Server/Serv/ChatServerServicePool/"


ChatServerPoolType = _ChatServerPool()

__all__ = ("Login", "ClientType", "ChatServerType", "ClientPoolType", "ChatServerPoolType")
