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


def verificationSender(recv: str):
    code = str(uuid.uuid3(uuid.NAMESPACE_DNS, recv))
    code = random.choices(code, k=6)

    for x in range(len(code)):
        if int(random.random() + 0.5):
            code[x] = code[x].upper()

    code_str = ''.join(code)

    with open(r"F:\Message_Plus\Resource\AuthenticationServer\EmailTemplate.html", "r", encoding="utf-8") as f:
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
        return code
    except Exception:
        raise


def main():
    pass


if __name__ == '__main__':
    main()


__all__ = ("verificationSender", )
