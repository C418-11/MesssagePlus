# -*- coding: utf-8 -*-

import json
import socket
from typing import Union

from Lib.SocketIO import Address
from Lib.SocketIO import SocketIo
from Lib.simple_tools import Disable
from AuthenticationSystem.Events.Login import *


class Client(SocketIo):
    def __init__(self, address: Union[Address, socket.socket], print_error: bool = True):
        super().__init__(address=address, print_error=print_error)

    def send_whit_json(self, data):
        js = json.dumps(data)
        byte = js.encode("utf-8")
        super().send(byte)

    def send_event(self, event):
        self.send_whit_json(event.dump())

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
    c.send_whit_json({"type": "Client"})
    print(c.recv())
    c.send_event(ACK_DATA("Client's name", "lk!", "Client"))
    c.close()


if __name__ == "__main__":
    main()
