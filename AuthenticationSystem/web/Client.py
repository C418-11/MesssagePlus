# -*- coding: utf-8 -*-
# cython: language_level = 3


import socket
import time
from typing import Optional
from typing import override
from typing import Union

from tqdm import tqdm

from AuthenticationSystem.Events.Login import ACK_DATA
from AuthenticationSystem.Serv.Login.Database import LoginKey
from Lib.SocketIO import Address
from Lib.SocketIO import SocketIo
from Lib.base_conversion import Base
from Lib.simple_tools import Disable


class Client(SocketIo):
    def __init__(self, address: Union[Address, socket.socket], print_error: bool = True):
        super().__init__(address=address, print_error=print_error)

    def init(self, service_type, timeout: Optional[float]):
        old_timeout = self.gettimeout()
        self.settimeout(timeout)
        self.send_json({"type": service_type})
        yield self.recv()
        self.send_event(
            ACK_DATA(
                uuid=Base("abc", 36),
                login_key=LoginKey("123", time.time() - 50),
                email="553515788@qq.com"
            )
        )
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


def _main_():
    c = Client(Address("127.0.0.1", 32767))
    init = c.init("Client", 10)
    print(init)
    print(next(init))
    print(next(init))
    while True:
        try:
            print(c.recv())
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

    loop_times = 1

    t.reset(loop_times)

    for x in range(loop_times):
        _main_()
        t.update(1)
        t.refresh()

    t.close()


if __name__ == "__main__":
    example()

__all__ = ("Client", "example")
