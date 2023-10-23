# -*- coding: utf-8 -*-
# cython: language_level = 3


import socket
from typing import Union

from AuthenticationSystem.Events.Login import *
from Lib.SocketIO import Address
from Lib.SocketIO import SocketIo
from Lib.simple_tools import Disable
from tqdm import tqdm


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


def _main_():
    c = Client(Address("127.0.0.1", 32767))
    c.settimeout(10)
    c.send_json({"type": "Client"})
    c.recv()
    c.send_event(ACK_DATA("Client's name", "lk!", "Client"))
    while True:
        try:
            c.recv()
        except (TimeoutError, ConnectionError, EOFError):
            break
    c.close()


def example():
    t = tqdm(
        total=-1,
        leave=True,
        unit="client",
        desc="Loop",
    )

    loop_times = 10000

    t.reset(loop_times)

    for x in range(loop_times):
        _main_()
        t.update(1)
        t.refresh()

    t.close()


if __name__ == "__main__":
    example()
