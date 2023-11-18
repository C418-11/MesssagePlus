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


def ToFontMetrics(font: Union[QFont, QFontMetrics, str]):
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
    return fm


def elidedText(text, font: Union[QFont, QFontMetrics, str], max_width, mode=Qt.ElideMiddle):
    fm = ToFontMetrics(font)
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


def add_line_breaks(text: str, width: int, font_metrics: QFontMetrics):
    # 获取文本宽度
    def get_width(_text):
        return font_metrics.size(Qt.TextExpandTabs, _text).width()

    # 获取文本宽度
    text_width = get_width(text)

    # 如果文本宽度不超过指定的宽度，则直接返回文本
    if text_width < width:
        return text

    # 否则，需要在文本中添加换行符
    # 这里使用了字符串的split和join方法
    # 将文本按照换行符分割成多个子字符串
    lines = text.split('\n')
    # 遍历每个子字符串，并计算其宽度
    # 如果子字符串的宽度不超过指定的宽度，则直接将其添加到结果字符串中
    # 如果子字符串的宽度超过了指定的宽度，则需要在其周围添加换行符，并将其添加到结果字符串中
    result = ''
    for line in lines:
        # 获取子字符串的宽度
        line_width = get_width(line)
        # 如果子字符串的宽度不超过指定的宽度，则直接将其添加到结果字符串中
        if line_width < width:
            result += line + '\n'
        # 如果子字符串的宽度超过了指定的宽度，则需要在其周围添加换行符，并将其添加到结果字符串中
        else:
            chr_width = 0
            for sub_word in str(line):
                chr_width += get_width(sub_word)
                if chr_width < width:
                    result += sub_word
                else:
                    result += '\n' + sub_word
                    chr_width = 0

    # 返回结果字符串
    return result


__all__ = ("showException", "fontFromPath", "ToFontMetrics", "elidedText", "getFileImage", "add_line_breaks")
