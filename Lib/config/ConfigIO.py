# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import json
import os.path
import sys
from abc import ABC, abstractmethod
from json import JSONDecodeError

from Lib.log import Level
from Lib.log import Logging
from . import Progressbar
from .Progressbar import config_counter


class BaseIO:
    _ENCODING = "utf-8"
    _READ_SIZE = 1024 * 4
    _NEW_LINE = '\n'
    _INDENT = 4
    _BASE_PATH = "./configs/"

    def _read_config_file(self, file_path):
        text = ''
        with open(file=file_path, mode='r', encoding=self._ENCODING) as f:
            text += f.read(self._READ_SIZE)
        return text

    def _write_config_file(self, file_path, text_):
        with open(file_path, 'w', newline=self._NEW_LINE, encoding=self._ENCODING) as f:
            f.write(text_)

    def _dumps(self, data):
        return json.dumps(data, indent=self._INDENT)

    @staticmethod
    def _loads(txt):
        return json.loads(txt)


logger_args: dict


@config_counter(count=1)
class _LoadBaseLoggerConfig(BaseIO):
    DefaultConfig = {
        "output_level": Level.NEVER.level,
        "file": "stdout",
        "warn_file": "stderr"
    }

    def __init__(self):
        global logger_args
        file_path = os.path.join(self._BASE_PATH, "config_loader\\logger_setting.json")
        file_path = os.path.normpath(file_path)

        try:
            txt = self._read_config_file(file_path)
            json_ = self._loads(txt)
        except (FileNotFoundError, JSONDecodeError):
            try:
                os.makedirs(os.path.dirname(file_path))
            except FileExistsError:
                pass
            self._write_config_file(file_path, self._dumps(self.DefaultConfig))
            json_ = self.DefaultConfig

        std_o = {"stdout": sys.stdout, "stderr": sys.stderr}

        for item in ["file", "warn_file"]:
            if json_[item] in std_o:
                json_[item] = std_o[json_[item]]

            else:
                json_[item] = open(json_[item], mode='a', encoding=self._ENCODING, newline=self._NEW_LINE)

        logger_args = json_

        Progressbar.update(0)
        Progressbar.update(1)


_LoadBaseLoggerConfig()


class IO(ABC, BaseIO):
    _logger = Logging.Logger(**logger_args)
    DEFAULT_FILES = None

    def __init__(self):
        if self.DEFAULT_FILES is None:
            self.DEFAULT_FILES = {}
        self.data = {}
        self.data_to_write = {}

        self._progress_bar_hook()

        for raw in self.DEFAULT_FILES:
            default_data = self.DEFAULT_FILES[raw]
            path = os.path.join(self._BASE_PATH, raw)
            path = os.path.normpath(path)

            try:
                self._logger.debug(f"[Config](INIT LEVEL) File will be read (file='{path}')")
                self.data[default_data["key"]] = self._read(path, raw)
                self.data_to_write[raw] = {"key": default_data["key"], "data": self.data[default_data["key"]]}
                self._logger.info(f"[Config](INIT LEVEL) Loaded config file (path='{path}')")
            except JSONDecodeError as err:
                self._logger.error(f"[Config](INIT LEVEL) Configuration file format error (path='{path}' err='{err}')")
                raise

            Progressbar.update(1)

    def save(self):
        for raw in self.data_to_write:
            data = self.data_to_write[raw]
            path = os.path.join(self._BASE_PATH, raw)
            path = os.path.normpath(path)
            self._write_config_file(path, self._dumps(data["data"]))
            self._logger.info(f"[Config](SAVE LEVEL) Saved config file (path='{path}')")

        for raw in self.DEFAULT_FILES:
            default_data = self.DEFAULT_FILES[raw]
            path = os.path.join(self._BASE_PATH, raw)
            path = os.path.normpath(path)

            try:
                self._logger.debug(f"[Config](REREAD LEVEL) File will be read (file='{path}')")
                self.data[default_data["key"]] = self._read(path, raw)
                self.data_to_write[raw] = {"key": default_data["key"], "data": self.data[default_data["key"]]}
                self._logger.info(f"[Config](REREAD LEVEL) Loaded config file (path='{path}')")
            except JSONDecodeError as err:
                self._logger.error(
                    f"[Config](REREAD LEVEL) Configuration file format error (path='{path}' err='{err}')"
                )
                raise

    def _progress_bar_hook(self):
        self._logger.debug(f"[Config](Progressbar Hook) Try to hook progress bar")
        try:
            checker = getattr(self, "check_count")
        except AttributeError:
            self._logger.debug(f"[Config](Progressbar Hook) No hook found")
        else:
            try:
                checker(num=len(self.DEFAULT_FILES))
                self._logger.debug(f"[Config](Progressbar Hook) Hooked progress bar")
                return
            except ValueError:
                self._logger.error(
                    f"[Config](Progressbar Hook) Configuration file count is inconsistent within the context"
                )
                raise

    @property
    @abstractmethod
    def BASE_DIR(self) -> str:
        """Interface for mixed classes"""

    def _write_default(self, file_path, raw_path):
        file_data = self.DEFAULT_FILES[raw_path]

        just_dir = os.path.dirname(file_path)
        if not os.path.isdir(just_dir):
            self._logger.warn(f"[Config] Dir Not Find #The dir will be created (dir={just_dir})")
            os.makedirs(just_dir)
            self._logger.debug(f"[Config] Successfully created dir (dir={just_dir})")

        self._write_config_file(file_path, self._dumps(file_data["data"]))

    def _read(self, path, raw):
        try:
            return self._loads(self._read_config_file(path))
        except FileNotFoundError:
            self._logger.warn(f"[Config] File Not Found (path='{path}')")
            self._write_default(path, raw)
            self._logger.info(f"[Config] Write default config (path='{path}')")
            return self.DEFAULT_FILES[raw]["data"]

    def __getattribute__(self, item):
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            if item == "data":
                raise
            try:
                return self.data[item]
            except KeyError:
                pass
            raise


__all__ = ("IO",)
