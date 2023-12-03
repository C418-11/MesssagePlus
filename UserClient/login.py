# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

from enum import StrEnum
from tkinter import messagebox
from typing import Optional

from AuthenticationSystem.Config.UserClient.WebConfig import ClientConfig
from AuthenticationSystem.Events import Login
from AuthenticationSystem.Events.Login import FailType
from AuthenticationSystem.Serv.Login.Database import LoginKey
from AuthenticationSystem.web.Client import Client
from UserClient.Config import Userdata
from Lib.SocketIO import Address
from Lib.base_conversion import Base
from Lib.log import Logging
from Lib.config import Progressbar
from Ui.LoginWindow import UiLoginWindow
from Ui.RegisterWindow import UiRegisterWindow
from Ui.tools import showException
from PyQt5.QtWidgets import QMainWindow, QApplication

import sys

Progressbar.close()


class IllegalEventInContext(Exception):
    def __init__(self, event):
        self.event = event

    def __str__(self):
        return f"An event was received that was not valid in the current login protocol (event={self.event})"


class InvalidClientType(Exception):
    def __init__(self, type_):
        self.type = type_

    def __str__(self):
        return f"Invalid client type (type={self.type})"


class LoginFailed(Exception):
    def __init__(self, type_: FailType, client: Client):
        self.type = type_
        self.client = client

    def __str__(self):
        return f"Login failed (type={self.type})"


class WrongKeyValue(StrEnum):
    UUID = "uuid"
    UUID_BASE = "uuid_base"
    LOGIN_KEY = "login_key"
    LOGIN_KEY_TIMEOUT = "login_key_timeout"
    EMAIL = "email"
    PASSWORD = "password"


class WrongInConfig(Exception):
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return f"Wrong in config (key={self.key})"


