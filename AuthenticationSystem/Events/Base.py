# -*- coding: utf-8 -*-

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import json
from abc import abstractmethod
from abc import ABC
from typing import Self


class Event(ABC):
    @property
    @abstractmethod
    def Name(self):
        ...

    @classmethod
    def load(cls, *args, **kwargs):
        return cls()

    def dump(self) -> dict:
        return {self.Name: None}

    def to_str(self) -> str:
        return json.dumps(self.dump())


class EventWithData(Event):

    @classmethod
    @abstractmethod
    def load(cls, *args) -> Self:
        ...

    @classmethod
    def load_str(cls, txt) -> Self:
        return cls.load(json.loads(txt))

    @abstractmethod
    def dump(self) -> dict:
        ...


EventDict = {}


def EventRegister(cls: Event):
    EventDict[cls.Name] = cls
    return cls


__all__ = ("Event", "EventDict", "EventRegister", "EventWithData")
