# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import sys
from abc import ABC
from abc import abstractmethod
from threading import Thread

from AuthenticationSystem.Config.ServConfig import ServerConfig
from AuthenticationSystem.Events import Login
from AuthenticationSystem.Events.Login import FAILED
from AuthenticationSystem.Serv.Base import ABCService
from AuthenticationSystem.Serv.Base import ABCServicePool
from AuthenticationSystem.Serv.Base import PoolTypeRegistry
from AuthenticationSystem.Serv.Base import ServiceTypeRegistry
from AuthenticationSystem.Serv.Login.Login import Login, LostConnectError
from Lib.SocketIO import Address
from Lib.SocketIO import SocketIo
from Lib.database.DataBase import DataBaseClient
from Lib.log import Logging
from Lib.simple_tools import ThreadPool


class LoginFailed(Exception):
    def __str__(self):
        return "Login Failed"


class LoginManagerMixin(Login, ABC):

    db_client: DataBaseClient
    user_data: dict
    _cSocket: SocketIo

    @property
    @abstractmethod
    def logger(self) -> Logging.Logger:
        ...

    def _stop(self, _addr, *, fail_reason=None):
        if fail_reason is not None:
            self._cSocket.send_json(Login.FAILED(fail_reason).dump())
        self.logger.debug(f"[{self.TYPE}] Stop (addr='{_addr}')")
        self._cSocket.close()
        try:
            self.db_client.close()
        except AttributeError:
            pass
        self.logger.error(f"[{self.TYPE}] Exit")
        sys.exit(1)

    def get_data(self, _addr):
        try:
            raw_user_data, db_client = super()._get_data()
        except LostConnectError:
            self.login_logger.debug(f"[{self.TYPE}] LostConnectError (addr='{_addr}')")
            self._stop(_addr)
            raise LoginFailed
        self.db_client = db_client
        user_data = raw_user_data.dump().values()
        user_data = list(user_data)[0]

        if user_data["client_type"] != self.TYPE:
            repr_ = f"(addr='{_addr}' type='{user_data['client_type']}' need_type='{self.TYPE}')"
            self.logger.warn(
                f"[{self.TYPE}] Invalid client type {repr_}"
            )
            self._stop(_addr, fail_reason=FAILED.TYPE.INVALID_CLIENT_TYPE)
            raise LoginFailed

        try:
            self._cSocket.send_json(Login.SUCCESS().dump())
        except ConnectionError:
            self.logger.debug(f"[{self.TYPE}] Lost Connect! #just before i told it login success (addr='{_addr}')")
            self._stop(_addr)
            raise LoginFailed

        self.user_data = user_data

    def login(self, addr):
        self.get_data(addr)

        self._find_user_in_db(...)  # todo
        # warn todo
        # 从数据库中查找是否有登录数据
        # 如果查找到并且匹配就直接登录
        # 如果没有找到就尝试注册


@ServiceTypeRegistry
class Client(ABCService, LoginManagerMixin):
    Config = ServerConfig.ClientType
    logger = Logging.Logger(Config.log_level, *Config.log_files)
    TYPE = "Client"

    def __init__(self, conn, addr, *_, **__):
        super().__init__(conn, addr)

    def start(self):
        self.logger.debug(f"[{self.TYPE}] Start (addr='{self._address}')")
        try:
            self.login(self._address)
        except LoginFailed:
            pass


@ServiceTypeRegistry
class ChatServer(ABCService, LoginManagerMixin):
    Config = ServerConfig.ChatServerType
    logger = Logging.Logger(Config.log_level, *Config.log_files)
    TYPE = "ChatServer"

    def __init__(self, conn, addr, *_, **__):
        super().__init__(conn, addr)

    def start(self):
        ...


@PoolTypeRegistry
class ClientServicePool(ABCServicePool):
    TYPE = "Client"
    Config = ServerConfig.ClientPoolType
    logger = Logging.Logger(Config.log_level, *Config.log_files)

    def __init__(self):
        self._client_pool = ThreadPool()

    def add_service(self, conn: SocketIo, addr: Address, *args, **kwargs):
        self.logger.info(f"[ClientServicePool] Recv new request (addr='{addr}')")

        obj = Client(conn, addr, *args, **kwargs)

        thread = Thread(target=obj.start, daemon=True, name="ClientServ")

        self._client_pool.add(thread)
        self.logger.info(f"[ClientServicePool] Added thread obj to pool (addr='{addr}')")
        thread.start()

        self.logger.debug(f"[ClientServicePool] Started serv (addr='{addr}')")


@PoolTypeRegistry
class ChatServerServicePool(ABCServicePool):
    TYPE = "ChatServer"
    Config = ServerConfig.ChatServerPoolType
    logger = Logging.Logger(Config.log_level, *Config.log_files)

    def __init__(self):
        self._chat_server_pool = ThreadPool()

    def add_service(self, conn: SocketIo, addr: Address, *args, **kwargs):
        self.logger.info(f"[ChatServerServicePool] Recv new request (addr='{addr}')")

        obj = ChatServer(conn, addr, *args, **kwargs)

        thread = Thread(target=obj.start, daemon=True, name="ChatServerServ")

        self._chat_server_pool.add(thread)
        self.logger.info(f"[ChatServerServicePool] Added thread obj to pool (addr='{addr}')")
        thread.start()

        self.logger.debug(f"[ChatServerServicePool] Started serv (addr='{addr}')")


__all__ = ("Client", "ChatServer")
