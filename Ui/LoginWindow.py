# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow


class UiLoginWindow(object):
    def __init__(self, main_window: QMainWindow):
        self.main_window = main_window
        self.Title = None
        self.GetUUID = None
        self.GetPassword = None
        self.centralWidget = None

    def setupUi(self):
        self.centralWidget = QtWidgets.QWidget(self.main_window)
        self.centralWidget.setObjectName("centralWidget")

        self.GetUUID = QtWidgets.QLineEdit(self.centralWidget)
        self.GetUUID.setGeometry(QtCore.QRect(330, 300, 171, 21))
        self.GetUUID.setMaxLength(20)
        self.GetUUID.setObjectName("GetUUID")

        self.GetPassword = QtWidgets.QLineEdit(self.centralWidget)
        self.GetPassword.setGeometry(QtCore.QRect(330, 340, 171, 21))
        self.GetPassword.setMaxLength(20)
        self.GetPassword.setObjectName("GetPassword")
        self.GetPassword.setEchoMode(QtWidgets.QLineEdit.Password)

        self.Title = QtWidgets.QLabel(self.centralWidget)
        self.Title.setGeometry(QtCore.QRect(350, 120, 131, 51))
        font = QtGui.QFont()
        font.setPointSize(30)
        self.Title.setFont(font)
        self.Title.setCursor(QtGui.QCursor(Qt.ArrowCursor))
        self.Title.setAlignment(Qt.AlignCenter)
        self.Title.setObjectName("Title")
        self.main_window.setCentralWidget(self.centralWidget)

        self.ReTranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self.main_window)

    def ReTranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.GetUUID.setPlaceholderText(_translate("LoginWindow", "请输入uuid..."))
        self.GetPassword.setPlaceholderText(_translate("LoginWindow", "请输入密码..."))
        self.Title.setText(_translate("LoginWindow", "登录"))
