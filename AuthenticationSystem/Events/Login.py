# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

from enum import StrEnum
from typing import override

from AuthenticationSystem.Events.Base import Event
from AuthenticationSystem.Events.Base import EventWithData
from AuthenticationSystem.Events.Base import FailEvent
from AuthenticationSystem.Events.Base import SuccessEvent
from AuthenticationSystem.Events.Base import EventRegister
from AuthenticationSystem.Serv.Login.Database import LoginKey
from Lib.base_conversion import Base


@EventRegister
class _AskData(Event):
    Name = "Login.ASK_DATA"


ASK_DATA = _AskData


class ClientTypeNotFind(LookupError):
    def __init__(self, client_type: str):
        self._client_type = client_type

    @property
    def client_type(self):
        return self._client_type

    def __str__(self):
        return f"ClientType Not Find (clientType='{self.client_type}')"


@EventRegister
class _AckData(EventWithData):
    Name = "Login.ACK_DATA"

    def __init__(self, uuid: Base, login_key: LoginKey, email: str):
        self._uuid = uuid
        self._login_key = LoginKey(login_key.key, login_key.timeout_timestamp)
        self._email = email

    @property
    def uuid(self):
        return self._uuid

    @property
    def login_key(self):
        return self._login_key

    @property
    def email(self):
        return self._email

    @classmethod
    @override
    def load(cls, _json):
        _json[cls.Name]["uuid"] = Base.fromDict(_json[cls.Name]["uuid"])
        _json[cls.Name]["login_key"] = LoginKey.fromDict(_json[cls.Name]["login_key"])
        return cls(**_json[cls.Name])

    @override
    def dump(self):
        return {
            self.Name: {
                "uuid": self._uuid.toDict(),
                "login_key": self._login_key.toDict(),
                "email": self._email,
            }
        }


ACK_DATA = _AckData


@EventRegister
class _InvalidClientType(EventWithData, FailEvent):
    Name = "Login.INVALID_CLIENT_TYPE"

    def __init__(self, client_type):
        self._client_type = client_type

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
                "client_type": self._client_type,
            }
        }


INVALID_CLIENT_TYPE = _InvalidClientType


@EventRegister
class _LoginSuccess(Event, SuccessEvent):
    Name = "Login.LOGIN_SUCCESS"


SUCCESS = _LoginSuccess()


class FailType(StrEnum):
    UNKNOWN_DATABASE_ERROR = "Unknown Database Error"
    NOTSET = "NotSet"
    FAILED_TO_ACQUIRE_DATA = "Failed to Acquire Data"
    INVALID_DATA = "Invalid Data"
    USER_NOT_FOUND = "User Not Found"
    UNKNOWN_SERVER_ERROR = "Unknown Server Error"


@EventRegister
class _LoginFailed(EventWithData, FailEvent):
    Name = "Login.LOGIN_FAILED"

    def __init__(self, type_: FailType = FailType.NOTSET):
        self._type = FailType(type_)

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


@EventRegister
class _AskVerificationCode(Event):
    Name = "Login.ASK_VERIFICATION_CODE"


ASK_VERIFICATION_CODE = _AskVerificationCode()


@EventRegister
class _AckVerificationCode(EventWithData):
    Name = "Login.ACK_VERIFICATION_CODE"

    def __init__(self, code: str):
        self._code = code

    @property
    def code(self) -> str:
        return self._code

    @classmethod
    @override
    def load(cls, _json):
        return cls(**_json[cls.Name])

    @override
    def dump(self):
        return {
            self.Name: {
                "code": self._code
            }
        }


ACK_VERIFICATION_CODE = _AckVerificationCode


@EventRegister
class _RegisterSuccess(EventWithData, SuccessEvent):
    Name = "Login.REGISTER_SUCCESS"

    def __init__(self, uuid: Base, login_key: LoginKey):
        self._uuid = uuid
        self._login_key = login_key

    @property
    def uuid(self) -> Base:
        return self._uuid

    @property
    def login_key(self) -> LoginKey:
        return self._login_key

    @classmethod
    @override
    def load(cls, _json):
        _json[cls.Name]["uuid"] = Base.fromDict(_json[cls.Name]["uuid"])
        _json[cls.Name]["login_key"] = LoginKey.fromDict(_json[cls.Name]["login_key"])
        return cls(**_json[cls.Name])

    @override
    def dump(self):
        return {
            self.Name: {
                "uuid": self._uuid.toDict(),
                "login_key": self._login_key.toDict(),
            }
        }


REGISTER_SUCCESS = _RegisterSuccess


__all__ = (
    "ASK_DATA",
    "ACK_DATA",
    "INVALID_CLIENT_TYPE",
    "SUCCESS",
    "FailType",
    "FAILED",
    "ASK_VERIFICATION_CODE",
    "ACK_VERIFICATION_CODE",
    "REGISTER_SUCCESS"
)
