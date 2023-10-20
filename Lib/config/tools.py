# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"


import sys


def init_files(file_path, mode, *args, encoding: str = "utf-8", **kwargs):
    if file_path is None:
        return file_path

    std_o = {"stdout": sys.stdout, "stderr": sys.stderr, "stdin": sys.stdin}

    if file_path in std_o:
        file = std_o[file_path]

    else:
        file = open(file_path, mode=mode, encoding=encoding, *args, **kwargs)

    return file