class LoginAuthenticationSystem:
    Config = ClientConfig.Client
    Userdata = Userdata.UserData
    logger = Logging.Logger(output_level=Config.log_level, file=Config.log_files[0], warn_file=Config.log_files[1])

    def __init__(self):
        self.app = QApplication(sys.argv)
        main_window = QMainWindow()
        self.ui = UiLoginWindow(main_window)
        self.ui.setupUi()
        self.main_window = main_window

    def check_config(self):
        if not isinstance(self.Userdata.uuid, str):
            raise WrongInConfig(WrongKeyValue.UUID)
        if not isinstance(self.Userdata.uuid_base, int):
            raise WrongInConfig(WrongKeyValue.UUID_BASE)

        if not isinstance(self.Userdata.login_key, str):
            raise WrongInConfig(WrongKeyValue.LOGIN_KEY)

        if not isinstance(self.Userdata.login_key_timeout, float):
            raise WrongInConfig(WrongKeyValue.LOGIN_KEY_TIMEOUT)

        if not isinstance(self.Userdata.email, str):
            raise WrongInConfig(WrongKeyValue.EMAIL)

        if not isinstance(self.Userdata.password, str):
            raise WrongInConfig(WrongKeyValue.PASSWORD)

    def get_client(self, log_head):
        try:
            client = Client(Address(*self.Config.address))
        except ConnectionRefusedError as err:
            self.logger.error(
                f"{log_head} Connection refused #"
                f" The configured authentication server may not be online (err={err})"
            )

            messagebox.showerror(
                "Error",
                "Failed to connect to the authentication server (Check the configuration file)"
            )
            raise err
        init = client.init("Client", self.Config.login_timeout)
        event = next(init).decode()
        event: str

        if Login.INVALID_CLIENT_TYPE.eq_str(event):
            client_type = Login.INVALID_CLIENT_TYPE.loadStr(event).client_type
            self.logger.error(
                f"{log_head} The authentication client service type you selected is not available on this "
                f"authentication server (client_type={client_type})"
            )
            raise InvalidClientType(client_type)

        if not Login.ASK_DATA.eq_str(event):
            self.logger.error(
                f"{log_head} An event was received that was not valid in the current login protocol"
                f" (event={event})"
            )
            raise IllegalEventInContext(event)
        return init, client

    def login(self):
        log_head = "[Login AuthenticationSystem]"
        self.logger.info(f"{log_head} Start login authentication system")

        try:
            self.check_config()
        except WrongInConfig:
            self.register()

        init, client = self.get_client(log_head)

        event = (init.send(
            Login.ACK_DATA(
                uuid=Base(self.Userdata.uuid, self.Userdata.uuid_base),
                login_key=LoginKey(
                    self.Userdata.login_key,
                    self.Userdata.login_key_timeout,
                ),
                email=self.Userdata.email,
                password=self.Userdata.password
            )
        )).decode()
        event: str

        if Login.FAILED.eq_str(event):
            print(event)
            failed_type = Login.FAILED.loadStr(event).type
            failed_type: FailType
            if failed_type == FailType.WRONG_PASSWORD:
                self.logger.error(f"{log_head} Connection fail # Wrong password (pw='{self.Userdata.password}')")

            raise LoginFailed(failed_type, client)

        if not Login.SUCCESS.eq_str(event):
            raise ValueError(f"An event was received that was not valid in the current login protocol (event={event})")

        try:
            next(init)
        except StopIteration:
            pass
        self.logger.info(f"{log_head} Login success (uuid='{self.Userdata.uuid}')")
        return client

    @showException
    def on_register(self, register_window, client, log_head, *_, **__):
        if client is None:
            password = register_window.GetPassword.text()
            password: str
            if len(password) < 8:
                return
            email = register_window.GetEmail.text()
            email: str
            if len(email) < 5:
                return
            if '@' not in email:
                return

            init, client = self.get_client(log_head)

            event = (init.send(
                Login.ACK_DATA(
                    uuid=Base('-404', 36),
                    login_key=LoginKey(
                        '-404',
                        -404,
                    ),
                    email=email,
                    password=password
                )
            )).decode()
            event: str

            print(event)

            try:
                next(init)
            except StopIteration:
                pass

            client.send_json(Login.REGISTER.dump())
            try:
                print(client.recv())
            except Exception as err:
                client.close()
                print(err)

            register_window.GetEmail.setEnabled(False)
            register_window.GetPassword.setEnabled(False)
            register_window.GetVerificationCode.setEnabled(True)
            return client

        verification_code: str = register_window.GetVerificationCode.text()
        if len(verification_code) != 6:
            return
        try:
            client.send_json(Login.ACK_VERIFICATION_CODE(verification_code).dump())
        except Exception as _err:
            print(_err)
            client.close()
            self.app.exit(0)
        self.app.exit(0)
        return client

    def register(self) -> None:
        log_head = "[Register AuthenticationSystem]"
        self.logger.info(f"{log_head} Start register authentication system")

        register_window = UiRegisterWindow(self.main_window)
        register_window.setupUi()
        client: Optional[Client] = None

        def reg_wrapper():
            def func() -> None:
                nonlocal client
                client = self.on_register(register_window, client, log_head)
            return func

        self.main_window.show()

        register_window.RegisterButton.clicked.connect(reg_wrapper())
        ret_code = self.app.exec_()
        if ret_code != 0:
            sys.exit(ret_code)

        email = register_window.GetEmail.text()
        password = register_window.GetPassword.text()

        try:
            reg_success_event = Login.REGISTER_SUCCESS.loadStr(client.recv())
            reg_success_event: Login.REGISTER_SUCCESS
            key = list(self.Userdata.data_to_write.keys())[0]
            new_data = {
                "uuid": reg_success_event.uuid.toString(),
                "uuid_base": reg_success_event.uuid.base,
                "login_key": reg_success_event.login_key.key,
                "login_key_timeout": reg_success_event.login_key.timeout_timestamp,
                "email": email,
                "password": password
            }
            self.Userdata.data_to_write[key]["data"] = new_data
            self.Userdata.save()
        except Exception as err:
            client.close()
            raise err


__all__ = ("LoginAuthenticationSystem",)
