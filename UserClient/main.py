# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"


import sys
import time

from PyQt5.QtWidgets import QApplication, QMainWindow

from Lib.base_conversion import Base
from Ui.ChatWindow import UIChatWindow, MessageData
from Ui.tools import showException


def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = UIChatWindow(window)
    ui.setupUi()

    @showException
    def clicked(*_):
        txt = str(ui.Getter.toPlainText())
        ui.add(MessageData(Base.from_int(10, 10), txt, "You", time.time()), 15)
        ui.Getter.clear()

    # noinspection PyUnresolvedReferences
    ui.SendMessageButton.clicked.connect(clicked)

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
