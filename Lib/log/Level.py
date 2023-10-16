# -*- coding: utf-8 -*-

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import copy
from collections import defaultdict
from typing import Self, List


class LevelList:
    def __init__(self):
        self._level_to_weight = defaultdict(lambda: 0)
        self._weight_to_level = defaultdict(lambda: [])

    def add(self, level, weight):
        level = level.upper()

        if level in self._level_to_weight:
            raise ValueError(f"Level {level} already exist")

        self._level_to_weight[level] = weight
        self._weight_to_level[weight].append(level)

    def get_weight(self, level):
        if level in self._level_to_weight:
            return self._level_to_weight[level.upper()]
        raise KeyError(f"level {level} not in level_list")

    def get_level(self, weight):
        if weight in self._weight_to_level:
            return self._weight_to_level[weight]
        raise KeyError(f"weight {weight} not in weight_list")

    def levels(self):
        return list(self._level_to_weight.keys())

    @property
    def level_to_weight(self):
        return copy.deepcopy(dict(self._level_to_weight))

    @property
    def weight_to_level(self):
        return copy.deepcopy(dict(self._weight_to_level))

    def __getattribute__(self, item):
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            if item in self._level_to_weight:
                return self._level_to_weight[str(item).upper()]
            raise

    def __iter__(self):
        return iter(self._level_to_weight)

    def __getitem__(self, item):
        if item in self._level_to_weight:
            return self._level_to_weight[item]
        raise KeyError(f"level {item} is not in level_list")


default_level_list = LevelList()


class Level:
    level_list = default_level_list

    def __init__(self, level, weight):
        self._level = level
        self._weight = weight

        if self._level not in self.level_list or self.level_list[self._level] != self._weight:
            self.level_list.add(self._level, self._weight)

    @classmethod
    def by_level(cls, level) -> Self:
        return cls(level, cls.level_list[level])

    @classmethod
    def by_weight(cls, weight) -> List[Self]:
        ls = []
        for level in cls.level_list.get_level(weight):
            ls.append(cls(level, weight))
        return ls

    @property
    def level(self):
        return self._level

    @property
    def weight(self):
        return self._weight


DEBUG = Level("DEBUG", 0)
INFO = Level("INFO", 1)
WARN = Level("WARN", 2)
ERROR = Level("ERROR", 3)

__all__ = ("default_level_list", "LevelList", "Level", *default_level_list.levels())
