# -*- coding: utf-8 -*-

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import sys
import traceback

from AuthenticationSystem.Config.ServConfig import ServerConfig
from AuthenticationSystem.Events import Login
from Lib.SocketIO import SocketIo
from Lib.database import logging as db_logging
from Lib.database.DataBase import DataBaseServer, DataBaseClient
from Lib.database.SocketIO import Address as db_Address
from Lib.log import Logging
from Lib.database.Event import *

DBConfig = ServerConfig.Login.DB
DB_ADDR = db_Address(*DBConfig.addr)

if DBConfig.enable_builtin_db:
    try:
        level = db_logging.level_list.GetNameLevel(DBConfig.log_level)
    except KeyError:
        level = db_logging.level_list.GetWeightLevel(DBConfig.log_level)

    s_db = DataBaseServer(
        name=DBConfig.server_name,
        file=DBConfig.input_file,
        log_file=DBConfig.log_file,
        disable_log=DBConfig.disable_log,
        debug=DBConfig.debug_mode,
        log_level=level
    )
    s_db.bind(DB_ADDR.get())
    s_db.listen(DBConfig.listen)
    s_db.start()


class LoginDatabaseFailedError(Exception):
    def __init__(self, ret_code):
        self.ret_code = ret_code

    def __str__(self):
        return f"Login Database Failed (ret_code={self.ret_code})"


class LostConnectError(ConnectionError):
    def __str__(self):
        return "Lost connect"


class LoginMixin:
    _cSocket: SocketIo

    Config = ServerConfig.Login
    login_logger = Logging.Logger(Config.log_level, *Config.log_files)
    TIMEOUT = Config.timeout
    DB_AND_STORE = (DBConfig.db_name, DBConfig.store_name)
    CLIENT_TYPE = None

    def _init_db_client(self):
        client = DataBaseClient(DB_ADDR)
        old_timeout = client.gettimeout()
        client.settimeout(self.TIMEOUT)

        log_head = f"[Login][DBClientLogin][{self.CLIENT_TYPE}]"

        ret = client.recv()

        if ret != LOGIN.ASK_USER_AND_PASSWORD:
            self.login_logger.error(
                f"{log_head} Received an unexpected event request before logging in (event='{type(ret).raw}: {ret}')"
            )

        ret = client.send_request(LOGIN.ACK_USER_AND_PASSWORD(DBConfig.username, DBConfig.password))

        client.settimeout(old_timeout)

        match ret:
            case LOGIN.LOGIN_SUCCESS:
                self.login_logger.info(f"{log_head} Login Success")
                return client
            case LOGIN.WRONG_PASSWORD:
                self.login_logger.error(f"{log_head} Wrong DB password (pw='{DBConfig.password}')")
            case LOGIN.USER_NOT_FIND:
                self.login_logger.error(f"{log_head} User Not Find (username='{DBConfig.username}')")
            case _:
                self.login_logger.error(f"{log_head} unknown return value (value={ret.raw}: {ret})")

        raise LoginDatabaseFailedError(ret)

    def _login(self, client_type):
        self.CLIENT_TYPE = client_type

        addr = self._cSocket.getpeername()
        self.login_logger.debug(f"[Login][{self.CLIENT_TYPE}] Recv new login request (addr='{addr}')")
        old_timeout = self._cSocket.gettimeout()
        self._cSocket.settimeout(self.TIMEOUT)
        self._cSocket.send(Login.ASK_DATA().to_str().encode())

        data = {}
        load_success = False
        try:
            data = Login.ACK_DATA.load_str(self._cSocket.recv().decode())
            load_success = True
        except (ConnectionResetError, TimeoutError, EOFError) as err:
            self.login_logger.info(
                f"[Login][{self.CLIENT_TYPE}] Lost Connect (addr='{addr}' reason='{type(err).__name__}: {err}')"
            )
        except Exception as err:
            self.login_logger.error(
                f"[Login][{self.CLIENT_TYPE}] An un except exception recv (exc='{type(err.__name__)}: {err}')"
            )
            traceback.print_exception(err, file=sys.stderr)

        if not load_success:
            raise LostConnectError

        client = self._init_db_client()
        self._cSocket.settimeout(old_timeout)

        return data, client
