# -*- coding: utf-8 -*-
# cython: language_level = 3


__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

from itertools import count
from typing import Optional

from Lib.base_conversion import Base
from dataclasses import dataclass
from datetime import datetime

from PyQt5.QtCore import QSize
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QRect
from PyQt5.QtCore import QMetaObject
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QPushButton
from Ui.BaseWidgets import SmoothlyScrollArea


@dataclass
class MessageData:
    """
    message_uuid: Base
    message: str
    username: str
    time_stamp: float
    """
    message_uuid: Base
    message: str
    username: str
    time_stamp: float


class Message(QWidget):
    def __init__(self, scroll_area, /, *, message_data: MessageData):
        super().__init__(scroll_area)
        self.setMinimumSize(QSize(500, 50))
        geometry = list(self.geometry().getRect())
        geometry[1] = 0
        geometry[3] = 50
        self.setGeometry(QRect(*geometry))
        self.setObjectName("Message")
        self.message_data = message_data
        self.time_label = self.TimeLabel(self, time_stamp=self.message_data.time_stamp)
        self.message = self.ShowMessage(self, message=self.message_data.message)
        self.username_label = self.UsernameLabel(self, username=self.message_data.username)

        self.time_label.move(QPoint(0, 0))
        self.message.move(QPoint(0, 12))
        self.username_label.move(QPoint(0, 22))

    class TimeLabel(QLabel):
        def __init__(self, parent, /, *, time_stamp: float) -> None:
            super().__init__(parent)
            self.resize(QSize(200, 8))
            self.setObjectName("Time")
            self.time_stamp = time_stamp
            self.ReTranslateUi()

        def ReTranslateUi(self):
            _translate = QCoreApplication.translate
            time_format = _translate("TimeLabel", "%Y-%m-%d %H:%M:%S.%f")
            time_str = datetime.fromtimestamp(self.time_stamp).strftime(time_format)
            self.setText(time_str)

    class UsernameLabel(QLabel):
        def __init__(self, parent, /, *, username):
            super().__init__(parent)
            self.resize(QSize(200, 16))
            self.setObjectName("Username")
            self.username = username
            self.setText(self.username)

    class ShowMessage(QLabel):
        def __init__(self, parent, /, *, message):
            super().__init__(parent)
            self.setObjectName("ShowMessage")
            self.message = message
            self.setText(self.message)


class UIChatWindow(object):
    def __init__(self, main_window):
        self.MainWindow = main_window
        self.Getter: Optional[QTextEdit] = None
        self.SendMessageButton: Optional[QPushButton] = None
        self.InputArea: Optional[QWidget] = None
        self.MessageLayout: Optional[QVBoxLayout] = None
        self.MessageScrollContents: Optional[QWidget] = None
        self.MessageArea: Optional[QScrollArea] = None
        self.MainWidget: Optional[QWidget] = None
        self.messages: dict[Base, Message] = {}
        self.count_message = count()

    def add(self, message_data: MessageData):
        msg_obj = Message(self.MessageScrollContents, message_data=message_data)
        msg_obj.resize(self.MessageScrollContents.width(), msg_obj.height())
        msg_obj.show()
        self.MessageLayout.addWidget(msg_obj)
        self.MessageLayout.setStretchFactor(msg_obj, 12)
        self.MessageLayout.setSpacing(0)
        self.MessageLayout.setStretch(next(self.count_message)-1, 1)
        self.messages[message_data.message_uuid] = msg_obj

    def setupUi(self):
        self.MainWindow.setObjectName("MainWindow")
        self.MainWindow.resize(837, 618)
        self.MainWidget = QWidget(self.MainWindow)
        self.MainWidget.setObjectName("MainWidget")

        self.MessageArea = SmoothlyScrollArea(self.MainWidget)
        self.MessageArea.setGeometry(QRect(0, 0, 600, 450))
        # self.MessageArea.setFrameShadow(QtWidgets.QFrame.Raised)
        # # self.MessageArea.setLineWidth(0)
        self.MessageArea.setWidgetResizable(True)
        # self.MessageArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.MessageArea.setObjectName("MessageArea")

        self.MessageScrollContents = QWidget(self.MessageScrollContents)
        self.MessageScrollContents.setGeometry(QRect(0, 0, 599, 449))
        self.MessageScrollContents.setObjectName("MessageScrollContents")

        self.MessageLayout = QVBoxLayout(self.MessageScrollContents)
        self.MessageScrollContents.setLayout(self.MessageLayout)
        self.MessageArea.setWidget(self.MessageScrollContents)

        self.InputArea = QWidget(self.MainWidget)
        self.InputArea.setGeometry(QRect(0, 509, 601, 111))
        self.InputArea.setObjectName("InputArea")

        self.SendMessageButton = QPushButton(self.InputArea)
        self.SendMessageButton.setGeometry(QRect(520, 80, 75, 23))
        self.SendMessageButton.setObjectName("SendMessageButton")

        self.Getter = QTextEdit(self.InputArea)
        self.Getter.setGeometry(QRect(0, 0, 601, 111))
        self.Getter.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
        self.Getter.setFrameShadow(QFrame.Raised)
        self.Getter.setObjectName("Getter")

        self.Getter.raise_()
        self.SendMessageButton.raise_()
        self.MainWindow.setCentralWidget(self.MainWidget)

        self.ReTranslateUi()
        QMetaObject.connectSlotsByName(self.MainWindow)

    def ReTranslateUi(self):
        _translate = QCoreApplication.translate
        self.MainWindow.setWindowTitle(_translate("ChatWindow", "主界面"))
        self.SendMessageButton.setText(_translate("ChatWindow", "发送"))


__all__ = ("UIChatWindow", "MessageData", "Message")
