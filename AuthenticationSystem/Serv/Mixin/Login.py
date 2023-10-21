# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"


import sys
import traceback
from typing import Union

from AuthenticationSystem.Config.ServConfig import ServerConfig
from AuthenticationSystem.Events import Login
from AuthenticationSystem.Events.Login import FAILED
from Lib.SocketIO import SocketIo
from Lib.config import tools as cf_tools
from Lib.database import logging as db_logging
from Lib.database.ABC import NameList
from Lib.database.DataBase import DataBaseClient
from Lib.database.DataBase import DataBaseServer
from Lib.database.Event import *
from Lib.database.Event.ABC import RunSuccess
from Lib.database.SocketIO import Address as db_Address
from Lib.global_thread_lock import OutputLock
from Lib.log import Logging
from Lib.config import Progressbar
from tqdm import tqdm

_DBConfig = ServerConfig.Login.DB
_DB_ADDR = db_Address(*_DBConfig.Server.address)
_DBName = _DBConfig.database_name
_DBStores = _DBConfig.store_list

_Config = ServerConfig.Login
_login_logger = Logging.Logger(_Config.log_level, *_Config.log_files)


class LoginData(NameList):
    def __init__(self, name, login_key):
        super().__init__(name=name, login_key=login_key)

    name: str
    login_key: str

    def ToNamelist(self):
        return NameList(name=self.name, login_key=self.login_key)


class LoginDatabaseFailedError(Exception):
    def __init__(self, ret_code):
        self.ret_code = ret_code

    def __str__(self):
        if isinstance(self.ret_code, Exception):
            self.ret_code = f"{type(self.ret_code).__name__}: {self.ret_code}"

        return f"Login Database Failed (ret_code={self.ret_code})"


if _DBConfig.BuiltinDatabase.enable:
    try:
        level = db_logging.level_list.GetNameLevel(_DBConfig.BuiltinDatabase.log_level)
    except KeyError:
        level = db_logging.level_list.GetWeightLevel(_DBConfig.BuiltinDatabase.log_level)

    input_file = cf_tools.init_files(_DBConfig.BuiltinDatabase.input_file, 'r')
    log_file = cf_tools.init_files(_DBConfig.BuiltinDatabase.log_file, 'a', newline='\n')
    s_db = DataBaseServer(
        name=_DBConfig.Server.name,
        file=input_file,
        log_file=log_file,
        disable_log=_DBConfig.BuiltinDatabase.disable_log,
        debug=_DBConfig.BuiltinDatabase.debug_mode,
        log_level=level
    )
    s_db.bind(_DB_ADDR.get())
    s_db.listen(_DBConfig.BuiltinDatabase.max_connections)
    s_db.start()

    del level


def _init_db_client(login_logger, timeout, client_type):
    log_head = f"[Login][DBClientLogin][{client_type}]"

    try:
        client = DataBaseClient(_DB_ADDR)
    except OSError as err:
        if err.errno == 10048:
            login_logger.error(
                f"{log_head} Failed to connect to database server #port exhausted?"
                f" ({type(err).__name__}: {err})"
            )
            raise LoginDatabaseFailedError(err)
        else:
            raise

    old_timeout = client.gettimeout()
    client.settimeout(timeout)
    ret = client.recv()

    if ret != LOGIN.ASK_USER_AND_PASSWORD:
        login_logger.error(
            f"{log_head} Received an unexpected event request before logging in (event='{type(ret).raw}: {ret}')"
        )

    ret = client.send_request(LOGIN.ACK_USER_AND_PASSWORD(_DBConfig.Userdata.username, _DBConfig.Userdata.password))

    client.settimeout(old_timeout)

    if ret == LOGIN.LOGIN_SUCCESS:
        login_logger.info(f"{log_head} Login Success")
        return client
    elif ret == LOGIN.WRONG_PASSWORD:
        login_logger.error(f"{log_head} Wrong DB password (pw='{_DBConfig.password}')")
    elif ret == LOGIN.USER_NOT_FIND:
        login_logger.error(f"{log_head} User Not Find (username='{_DBConfig.username}')")
    else:
        login_logger.error(f"{log_head} unknown return value (value={ret.raw}: {ret})")

    raise LoginDatabaseFailedError(ret)


