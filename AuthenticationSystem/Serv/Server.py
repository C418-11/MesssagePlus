# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import sys
import traceback
from threading import Thread
from typing import override

from AuthenticationSystem.Config.Server.ServConfig import ServerConfig
from AuthenticationSystem.Events import Login
from AuthenticationSystem.Serv.Base import ABCService
from AuthenticationSystem.Serv.Base import ABCServicePool
from AuthenticationSystem.Serv.Base import PoolTypeRegistry
from AuthenticationSystem.Serv.Base import ServiceTypeRegistry
from AuthenticationSystem.Serv.Login.Mixin import LoginMixin, InvalidLoginKey, WrongVerificationCode
from AuthenticationSystem.Serv.Login.Mixin import UnableSendVerificationCode
from AuthenticationSystem.Serv.Login.Mixin import UserNotFound
from AuthenticationSystem.Serv.Login.Mixin import WrongPassword
from Lib.SocketIO import Address
from Lib.SocketIO import SocketIo
from Lib.log import Logging
from Lib.simple_tools import ThreadPool


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

    def tryRegister(self, stop):
        self.logger.info(f"[{self.TYPE}] Try to register (addr='{self._address}', uuid='{self.userdata.uuid}')")
        try:
            self.register()
            self.logger.info(
                f"[{self.TYPE}] Register Success"
                f" (addr='{self._address}', uuid='{self.userdata.uuid}')"
            )
            stop(0)
        except UnableSendVerificationCode:
            self.logger.warn(
                f"[{self.TYPE}] Unable to send verification code"
                f" (addr='{self._address}', uuid='{self.userdata.uuid}')"
            )
            stop(1)
        except WrongVerificationCode:
            self.logger.info(
                f"[{self.TYPE}] Wrong verification code"
                f" (addr='{self._address}', uuid='{self.userdata.uuid}')"
            )
            stop(0)
        except (ConnectionError, EOFError, TimeoutError):
            self.logger.info(
                f"[{self.TYPE}] LostConnect"
                f" (addr='{self._address}', uuid='{self.userdata.uuid}')"
            )
            stop(1)

    def tryLogin(self):
        def stop(_status=None):
            self.logger.info(f"[{self.TYPE}] Stop (addr='{self._address}')")
            self._cSocket.close()
            self.db_client.close()
            sys.exit(_status)

        try:
            self.login()
            return
        except WrongPassword:
            self.logger.info(
                f"[{self.TYPE}] Wrong password"
                f" (addr='{self._address}', uuid='{self.userdata.uuid}')"
            )
            stop(0)
        except InvalidLoginKey:
            self.logger.info(
                f"[{self.TYPE}] Invalid login key"
                f" (addr='{self._address}', uuid='{self.userdata.uuid}')"
            )
            try:
                event = self._cSocket.recv().decode()
            except (ConnectionError, EOFError):
                stop(1)
                raise
            if Login.REGISTER.eq_str(event):
                self.logger.info(f"[{self.TYPE}] Register (addr='{self._address}', uuid='{self.userdata.uuid}')")
                self.tryRegister(stop)
            stop(0)
        except UserNotFound:
            try:
                event = self._cSocket.recv().decode()
            except (ConnectionError, EOFError):
                stop(1)
                raise
            if Login.REGISTER.eq_str(event):
                self.logger.info(f"[{self.TYPE}] Register (addr='{self._address}', uuid='{self.userdata.uuid}')")
                self.tryRegister(stop)
            stop(0)

        except Exception as err:
            self.logger.error(
                f"[{self.TYPE}] Unhandled exception occurred!"
                f" (addr='{self._address}', uuid='{self.userdata.uuid}', err='{type(err).__name__}: {err}')"
            )
            traceback.print_exception(err, file=self.logger.warn_file)
            stop(1)

        stop(1)

    @override
    def start(self):
        self.logger.debug(f"[{self.TYPE}] Start (addr='{self._address}')")
        self.tryLogin()
        self.db_client.close()
        self._cSocket.close()


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
