# -*- coding: utf-8 -*-

from distutils import core
from Cython.Build import cythonize

ls = []

for x in ls:
    core.setup(ext_modules=cythonize(x))  # 这里填写的就是你的参数，注意在同一目录下
