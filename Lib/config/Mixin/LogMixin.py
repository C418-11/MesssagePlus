# -*- coding: utf-8 -*-

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import os.path
import sys

from Lib.config.Mixin import Base
from Lib.log import Level


def LogMixinChecker(cls_func):
    return Base.MixinFlagChecker("log_mixin_is_init", cls_func)


class LogMixin(Base.ConfigIoLike):
    """Must be init before ConfigIO.IO"""

    _logger_data: dict

    def __init__(self):
        if self.DEFAULT_FILES is None:
            self.DEFAULT_FILES = {}
        self.DEFAULT_FILES.update(self._DEFAULT_LOG_DATA)
        self._log_mixin_is_init = True
        self._log_mixin_file_is_init = False

    def _init_log_file(self):
        std_o = {"stdout": sys.stdout, "stderr": sys.stderr}

        for item in ["file", "warn_file"]:
            if self._logger_data[item] in std_o:
                self._logger_data[item] = std_o[self._logger_data[item]]

            else:
                self._logger_data[item] = open(
                    self._logger_data[item], mode='a', encoding=self._ENCODING, newline=self._NEW_LINE
                )

    @property
    def log_mixin_is_init(self):
        return self._log_mixin_is_init

    @property
    def _DEFAULT_LOG_DATA(self) -> dict:
        return {
            os.path.join(self.BASE_DIR, "logger.json"): {
                "data": {
                    "log_level": Level.DEBUG.level,
                    "file": "stdout",
                    "warn_file": "stderr"
                },
                "key": "_logger_data"
            }
        }

    @property
    @LogMixinChecker
    def log_level(self):
        return self._logger_data["log_level"]

    @property
    @LogMixinChecker
    def log_files(self):
        if not self._log_mixin_file_is_init:
            self._init_log_file()
            self._log_mixin_file_is_init = True
        return self._logger_data["file"], self._logger_data["warn_file"]


__all__ = ("LogMixin",)
