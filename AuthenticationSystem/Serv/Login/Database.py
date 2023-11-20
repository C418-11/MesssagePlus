# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

from typing import TextIO, Union

from Lib.SocketIO import Address
from Lib.database import logging
from Lib.database.ABC import NameList
from Lib.database.DataBase import DataBaseServer


class LoginData(NameList):
    def __init__(self, name, login_key):
        super().__init__(name=name, login_key=login_key)

    name: str
    login_key: str

    def ToNamelist(self):
        return NameList(name=self.name, login_key=self.login_key)


def build_database(
        *,
        name: str,
        address: Address,
        max_connections: int,
        log_level: Union[str, float],
        input_file: TextIO,
        enable_log: bool,
        log_file: TextIO,
        enable_debug: bool
):
    try:
        level = logging.level_list.GetNameLevel(log_level)
    except KeyError:
        level = logging.level_list.GetWeightLevel(log_level)

    s_db = DataBaseServer(
        name=name,
        file=input_file,
        log_file=log_file,
        disable_log=not enable_log,
        debug=enable_debug,
        log_level=level
    )
    s_db.bind(address.get())
    s_db.listen(max_connections)
    s_db.start()
    return s_db
