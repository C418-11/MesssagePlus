# -*- coding: utf-8 -*-

import json
from typing import Union
from .BaseEventType import ABCEvent
from .BaseEventType import SuccessEvent
from .BaseEventType import FailedEvent
from ..ABC import ABCServer


class Event(ABCEvent):
    raw: str

    def __str__(self) -> str:
        """
        :return: 事件名
        """
        return self.raw

    def __repr__(self) -> str:
        """
        :return: 事件名
        """
        return self.raw

    def __eq__(self, other) -> bool:
        """
        :param other: 另一个事件
        :return: 是否相等
        """
        return self.raw == str(other)

    def __hash__(self) -> int:
        """
        :return: 哈希值
        """
        return hash(self.raw)

    def func(self, server: ABCServer, **_kwargs):
        """
        :param server: 数据库服务器
        """
        raise AttributeError(f"type object '{self.__name__}' has no attribute 'func'")


def MKEvent(name: str) -> Event:
    event = Event()
    event.raw = name
    return event


class RunSuccess(Event, SuccessEvent):
    raw = "EVENT.RUN_SUCCESS"

    def __eq__(self, other):
        return isinstance(other, type(self))


RUN_SUCCESS = RunSuccess()


class RunFailed(Event, FailedEvent):
    raw = "EVENT.RUN_FAILED"

    def __eq__(self, other):
        return isinstance(other, type(self))


RUN_FAILED = RunFailed()


def WriteJson(server: ABCServer, arg: dict, file_name: str):
    data = json.dumps(arg, indent=4)
    with open(server.path + file_name, encoding='utf-8', mode='w', newline='\n') as file:
        file.write(data)


def GetUsers(server: ABCServer) -> Union[dict, str]:
    """
    :param server: 数据库服务器
    :return: 用户注册表对象
    """

    try:
        users = json.load(open(server.path + server.USERDATA_FILE, encoding='utf-8', mode='r'))  # 加载用户名单
        return users
    except FileNotFoundError:
        WriteJson(server=server, arg={"default": {"password": "default"}}, file_name=server.USERDATA_FILE)

        users = json.load(open(server.path + server.USERDATA_FILE, encoding='utf-8', mode='r'))  # 加载用户名单
        return users


__EventToFunc = {}


def RegEvent(cls: Event):
    __EventToFunc[cls.raw] = cls.func
    return cls


EVENT_NOT_FIND = MKEvent("EVENT.EVENT_NOT_FIND")


def EventToFunc(event: Event, server: ABCServer = None, run: bool = False, **kwargs):
    try:
        func = __EventToFunc[event.raw]
    except KeyError:
        return EVENT_NOT_FIND
    except AttributeError:
        return EVENT_NOT_FIND
    if run:
        ret = func(self=event, server=server, **kwargs)
        if ret is None:
            ret = RUN_SUCCESS
        return ret
    return func


__all__ = (
    "Event",
    "MKEvent",
    "RunSuccess",
    "RUN_SUCCESS",
    "RunFailed",
    "RUN_FAILED",
    "WriteJson",
    "GetUsers",
    "RegEvent",
    "EVENT_NOT_FIND",
    "EventToFunc"
)
