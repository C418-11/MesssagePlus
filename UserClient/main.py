# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"


import sys
import time

from Lib.base_conversion import Base
from Ui.tools import showException
from PyQt5.QtWidgets import QApplication, QMainWindow
from Ui.ChatWindow import UIChatWindow, MessageData


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
