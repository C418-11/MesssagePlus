# -*- coding: utf-8 -*-
# cython: language_level = 3

"""
May this file will help you to do st :D
"""
import copy
import pickle
import socket
import sys
import threading
import time
from collections import deque
from datetime import datetime
from numbers import Integral
from numbers import Real
from threading import Thread
from typing import TextIO
from typing import Type
from typing import Union

from ..database import logging
from ..database.ABC import ABCDataBase
from ..database.ABC import ABCServer
from ..database.ABC import ABCStore
from ..database.ABC import BuildPath
from ..database.ABC import NameList
from ..database.Event import *
from ..database.Event.ABC import EVENT_NOT_FIND
from ..database.Event.ABC import Event
from ..database.Event.ABC import EventToFunc
from ..database.Event.ABC import RUN_FAILED
from ..database.Event.BaseEventType import FailedEvent
from ..database.Event.BaseEventType import SuccessEvent
from ..database.SocketIO import Address
from ..database.SocketIO import Server
from ..database.SocketIO import SocketIo
from ..database.logging import DEBUG
from ..database.logging import INFO
from ..database.logging import WARNING

PATH = ".\\DataBases\\"


class Store(ABCStore):
    database: ABCDataBase

    def __init__(self, __store_path: str, database: ABCDataBase):
        super().__init__(__store_path, database)

    def set_format(self, format_: NameList):
        if self.database.BinJsonReader(self.path + self.database.INFO_FILE)["format"] is not None:
            raise RuntimeError("Format has been set")
        self.database.BinJsonChanger(self.path + self.database.INFO_FILE, ("format",), pickle.dumps(format_))

        self.history("set_format", {"format": format_.ToDict()})
        self.save()

        self.reload()

    def append(self, line: NameList):
        if line in self.data:
            raise ValueError("Line already exists!")
        self.data.append(line.ToDict())
        self.history("append", {"line": line.ToDict()})
        self.save()

    def search(self, keyword, value):
        if type(keyword is str):
            keyword = (keyword, )
        ret = []
        for line in self.data:
            for path in keyword[:-1]:
                line = line[path]
            try:
                if line[keyword[-1]] == value:
                    ret.append(self.format(line))
            except KeyError:
                return STORE.KEY_NOT_FIND
        if ret:
            return ret
        return [copy.deepcopy(self.format)]

    def locate(self, line):
        last = 0
        lines = []

        while True:
            try:
                i = self.data.index(line.ToDict(), last)
            except ValueError:
                break
            lines.append(i)
            last = i + 1

        if not lines:
            return [STORE.LINE_NOT_FIND]

        return lines


class DataBase(ABCDataBase):
    def __init__(self, __name: str,
                 __path: str,
                 *,
                 time_format: str = "%Y-%m-%d %H:%M:%S",
                 log_format: str = "[{time}] (level): {store} :: {msg}",
                 log_mode: "a | w" = 'a'):
        super().__init__(__name, __path)

        path = PATH
        if PATH.endswith('\\'):
            path = PATH[:-1]

        self.path = '\\'.join((path, __path, __name, ''))
        self.log_path = self.path + self.LOG_File

        BuildPath(path=self.path)

        self.time_format = time_format
        self.log_format = log_format

        self.logging = logging.Logger(name=self.name, stream=open(self.log_path, f"{log_mode}b"))
        self.logging.type = bytes
        self.logging: logging.Logger
        self.store = {"default": Store}

        self.stores = set()
        for store_path in self._DBPathFinder():
            try:
                cls = pickle.loads(self.StringToPickleBytes(self.BinJsonReader(store_path + self.INFO_FILE)["cls"]))
                self.stores.add(cls(store_path, self))
            except Exception as err:
                self.log(msg=f"An error was raised while loading Store store_path={store_path} err={err}",
                         level=WARNING)

    def create(self, __store_type, __store_name):
        store_path = self.store_path(__store_name)

        id_ = time.time()

        try:
            info = self.BinJsonReader(store_path + DataBase.INFO_FILE)
            id_ = info["id"]
        except FileNotFoundError:
            pass
        except KeyError:
            pass

        BuildPath(path=store_path)

        cls = self.store[__store_type]

        self.BinJsonWriter(
            store_path + self.INFO_FILE,
            {
                "id": str(id_),
                "cls": self.PickleBytesToString(pickle.dumps(cls)),
                "name": __store_name,
                "format": None,
                "history_format": "[{time_}]({type_}): {value}"
            }
        )
        self.BinJsonCreate(
            store_path + self.DATA_FILE,
            []
        )
        self.BinJsonCreate(
            store_path + self.HISTORY_FILE,
            []
        )

        self.stores.add(cls(store_path, self))

    def log(self, msg: str, level, store: str = "SYSTEM"):
        time_ = time.strftime(self.time_format, time.localtime())
        message = self.log_format.format(time=time_, level=level, store=store, msg=msg)

        bin_msg = message.encode(encoding="utf-8", errors="replace")

        self.logging.bin_log(msg=bin_msg, level=level)

    def __getitem__(self, item):
        for st in self.stores:
            if st.name == item:
                return st
        raise KeyError(item)


