# -*- coding: utf-8 -*-
# cython: language_level = 3

import json
import os
import pickle
import time
from abc import ABC
from abc import abstractmethod
from typing import BinaryIO
from typing import TextIO
from typing import Type
from typing import Union

from ..database.Event.BaseEventType import SuccessEvent
from ..database.SocketIO import SocketIo


class NameList(SuccessEvent):
    def __init__(self, *args, **kwargs):
        self._attributes = dict()
        for name in args:
            self.__setattr__(name, None)
        for name, value in kwargs.items():
            self.__setattr__(name, value)

    def ToDict(self) -> dict:
        dict_ = {}
        for attr in self._attributes:
            dict_[attr] = self.__getattribute__(attr)
        return dict_

    def __call__(self, k_v: dict):
        return type(self)(**k_v)

    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)
        if key != "_attributes":
            self._attributes[key] = value

    def __delattr__(self, item):
        if item != "_attributes":
            del self._attributes[item]
        object.__delattr__(self, item)

    def __getattribute__(self, item):
        return object.__getattribute__(self, item)

    def __str__(self):
        k_v = ""
        for attr in self._attributes:
            k_v += f"{attr}={self.__getattribute__(attr)} "
        return f"{type(self).__name__}({k_v[:-1]})"

    def __repr__(self):
        return str(self)


class ABCStore(ABC):
    path: str
    name: str

    info: dict
    data: list[dict]
    histories: list[str]
    history_format: str

    _id: str
    format: Union[NameList, None]

    def __init__(self, __store_path: str, database):
        self.path = __store_path
        self.database = database

        BuildPath(path=self.path)

        self.info = self.database.BinJsonReader(self.path + self.database.INFO_FILE)
        self.data = self.database.BinJsonReader(self.path + self.database.DATA_FILE)
        self.histories = self.database.BinJsonReader(self.path + self.database.HISTORY_FILE)

        self._id = self.info["id"]
        self.name = self.info["name"]

        self.history_format = self.info["history_format"]

        format_ = self.info["format"]
        self.format = None
        if format_ is not None:
            self.format = pickle.loads(database.StringToPickleBytes(format_))

    def reload(self) -> None:
        BuildPath(path=self.path)

        self.info = self.database.BinJsonReader(self.path + self.database.INFO_FILE)
        self.data = self.database.BinJsonReader(self.path + self.database.DATA_FILE)
        self.histories = self.database.BinJsonReader(self.path + self.database.HISTORY_FILE)

        self.name = self.info["name"]

        self.history_format = self.info["history_format"]

        format_ = self.info["format"]
        self.format = None
        if format_ is not None:
            self.format = pickle.loads(self.database.StringToPickleBytes(format_))

    def save(self) -> None:
        self.database.BinJsonWriter(self.path + self.database.DATA_FILE, self.data)
        self.database.BinJsonWriter(self.path + self.database.HISTORY_FILE, self.histories)

    def history(self, type_, value) -> None:
        time_ = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        history = self.history_format.format(time_=time_, type_=type_, value=value)
        self.histories.append(history)

    @abstractmethod
    def set_format(self, format_: NameList) -> None: ...

    @abstractmethod
    def append(self, line: NameList) -> None: ...

    @abstractmethod
    def search(self, keyword: Union[str, tuple[str]], value) -> list[NameList]: ...

    @abstractmethod
    def locate(self, line: NameList) -> int: ...

    def set_history_format(self, format_: str = "[{time_}]({type_}): {value}") -> None:
        self.database.BinJsonChanger(self.path + self.database.INFO_FILE, ("history_format",), format_)
        self.history_format = format_
        self.info["history_format"] = format_
        self.history("set_history_format", {"format": format_})

    def __setitem__(self, key: int, value: dict) -> None:
        self.data[key] = value
        self.history("set_line", {"index": key, "value": value})
        self.save()

    def __getitem__(self, item: int) -> dict:
        return self.data[item]

    def __delitem__(self, key) -> None:
        last_value = self.data[key]
        self.history("del_start", {"index": key, "last_value": last_value})
        self.data.__delitem__(key)
        self.history("del_finish", {"index": key, "last_value": last_value})
        self.save()

    def __eq__(self, other) -> bool:
        if not isinstance(other, ABCStore):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)


