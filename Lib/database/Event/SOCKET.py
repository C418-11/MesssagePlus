# -*- coding: utf-8 -*-
# cython: language_level = 3

from .ABC import MKEvent

CONNECT_CLOSE = MKEvent("SOCKET.CONNECT_CLOSE")

__all__ = ("CONNECT_CLOSE", )
