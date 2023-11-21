# -*- coding: utf-8 -*-
# cython: language_level = 3


import json
import socket
import sys
from numbers import Real
from threading import Thread
from typing import Union, Any, override

from AuthenticationSystem.Config.Server.WebConfig import ServerConfig
from AuthenticationSystem.Serv.Base import ServicePoolTypes
from AuthenticationSystem.Serv.Login.Login import LostConnectError
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
        self.logger.debug("[ServManager] Enter Loop thread")
        while self._running:
            try:
                conn, addr = self._get(1)
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
        self.logger.debug("[ServManager] Exit Loop thread!")

    def _serv_classify(self, conn: SocketIo, addr: Address, uuid):
        conn_timeout = conn.gettimeout()
        conn.settimeout(10)

        log_head = "[ServManager.ClassifyThread]"

        try:
            byte_data = conn.recv()
        except (ConnectionError, TimeoutError, EOFError):
            self.logger.info(f"{log_head} Lost connect! #during wait client type (addr={addr})")
            conn.close()
            sys.exit(1)
        conn.settimeout(conn_timeout)

        byte_data: bytes
        js = byte_data.decode(encoding="utf-8")
        data = json.loads(js)
        success_add_serv = False
        try:
            ServicePoolTypes[data["type"]].add_service(conn, addr, data)
            success_add_serv = True
        except LostConnectError:
            self.logger.info(f"{log_head} Adding service failed # Lost connect (addr={addr})")
        except Exception as err:
            self.logger.warn(f"{log_head} Adding service failed "
                             f"# An uncaught error was encountered: "
                             f"(err={type(err).__name__}: {err}, addr={addr})")

        if not success_add_serv:
            conn.close()
            sys.exit(1)

        try:  # 这玩意里面是弱引用字典，找不到 是正常的
            self._classifying_serv_pool.remove(uuid)
        except KeyError:
            pass
        sys.exit(0)

    @override
    def start(self):
        super().start()
        self._serv_manager_thread.start()
        self.logger.info("[Server] Start!")

    @override
    def bind(self, address: Union[Address, tuple[Any, ...], str, bytes]):
        self.logger.info(f"[Server] Bind addr (addr='{address}')")
        super().bind(address)

    @override
    def listen(self, _backlog: int):
        self.logger.debug(f"[Server] Listen (backlog={_backlog})")
        super().listen(_backlog)

    @override
    def stop(self):
        self.logger.info("[Server] Stop!")
        self._running = False
        super().stop()

    @override
    def join(self, timeout=None):
        self._serv_manager_thread.join(timeout)
        super().join(timeout)

    @override
    def restart(self, init_socket: Union[tuple, socket.socket]):
        """banned func, I don't think it's necessary to restart server"""
        raise AttributeError("Server can not restart!")

    @Disable
    @override
    def get(*args, **kwargs):
        ...

    @Disable
    @override
    def get_que(self):
        ...


__all__ = ("Server",)
