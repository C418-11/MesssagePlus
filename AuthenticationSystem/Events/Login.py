# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

from enum import IntEnum

from AuthenticationSystem.Events.Base import Event, EventWithData, SuccessEvent, FailEvent


class _AskData(Event):
    Name = "Login.ASK_DATA"


ASK_DATA = _AskData


class _AckData(EventWithData):
    Name = "Login.ACK_DATA"

    def __init__(self, uuid, login_key, client_type):
        self._uuid = uuid
        self._login_key = login_key
        self._client_type = client_type

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
    def load(cls, _json):
        return cls(**_json[cls.Name])

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
    def load(cls, _json):
        return cls(**_json[cls.Name])

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

    class TYPE(IntEnum):
        UNKNOWN_SERVER_ERROR = -1
        NOTSET = 0
        INVALID_CLIENT_TYPE = 1
        LOGIN_TIMEOUT = 2
        FAILED_TO_ACQUIRE_DATA = 3
        INVALID_DATA = 4

    def __init__(self, info=TYPE.NOTSET):
        self._info = info

    @property
    def info(self):
        return self._info

    @classmethod
    def load(cls, _json):
        return cls(**_json[cls.Name])

    def dump(self):
        return {
            self.Name: {
                "info": self._info,
            }
        }


FAILED = _LoginFailed

__all__ = ("ASK_DATA", "ACK_DATA", "LOGIN_TIMEOUT", "INVALID_CLIENT_TYPE", "SUCCESS", "FAILED")
