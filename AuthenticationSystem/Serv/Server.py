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
from AuthenticationSystem.Serv.Base import ABCService
from AuthenticationSystem.Serv.Base import ABCServicePool
from AuthenticationSystem.Serv.Base import PoolTypeRegistry
from AuthenticationSystem.Serv.Base import ServiceTypeRegistry
from AuthenticationSystem.Serv.Mixin.Login import LoginMixin
from Lib.SocketIO import Address
from Lib.SocketIO import SocketIo
from Lib.database.DataBase import DataBaseClient
from Lib.log import Logging
from Lib.simple_tools import ThreadPool


class LoginManagerMixin(LoginMixin, ABC):

    db_client: DataBaseClient

    @property
    @abstractmethod
    def logger(self) -> Logging.Logger:
        ...

    def _stop(self, _addr):
        self.logger.debug(f"[{self.TYPE}] Stop (addr='{_addr}')")
        self._cSocket.close()
        self.db_client.close()
        self.logger.error(f"[{self.TYPE}] Exit")
        sys.exit(1)

    def _login_all(self, _addr):
        self.logger.debug(f"[{self.TYPE}] Start (addr='{_addr}')")

        raw_user_data, db_client = super()._login()
        self.db_client = db_client
        user_data = raw_user_data.dump().values()
        user_data = list(user_data)[0]

        if user_data["client_type"] != self.TYPE:
            repr_ = f"(addr='{_addr}' type='{user_data['client_type']}' need_type='{self.TYPE}')"
            self.logger.error(
                f"[{self.TYPE}] Invalid client type {repr_}"
            )
            self._cSocket.send_json(Login.INVALID_CLIENT_TYPE(user_data["client_type"], self.TYPE).dump())
            self._stop(_addr)

        self._cSocket.send_json(Login.SUCCESS().dump())
        self.logger.debug(f"[{self.TYPE}] Login Success (addr='{_addr}' user_data='{user_data}')")

        self._stop(_addr)


@ServiceTypeRegistry
class Client(ABCService, LoginManagerMixin):
    Config = ServerConfig.ClientType
    logger = Logging.Logger(Config.log_level, *Config.log_files)
    TYPE = "Client"

    def __init__(self, conn, addr, *_, **__):
        super().__init__(conn, addr)

    def start(self):
        self._login_all(self._address)


@ServiceTypeRegistry
class ChatServer(ABCService, LoginManagerMixin):
    Config = ServerConfig.ChatServerType
    logger = Logging.Logger(Config.log_level, *Config.log_files)
    TYPE = "ChatServer"

    def __init__(self, conn, addr, *_, **__):
        super().__init__(conn, addr)

    def start(self):
        self._login_all(self._address)


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
