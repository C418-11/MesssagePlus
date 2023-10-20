# -*- coding: utf-8 -*-
# cython: language_level = 3

import sys
from datetime import datetime

from Lib.log import Level


class Logger:
    level_list = Level.default_level_list
    FORMAT = "[{time}]({level}){text}\n"

    def __init__(self, output_level=Level.INFO, file=sys.stdout, warn_file=sys.stdout):
        if type(output_level) is int:
            output_level = Level.Level.by_weight(output_level)[0]
        if type(output_level) is str:
            output_level = Level.Level.by_level(output_level)
        self._output_level = output_level
        if not file.writable():
            raise TypeError("File obj is not writeable")
        self._file = file
        self._warn_file = warn_file

    @classmethod
    def _format(cls, time_str, level, text):
        all_kwarg = {"time": time_str, "level": level.level, "text": text}
        return cls.FORMAT.format(**all_kwarg)

    @classmethod
    def _format_time(cls):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    def log(self, level, text):
        if level.weight >= self._output_level.weight:
            txt = self._format(self._format_time(), level, text)
            self._file.write(txt)

    def log_warn(self, level, text):
        if level.weight >= self._output_level.weight:
            txt = self._format(self._format_time(), level, text)
            self._warn_file.write(txt)

    def debug(self, text):
        self.log(level=Level.DEBUG, text=text)

    def info(self, text):
        self.log(level=Level.INFO, text=text)

    def warn(self, text):
        self.log_warn(level=Level.WARN, text=text)

    def error(self, text):
        self.log_warn(level=Level.ERROR, text=text)


def main():
    pass


if __name__ == "__main__":
    main()
