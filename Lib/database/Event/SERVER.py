# -*- coding: utf-8 -*-
# cython: language_level = 3

from .ABC import MKEvent

STOP = MKEvent("SERVER.STOP")
RESTART = MKEvent("SERVER.RESTART")


__all__ = ("STOP", "RESTART")
