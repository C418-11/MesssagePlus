# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import random
import smtplib
import uuid
from email.header import Header
from email.mime.text import MIMEText

from AuthenticationSystem.Config.Server import APIConfig

config = APIConfig.Verification


class APIUserPasswordNotConfigured(ValueError):
    def __str__(self):
        return "The API user or password is not configured"


if not config.userEmail or not config.userPassword:
    raise APIUserPasswordNotConfigured()


def verificationSender(recv: str) -> list[str]:
    ls = [str(uuid.uuid4()) for _ in range(3)]
    code_ls = random.choices(''.join(ls), k=6)
    code_ls: list[str]

    for x in range(len(code_ls)):
        if int(random.random() + 0.5):
            code_ls[x] = code_ls[x].upper()
            if code_ls[x] == "-":
                code_ls[x] = "+"

    code_str = ''.join(code_ls)

    with open(config.emailTemplate, "r", encoding="utf-8") as f:
        msg_str = f.read()

    msg_str = msg_str.replace("{{captcha_text}}", code_str)
    msg_str = msg_str.replace("{{email}}", recv)

    message = MIMEText(msg_str, _subtype="html", _charset="utf-8")
    message["From"] = Header(f"MessagePlus 官方账号<{config.userEmail}>", charset="utf-8")
    message["To"] = Header(recv, charset="utf-8")
    message["Subject"] = Header("MessagePlus: 您的一次性代码", charset="utf-8")

    try:
        with smtplib.SMTP() as smtp_obj:
            smtp_obj.connect(*config.smtpAddr)
            smtp_obj.login(config.userEmail, config.userPassword)
            smtp_obj.sendmail(config.userEmail, recv, message.as_string())
        return code_ls
    except Exception:
        raise


def main():
    pass


if __name__ == '__main__':
    main()

__all__ = ("verificationSender",)
