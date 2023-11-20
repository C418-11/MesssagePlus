# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

from numbers import Real
from typing import TextIO
from typing import Self
from typing import Optional

from Lib.SocketIO import Address
from Lib.database import logging
from Lib.database.ABC import NameList
from Lib.database.DataBase import DataBaseServer


class LoginData(NameList):
    def __init__(self, uuid: Optional[str], login_key: Optional[str]) -> None:
        super().__init__(uuid=uuid, login_key=login_key)

    uuid: str
    login_key: str

    def ToNamelist(self) -> NameList:
        return NameList(uuid=self.uuid, login_key=self.login_key)

    def empty(self) -> Self:
        return type(self)(None, None)

    def is_empty(self) -> bool:
        if self.uuid is None or self.login_key is None:
            return True
        return False

    def __eq__(self, other) -> bool:
        try:
            return self.uuid == other.uuid and self.login_key == other.login_key
        except AttributeError:
            return NotImplemented


def build_database(
        *,
        name: str,
        address: Address,
        max_connections: int,
        log_level: Real,
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
