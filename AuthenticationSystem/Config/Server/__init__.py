# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

__all__ = ("ServConfig", "WebConfig", "APIConfig", "ServerConfig")


for module in __all__:
    exec("from .%s import *" % module)
