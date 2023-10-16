# -*- coding: utf-8 -*-

from abc import ABC


class ABCEvent(ABC):
    ...


class SuccessEvent(ABCEvent):
    ...


class FailedEvent(ABCEvent):
    ...


__all__ = (
    "ABCEvent",
    "SuccessEvent",
    "FailedEvent"
)