def _init_database():
    c_db = _init_db_client(_login_logger, _Config.timeout, "InitDatabase")
    log_head = f"[Login][DBServer-AutoInit]"

    event_ls = [
        LOGIN.ACK_USER_AND_PASSWORD(_DBConfig.Userdata.username, _DBConfig.Userdata.password),
        DATABASE.INIT("default", _DBName),
    ]

    event_ls *= 9997
    # warn 这玩意用完记得删

    if _DBConfig.AutoInit.init_store:
        for store in _DBStores:
            temp = [
                STORE.CREATE(_DBName, "default", store),
                STORE.SET_FORMAT(_DBName, store, LoginData(None, None).ToNamelist()),
                STORE.SET_HISTORY_FORMANT(_DBName, store, "[{time_}]({type_}): {value}"),
            ]
            event_ls += temp

    c_db.settimeout(_Config.timeout)

    progress_bar = tqdm(
        total=len(event_ls),
        leave=True,
        unit="events",
        desc="DBServer-AutoInit",
        file=sys.stdout,
    )

    progress_bar.set_lock(OutputLock)

    for event in event_ls:
        _login_logger.debug(f"{log_head} Send event to DBServer (event='{event}')")
        ret = c_db.send_request(event)
        _login_logger.debug(f"{log_head} Recv return value from DBServer (ret='{ret}')")
        if not isinstance(ret, RunSuccess):
            _login_logger.warn(
                f"{log_head} Return value is not instance of RUN_SUCCESS #may failed "
                f"(ret='{repr(ret)}')"
            )
        else:
            _login_logger.debug(
                f"{log_head} Successfully execute event (ret='{ret}')"
            )
        progress_bar.update(1)
        progress_bar.refresh()

    progress_bar.close()

    c_db.close()


Progressbar.close()


if _DBConfig.AutoInit.init_database:
    _init_database()


class LostConnectError(ConnectionError):
    def __str__(self):
        return "Lost connect"


class LoginMixin:
    _cSocket: SocketIo

    _login_Config = _Config
    TIMEOUT = _login_Config.timeout
    TYPE: Union[None, str]
    login_logger = _login_logger

    def _init_db_client(self):
        return _init_db_client(self.login_logger, self.TIMEOUT, self.TYPE)

    def _login(self, client_type=None) -> tuple[Login.ACK_DATA, DataBaseClient]:
        if (client_type is None) and (self.TYPE is None):
            raise ValueError("client_type is None")
        if self.TYPE is None:
            self.TYPE = client_type

        log_head = f"[Login][{self.TYPE}]"

        addr = self._cSocket.getpeername()
        self.login_logger.debug(f"{log_head} Recv new login request (addr='{addr}')")
        old_timeout = self._cSocket.gettimeout()
        self._cSocket.settimeout(self.TIMEOUT)
        self._cSocket.send_json(Login.ASK_DATA().dump())

        data = {}
        load_success = False
        try:
            data = Login.ACK_DATA.load_str(self._cSocket.recv().decode())
            load_success = True
        except (ConnectionResetError, TimeoutError, EOFError) as err:
            # 这些错误发生大概率是连接直接断了, 所以没必要发送LOGIN FAILED事件
            self.login_logger.info(
                f"{log_head} Lost Connect (addr='{addr}' reason='{type(err).__name__}: {err}')"
            )
        except Exception as err:
            self.login_logger.error(
                f"{log_head} An un except exception recv (exc='{type(err.__name__)}: {err}')"
            )
            self._cSocket.send_json(Login.FAILED(FAILED.TYPE.INVALID_DATA).dump())
            traceback.print_exception(err, file=sys.stderr)

        if not load_success:
            self._cSocket.close()
            raise LostConnectError

        try:
            client = self._init_db_client()
        except LoginDatabaseFailedError as err:
            self.login_logger.error(
                f"{log_head} Lost Connect! (reason='{type(err).__name__}: {err}')"
            )
            try:
                self._cSocket.send_json(Login.FAILED(FAILED.TYPE.FAILED_TO_ACQUIRE_DATA).dump())
            except ConnectionError:
                pass
            self._cSocket.close()
            raise LostConnectError

        except Exception as err:
            self.login_logger.error(
                f"{log_head} Lost Connect! Unhandled exception occurred (reason={type(err).__name__}：{err})"
            )
            self._cSocket.send_json(Login.FAILED(FAILED.TYPE.UNKNOWN_SERVER_ERROR).dump())
            self._cSocket.close()
            raise LostConnectError

        self._cSocket.settimeout(old_timeout)

        return data, client
