# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import sys
import time

from PyQt5.QtWidgets import QApplication, QMainWindow

from Lib.base_conversion import Base
from Ui.ChatWindow import UiChatWindow, MessageData
from Ui.LoginWindow import UiLoginWindow
from Ui.RegisterWindow import UiRegisterWindow
from Ui.tools import showException
from UserClient.login import LoginAuthenticationSystem, ReCallFunc


def chat_window():
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = UiChatWindow(window)
    ui.setupUi()

    @showException
    def clicked(*_):
        txt = str(ui.InputArea.Getter.toPlainText())
        ui.MessageArea.add(MessageData(Base.fromInt(10, 10), txt, "You", time.time()), 15)
        ui.InputArea.Getter.clear()

    # noinspection PyUnresolvedReferences
    ui.InputArea.SendMessageButton.clicked.connect(clicked)

    window.show()
    sys.exit(app.exec_())


def login_window():
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = UiLoginWindow(window)
    ui.setupUi()

    window.show()
    sys.exit(app.exec_())


def register_window():
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = UiRegisterWindow(window)
    ui.setupUi()

    window.show()
    sys.exit(app.exec_())


def main():
    # login_window()
    # register_window()
    # chat_window()
    login = LoginAuthenticationSystem()
    try:
        login.login()
    except ReCallFunc:
        login.login()


if __name__ == "__main__":
    main()
