# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

from enum import IntEnum
from enum import StrEnum
from typing import override

from AuthenticationSystem.Events.Base import Event
from AuthenticationSystem.Events.Base import EventWithData
from AuthenticationSystem.Events.Base import FailEvent
from AuthenticationSystem.Events.Base import SuccessEvent
from Lib.base_conversion import Base


class _AskData(Event):
    Name = "Login.ASK_DATA"


ASK_DATA = _AskData


class _AckData(EventWithData):
    Name = "Login.ACK_DATA"

    class ClientType(StrEnum):
        Client = "Client"
        ChatServer = "ChatServer"

    def __init__(self, uuid: Base, login_key: str, client_type: ClientType):
        self._uuid = uuid
        self._login_key = login_key
        self._client_type = self.ClientType(client_type)

    @property
    def uuid(self):
        return self._uuid

    @property
    def login_key(self):
        return self._login_key

    @property
    def client_type(self):
        return self._client_type

    @classmethod
    @override
    def load(cls, _json):
        return cls(**_json[cls.Name])

    @override
    def dump(self):
        return {
            self.Name: {
                "uuid": self._uuid,
                "login_key": self._login_key,
                "client_type": self._client_type
            }
        }


ACK_DATA = _AckData


class _TimeOut(Event, FailEvent):
    Name = "Login.LOGIN_TIMEOUT"


LOGIN_TIMEOUT = _TimeOut


class _InvalidClientType(EventWithData, FailEvent):
    Name = "Login.INVALID_CLIENT_TYPE"

    def __init__(self, client_type, need_type):
        self._client_type = client_type
        self._need_type = need_type

    @property
    def client_type(self):
        return self._client_type

    @property
    def need_type(self):
        return self._need_type

    @classmethod
    @override
    def load(cls, _json):
        return cls(**_json[cls.Name])

    @override
    def dump(self):
        return {
            self.Name: {
                "client_type": self._client_type,
                "need_type": self._need_type
            }
        }


INVALID_CLIENT_TYPE = _InvalidClientType


class _LoginSuccess(Event, SuccessEvent):
    Name = "Login.LOGIN_SUCCESS"


SUCCESS = _LoginSuccess()


class _LoginFailed(EventWithData, FailEvent):
    Name = "Login.LOGIN_FAILED"

    class FailType(IntEnum):
        UNKNOWN_SERVER_ERROR = -1
        NOTSET = 0
        INVALID_CLIENT_TYPE = 1
        LOGIN_TIMEOUT = 2
        FAILED_TO_ACQUIRE_DATA = 3
        INVALID_DATA = 4

    def __init__(self, type_=FailType.NOTSET):
        self._type = self.FailType(type_)

    @property
    def type(self):
        return self._type

    @classmethod
    @override
    def load(cls, _json):
        return cls(**_json[cls.Name])

    @override
    def dump(self):
        return {
            self.Name: {
                "info": self._type,
            }
        }


FAILED = _LoginFailed

__all__ = ("ASK_DATA", "ACK_DATA", "LOGIN_TIMEOUT", "INVALID_CLIENT_TYPE", "SUCCESS", "FAILED")
