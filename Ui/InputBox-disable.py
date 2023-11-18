# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import sys

from PyQt5.QtCore import QRect, QPoint, Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QPushButton

from Ui.ShowObj import File
from Ui.tools import showException


class Getter(QTextEdit):
    recv_file = pyqtSignal(QUrl, name="recv_file")

    def __init__(self, prent):
        super().__init__(prent)
        self.setGeometry(100, 100, 600, 600)
        self.setWindowTitle("Getter")
        self.setStyleSheet("background: rgba(0,0,0,0);border: 0px;")
        self.setGeometry(self.geometry())
        self.textChanged.connect(self.change)
        self.last_text = ''

    @showException
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    @showException
    def dropEvent(self, event):
        for sth in event.mimeData().urls():
            # noinspection PyUnresolvedReferences
            self.recv_file.emit(sth)

    @showException
    def change(self):
        print('-'*70)
        print(self.toPlainText())
        print("++"*10)
        print(get(list(enumerate(self.toPlainText())), list(enumerate(self.last_text))))
        print('-'*70)
        self.last_text = self.toPlainText()


def get(now_str, old_str):
    if now_str != old_str:
        #changes = [(c1, c2) for c1, c2 in zip(now_str, old_str) if c1 in now_str and c1 not in old_str]
        changes = []
        changes.extend([("add", c1) for c1 in now_str if c1 not in old_str])
        changes.extend([("sub", c1) for c1 in old_str if c1 not in now_str])
    else:
        changes = []
    return changes


class GetInput(QWidget):
    @showException
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(100, 100, 500, 500)
        self.setWindowTitle("Get Input")
        self.setGeometry(self.geometry())

        self.Getter = Getter(self)

        self.SendButton = QPushButton("Text", self)

        geometry = self.Getter.geometry()
        r_b_p = QPoint(geometry.width(), geometry.height())

        self.SendButton.setGeometry(QRect(r_b_p.x(), r_b_p.y(), 100, 50))
        self.line = [[]]
        self.index = [0, 0]  # y, x
        self._course_pos = [0, 4]  # y, x
        self.img_size = 128, 32  # width, height

        # noinspection PyUnresolvedReferences
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

    @showException
    def ToWidget(self, url: QUrl):

        if url.isLocalFile():
            print(url.toLocalFile())
            file_shower = File(self, url.toLocalFile(), r"F:\Message_Plus\font\bamboo_stone_body.ttf")
            file_shower.resize(*self.img_size)
            self.AutoNextLine(file_shower)
            self.Getter.insertHtml(
                f'<img src="F:/Message_Plus/resource/white.jpg"'
                f' width="{file_shower.width()}" height="{file_shower.height()}">'
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = GetInput()
    gui.resize(800, 800)
    gui.show()
    sys.exit(app.exec_())
