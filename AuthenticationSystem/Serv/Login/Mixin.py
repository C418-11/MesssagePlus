# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import time
import uuid
from dataclasses import dataclass
from typing import Optional

from AuthenticationSystem.Events import Login
from AuthenticationSystem.Events.Login import FailType
from AuthenticationSystem.Serv.Login.Database import LoginKey, LoginData
from AuthenticationSystem.Serv.Login.Login import LoginManager
from Lib.SocketIO import Address, SocketIo
from Lib.VerificationCode.Email import verificationSender


@dataclass
class LoginStatus:
    find_user: bool
    loginKey_current: bool
    loginKey_timeout: bool
    password_current: bool
    email_current: bool


class LoginException(Exception):
    def __init__(self, login_status: Optional[LoginStatus], *, uuid_: str, addr: Address):
        self._login_status = login_status
        self._uuid = uuid_
        self._addr = addr

    @property
    def login_status(self):
        return self._login_status

    @property
    def uuid(self):
        return self._uuid

    @property
    def addr(self):
        return self._addr


class UserNotFound(LoginException):

    def __str__(self):
        return f"User Not Found (uuid={self._uuid}, addr={self._addr})"


class UnableSendVerificationCode(LoginException):
    def __init__(self, *, uuid_: str, addr: Address, err, recv: str):
        super().__init__(None, uuid_=uuid_, addr=addr)
        self._err = err
        self._recv = recv

    @property
    def err(self):
        return self._err

    @property
    def recv(self):
        return self._recv

    def __str__(self):
        return (
            f"Unable Send Verification Code"
            f" (addr='{self._addr}', uuid='{self._uuid}', err='{type(self._err)}: {self._err}', recv='{self._recv}')"
        )


class InvalidLoginKey(LoginException):
    def __init__(self, login_status, *, uuid_: str, addr: Address, login_key: str):
        super().__init__(login_status, uuid_=uuid_, addr=addr)
        self._login_key = login_key

    @property
    def login_key(self):
        return self._login_key

    def __str__(self):
        return f"Login Key Doesnt Exist (addr='{self._addr}', uuid='{self._uuid}', login_key='{self._login_key}')"


class LoginKeyTimeout(LoginException):
    def __init__(self, login_status, *, uuid_: str, addr: Address, login_key: str):
        super().__init__(login_status, uuid_=uuid_, addr=addr)
        self._login_key = login_key

    @property
    def login_key(self):
        return self._login_key

    def __str__(self):
        return f"Login Key Timeout (addr='{self._addr}', uuid='{self._uuid}', login_key='{self._login_key}')"


class WrongPassword(LoginException):
    def __str__(self):
        return f"Wrong Password (addr='{self._addr}', uuid='{self._uuid}')"


class WrongVerificationCode(LoginException):
    def __init__(self, *, uuid_: str, addr: Address):
        super().__init__(None, uuid_=uuid_, addr=addr)

    def __str__(self):
        return f"Wrong Verification Code (addr='{self._addr}', uuid='{self._uuid}')"


