# -*- coding: utf-8 -*-

from .ABC import Event
from .ABC import GetUsers
from .ABC import MKEvent
from .ABC import RegEvent
from .ABC import WriteJson
from ..ABC import ABCServer

USER_NOT_FIND = MKEvent("USER.USER_NOT_FIND")
WRONG_PASSWORD = MKEvent("USER.WRONG_PASSWORD")

USER_ALREADY_EXISTS = MKEvent("USER.USER_ALREADY_EXISTS")


@RegEvent
class RegUser(Event):
    raw = "USER.REG_USER"

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def func(self, server: ABCServer, **_kwargs):
        users = GetUsers(server=server)
        try:
            users[self.username]
        except KeyError:
            pass
        else:
            return USER_ALREADY_EXISTS

        users[self.username] = {"password": self.password}

        WriteJson(server=server, arg=users, file_name=server.USERDATA_FILE)


REG = RegUser


@RegEvent
class ReSetPassword(Event):
    raw = "USER.RESET_PASSWORD"

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def func(self, server: ABCServer, **_kwargs):
        users = GetUsers(server=server)

        if self.username not in users.keys():
            return USER_NOT_FIND
        users[self.username]["password"] = self.password

        WriteJson(server=server, arg=users, file_name=server.USERDATA_FILE)


RESET_PASSWORD = ReSetPassword


@RegEvent
class DelUser(Event):
    raw = "USER.DEL_User"

    def __init__(self, username: str):
        self.username = username

    def func(self, server: ABCServer, **_kwargs):
        users = GetUsers(server=server)
        if self.username not in users.keys():
            return USER_NOT_FIND

        del users[self.username]

        WriteJson(server=server, arg=users, file_name=server.USERDATA_FILE)


DEL = DelUser


__all__ = (
    "USER_NOT_FIND",
    "WRONG_PASSWORD",
    "USER_ALREADY_EXISTS",
    "REG",
    "RESET_PASSWORD",
    "DEL"
)
