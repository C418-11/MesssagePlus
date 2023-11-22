# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

from numbers import Real
from typing import Optional
from typing import Self
from typing import TextIO

from Lib.SocketIO import Address
from Lib.database import logging
from Lib.database.ABC import NameList
from Lib.database.DataBase import DataBaseServer


class LoginKey:
    def __init__(self, key: str, timeout_timestamp: float) -> None:
        self._key = key
        self._timeout_timestamp = timeout_timestamp

    @property
    def key(self):
        return self._key

    @property
    def timeout_timestamp(self):
        return self._timeout_timestamp

    @classmethod
    def fromDict(cls, data: dict):
        key = data["key"]
        timeout_timestamp = data["timeout_timestamp"]
        return cls(key, timeout_timestamp)

    def toDict(self):
        return {"key": self._key, "timeout_timestamp": self._timeout_timestamp}

    def __eq__(self, other) -> bool:
        """
        key相等不代表没超时
        """
        try:
            return self._key == other.key
        except AttributeError:
            return NotImplemented

    def updateTimeout(self, timestamp: float) -> None:
        """
        :param timestamp: 所要更新的时间戳
        """
        if timestamp < self._timeout_timestamp:
            # 不能小于原来的时间戳
            raise ValueError(
                f"Cannot be less than the original timestamp"
                f" (old={self._timeout_timestamp}, new={timestamp}"
            )
        self._timeout_timestamp = timestamp

    def checkTimeout(self, timestamp: float) -> bool:
        """
        :param timestamp: 所要对比的时间戳
        如果超时了就返回True，否则返回False
        """
        return timestamp > self._timeout_timestamp

    def __repr__(self):
        return f"{type(self).__name__}(key={self._key}, timeout_stamp={self._timeout_timestamp})"


class LoginData(NameList):
    def __init__(self, uuid: Optional[str], login_key: Optional[LoginKey]) -> None:
        super().__init__(uuid=uuid, login_key=login_key)

    uuid: str
    login_key: LoginKey

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
