# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import os
from typing import Union

from PyQt5.QtCore import QSize, pyqtSignal, QPoint, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QLabel

from Ui.tools import fontFromPath, elidedText, getFileImage


class File(QWidget):
    resize_event = pyqtSignal(QSize, name="resize")

    def __init__(self, parent, file_path, font: Union[QFont, str] = None, file_name_height=None):
        super().__init__(parent)

        self.file_path = file_path

        if isinstance(font, str):
            font = fontFromPath(font, 15)
        self.setFont(font)

        if file_name_height is None:
            file_name_height = self.fontMetrics().height()
        self.file_name_height = file_name_height

        self.file_img_label = QLabel(self)
        self.file_name_label = QLabel(self)

        self.file_img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.refresh_file_img_label()
        self.refresh_file_name_label()

        # noinspection PyUnresolvedReferences
        self.resize_event.connect(self.resize_child)

    def refresh_file_name_label(self):
        self.file_name_label.move(self.pos() + QPoint(0, self.height()-self.file_name_height))
        self.file_name_label.setFont(self.font())

        self.setText(elidedText(self.fileName(), self.font(), self.width()))

    def refresh_file_img_label(self):
        self.file_img_label.move(self.pos())
        self.setPixmap(self.getFileImage(self.file_path))

    def resize_child(self, a0: QSize):
        self.file_img_label.resize(a0)
        self.file_name_label.resize(QSize(a0.width(), self.file_name_height))
        self.refresh_file_name_label()
        self.refresh_file_img_label()

    def fileName(self):
        return os.path.basename(self.file_path)

    def setPixmap(self, *args, **kwargs):
        return self.file_img_label.setPixmap(*args, **kwargs)

    def setText(self, *args, **kwargs):
        return self.file_name_label.setText(*args, **kwargs)

    def getFileImage(self, file_path):

        pixmap = getFileImage(file_path, QSize(self.width(), self.height()-self.file_name_height))

        return pixmap

    def resize(self, *args: Union[QSize, list[int, int]]) -> None:
        """
        resize(self, int, int) -> None
        resize(self, Qsize) -> None
        """
        if isinstance(args[0], QSize):
            qsize = args[0]
        elif len(args) == 2:
            qsize = QSize(*args)
        else:
            raise TypeError("Unknown value (help(resize) for info)")
        super().resize(qsize + QSize(0, self.file_name_height))
        # noinspection PyUnresolvedReferences
        self.resize_event.emit(qsize)


__all__ = ("File", )