class LoginMixin(LoginManager):

    def __init__(self, socket: SocketIo, store: str):
        LoginManager.__init__(self, socket, store)

    def login(self):
        log_head = f"[LoginManager.Login]"
        user_datas = self._find_user_in_db(self.userdata.uuid)
        addr = self._cSocket.getpeername()
        _uuid = self.userdata.uuid

        status = LoginStatus(False, False, False, False, False)

        try:
            userdata = user_datas[0]
            status.find_user = True
        except IndexError:
            self._cSocket.send_json(Login.FAILED(FailType.USER_NOT_FOUND).dump())
            self.login_logger.info(f"{log_head} User Not Found (addr={addr}, uuid={_uuid})")
            raise UserNotFound(status, uuid_=_uuid, addr=addr)

        login_key = LoginKey.fromDict(userdata.login_key)

        status.loginKey_current = self.userdata.login_key == login_key
        status.loginKey_timeout = login_key.checkTimeout(time.time() - self.login_Config.loginKeyMaxAllowTimeout)
        status.password_current = self.userdata.password == userdata.password
        status.email_current = self.userdata.email == userdata.email

        if login_key.checkTimeout(time.time()):
            login_key.updateTimeout(time.time() + self.login_Config.loginKeyNextTimeout)
            self.userdata.login_key.updateTimeout(login_key.timeout_timestamp)
            self._write_data_to_db(self.userdata)

        if all([
            status.loginKey_current,
            not status.loginKey_timeout,
            status.password_current,
            status.email_current
        ]):

            self.login_logger.info(
                f"{log_head} Login Success (addr='{addr}', uuid='{_uuid}', userdata={self.userdata})"
            )
            self._cSocket.send_json(Login.SUCCESS.dump())
            return
        elif not status.loginKey_current:
            self.login_logger.info(
                f"{log_head} Login Failed # Invalid Login Key (addr='{addr}', uuid='{_uuid}', userdata={self.userdata})"
            )
            self._cSocket.send_json(Login.FAILED(FailType.INVALID_LOGIN_KEY).dump())
            raise InvalidLoginKey(status, addr=addr, uuid_=_uuid, login_key=self.userdata.login_key)
        elif status.loginKey_timeout:
            self.login_logger.info(
                f"{log_head} Login Failed # Login Key Timeout (addr='{addr}', uuid='{_uuid}', userdata={self.userdata})"
            )
            self._cSocket.send_json(Login.FAILED(FailType.LOGIN_KEY_TIMEOUT).dump())
            raise LoginKeyTimeout(status, addr=addr, uuid_=_uuid, login_key=self.userdata.login_key)
        elif not status.password_current:
            self.login_logger.info(
                f"{log_head} Login Failed # Wrong Password (addr='{addr}', uuid='{_uuid}', userdata={self.userdata})"
            )
            self._cSocket.send_json(Login.FAILED(FailType.WRONG_PASSWORD).dump())
            raise WrongPassword(status, addr=addr, uuid_=_uuid)
        elif not status.email_current:
            self.login_logger.info(
                f"{log_head} Login Failed # Wrong Email (addr='{addr}', uuid='{_uuid}', userdata={self.userdata})"
            )
            self._cSocket.send_json(Login.FAILED(FailType.WRONG_EMAIL).dump())
            raise WrongPassword(status, addr=addr, uuid_=_uuid)
        else:
            self.login_logger.error(f"Unhandled Login Status (addr='{addr}', uuid='{_uuid}', userdata={self.userdata}")
            raise Exception(f"Unhandled Login Status (addr='{addr}', uuid='{_uuid}', userdata={self.userdata})")

    def register(self):
        log_head = f"[LoginManager.Register]"
        addr = self._cSocket.getpeername()
        _uuid = self.userdata.uuid

        try:
            verification_code = verificationSender(self.userdata.email)
        except Exception as err:
            self.login_logger.error(
                f"{log_head} Failed to send the verification code"
                f" (addr='{addr}', uuid={_uuid}, err={type(err).__name__}: {err})"
            )
            self._cSocket.send_json(Login.FAILED(FailType.UNKNOWN_SERVER_ERROR).dump())
            self._cSocket.close()
            raise UnableSendVerificationCode(addr=addr, uuid_=_uuid, err=err, recv=self.userdata.email)

        self.login_logger.info(
            f"{log_head} Send Verification Code"
            f" (addr='{addr}', uuid='{_uuid}', verification_code='{verification_code}')"
        )
        self._cSocket.send_json(Login.ASK_VERIFICATION_CODE.dump())

        old_timeout = self._cSocket.gettimeout()
        self._cSocket.settimeout(None)

        try:
            raw_data = self._cSocket.recv().decode()
            self._cSocket.settimeout(old_timeout)
        except (ConnectionError, EOFError) as err:
            self.login_logger.info(
                f"{log_head} Lost Connect #during wait Login.ACK_VERIFICATION_CODE"
                f" (addr='{addr}', uuid='{_uuid}', reason='{type(err).__name__}: {err}')"
            )
            self._cSocket.close()
            raise

        ver_code = Login.ACK_VERIFICATION_CODE.loadStr(raw_data)
        ver_code: Login.ACK_VERIFICATION_CODE
        if ver_code.code == ''.join(verification_code):
            self.login_logger.info(
                f"{log_head} Register Success "
                f"(addr='{addr}', uuid='{_uuid}', userdata={self.userdata},"
                f" verification_code='{verification_code}')"
            )
            new_key = LoginKey(str(uuid.uuid4()), time.time() + self.login_Config.loginKeyNextTimeout)

            new_data = LoginData(
                uuid=str(self.userdata.uuid),
                uuid_base=self.userdata.uuid.base,
                login_key=new_key.toDict(),
                email=self.userdata.email,
                password=self.userdata.password
            )

            self._write_data_to_db(new_data)
            self._cSocket.send_json(Login.REGISTER_SUCCESS(self.userdata.uuid, new_key).dump())
        else:
            self.login_logger.info(
                f"{log_head} Register Failed # Wrong Verification Code"
                f" (addr='{addr}', uuid='{_uuid}', userdata={self.userdata},"
                f" verification_code='{verification_code}')"
            )
            self._cSocket.send_json(Login.FAILED(FailType.WRONG_VERIFICATION_CODE).dump())
            raise WrongVerificationCode(addr=addr, uuid_=_uuid)


__all__ = (
    "LoginException",
    "UserNotFound",
    "UnableSendVerificationCode",
    "InvalidLoginKey",
    "LoginKeyTimeout",
    "WrongPassword",
    "LoginMixin",
    "WrongVerificationCode",
)
