# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow

from typing import Optional


class UiRegisterWindow(object):
    def __init__(self, main_window: QMainWindow):
        self.main_window: QMainWindow = main_window
        self.Title: Optional[QtWidgets.QLabel] = None
        self.GetEmail: Optional[QtWidgets.QLineEdit] = None
        self.GetPassword: Optional[QtWidgets.QLineEdit] = None
        self.GetVerificationCode: Optional[QtWidgets.QLineEdit] = None
        self.centralWidget: Optional[QtWidgets.QWidget] = None
        self.RegisterButton: Optional[QtWidgets.QPushButton] = None

    def setupUi(self):
        self.main_window.setMinimumSize(820, 670)

        self.centralWidget = QtWidgets.QWidget(self.main_window)
        self.centralWidget.setObjectName("centralWidget")

        self.GetEmail = QtWidgets.QLineEdit(self.centralWidget)
        self.GetEmail.setGeometry(QtCore.QRect(330, 300, 171, 21))
        self.GetEmail.setMaxLength(20)
        self.GetEmail.setObjectName("GetEmail")

        self.GetPassword = QtWidgets.QLineEdit(self.centralWidget)
        self.GetPassword.setGeometry(QtCore.QRect(330, 340, 171, 21))
        self.GetPassword.setMaxLength(20)
        self.GetPassword.setObjectName("GetPassword")
        self.GetPassword.setEchoMode(QtWidgets.QLineEdit.Password)

        self.GetVerificationCode = QtWidgets.QLineEdit(self.centralWidget)
        self.GetVerificationCode.setGeometry(QtCore.QRect(330, 380, 171, 21))
        self.GetVerificationCode.setMaxLength(6)
        self.GetVerificationCode.setObjectName("GetVerificationCode")
        self.GetVerificationCode.setEnabled(False)

        self.Title = QtWidgets.QLabel(self.centralWidget)
        self.Title.setGeometry(QtCore.QRect(350, 120, 131, 51))
        font = QtGui.QFont()
        font.setPointSize(30)
        self.Title.setFont(font)
        self.Title.setCursor(QtGui.QCursor(Qt.ArrowCursor))
        self.Title.setAlignment(Qt.AlignCenter)
        self.Title.setObjectName("Title")

        self.RegisterButton = QtWidgets.QPushButton(self.centralWidget)
        self.RegisterButton.setGeometry(QtCore.QRect(330, 420, 171, 31))
        self.RegisterButton.setObjectName("RegisterButton")

        self.main_window.setCentralWidget(self.centralWidget)

        self.ReTranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self.main_window)

    def ReTranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.GetEmail.setPlaceholderText(_translate("RegisterWindow", "请输入邮箱..."))
        self.GetPassword.setPlaceholderText(_translate("RegisterWindow", "请输入密码..."))
        self.GetVerificationCode.setPlaceholderText(_translate("RegisterWindow", "请输入验证码..."))
        self.Title.setText(_translate("RegisterWindow", "注册"))
        self.RegisterButton.setText(_translate("RegisterWindow", "注册"))
