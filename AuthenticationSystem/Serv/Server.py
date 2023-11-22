# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import time
from threading import Thread
from typing import override

from AuthenticationSystem.Config.Server.ServConfig import ServerConfig
from AuthenticationSystem.Events import Login
from AuthenticationSystem.Events.Login import FailType
from AuthenticationSystem.Serv.Base import ABCService
from AuthenticationSystem.Serv.Base import ABCServicePool
from AuthenticationSystem.Serv.Base import PoolTypeRegistry
from AuthenticationSystem.Serv.Base import ServiceTypeRegistry
from AuthenticationSystem.Serv.Login.Login import LoginManager
from Lib.SocketIO import Address
from Lib.SocketIO import SocketIo
from Lib.VerificationCode.Email import verificationSender
from Lib.log import Logging
from Lib.simple_tools import ThreadPool


class LoginException(Exception):
    ...


class UserNotFound(LoginException):
    def __init__(self, uuid: str):
        self._uuid = uuid

    @property
    def uuid(self):
        return self._uuid

    def __str__(self):
        return f"User Not Found (uuid={self._uuid})"


class UnableSendVerificationCode(LoginException):
    def __init__(self, err, recv: str):
        self._err = err
        self._recv = recv

    @property
    def err(self):
        return self._err

    @property
    def recv(self):
        return self._recv

    def __str__(self):
        return f"Unable Send Verification Code (recv='{self._recv}', err='{type(self._err)}: {self._err}')"


class LoginKeyDoesntExist(LoginException):
    def __init__(self, uuid: str, login_key: str):
        self._uuid = uuid
        self._login_key = login_key

    @property
    def uuid(self):
        return self._uuid

    @property
    def login_key(self):
        return self._login_key

    def __str__(self):
        return f"Login Key Doesnt Exist (uuid={self._uuid}, login_key={self._login_key})"


class LoginMixin(LoginManager):

    def __init__(self, socket: SocketIo, store: str):
        LoginManager.__init__(self, socket, store)

    def login(self):
        log_head = f"[LoginManager.Login]"
        user_datas = self._find_user_in_db(self.userdata.uuid)

        try:
            userdata = user_datas[0]
        except IndexError:
            self._cSocket.send_json(Login.FAILED(FailType.USER_NOT_FOUND).dump())
            self.login_logger.info(f"{log_head} User Not Found (uuid={self.userdata.uuid})")
            raise UserNotFound(self.userdata.uuid)

        key_is_eq = self.userdata.login_key == userdata.login_key.key
        key_is_not_timeout = not userdata.login_key.checkTimeout(time.time())

        if key_is_eq and key_is_not_timeout:
            self.login_logger.info(
                f"{log_head} Login Success (uuid='{self.userdata.uuid}', userdata={self.userdata})"
            )
            self._cSocket.send_json(Login.SUCCESS.dump())
            return
        else:
            self.login_logger.info(
                f"{log_head} Login Failed (uuid='{self.userdata.uuid}', userdata={self.userdata})"
            )
            self._cSocket.send_json(Login.FAILED().dump())
            raise LoginKeyDoesntExist(self.userdata.uuid, self.userdata.login_key)

    def register(self):
        log_head = f"[LoginManager.Register]"
        try:
            verification_code = verificationSender(self.userdata.email)
        except Exception as err:
            self.login_logger.error(
                f"{log_head} Failed to send the verification code"
                f" (err={type(err).__name__}: {err})"
            )
            self._cSocket.send_json(Login.FAILED(FailType.UNKNOWN_SERVER_ERROR).dump())
            self._cSocket.close()
            return UnableSendVerificationCode(err, self.userdata.email)

        self.login_logger.info(
            f"{log_head} Send Verification Code"
            f" (uuid={self.userdata.uuid}, verification_code={verification_code})"
        )
        self._cSocket.send_json(Login.ASK_VERIFICATION_CODE.dump())
        # todo


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
        except UserNotFound:
            self.register()
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
