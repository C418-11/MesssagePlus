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
        :param timestamp: 所要更新到的时间戳
        """
        if timestamp <= self._timeout_timestamp:
            # 不能小于等于原来的时间戳
            raise ValueError(
                f"The timestamp {timestamp} is less than the current timestamp {self._timeout_timestamp}"
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
    def __init__(
            self,
            uuid: Optional[str],
            uuid_base: Optional[int],
            login_key: Optional[LoginKey],
            email: Optional[str],
            password: Optional[str]
    ) -> None:
        if uuid is not None and not isinstance(uuid, str):
            raise TypeError(f"uuid must be str, not {type(uuid)}")
        if uuid_base is not None and not isinstance(uuid_base, int):
            raise TypeError(f"uuid_base must be int, not {type(uuid_base)}")
        if login_key is not None and not isinstance(login_key, dict):
            raise TypeError(f"login_key must be dict, not {type(login_key)}")
        if email is not None and not isinstance(email, str):
            raise TypeError(f"email must be str, not {type(email)}")
        if password is not None and not isinstance(password, str):
            raise TypeError(f"password must be str, not {type(password)}")

        super().__init__(
            uuid=uuid,
            uuid_base=uuid_base,
            login_key=login_key,
            email=email,
            password=password
        )

    uuid: str
    uuid_base: int
    login_key: dict
    email: str
    password: str

    def ToNamelist(self) -> NameList:
        return NameList(
            uuid=self.uuid,
            uuid_base=self.uuid_base,
            login_key=self.login_key,
            email=self.email,
            password=self.password
        )

    @classmethod
    def empty(cls) -> Self:
        return cls(
            None,
            None,
            None,
            None,
            None
        )

    def hasNone(self) -> bool:
        is_none = False
        for value in self._attributes:
            if value is None:
                is_none = True
                break
        return is_none

    def hasEmpty(self) -> bool:
        is_empty = False
        for value in self._attributes:
            if not value:
                is_empty = True
                break
        return is_empty

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
