# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"


from collections import deque
from enum import Enum
from math import cos, pi

from PyQt5.QtCore import QDateTime, Qt, QTimer, QPoint
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QApplication, QScrollArea

from Ui.tools import showException


class SmoothlyScrollArea(QScrollArea):
    """ A scroll area which can scroll smoothly """

    @showException
    def __init__(self, parent=None, orient=Qt.Vertical):
        """
        Parameters
        ----------
        parent: QWidget
            parent widget

        orient: Orientation
            scroll orientation
        """
        super().__init__(parent)
        self.orient = orient
        self.fps = 60
        self.duration = 400
        self.stepsTotal = 0
        self.stepRatio = 4
        self.acceleration = 1
        self.lastWheelEvent = None
        self.scrollStamps = deque()
        self.stepsLeftQueue = deque()
        self.smoothMoveTimer = QTimer(self)
        self.smoothMode = SmoothMode(SmoothMode.LINEAR)
        # noinspection PyUnresolvedReferences
        self.smoothMoveTimer.timeout.connect(self._smoothMove)

    @showException
    def setSmoothMode(self, smooth_mode):
        """ set smooth mode """
        self.smoothMode = smooth_mode

    @showException
    def wheelEvent(self, e):
        if self.smoothMode == SmoothMode.NO_SMOOTH:
            super().wheelEvent(e)
            return

        now = QDateTime.currentDateTime().toMSecsSinceEpoch()
        self.scrollStamps.append(now)
        while now - self.scrollStamps[0] > 500:
            self.scrollStamps.popleft()

        acceleration_ratio = min(len(self.scrollStamps) / 15, 1)
        if not self.lastWheelEvent:
            self.lastWheelEvent = QWheelEvent(e)
        else:
            self.lastWheelEvent = e

        self.stepsTotal = self.fps * self.duration / 1000

        delta = e.angleDelta().y() * self.stepRatio
        if self.acceleration > 0:
            delta += delta * self.acceleration * acceleration_ratio

        self.stepsLeftQueue.append([delta, self.stepsTotal])

        self.smoothMoveTimer.start(int(1000 / self.fps))

    @showException
    def _smoothMove(self):
        """ scroll smoothly when timer time out """
        total_delta = 0

        for i in self.stepsLeftQueue:
            total_delta += int(self._subDelta(i[0], i[1]))
            i[1] -= 1

        while self.stepsLeftQueue and self.stepsLeftQueue[0][1] == 0:
            self.stepsLeftQueue.popleft()

        if self.orient == Qt.Vertical:
            p = QPoint(0, total_delta)
            bar = self.verticalScrollBar()
        else:
            p = QPoint(total_delta, 0)
            bar = self.horizontalScrollBar()

        e = QWheelEvent(
            self.lastWheelEvent.pos(),
            self.lastWheelEvent.globalPos(),
            QPoint(),
            p,
            round(total_delta),
            self.orient,
            self.lastWheelEvent.buttons(),
            Qt.NoModifier
        )

        QApplication.sendEvent(bar, e)

        if not self.stepsLeftQueue:
            self.smoothMoveTimer.stop()

    @showException
    def _subDelta(self, delta, steps_left):
        """ get the interpolation for each step """
        m = self.stepsTotal / 2
        x = abs(self.stepsTotal - steps_left - m)

        res = 0
        if self.smoothMode == SmoothMode.NO_SMOOTH:
            res = 0
        elif self.smoothMode == SmoothMode.CONSTANT:
            res = delta / self.stepsTotal
        elif self.smoothMode == SmoothMode.LINEAR:
            res = 2 * delta / self.stepsTotal * (m - x) / m
        elif self.smoothMode == SmoothMode.QUADRATIC:
            res = 3 / 4 / m * (1 - x * x / m / m) * delta
        elif self.smoothMode == SmoothMode.COSINE:
            res = (cos(x * pi / m) + 1) / (2 * m) * delta

        return res


class SmoothMode(Enum):
    """ Smooth mode """
    NO_SMOOTH = 0
    CONSTANT = 1
    LINEAR = 2
    QUADRATIC = 3
    COSINE = 4


__all__ = ("SmoothlyScrollArea", "SmoothMode")
