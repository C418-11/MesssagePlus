# -*- coding: utf-8 -*-
# cython: language_level = 3


__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"


from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtWidgets, QtGui


class Message(QtWidgets.QWidget):
    def __init__(self, scroll_area):
        super().__init__(scroll_area)

        geometry = list(self.geometry().getRect())
        geometry[1] = 0
        geometry[3] = 30
        self.setGeometry(QtCore.QRect(*geometry))
        self.setObjectName("Message")

    class TimeLabel(QtWidgets.QLabel):
        def __init__(self, parent, time_stamp):
            super().__init__(parent)
            self.setGeometry(QtCore.QRect(0, 0, 71, 16))
            self.setObjectName("Time")
            self.setText(datetime.fromtimestamp(time_stamp).strftime("%Y-%m-%d %H:%M:%S.%f"))

    class UsernameLabel(QtWidgets.QLabel):
        def __init__(self, parent):
            super().__init__(parent)
            self.setGeometry(QtCore.QRect(260, 0, 71, 16))
            self.setObjectName("Username")

    class ShowMessage(QtWidgets.QGraphicsView):
        def __init__(self, parent):
            super().__init__(parent)
            self.setGeometry(QtCore.QRect(0, 0, 601, 61))
            self.setStyleSheet("background:rgba(0, 0, 0, 0);")
            self.setFrameShadow(QtWidgets.QFrame.Raised)
            self.setObjectName("ShowMessage")
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setRenderHints(QtGui.QPainter.Antialiasing)


class UIChatWindow(object):
    def __init__(self, main_window):
        self.MainWindow = main_window
        self.InputShow = None
        self.SendMessageButton = None
        self.InputArea = None
        self.scrollAreaWidgetContents = None
        self.MessageArea = None
        self.MainWidget = None

    def setupUi(self):
        self.MainWindow.setObjectName("MainWindow")
        self.MainWindow.resize(837, 618)
        self.MainWidget = QtWidgets.QWidget(self.MainWindow)
        self.MainWidget.setObjectName("MainWidget")

        self.MessageArea = QtWidgets.QScrollArea(self.MainWidget)
        self.MessageArea.setGeometry(QtCore.QRect(0, 40, 600, 450))
        self.MessageArea.setFrameShadow(QtWidgets.QFrame.Raised)
        self.MessageArea.setLineWidth(0)
        self.MessageArea.setWidgetResizable(True)
        self.MessageArea.setObjectName("MessageArea")

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 599, 449))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        self.MessageArea.setWidget(self.scrollAreaWidgetContents)
        self.InputArea = QtWidgets.QWidget(self.MainWidget)
        self.InputArea.setGeometry(QtCore.QRect(0, 509, 601, 111))
        self.InputArea.setObjectName("InputArea")

        self.SendMessageButton = QtWidgets.QPushButton(self.InputArea)
        self.SendMessageButton.setGeometry(QtCore.QRect(520, 80, 75, 23))
        self.SendMessageButton.setObjectName("SendMessageButton")

        self.InputShow = QtWidgets.QGraphicsView(self.InputArea)
        self.InputShow.setGeometry(QtCore.QRect(0, 0, 601, 111))
        self.InputShow.setStyleSheet("background:rgba(0, 0, 0, 0);")
        self.InputShow.setFrameShadow(QtWidgets.QFrame.Raised)
        self.InputShow.setObjectName("InputShow")

        self.InputShow.raise_()
        self.SendMessageButton.raise_()
        self.MainWindow.setCentralWidget(self.MainWidget)

        self.ReTranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)

    def ReTranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.MainWindow.setWindowTitle(_translate("MainWindow", "主界面"))
        self.SendMessageButton.setText(_translate("MainWindow", "发送"))


__all__ = ("UIChatWindow",)
