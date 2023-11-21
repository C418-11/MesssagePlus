# -*- coding: utf-8 -*-
# cython: language_level = 3
from typing import override

from .ABC import Event
from .ABC import RegEvent
from ..ABC import ABCServer


@RegEvent
class DebugEvent(Event):
    raw = "DEBUG.DEBUG_EVENT"

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @override
    def func(self, server: ABCServer, **_kwargs):
        print("DEBUG_EVENT(server={}, event={}, kwargs={})".format(server, self, _kwargs))


DEBUG = DebugEvent

__all__ = ("DEBUG",)
