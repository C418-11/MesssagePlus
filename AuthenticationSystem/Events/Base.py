# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import json
from abc import ABC
from abc import abstractmethod
from typing import Self
from typing import override


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
    @override
    def load(cls, *args) -> Self:
        ...

    @classmethod
    def load_str(cls, txt) -> Self:
        return cls.load(json.loads(txt))

    @abstractmethod
    @override
    def dump(self) -> dict:
        ...

    def __getattribute__(self, item):
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            try:
                return self.dump()[item]
            except KeyError:
                pass
            raise

    def __repr__(self):
        return f"{self.dump()}"


EventDict = {}


def EventRegister(cls: Event):
    EventDict[cls.Name] = cls
    return cls


class SuccessEvent(ABC):
    ...


class FailEvent(ABC):
    ...


__all__ = ("Event", "EventDict", "EventRegister", "EventWithData", "SuccessEvent", "FailEvent")