class DataBaseServer(ABCServer):
    """
    DataBase Server
    """

    def __init__(self,
                 name: str = "DefaultDataBaseServer",
                 path: str = PATH,
                 init_socket: tuple = None,
                 file: Union[TextIO, None] = sys.stdin,
                 databases: dict[str, Type[ABCDataBase]] = None,
                 *,
                 debug: bool = False,
                 time_format: str = "%Y-%m-%d %H:%M:%S.%f",
                 disable_log: bool = False,
                 log_file: TextIO = sys.stderr,
                 log_level: Integral = WARNING,
                 log_format: str = "({level}) [{time}]: {server} :: {msg}"):
        """
        :param name: 数据库名称
        :param path: 数据库位置文件夹
        :param init_socket: 数据库的网络套接字初始化参数
        :param file: 运行时需逐行读取并执行的流  值为 None 时不进行读取
        :param databases: 指定数据库类型

        :param debug: 是否开启调试模式
        :param time_format: 时间格式化模板
        :param disable_log: 是否禁止记录日志
        :param log_file: 日志文件
        :param log_level: 最低日志输出等级
        :param log_format: 日志格式化模板
        """

        self.name = name
        self.path = path + name + "\\"
        self.file = file
        if databases is None:
            databases = {"default": DataBase}
        self.databases = databases

        self.debug = debug

        BuildPath(path=self.path)

        self.time_format = time_format

        self.logging = logging.Logger(name=name, level=log_level, stream=log_file)
        self.logging.disable = disable_log
        self.log_format = log_format

        self.log(msg=f"Init name={self.name} path={self.path}", level=DEBUG)

        if init_socket is None:
            init_socket = (socket.AF_INET, socket.SOCK_STREAM)
        self.init_socket = init_socket
        self.server = Server(socket.socket(*self.init_socket))

        self.running = False
        self.cont_serve = 0
        self.recv_thread = Thread(target=self._recv_loop, name=self.name + "'s RecvLoop", daemon=True)
        self.file_input_thread = Thread(target=self._file_input_loop, name=self.name + "'s File Input", daemon=True)

        self.DBs = set()

    def _EventRunnerMaker(self, *, name: str = None):
        rollback_stack = deque(maxlen=64)

        if name is not None:
            name += ' '
        else:
            name = ''

        def Runner(event: Event):
            nonlocal self
            nonlocal rollback_stack
            nonlocal name

            rollback_stack.append(event)

            try:
                return_code = EventToFunc(event, self, True)
            except Exception as err:
                self.log(
                    msg=f"{name}An error occurred while executing the event request! err_type={type(err)} err={err}",
                    level=WARNING)
                rollback_stack.pop()
                if self.debug:
                    raise
                return RUN_FAILED

            if return_code == EVENT_NOT_FIND:
                self.log(msg=f"{name}An undefined event was requested! event={event}", level=INFO)
                rollback_stack.pop()
            elif isinstance(return_code, FailedEvent):
                self.log(msg=f"{name}Event request execution failed! return_code={return_code}", level=INFO)
            elif not (isinstance(return_code, SuccessEvent) or type(return_code) in (
                    int, bool, str, list, bytes, tuple, dict, set)):
                self.log(msg=f"{name}Event request may fail to execute! return_code={return_code}", level=INFO)

            return return_code

        return Runner

    def _file_input_loop(self):
        self.log(msg="Enter File Input", level=DEBUG)

        _EventRunner = self._EventRunnerMaker()

        if self.file is None:
            self.log(msg="self.file is None so 'File Input Loop' Exit", level=INFO)
            sys.exit(0)

        while self.running:
            line = self.file.readline()
            line = line.replace('\n', '')
            self.log(msg=f"A new line was read from the stream line={line}", level=DEBUG)
            if line == SERVER.STOP:
                self.stop()
                self.join()
                break

            if line == SERVER.RESTART:
                Thread(target=self.restart, name=self.name + "'s RESTART", daemon=True).start()
                break

            try:
                ret = eval(line)
                self.log(msg=f"A new line was executed from the stream ret_code={ret}", level=INFO)
            except Exception as err:
                self.log(f"An error was thrown while running a line in the flow err_type={type(err)} err={err}",
                         level=WARNING)

        self.log(msg="Exit File Input", level=DEBUG)

    def _serve(self, conn: SocketIo, name: str):
        conn_peer_name = conn.getpeername()
        self.log(msg=f"{name} Serve Start! name={name} conn={conn_peer_name}", level=INFO)

        conn.settimeout(5)
        conn.send_obj(LOGIN.ASK_USER_AND_PASSWORD)

        ret_login = LOGIN.LOGIN_FAILED

        try:
            login = conn.recv_obj()
            ret_login = EventToFunc(login, self, True)

            conn.send_obj(ret_login)
            if ret_login != LOGIN.LOGIN_SUCCESS:
                self.log(msg=f"{name} Lost Connect! reason={ret_login}", level=WARNING)
                conn.close()

        except TimeoutError:
            ret_login = LOGIN.ASK_USER_AND_PASSWORD_TIMEOUT
            conn.send_obj(ret_login)
            self.log(msg=f"{name} Lost Connect! reason={ret_login}", level=WARNING)
        except Exception as err:
            try:
                conn.send_obj(ret_login)
            except OSError:
                pass
            self.log(
                msg=f"{name} An unknown error was thrown during login! err_type={type(err)} err={err}", level=WARNING)

        event_runner = self._EventRunnerMaker(name=name)

        while self.running and ret_login == LOGIN.LOGIN_SUCCESS:
            try:
                event = conn.recv_obj()
                event: Event
                self.log(msg=f"{name} Received a new event request! event={event}", level=INFO)
            except TimeoutError:
                continue
            except EOFError:
                self.log(msg=f"{name} Lost Connect! reason={SOCKET.CONNECT_CLOSE}", level=INFO)
                break

            return_code = event_runner(event)

            try:
                conn.send_obj(return_code)
            except ConnectionResetError:
                self.log(msg=f"{name} Lost Connect! reason={SOCKET.CONNECT_CLOSE}", level=INFO)
                break
            except OSError:
                self.log(msg=f"{name} Lost Connect! reason={SOCKET.CONNECT_CLOSE}", level=INFO)
                break

        self.log(msg=f"{name} Serve End! conn={conn_peer_name}", level=INFO)
        conn.close()

    def _recv_loop(self):
        self.log(msg=f"Enter RecvLoop", level=DEBUG)

        cont = 0

        while self.running:
            try:
                c_socket = self.server.get(10)[0]
                c_socket: socket.socket
            except TimeoutError:
                continue
            except threading.ThreadError:
                raise
            self.log(msg=f"Received a new connect request socket={c_socket.getpeername()}", level=INFO)
            conn = SocketIo(c_socket)

            cont += 1
            thread_name = f"Serve-{cont}"

            Thread(target=self._serve, kwargs={"conn": conn, "name": thread_name}, daemon=True,
                   name=thread_name).start()

        self.log(msg=f"Exit RecvLoop", level=DEBUG)

    def log(self, msg, level):
        level_name = logging.getWeightName(level=level)
        time_ = datetime.now().strftime(self.time_format)[:-4]

        message = self.log_format.format(time=time_, level=level_name, server=self.name, msg=msg)

        self.logging.log(level=level, msg=message)  # 输出日志

    def _start_thread(self):
        try:
            self.recv_thread.start()
        except RuntimeError:
            self.recv_thread.join(10)
            self.recv_thread = Thread(target=self._recv_loop, name=self.name + "'s RecvLoop", daemon=True)
            self.recv_thread.start()
        try:
            self.file_input_thread.start()
        except RuntimeError:
            self.file_input_thread.join(10)
            self.file_input_thread = Thread(target=self._file_input_loop, name=self.name + "'s File Input", daemon=True)
            self.file_input_thread.start()

    def start(self):
        self.log(msg=f"Start!", level=INFO)
        self.running = True
        self.server.start()

        self._start_thread()

    def stop(self):
        self.log(msg=f"Stop!", level=INFO)
        self.running = False
        self.server.stop()
        self.server.join(10)

    def restart(self):
        self.log(msg=f"ReStart!", level=INFO)
        self.stop()
        self.join(10)
        self.server.restart(self.init_socket)
        self.start()

    def join(self, timeout=None):
        self.recv_thread.join(timeout=timeout)

    def bind(self, _address: Union[Address, tuple[str, int]]):
        self.log(msg=f"Bind address={_address}", level=INFO)
        self.server.bind(_address)

    def listen(self, _backlog: int):
        self.log(msg=f"Listen backlog={_backlog}", level=DEBUG)
        self.server.listen(_backlog)

    def is_alive(self):
        return self.running

    def __getitem__(self, item):
        for db in self.DBs:
            if db.name == item:
                return db
        raise KeyError(item)


