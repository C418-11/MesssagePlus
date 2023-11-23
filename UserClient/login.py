# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import time

from AuthenticationSystem.Config.UserClient.WebConfig import ClientConfig
from AuthenticationSystem.Events import Login
from AuthenticationSystem.Events.Login import ACK_DATA
from AuthenticationSystem.Serv.Login.Database import LoginKey
from AuthenticationSystem.web.Client import Client
from Lib.SocketIO import Address
from Lib.base_conversion import Base
from Lib.log import Logging


class LoginAuthenticationSystem:
    Config = ClientConfig.Client
    logger = Logging.Logger(output_level=Config.log_level, file=Config.log_files[0], warn_file=Config.log_files[1])

    def __init__(self, uuid, password):
        print(self.Config.data)
        # todo

    def login(self):
        log_head = "[Login AuthenticationSystem]"
        self.logger.info(f"{log_head} Start login authentication system")
        c = Client(Address(*self.Config.address))
        init = c.init("Client", self.Config.login_timeout)
        event = next(init)
        if not isinstance(event, Login.ASK_DATA):
            c.close()

        print(init.send(
            ACK_DATA(
                uuid=Base("abc", 36),
                login_key=LoginKey("123", time.time() - 50),
                email="553515788@qq.com"
            )
        ))

        try:
            next(init)
        except StopIteration:
            pass

        print(c.recv())
        c.send_json(Login.ACK_VERIFICATION_CODE(input()).dump())
        while True:
            try:
                print(c.recv())
            except (TimeoutError, ConnectionError, EOFError):
                break
        c.close()


__all__ = ("main",)
