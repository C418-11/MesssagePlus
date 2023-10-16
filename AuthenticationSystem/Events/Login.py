# -*- coding: utf-8 -*-

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"


from AuthenticationSystem.Events.Base import Event, EventWithData


class _AskData(Event):
    Name = "Login.ASK_DATA"


ASK_DATA = _AskData


class _AckData(EventWithData):
    Name = "Login.ACK_DATA"

    def __init__(self, name, login_key, client_type):
        self._name = name
        self._login_key = login_key
        self._client_type = client_type

    @property
    def name(self):
        return self._name

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
                "name": self._name,
                "login_key": self._login_key,
                "client_type": self._client_type
            }
        }


ACK_DATA = _AckData


class _TimeOut(Event):
    Name = "Login.LOGIN_TIMEOUT"


LOGIN_TIMEOUT = _TimeOut


__all__ = ("ASK_DATA", "ACK_DATA", "LOGIN_TIMEOUT")
