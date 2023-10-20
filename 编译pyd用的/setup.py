# -*- coding: utf-8 -*-
# cython: language_level = 3

import os
import subprocess
from typing import Union
import re

from Cython.Build import cythonize
from setuptools import find_packages
from setuptools import setup


def _get_dependency_versions() -> dict[str, str]:
    result = subprocess.run(['pip', 'freeze'], capture_output=True, text=True)

    dependencies = result.stdout.split('\n')
    dependency_versions = {}
    for dep in dependencies:
        if not dep:
            continue
        dep_name, dep_version = dep.split('==')
        dependency_versions[dep_name] = dep_version

    return dependency_versions


def _get_all_extension_files(directory, extension=".py") -> list[str]:
    _py_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                _py_files.append(os.path.join(root, file))
    return _py_files


def _make_path(path_a, path_b):
    return os.path.normpath(os.path.join(path_a, path_b))


class PyToPyd:
    def __init__(self, output_dir: Union[str, None] = None):
        if output_dir is None:
            output_dir = os.path.dirname(__file__)

        self.output_dir = _make_path(output_dir, "Build")
        self.c_path = _make_path(self.output_dir, "c")
        self.temp_path = _make_path(self.output_dir, "temp")
        self.pyd_path = _make_path(self.output_dir, "pyd")

    def _make_c_file(self, file):
        return cythonize(file, build_dir=self.c_path)

    @staticmethod
    def _dependency_versions():
        dependency_versions = []
        for dep, ver in _get_dependency_versions().items():
            dependency_versions.append(dep + "==" + ver)
        return dependency_versions

    def make(self, file):
        setup(
            ext_modules=self._make_c_file(file),
            script_name="setup.py",
            script_args=[
                "build_ext",
                "--build-lib",
                self.pyd_path,
                "--build-temp",
                self.temp_path,
            ],
            packages=find_packages(),
            install_requires=self._dependency_versions(),
            author="C418____11",
            author_email="553515788@qq.com",
            url="https://github.com/C418-11/MesssagePlus",
        )

    def make_all(self, dir_path):
        for path in _get_all_extension_files(dir_path):
            self.make(path)


def _rename_file(file_name, replace, to):
    print(f"Renaming {file_name}")
    new_file_name = re.sub(replace, to, file_name)
    if file_name != new_file_name:
        os.rename(file_name, new_file_name)


def _rename_all(dir_path, replace, to, extension=".pyd"):
    for path in _get_all_extension_files(dir_path, extension):
        _rename_file(path, replace, to)


def _main():
    type_ = input("1: Pyd, 2: Rename, 3: All, 4: Exit\n")

    compiler = PyToPyd()

    def a():
        compiler.make_all(r"F:\Message_Plus\Lib")
        compiler.make_all(r"F:\Message_Plus\AuthenticationSystem")

    def b():
        _rename_all(compiler.pyd_path, r".cp312-win_amd64", r"")

    match int(type_):
        case 1:
            a()
        case 2:
            b()
        case 3:
            a()
            b()
        case 4:
            exit()
        case _:
            print("Unknown type")


if __name__ == "__main__":
    _main()

__all__ = ("PyToPyd",)
