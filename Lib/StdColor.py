# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import sys

import colorama


class ColorWrite:
    def __init__(self, super_, font_color=None, bg_color=None):
        colorama.init()
        self.super_ = super_
        self.font_color = font_color
        self.bg_color = bg_color

    def write(self, text):
        pre = ""
        if self.font_color is not None:
            pre += self.font_color
        if self.bg_color is not None:
            pre += self.bg_color

        self.super_.write(pre + text + colorama.Style.RESET_ALL)

    def __getattribute__(self, item):
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            try:
                return object.__getattribute__(self.super_, item)
            except AttributeError:
                pass
            raise


sys.stdout = ColorWrite(sys.__stdout__, None)
sys.stderr = ColorWrite(sys.__stderr__, colorama.Fore.RED)


__all__ = ("ColorWrite",)
