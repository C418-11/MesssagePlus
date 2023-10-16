# -*- coding: utf-8 -*-

import sys
from numbers import Integral
from numbers import Real
from typing import BinaryIO
from typing import TextIO
from typing import Union


class Level:

    def __init__(self, name: str, weight: Real):
        self.name = name
        self.weight = weight
        level_list.add(self)

    def __getitem__(self, item: Integral):
        return [self.name, self.weight][item]

    def __eq__(self, other):
        return self.name == str(other)

    def __int__(self):
        return int(self.weight)

    def __float__(self):
        return float(self.weight)

    def __str__(self):
        return f"Level(name={self.name}, weight={self.weight})"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.name)


class LevelSet:
    def __init__(self):
        self.NameToLevel = {}
        self.WeightToLevel = {}

    def add(self, element: Level):
        if element.name in self.NameToLevel.keys():
            raise ValueError(f"Name {element.name} already exists")
        if element.weight in self.WeightToLevel.keys():
            raise ValueError(f"Weight {element.weight} already exists")

        self.NameToLevel[element.name] = element
        self.WeightToLevel[element.weight] = element

    def GetWeightLevel(self, level: Union[Real, Level]) -> Level:
        if isinstance(level, Level):
            level = level.weight
        return self.WeightToLevel[level]

    def GetNameLevel(self, name: Union[str, Level]) -> Level:
        if isinstance(name, Level):
            name = name.name
        return self.NameToLevel[name]


level_list = LevelSet()


def getWeightName(level: Union[Real, Level]) -> str:
    return level_list.GetWeightLevel(level=level).name


def getNameWeight(name: str) -> Real:
    return level_list.GetNameLevel(name=name).weight


ERROR = Level("ERROR", 40)
WARNING = Level("WARNING", 30)
WARN = WARNING
INFO = Level("INFO", 20)
INIT = Level("INIT", 15)
DEBUG = Level("DEBUG", 10)
IMPORT = Level("IMPORT", 1)
NOTSET = Level("NOTSET", 0)


class Logger:
    def __init__(self, name, level=NOTSET, stream: Union[TextIO, BinaryIO] = None):
        self.name = name
        self.level = level
        if stream is None:
            stream = sys.stderr
        self.stream = stream

        self.disable = False

        self.type = str

    def log(self, msg: str, level: Union[Level, str, Real]):
        if self.disable:
            return
        if self.type is not str:
            raise TypeError(f"Str not {type(self.type)}")
        if type(level) is str:
            level = getNameWeight(name=level)
        if float(level) < float(self.level):
            return
        if not (msg.endswith('\n') or msg.endswith('\r')):
            msg += '\n'

        self.stream: TextIO

        self.stream.write(msg)

    def bin_log(self, msg: Union[bytes, bytearray], level: Union[Level, str, Real]):
        if self.disable:
            return
        if not (self.type is bytes or self.type is bytearray):
            raise TypeError(f"Bytes not {type(self.type)}")
        if type(level) is str:
            level = getNameWeight(name=level)
        if float(level) < float(self.level):
            return
        if not (msg.endswith(b'\n') or msg.endswith(b'\r')):
            msg += b'\n'

        self.stream: BinaryIO

        self.stream.write(msg)

    def close(self):
        self.stream.close()


def main():
    pass


if __name__ == '__main__':
    main()
