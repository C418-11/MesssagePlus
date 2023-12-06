# -*- coding: utf-8 -*-
# cython: language_level = 3


import socket
from typing import Optional, Generator
from typing import Union
from typing import override

from AuthenticationSystem.Events import Login
from Lib.SocketIO import Address
from Lib.SocketIO import SocketIo
from Lib.simple_tools import Disable


class Client(SocketIo):
    def __init__(self, address: Union[Address, socket.socket], print_error: bool = True):
        super().__init__(address=address, print_error=print_error)

    def init(self, service_type, timeout: Optional[float]) -> Generator[bytes, Login.ACK_DATA, None]:
        old_timeout = self.gettimeout()
        self.settimeout(timeout)
        self.send_json({"type": service_type})
        _ack_data = yield self.recv()
        self.send_event(_ack_data)
        yield self.recv()
        self.settimeout(old_timeout)

    def send_event(self, event):
        self.send_json(event.dump())

    @Disable
    @override
    def send_obj(self, *args, **kwargs):
        pass

    @Disable
    @override
    def recv_obj(self, *args, **kwargs):
        pass


__all__ = ("Client",)
