# -*- coding: utf-8 -*-
# cython: language_level = 3
__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.0.0.8 R"

# 版本名称规则
# R 正式版
# B | A 测试版
# T 临时版
# 版本最后面英文字母小写表小版本 a~z

"""

DataBase Lib

"""

import sys


class __NotSet:

    def __gt__(self, other):
        return False

    def __repr__(self):
        return "NotSet"


__RUN_VERSION = (3, 11, __NotSet())
ver_info = sys.version_info.major, sys.version_info.minor, sys.version_info.micro
if ver_info < __RUN_VERSION:
    raise ImportError("Python version Error (at lease {0} now {1})".format(__RUN_VERSION, ver_info))

__all__ = ("ABC", "DataBase", "Event", "logging", "SocketIO")

if __name__ == '__main__':
    pass
