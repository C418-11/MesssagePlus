# -*- coding: utf-8 -*-
# cython: language_level = 3

import sys
from datetime import datetime
from threading import Thread

from Lib.global_thread_lock import ProcessLock
from Lib.log import Level


class Logger:
    level_list = Level.default_level_list
    FORMAT = "[{time}]({level}){text}\n"
    lock = ProcessLock("log")

    def __init__(self, output_level=Level.INFO, file=sys.stdout, warn_file=sys.stdout, lock=None):
        if type(output_level) is int:
            output_level = Level.Level.by_weight(output_level)[0]
        if type(output_level) is str:
            output_level = Level.Level.by_level(output_level)
        self._output_level = output_level
        if not file.writable():
            raise TypeError("File obj is not writeable")
        self._file = file
        self._warn_file = warn_file
        self._lock = lock

    @property
    def file(self):
        return self._file

    @property
    def warn_file(self):
        return self._warn_file

    @classmethod
    def _format(cls, time_str, level, text):
        all_kwarg = {"time": time_str, "level": level.level, "text": text}
        return cls.FORMAT.format(**all_kwarg)

    @classmethod
    def _format_time(cls):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    @lock
    def log_in_thread(self, level, text, file):
        if level.weight >= self._output_level.weight:
            txt = self._format(self._format_time(), level, text)
            file.write(txt)

    def log(self, level, text):
        Thread(target=self.log_in_thread, args=(level, text, self._file), daemon=True).start()

    def log_warn(self, level, text):
        Thread(target=self.log_in_thread, args=(level, text, self._warn_file), daemon=True).start()

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
