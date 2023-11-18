# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import os
import traceback
from functools import wraps
from typing import Union

from PyQt5.QtCore import Qt, QFileInfo, QSize
from PyQt5.QtGui import QFontDatabase, QFont, QFontMetrics, QPixmap
from PyQt5.QtWidgets import QFileIconProvider


def showException(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            traceback.print_exception(err)

    return wrapper


def fontFromPath(font_path, point_size=None):
    font_db = QFontDatabase()
    font_id = font_db.addApplicationFont(font_path)

    # 获取字体名称
    font_families = font_db.applicationFontFamilies(font_id)

    # 创建QFont对象
    font = QFont()
    font.setFamily(font_families[0])
    if point_size is not None:
        font.setPointSize(point_size)  # 设置字号
    return font


def elidedText(text, font: Union[QFont, QFontMetrics, str], max_width, mode=Qt.ElideMiddle):
    if isinstance(font, str):
        font = fontFromPath(font)
    if isinstance(font, QFont):
        font = QFontMetrics(font)
    if isinstance(font, QFontMetrics):
        fm = font
    else:
        # 抛出TypeError告诉调用者无法将font转换为QFontMetrics
        raise TypeError("font must be a QFont, QFontMetrics or str"
                        " but got {}".format(type(font)))

    return fm.elidedText(text, mode, max_width)


def getFileImage(
        file_path,
        size: Union[QSize, None],
        *,
        scaled_args=(Qt.KeepAspectRatio, Qt.SmoothTransformation)
) -> QPixmap:

    file_info = QFileInfo(file_path)
    icon_provider = QFileIconProvider()

    if size is None:
        size = QSize(32, 32)
    elif not isinstance(size, QSize):
        raise TypeError("size must be None or QSize")

    ext_name = os.path.splitext(file_path)[1].lower()

    if ext_name in (
            ".jpg", ".jpeg", ".png", ".bmp", ".gif", "ppm", ".tif", ".tiff", ".xbm", ".xpm"
    ):
        pixmap = QPixmap(file_path)
    else:
        pixmap = icon_provider.icon(file_info).pixmap(32)

    pixmap = pixmap.scaled(size, *scaled_args)
    return pixmap


__all__ = ("showException", "fontFromPath", "elidedText", "getFileImage")