class DataBaseClient:
    def __init__(self, __address: Address):
        self.c_s = SocketIo(__address)

    def recv(self):
        return self.c_s.recv_obj()

    def close(self):
        self.c_s.close()

    def send_request(self, __event: Event):
        self.c_s.send_obj(__event)
        return self.recv()

    def send_list(self, __event_list: list[Event]) -> list:
        ret_list = []
        for event in __event_list:
            try:
                ret_list.append(self.send_request(event))
            except Exception as err:
                ret_list.append(err)
        return ret_list

    def send_dict(self, __event_dict: dict[any, Event]) -> dict[any, Event]:
        ret_dict = {}
        for key, value in __event_dict.items():
            try:
                ret_dict[key] = self.send_request(value)
            except Exception as err:
                ret_dict[key] = err
        return ret_dict

    def gettimeout(self):
        return self.c_s.gettimeout()

    def settimeout(self, timeout: Union[Real, None] = None):
        self.c_s.settimeout(timeout)


def mv_client():
    client = DataBaseClient(Address("127.0.0.1", 12345))
    client.settimeout(3)

    db_and_store = ("TestDB", "Store")

    _event_list = [
        LOGIN.ACK_USER_AND_PASSWORD("default", "default"),
        DATABASE.INIT("default", db_and_store[0]),
        STORE.CREATE(db_and_store[0], "default", db_and_store[1]),
        STORE.SET_FORMAT(*db_and_store, NameList("a", "b")),
        STORE.SET_HISTORY_FORMANT(*db_and_store, "[{time_}]({type_}): {value}"),
        STORE.APPEND(*db_and_store, NameList(a=1, b=2)),
        STORE.GET_LINE(*db_and_store, 0),
        STORE.SET_LINE(*db_and_store, 0, NameList(a=11, b=22)),
        STORE.GET_LINE(*db_and_store, 0),
        STORE.APPEND(*db_and_store, NameList(a=11, b=22)),
        STORE.SEARCH(*db_and_store, "a", 11),
        STORE.LOCATE(*db_and_store, NameList(a=11, b=22)),
        STORE.DEL_LINE(*db_and_store, 0),
        STORE.LOCATE(*db_and_store, NameList(a=11, b=22))
    ]

    _event_dict = {}
    for i, event in enumerate(_event_list):
        _event_dict[f"{'{'}{i}{'}'} {event.raw}"] = event

    print(client.recv())
    # ret_list = client.send_list(_event_list, 10)
    # for event in ret_list:
    #     print(event)

    ret_dict = client.send_dict(_event_dict)
    for k, v in ret_dict.items():
        print(k, "\nK<-->V\n", v)
        print()
        print()

    client.close()

    time.sleep(2)


def example():
    """调用这玩意看看例子"""

    s = DataBaseServer(log_level=DEBUG, debug=True)

    s.bind(("127.0.0.1", 12345))
    s.listen(1)
    s.start()

    mv_client()

    s.stop()
    s.join()


__all__ = ("PATH", "Store", "DataBase", "DataBaseServer", "DataBaseClient", "example")
