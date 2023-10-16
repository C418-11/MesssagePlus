# -*- coding: utf-8 -*-

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

from abc import ABC
from abc import abstractmethod
from typing import Type

from Lib.SocketIO import SocketIo, Address


class ABCServ(ABC):
    def __init__(self, conn: SocketIo, addr: Address):
        self._cSocket = conn
        self._address = addr

    @abstractmethod
    def thread(self):
        """服务启动入口"""

    @property
    @abstractmethod
    def TYPE(self) -> str:
        """类型名"""


class ABCPool(ABC):

    @abstractmethod
    def add(self, conn, addr, data):
        """添加新的服务入池"""

    @property
    @abstractmethod
    def TYPE(self) -> str:
        """类型名"""


ServTypes = {}
PoolTypes = {}


def ServRegister(cls: ABCServ):
    try:
        ServTypes[cls.TYPE]
    except KeyError:
        ServTypes[cls.TYPE] = cls
    else:
        raise ValueError(f"Type '{cls.TYPE}' already exists")
    return cls


def PoolRegister(cls: Type[ABCPool]):
    try:
        PoolTypes[cls.TYPE]
    except KeyError:
        PoolTypes[cls.TYPE] = cls()
    else:
        raise ValueError(f"Type '{cls.TYPE}' already exists")
    return cls


__all__ = ("ServTypes", "PoolTypes", "ABCServ", "ABCPool", "ServRegister", "PoolRegister")
