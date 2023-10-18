# -*- coding: utf-8 -*-

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

from abc import ABC
from abc import abstractmethod
from typing import Type

from Lib.SocketIO import SocketIo, Address


class ABCService(ABC):
    def __init__(self, conn: SocketIo, addr: Address):
        self._cSocket = conn
        self._address = addr

    @abstractmethod
    def start(self):
        """服务启动入口"""

    @property
    @abstractmethod
    def TYPE(self) -> str:
        """类型名"""


class ABCServicePool(ABC):

    @abstractmethod
    def add_service(self, conn, addr, data):
        """添加新的服务入池"""

    @property
    @abstractmethod
    def TYPE(self) -> str:
        """类型名"""


ServiceTypes = {}
ServicePoolTypes = {}


def ServiceTypeRegistry(service_class: Type[ABCService]):
    if service_class.TYPE in ServiceTypes:
        raise ValueError(f"Service type '{service_class.TYPE}' already exists")
    ServiceTypes[service_class.TYPE] = service_class
    return service_class


def PoolTypeRegistry(pool_class: Type[ABCServicePool]):
    if pool_class.TYPE in ServicePoolTypes:
        raise ValueError(f"Pool type '{pool_class.TYPE}' already exists")
    ServicePoolTypes[pool_class.TYPE] = pool_class()
    return pool_class


__all__ = (
    "ServiceTypes",
    "ServicePoolTypes",
    "ABCService",
    "ABCServicePool",
    "ServiceTypeRegistry",
    "PoolTypeRegistry"
)
