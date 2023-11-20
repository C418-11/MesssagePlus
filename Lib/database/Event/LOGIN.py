# -*- coding: utf-8 -*-
# cython: language_level = 3
from typing import override

from .ABC import Event
from .ABC import GetUsers
from .ABC import MKEvent
from .ABC import RegEvent
from .ABC import RunFailed
from .ABC import RunSuccess
from .USER import USER_NOT_FIND
from .USER import WRONG_PASSWORD
from ..ABC import ABCServer
from ..logging import INFO


class LoginSuccess(RunSuccess):
    raw = "LOGIN.LOGIN_SUCCESS"


LOGIN_SUCCESS = LoginSuccess()


class LoginFailed(RunFailed):
    raw = "LOGIN.LOGIN_FAILED"


LOGIN_FAILED = LoginFailed()


@RegEvent
class AckUserAndPassword(Event):
    raw = "LOGIN.ACK_USER_AND_PASSWORD"

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    @override
    def func(self, server: ABCServer, **_kwargs):
        """
        :return: USER_NOT_FIND | WRONG_PASSWORD | LOGIN_SUCCESS
        """

        server.log(msg=f"{self.username} Try Login username={self.username} password={self.password}", level=INFO)

        users = GetUsers(server=server)

        if self.username not in users.keys():  # 判断是否有此账户
            return USER_NOT_FIND

        user_info = users[self.username]
        user_info: dict

        if self.password != user_info["password"]:  # 判断密码是否正确
            return WRONG_PASSWORD

        server.log(msg=f"{self.username} Success Login username={self.username} info={user_info}", level=INFO)
        return LOGIN_SUCCESS


ACK_USER_AND_PASSWORD = AckUserAndPassword

ASK_USER_AND_PASSWORD = MKEvent("LOGIN.ASK_USER_AND_PASSWORD")
ASK_USER_AND_PASSWORD_TIMEOUT = MKEvent("LOGIN.ASK_USER_AND_PASSWORD_TIMEOUT")

__all__ = ("LOGIN_SUCCESS", "LoginFailed", "ACK_USER_AND_PASSWORD", "ASK_USER_AND_PASSWORD",
           "ASK_USER_AND_PASSWORD_TIMEOUT")
