# -*- coding: utf-8 -*-

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import sys
from threading import Thread

from AuthenticationSystem.Config.ServConfig import ServerConfig
from AuthenticationSystem.Serv.Base import ABCPool
from AuthenticationSystem.Serv.Base import ABCServ
from AuthenticationSystem.Serv.Base import PoolRegister
from AuthenticationSystem.Serv.Base import ServRegister
from AuthenticationSystem.Serv.Mixin.Login import LoginMixin
from AuthenticationSystem.Events import Login
from Lib.SocketIO import Address
from Lib.SocketIO import SocketIo
from Lib.log import Logging
from Lib.simple_tools import ThreadPool


@ServRegister
class Client(ABCServ, LoginMixin):
    Config = ServerConfig.ClientType
    logger = Logging.Logger(Config.log_level, *Config.log_files)
    TYPE = "Client"

    def __init__(self, conn, addr, *_, **__):
        super().__init__(conn, addr)

    def thread(self):
        raw_user_data, db_client = self._login(self.TYPE)
        user_data = raw_user_data.dump().values()
        user_data = list(user_data)[0]

        if user_data["client_type"] != self.TYPE:
            repr_ = f"(addr='{self._address}' type='{user_data['client_type']}' need_type='{self.TYPE}')"
            self.logger.error(
                f"[Client] Invalid client type {repr_}"
            )
            self._cSocket.send_json(Login.INVALID_CLIENT_TYPE(user_data["client_type"], self.TYPE).dump())
            sys.exit(1)

        self.logger.debug(f"[Client] Login success (addr='{self._address}' user_data='{user_data}')")

        self._cSocket.close()
        db_client.close()
        self.logger.error("[Client] Exit")


@ServRegister
class ChatServer(ABCServ, LoginMixin):
    Config = ServerConfig.ChatServerType
    logger = Logging.Logger(Config.log_level, *Config.log_files)
    TYPE = "ChatServer"

    def __init__(self, conn, addr, *_, **__):
        super().__init__(conn, addr)

    def thread(self):
        user_data, db_client = self._login(self.TYPE)
        user_data = user_data.dump().values()
        user_data = list(user_data)[0]

        if user_data["client_type"] != self.TYPE:
            self.logger.error(f"[ChatServer] Invalid client type (type='{self.TYPE}')")

        self.logger.debug(f"[ChatServer] Login success (user_data='{user_data}')")

        self._cSocket.close()
        db_client.close()
        self.logger.error("[ChatServer] Exit")


@PoolRegister
class ClientPool(ABCPool):
    TYPE = "Client"
    Config = ServerConfig.ClientPoolType
    logger = Logging.Logger(Config.log_level, *Config.log_files)

    def __init__(self):
        self._client_pool = ThreadPool()

    def add(self, conn: SocketIo, addr: Address, *args, **kwargs):
        self.logger.info(f"[ClientPool] Recv new request (addr='{addr}')")

        obj = Client(conn, addr, *args, **kwargs)

        thread = Thread(target=obj.thread, daemon=True, name="ClientServ")

        self._client_pool.add(thread)
        self.logger.info(f"[ClientPool] Added thread obj to pool (addr='{addr}')")
        thread.start()

        self.logger.debug(f"[ClientPool] started thread (addr='{addr}')")


@PoolRegister
class ChatServerPool(ABCPool):
    TYPE = "ChatServer"
    Config = ServerConfig.ChatServerPoolType
    logger = Logging.Logger(Config.log_level, *Config.log_files)

    def __init__(self):
        self._chat_server_pool = ThreadPool()

    def add(self, conn: SocketIo, addr: Address, *args, **kwargs):
        """实例化+启动服务并扔进线程池"""
        self.logger.info(f"[ChatServerPool] Recv new request '{addr}'")

        obj = ChatServer(conn, addr, *args, **kwargs)

        thread = Thread(target=obj.thread, daemon=True, name="ChatServerServ")

        self._chat_server_pool.add(thread)
        self.logger.info(f"[ChatServerPool] Added thread obj to pool")
        thread.start()

        self.logger.debug(f"[ChatServerPool] started thread'{addr}'")


__all__ = ("Client", "ChatServer")
