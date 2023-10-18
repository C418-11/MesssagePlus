# -*- coding: utf-8 -*-

from distutils import core
from Cython.Build import cythonize
core.setup(ext_modules=cythonize("SocketIO.py"))  # 这里填写的就是你的参数，注意在同一目录下