class ABCDataBase(ABC):
    INFO_FILE = "INFO.BinJson"
    DATA_FILE = "DATA.BinData"
    HISTORY_FILE = "HISTORY.BinHistory"
    LOG_File = "Log.BinLog"

    name: str
    path: str
    stores: set[ABCStore]
    store: dict[str, Type[ABCStore]]

    def __init__(self, __name: str, __path: str) -> None:
        self.name = __name

    def store_path(self, __store_name: str):
        return f"{self.path}{__store_name}\\"

    def _DBPathFinder(self) -> set:
        dirs = {dir_name for dir_name in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, dir_name))}

        paths = set()
        for dir_ in dirs:
            try:
                path = self.store_path(dir_)
                open(path + self.INFO_FILE, mode='rb').close()
                paths.add(path)
            except FileNotFoundError:
                pass
        return paths

    @abstractmethod
    def create(self, __store_type, __store_name: str) -> None: ...

    @abstractmethod
    def log(self, msg: str, operator: str) -> None: ...

    @staticmethod
    def BinJsonReader(__file_path: str):
        txt = ""
        with open(__file_path, mode="rb") as file:
            txt += file.read(1024*4).decode("utf-8")
        data = json.loads(txt)
        return data

    @staticmethod
    def BinJsonWriter(__file_path: str, obj) -> None:
        data = json.dumps(obj)
        with open(__file_path, "wb") as file:
            file.write(data.encode("utf-8"))

    def BinJsonChanger(self, __file_path: str, path: tuple[str], value: Union[str, bytes]):
        json_obj = self.BinJsonReader(__file_path)
        if type(value) is bytes:
            value = self.PickleBytesToString(value)
        obj = json_obj
        for p in path[:-1]:
            obj = json_obj.__getitem__(p)
        obj.__setitem__(path[-1], value)
        self.BinJsonWriter(__file_path, json_obj)

    def BinJsonCreate(self, __file_path: str, default=None) -> None:
        try:
            self.BinJsonReader(__file_path)
            return
        except FileNotFoundError:
            pass

        data = json.dumps(default)
        with open(__file_path, "wb") as file:
            if default is not None:
                file.write(data.encode("utf-8"))

    @staticmethod
    def PickleBytesToString(byte: bytes):
        return byte.decode("unicode_escape")

    @staticmethod
    def StringToPickleBytes(string: str):
        return string.encode("utf-8", "unicode_escape").replace(b'\xc2', b'')

    @abstractmethod
    def __getitem__(self, item) -> ABCStore: ...


class ABCServer(ABC):
    name: str
    path: str
    file: Union[TextIO, BinaryIO]

    databases: dict[str, Type[ABCDataBase]]
    DBs: set[ABCDataBase]

    USERDATA_FILE: str = "Users.json"

    @abstractmethod
    def _file_input_loop(self) -> None:
        """
        运行时逐行读取并执行流
        """

    @abstractmethod
    def _serve(self, conn: SocketIo, name: str) -> None:
        """
        对客户端的服务方法 (在线程中)
        :param conn: 连接到的客户端套接字对象
        :param name: 线程名称
        """

    @staticmethod
    def _recv_loop(self) -> None:
        """
        接受客户端套接字连接请求的循环 (在线程中)
        """

    @abstractmethod
    def log(self, msg: str, level: int) -> None:
        """
        以指定格式输出日志
        :param msg: 日志消息
        :param level: 日志等级
        """

    @abstractmethod
    def _start_thread(self) -> None:
        """
        用于启动线程
        """

    @abstractmethod
    def start(self) -> None:
        """
        启动数据库服务器
        """

    @abstractmethod
    def stop(self) -> None:
        """
        停止数据库服务器
        """

    @abstractmethod
    def restart(self) -> None:
        """
        重启数据库服务器
        """

    @abstractmethod
    def join(self, timeout=None) -> None:
        """
        等待服务器完全关闭
        :param timeout: 超时时间
        """

    @abstractmethod
    def bind(self, __address: Union[tuple[any, ...], str, bytes]) -> None:
        """
        绑定数据库服务器
        :param __address: 绑定到的ip及端口
        """

    @abstractmethod
    def listen(self, __backlog: int) -> None:
        """
        :param __backlog: 最大连接等待数
        """

    @abstractmethod
    def is_alive(self) -> bool:
        """
        检查服务器是否开启
        """

    @abstractmethod
    def __getitem__(self, item) -> ABCDataBase: ...


def BuildPath(path: str):
    path_list = path.split('\\')
    try:
        path_list.remove('')
    except ValueError:
        pass

    temp = ""

    for part in path_list:
        temp += part + '\\'
        try:
            os.mkdir(temp[:-1])
        except FileExistsError:
            pass
