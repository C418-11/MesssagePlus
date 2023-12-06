# -*- coding: utf-8 -*-
# cython: language_level = 3


__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import time
from dataclasses import dataclass
from datetime import datetime
from itertools import count
from typing import Optional, Union

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QMetaObject
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QFont, QResizeEvent
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from Lib.base_conversion import Base
from Ui.BaseWidgets import RoundShadow
from Ui.BaseWidgets import SmoothlyScrollArea
from Ui.BaseWidgets import GetScale
from Ui.tools import add_line_breaks


class InputArea(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.Getter: Optional[QTextEdit] = None
        self.SendMessageButton: Optional[QPushButton] = None

        self.setObjectName("InputArea")
        self.SendMessageButton = QPushButton(self)
        self.SendMessageButton.setGeometry(QRect(520, 80, 75, 23))
        self.SendMessageButton.setObjectName("SendMessageButton")

        self.Getter = QTextEdit(self)
        self.Getter.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
        self.Getter.setFrameShadow(QFrame.Raised)
        self.Getter.setObjectName("Getter")

        self.SendMessageButton.raise_()

        self.ReTranslateUi()

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self.Getter.resize(event.size())

        width = event.size().width() - self.SendMessageButton.width() - 10
        height = event.size().height() - self.SendMessageButton.height() - 8
        self.SendMessageButton.move(width, height)

    def ReTranslateUi(self):
        _translate = QCoreApplication.translate
        self.SendMessageButton.setText(_translate("InputArea", "发送"))


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

        self.username_label.move(QPoint(10, 5))
        self.time_label.move(QPoint(10, self.username_label.height() + self.username_label.y()))
        self.message.move(QPoint(10, self.time_label.y() + self.time_label.height()))

        self.refreshSize()

    def refreshSize(self):
        width = self.parent().width()
        self.setMaximumWidth(width)
        self.setMinimumWidth(width)
        width -= 30
        self.background_rect.setWidth(width)

        self.message.resize(width, self.message.height())
        self.time_label.resize(width, self.time_label.height())
        self.username_label.resize(width, self.username_label.height())

        min_height = self.time_label.height() + self.username_label.height() + self.message.height()
        min_height += 10
        self.setMinimumHeight(min_height)
        self.background_rect.setHeight(min_height)

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

        def resizeEvent(self, event: QResizeEvent):
            self.size_width = event.size().width()
            super().resizeEvent(event)

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

        def resizeEvent(self, event: QResizeEvent):
            self.size_width = event.size().width()
            super().resizeEvent(event)

        def RefreshSize(self):
            min_size = self.fontMetrics().size(Qt.TextExpandTabs, self.text())
            self.resize(self.size_width, min_size.height())

    class ShowMessage(QLabel):
        def __init__(self, parent: QWidget, /, *, message: str, width: int, font: QFont):
            super().__init__(parent)
            self.setObjectName("ShowMessage")
            self.raw_message = message
            self.size_width = width

            if font is not None:
                self.setFont(font)

            self.message: Optional[str] = None

            self.RefreshText()

        def resizeEvent(self, event: QResizeEvent):
            if self.width() == self.size_width:
                return
            self.size_width = event.size().width()
            self.RefreshText()

        def RefreshSize(self):
            min_size = self.fontMetrics().size(Qt.TextExpandTabs, self.message)
            self.resize(self.size_width, min_size.height())

        def RefreshText(self):
            self.message = add_line_breaks(self.raw_message, self.size_width - 20, self.fontMetrics())
            self.setText(self.message)
            self.RefreshSize()


class MessageArea(SmoothlyScrollArea):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.messages: list[Message] = []
        self.count_message = count()

        self.MessageScrollContents = QWidget(self)
        self.MessageScrollContents.setMaximumWidth(self.width() - 2)
        self.MessageScrollContents.setMinimumWidth(self.width() - 2)
        self.MessageScrollContents.setObjectName("MessageScrollContents")

        self.MessageLayout = QVBoxLayout(self.MessageScrollContents)
        self.MessageScrollContents.setLayout(self.MessageLayout)
        self.setWidget(self.MessageScrollContents)

        # self.setFrameShadow(QFrame.Raised)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setObjectName("MessageArea")

    def resizeEvent(self, event: QResizeEvent):
        self.MessageScrollContents.setMaximumWidth(self.width() - 2)
        self.MessageScrollContents.setMinimumWidth(self.width() - 2)
        super().resizeEvent(event)

        for x in self.messages:
            x.refreshSize()

    def add(self, message_data: MessageData, spacing: int = 0):
        msg_obj = Message(self.MessageScrollContents, message_data=message_data)
        msg_obj.resize(self.MessageScrollContents.width(), msg_obj.height())
        msg_obj.show()
        self.MessageLayout.addWidget(msg_obj)
        self.MessageLayout.setStretchFactor(msg_obj, 12)
        self.MessageLayout.setSpacing(spacing)
        self.MessageLayout.setStretch(next(self.count_message) - 1, 1)
        self.messages.append(msg_obj)


class UiChatWindow(object):
    def __init__(self, main_window: QMainWindow):
        self.main_window = main_window

        self.InputArea: Optional[InputArea] = None
        self.MessageArea: Optional[MessageArea] = None

        self.centralWidget: Optional[GetScale] = None

    def setupUi(self):
        self.main_window.setMinimumSize(700, 500)

        self.centralWidget = GetScale(self.main_window)
        self.centralWidget.setObjectName("centralWidget")

        self.MessageArea = MessageArea(self.centralWidget)
        self.InputArea = InputArea(self.centralWidget)

        self.main_window.setCentralWidget(self.centralWidget)

        self.centralWidget.scaleChanged.connect(self.autoResize)

        QMetaObject.connectSlotsByName(self.main_window)

    def autoResize(self, scale_width: float, scale_height: float):
        self.MessageArea.resize(int(500 * scale_width), int(410 * scale_height))
        self.InputArea.move(0, self.MessageArea.height())
        self.InputArea.resize(int(500*scale_width), int(90*scale_height))


__all__ = ("UiChatWindow", "MessageData", "Message")
