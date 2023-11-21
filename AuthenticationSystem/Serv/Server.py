# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

from threading import Thread
from typing import override

from AuthenticationSystem.Config.Server.ServConfig import ServerConfig
from AuthenticationSystem.Events import Login
from AuthenticationSystem.Serv.Base import ABCService
from AuthenticationSystem.Serv.Base import ABCServicePool
from AuthenticationSystem.Serv.Base import PoolTypeRegistry
from AuthenticationSystem.Serv.Base import ServiceTypeRegistry
from AuthenticationSystem.Serv.Login.Login import LoginManager
from Lib.SocketIO import Address
from Lib.SocketIO import SocketIo
from Lib.log import Logging
from Lib.simple_tools import ThreadPool


class LoginFailed(Exception):
    def __str__(self):
        return "Login Failed"


class LoginMixin(LoginManager):

    def __init__(self, socket: SocketIo, store: str):
        LoginManager.__init__(self, socket, store)

    def login(self):
        # print(self._find_user_in_db(self.userdata.uuid))  # todo
        self._cSocket.send_json(Login.SUCCESS.dump())
        # warn todo
        # 从数据库中查找是否有登录数据
        # 如果查找到并且匹配就直接登录
        # 如果没有找到就尝试注册


@ServiceTypeRegistry
class Client(ABCService, LoginMixin):
    Config = ServerConfig.ClientType
    logger = Logging.Logger(Config.log_level, *Config.log_files)
    TYPE = "Client"

    def __init__(self, conn, addr, *_, **__):
        ABCService.__init__(self, conn, addr)
        try:
            LoginMixin.__init__(self, self._cSocket, self.TYPE)
        except (ConnectionError, TimeoutError) as err:
            self.logger.info(
                f"[{self.TYPE}] LostConnect"
                f" (addr='{self._address}', reason='{type(err).__name__}: {err}')"
            )
            raise

    @override
    def start(self):
        self.logger.debug(f"[{self.TYPE}] Start (addr='{self._address}')")
        try:
            self.login()
        except LoginFailed:
            pass
        self._cSocket.close()
        self.db_client.close()


@ServiceTypeRegistry
class ChatServer(ABCService, LoginMixin):
    Config = ServerConfig.ChatServerType
    logger = Logging.Logger(Config.log_level, *Config.log_files)
    TYPE = "ChatServer"

    def __init__(self, conn, addr, *_, **__):
        super().__init__(conn, addr)

    @override
    def start(self):
        ...


@PoolTypeRegistry
class ClientServicePool(ABCServicePool):
    TYPE = "Client"
    Config = ServerConfig.ClientPoolType
    logger = Logging.Logger(Config.log_level, *Config.log_files)

    def __init__(self):
        self._client_pool = ThreadPool()

    @override
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

    @override
    def add_service(self, conn: SocketIo, addr: Address, *args, **kwargs):
        self.logger.info(f"[ChatServerServicePool] Recv new request (addr='{addr}')")

        obj = ChatServer(conn, addr, *args, **kwargs)

        thread = Thread(target=obj.start, daemon=True, name="ChatServerServ")

        self._chat_server_pool.add(thread)
        self.logger.info(f"[ChatServerServicePool] Added thread obj to pool (addr='{addr}')")
        thread.start()

        self.logger.debug(f"[ChatServerServicePool] Started serv (addr='{addr}')")


__all__ = ("Client", "ChatServer")
