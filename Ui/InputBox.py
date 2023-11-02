# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"


import os
import sys
from typing import Union

from PyQt5.QtCore import QRect, QPoint, Qt, QFileInfo, pyqtSignal, QObject, QUrl, QSize
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QTextEdit, QLineEdit, QPushButton, \
    QGraphicsView, QLabel, QFileIconProvider

from Ui.tools import showException


class Getter(QTextEdit):
    recv_file = pyqtSignal(QUrl)

    def __init__(self, prent):
        super().__init__(prent)
        self.setGeometry(100, 100, 600, 600)
        self.setWindowTitle("Get File")
        # self.setStyleSheet("background: rgba(0,0,0,0);border: 0px;")
        self.setGeometry(self.geometry())

    @showException
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    @showException
    def dropEvent(self, event):
        for sth in event.mimeData().urls():
            self.recv_file.emit(sth)


def limit_file_name(name, max_length, max_not_show=3):
    file_name, ext_name = os.path.splitext(name)  # 分离后缀

    limited_name = file_name[::-1][:max(max_length - len(ext_name), 0)][::-1]  # 从后往前截取指定长度 (额外减掉了后缀的长度)

    not_show_length = min(max_not_show, max(len(limited_name), 0))  # 获取要替换的字符串长度
    not_show_index = not_show_length - max(max_length - len(limited_name) - len(ext_name), 0)  # 根据长度获取要替换的字符串的位置
    not_show_index = max(not_show_index, 0)  # 限制值不小于0

    limited_name = '*' * len(limited_name[0:not_show_index]) + limited_name[not_show_index:]  # 替换要替换的部分

    limited_ext = ext_name[::-1][:max_length][::-1]  # 从后往前截取指定长度

    return limited_name + limited_ext


class FileShow(QWidget):
    img_size = 32, 32
    resize_event = pyqtSignal(QSize)

    def __init__(self, parent, file_path, file_name_height):
        super().__init__(parent)

        self.file_img_label = QLabel(self)
        self.file_name_label = QLabel(self)
        self.file_path = file_path
        self.file_name_height = file_name_height

        self.setPixmap(self.GetLocalFileImage(file_path))

        self.file_name_label.move(self.pos()+QPoint(0, self.height()))
        self.setText(limit_file_name(self.fimeName(), 20))

        self.resize_event.connect(self.resize_child)

    def resize_child(self, a0: QSize):
        self.file_img_label.resize(a0)
        self.file_name_label.resize(QSize(a0.width(), self.file_name_height))

    def fimeName(self):
        return os.path.basename(self.file_path)

    def setPixmap(self, *args, **kwargs):
        return self.file_img_label.setPixmap(*args, **kwargs)

    def setText(self, *args, **kwargs):
        return self.file_name_label.setText(*args, **kwargs)

    def GetLocalFileImage(self, file_path):

        file_info = QFileInfo(file_path)
        icon_provider = QFileIconProvider()

        if os.path.splitext(file_path)[1].lower() in (
            ".jpg", ".jpeg", ".png", ".bmp", ".gif", "ppm", ".tif", ".tiff", ".xbm", ".xpm"
        ):
            pixmap = QPixmap(file_path)
        else:
            pixmap = icon_provider.icon(file_info).pixmap(32)

        pixmap = pixmap.scaled(*self.img_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
        print(self.size())
        super().resize(qsize + QSize(0, self.file_name_height))
        print(self.size())
        self.resize_event.emit(qsize)


class GetInput(QWidget):
    @showException
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 500, 500)
        self.setWindowTitle("Get Input")
        self.setGeometry(self.geometry())

        self.Getter = Getter(self)

        self.SendButton = QPushButton("wow", self)
        geometry = self.Getter.geometry()
        r_b_p = QPoint(geometry.width(), geometry.height())

        self.SendButton.setGeometry(QRect(r_b_p.x(), r_b_p.y(), 100, 50))
        self.line = [[]]
        self.index = [0, 0]  # y, x
        self._course_pos = [0, 0]  # y, x
        self.img_size = 128, 32  # width, height

        self.Getter.recv_file.connect(self.ToWidget)

    def AutoNextLine(self, widget: QWidget):
        """
        自动换行
        """
        widget.show()
        if widget.width()+self._course_pos[0] > self.Getter.width():
            self._course_pos[0] = 0
            self._course_pos[1] += widget.height()

            self.index[0] += 1
            self.index[1] = 0

            self.line.append([])

        cx, cy = self._course_pos
        x, y = cx + self.Getter.x(), cy + self.Getter.y()
        widget.move(x, y)

        self.line[self.index[0]].append(widget)

        self.index[1] += 1
        self._course_pos[0] += widget.width()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.line[self.index[0]].append(event.pos())

    @showException
    def ToWidget(self, url: QUrl):

        if url.isLocalFile():
            file_shower = FileShow(self, url.toLocalFile(), 20)
            file_shower.resize(*self.img_size)
            self.AutoNextLine(file_shower)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = GetInput()
    gui.resize(800, 800)
    gui.show()
    sys.exit(app.exec_())
