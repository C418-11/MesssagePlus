# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import os


def limit_file_name(name, max_length, max_not_show=3):
    file_name, ext_name = os.path.splitext(name)  # 分离后缀

    limited_name = file_name[::-1][:max(max_length - len(ext_name), 0)][::-1]  # 从后往前截取指定长度 (额外减掉了后缀的长度)

    not_show_length = min(max_not_show, max(len(limited_name), 0))  # 获取要替换的字符串长度
    not_show_index = not_show_length - max(max_length - len(limited_name) - len(ext_name), 0)  # 根据长度获取要替换的字符串的位置
    not_show_index = max(not_show_index, 0)  # 限制值不小于0

    limited_name = '*' * len(limited_name[0:not_show_index]) + limited_name[not_show_index:]  # 替换要替换的部分

    limited_ext = ext_name[::-1][:max_length][::-1]  # 从后往前截取指定长度

    return limited_name + limited_ext
