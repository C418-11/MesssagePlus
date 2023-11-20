# -*- coding: utf-8 -*-
# cython: language_level = 3


__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

from dataclasses import dataclass
from datetime import datetime
from itertools import count
from typing import Optional, Union

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtCore import QMetaObject
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from Lib.base_conversion import Base
from Ui.BaseWidgets import RoundShadow
from Ui.BaseWidgets import SmoothlyScrollArea
from Ui.tools import add_line_breaks


@dataclass
class MessageData:
    """
    message_uuid: Base
    message: str
    username: str
    time_stamp: float
    font: Optional[Union[str, QFont]] = None
    """
    message_uuid: Base
    message: str
    username: str
    time_stamp: float
    font: Optional[Union[str, QFont]] = None


class Message(RoundShadow, QWidget):
    def __init__(self, scroll_area: QWidget, /, *, message_data: MessageData):
        super().__init__(scroll_area)

        self.setObjectName("Message")
        self.message_data = message_data

        width = scroll_area.width()
        self.setMaximumWidth(width)
        self.setMinimumWidth(width)
        width -= 10
        self.username_label = self.UsernameLabel(
            self,
            width=width,
            username=self.message_data.username,
            font=message_data.font
        )
        self.time_label = self.TimeLabel(
            self,
            width=width,
            time_stamp=self.message_data.time_stamp,
            font=message_data.font
        )
        self.message = self.ShowMessage(
            self,
            width=width,
            message=self.message_data.message,
            font=message_data.font
        )

        self.username_label.setAlignment(Qt.AlignCenter)
        self.time_label.setAlignment(Qt.AlignCenter)

        self.username_label.move(QPoint(10, 0))
        self.time_label.move(QPoint(10, self.username_label.height()))
        self.message.move(QPoint(10, self.time_label.y() + self.time_label.height()))

        min_height = self.time_label.height() + self.username_label.height() + self.message.height()
        self.setMinimumHeight(min_height)
        self.background_rect = QRect(self.x(), self.y(), width-10, min_height)

    class TimeLabel(QLabel):
        def __init__(self, parent: QWidget, /, *, time_stamp: float, width: int, font: QFont) -> None:
            super().__init__(parent)
            self.setObjectName("Time")
            self.time_stamp = time_stamp
            self.size_width = width
            if font is not None:
                self.setFont(font)
            self.ReTranslateUi()
            self.RefreshSize()

        def ReTranslateUi(self):
            _translate = QCoreApplication.translate
            time_format = _translate("TimeLabel", "%Y-%m-%d %H:%M:%S.%f")
            time_str = datetime.fromtimestamp(self.time_stamp).strftime(time_format)

            self.setText(time_str)

        def RefreshSize(self):
            min_size = self.fontMetrics().size(Qt.TextExpandTabs, self.text())
            self.resize(self.size_width, min_size.height())

    class UsernameLabel(QLabel):
        def __init__(self, parent: QWidget, /, *, username, width: int, font: QFont):
            super().__init__(parent)
            self.setObjectName("Username")
            self.username = username
            self.size_width = width
            if font is not None:
                self.setFont(font)

            self.setText(self.username)
            self.RefreshSize()

        def RefreshSize(self):
            min_size = self.fontMetrics().size(Qt.TextExpandTabs, self.text())
            self.resize(self.size_width, min_size.height())

    class ShowMessage(QLabel):
        def __init__(self, parent: QWidget, /, *, message: str, width: int, font: QFont):
            super().__init__(parent)
            self.setObjectName("ShowMessage")
            self.raw_message = message
            self.size_width = width-50

            if font is not None:
                self.setFont(font)

            self.message = add_line_breaks(self.raw_message, self.size_width, self.fontMetrics())
            self.RefreshSize()

            self.setText(self.message)

        def RefreshSize(self):
            min_size = self.fontMetrics().size(Qt.TextExpandTabs, self.message)
            self.resize(min_size.width(), min_size.height())


class UIChatWindow(object):
    def __init__(self, main_window: QMainWindow):
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

    def add(self, message_data: MessageData, spacing: int = 0):
        msg_obj = Message(self.MessageScrollContents, message_data=message_data)
        msg_obj.resize(self.MessageScrollContents.width(), msg_obj.height())
        msg_obj.show()
        self.MessageLayout.addWidget(msg_obj)
        self.MessageLayout.setStretchFactor(msg_obj, 12)
        self.MessageLayout.setSpacing(spacing)
        self.MessageLayout.setStretch(next(self.count_message)-1, 1)
        self.messages[message_data.message_uuid] = msg_obj

    def setupUi(self):
        self.MainWindow.setObjectName("MainWindow")
        self.MainWindow.resize(837, 618)
        self.MainWidget = QWidget(self.MainWindow)
        self.MainWidget.setObjectName("MainWidget")

        self.MessageArea = SmoothlyScrollArea(self.MainWidget)
        self.MessageArea.setGeometry(QRect(0, 0, 600, 450))
        # self.MessageArea.setFrameShadow(QFrame.Raised)
        self.MessageArea.setWidgetResizable(True)
        self.MessageArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.MessageArea.setObjectName("MessageArea")

        self.MessageScrollContents = QWidget(self.MessageScrollContents)
        self.MessageScrollContents.setMaximumWidth(self.MessageArea.width()-2)
        self.MessageScrollContents.setMinimumWidth(self.MessageArea.width()-2)
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
