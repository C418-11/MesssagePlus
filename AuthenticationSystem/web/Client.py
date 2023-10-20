# -*- coding: utf-8 -*-
# cython: language_level = 3


import socket
from typing import Union

from AuthenticationSystem.Events.Login import *
from Lib.SocketIO import Address
from Lib.SocketIO import SocketIo
from Lib.simple_tools import Disable


class Client(SocketIo):
    def __init__(self, address: Union[Address, socket.socket], print_error: bool = True):
        super().__init__(address=address, print_error=print_error)

    def send_event(self, event):
        self.send_json(event.dump())

    @Disable
    def send_obj(self, obj):
        pass

    @Disable
    def recv_obj(self, byte: bytes):
        pass


__all__ = ("Client",)


def main():
    c = Client(Address("127.0.0.1", 32767))
    c.settimeout(10)
    c.send_json({"type": "Client"})
    print(c.recv())
    c.send_event(ACK_DATA("Client's name", "lk!", "Client"))
    while True:
        try:
            print(c.recv())
        except (TimeoutError, ConnectionError, EOFError):
            break
    c.close()


if __name__ == "__main__":
    main()
