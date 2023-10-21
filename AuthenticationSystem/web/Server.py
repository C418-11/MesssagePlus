# -*- coding: utf-8 -*-
# cython: language_level = 3


import json
import socket
import sys
from numbers import Real
from threading import Thread
from typing import Union, Any

from AuthenticationSystem.Config.WebConfig import ServerConfig
from AuthenticationSystem.Serv.Base import ServicePoolTypes
from Lib.SocketIO import Address
from Lib.SocketIO import Server as SocketServer
from Lib.SocketIO import SocketIo
from Lib.log import Logging
from Lib.simple_tools import Disable
from Lib.simple_tools import ThreadPool


class Server(SocketServer):
    socket_arg = (socket.AF_INET, socket.SOCK_STREAM)
    Config = ServerConfig.ServerType
    logger = Logging.Logger(output_level=Config.log_level, file=Config.log_files[0], warn_file=Config.log_files[1])

    def __init__(self):
        super().__init__(socket.socket(*self.socket_arg))

        self._serv_manager_thread = Thread(target=self._serv_manager, name="Server.ServManagerThread", daemon=True)
        self._classifying_serv_pool = ThreadPool()

    def _get(self, timeout: Union[Real, None] = float("inf")):
        return super().get(timeout=timeout)

    def _serv_manager(self):
        while self._running:
            try:
                conn, addr = self._get(10)
            except TimeoutError:
                continue

            conn = SocketIo(conn)
            addr = Address(*addr)
            self.logger.info(f"[ServManager] Recv Connect (addr={addr})")

            uuid = hash((conn, addr))
            classify_thread = Thread(target=self._serv_classify, args=[conn, addr, uuid],
                                     daemon=True,
                                     name="Server.ClassifyThread")
            self._classifying_serv_pool.add(classify_thread, uuid=uuid)
            classify_thread.start()

    def _serv_classify(self, conn: SocketIo, addr: Address, uuid):
        conn_timeout = conn.gettimeout()
        conn.settimeout(10)
        try:
            byte_data = conn.recv()
        except ConnectionError:
            self.logger.warn(f"[ServManager] Lost connect! #during wait client type (addr={addr})")
            conn.close()
            sys.exit()
        conn.settimeout(conn_timeout)

        byte_data: bytes
        js = byte_data.decode(encoding="utf-8")
        data = json.loads(js)

        ServicePoolTypes[data["type"]].add_service(conn, addr, data)

        try:  # 这玩意里面是弱引用字典，找不到是正常的
            self._classifying_serv_pool.remove(uuid)
        except KeyError:
            pass
        sys.exit(0)

    def start(self):
        super().start()
        self._serv_manager_thread.start()
        self.logger.info("[Server] Start!")

    def bind(self, address: Union[Address, tuple[Any, ...], str, bytes]):
        self.logger.info(f"[Server] Bind addr (addr='{address}')")
        super().bind(address)

    def listen(self, _backlog: int):
        self.logger.debug(f"[Server] Listen (backlog={_backlog})")
        super().listen(_backlog)

    @Disable
    def get(*args, **kwargs):
        ...

    @Disable
    def get_que(self):
        ...


def example():
    s = Server()
    s.bind(Address("127.0.0.1", 32767))
    s.listen(500)
    s.start()
    while input("STOP? (T/F)\n\r") != 'T':
        pass
    s.stop()


if __name__ == "__main__":
    example()
