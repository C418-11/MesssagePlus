# -*- coding: utf-8 -*-
# cython: language_level = 3

import json
import pickle
import socket
import struct
import sys
import threading
import time
import traceback
from collections import deque
from numbers import Integral
from numbers import Real
from threading import Thread
from typing import Any
from typing import Tuple
from typing import Union


class Address:
    def __init__(self, ip: str, port: int):
        self._ip = ip
        self._port = port

    @property
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    def get(self):
        return self.ip, self.port

    def __str__(self):
        return str(f"{self.ip}: {self.port}")

    def __repr__(self):
        return self.__str__()

    def __call__(self, *args, **kwargs):
        return self.get()

    def __hash__(self):
        return hash((self.ip, self.port))

    def __getitem__(self, item):
        return (self.ip, self.port)[item]


class Recv:
    def __init__(self, data=None):
        if data:
            self.data = data
        else:
            self.data = deque()

    def put(self, obj):
        return self.data.append(obj)

    def get(self, timeout: Union[Real, None] = float("inf")):
        start_time = time.time()

        try:
            return self.data.popleft()
        except IndexError:
            if timeout is None:
                raise

        timeout = float(timeout)

        delay = 0.5

        remainder_time = time.time() - start_time

        while remainder_time <= timeout:
            if delay > remainder_time:
                delay = remainder_time
            elif delay > 1:
                delay = 1

            try:
                return self.data.popleft()
            except IndexError:
                time.sleep(delay)

            delay += 0.01
            remainder_time = time.time() - start_time
        raise TimeoutError("Timeout waiting for return value")

    def clear(self):
        self.data.clear()

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return Recv(self.data.copy())

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, item):
        return self.data[item]

    def __delitem__(self, key):
        del self.data[key]

    def __len__(self):
        return len(self.data)

    def __bool__(self):
        return bool(self.data)

    def __iter__(self):
        return iter(self.data)


class SocketIo:
    def __init__(self, address: Union[Address, socket.socket], print_error: bool = True):

        """
        :param address: 绑定到的套接字
        :param print_error: 是否额外打印错误
        """

        if not isinstance(address, Address):
            self._cSocket = address
        else:
            self._cSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._cSocket.connect(address.get())

        self._print_error = print_error

        self._recv_queue = Recv()

        self._running = False
        self._recv_t = Thread(target=self._recv_loop, name="SocketIO.SocketIO.RecvThread", daemon=True)

    def _recv_all(self, max_size: Integral = None) -> bytes:
        if max_size is None:
            max_size = 4096

        max_size = int(max_size)

        packed_size = self._cSocket.recv(4)
        if not packed_size:
            raise EOFError("Empty size (Connect maybe closed)")

        size = struct.unpack('i', packed_size)[0]
        size: int

        recv_size = 0

        recv_bytes = []

        while recv_size <= size:
            temp_bytes = self._cSocket.recv(max(min(size - recv_size, max_size), 0))

            recv_size += temp_bytes.__sizeof__()
            recv_bytes.append(temp_bytes)

        return b''.join(recv_bytes)

    def _recv_loop(self):
        while self._running:
            try:
                byte = self._recv_all()
                self._recv_queue.put(byte)
            except ValueError:
                time.sleep(0.05)
            except Exception as err:
                self._cSocket.close()
                if self._print_error:
                    traceback.print_exception(err, file=sys.stderr)
                    break
                else:
                    raise

        self._running = False

    def start_recv(self):
        self._running = True
        self._recv_t.start()

    def stop_recv(self):
        self._running = False

    def recv(self, max_size: int = None) -> bytes:
        if self._recv_t.is_alive():
            raise threading.ThreadError("Recv Thread is alive!")

        return self._recv_all(max_size=max_size)

    def recv_obj(self, max_size: int = None):
        return pickle.loads(self.recv(max_size=max_size))

    def get_que(self):
        return self._recv_queue

    def send(self, byte: bytes):
        size_of = byte.__sizeof__()
        self._cSocket.sendall(struct.pack('i', size_of))
        self._cSocket.sendall(byte)

    def send_json(self, _json: Union[list, tuple, str, dict, set, bool, None], encode="utf-8"):
        txt = json.dumps(_json)
        byte = txt.encode(encode)
        self.send(byte)

    def send_obj(self, obj):
        byte = pickle.dumps(obj)
        self.send(byte=byte)

    def close(self):
        self._cSocket.close()

    def join(self, timeout=None):
        self._recv_t.join(timeout=timeout)

    def gettimeout(self):
        return self._cSocket.gettimeout()

    def settimeout(self, value):
        self._cSocket.settimeout(value)

    def getpeername(self):
        return Address(*self._cSocket.getpeername())


class Server:

    def __init__(self, s_socket: socket.socket):
        self._running = False
        self._s_socket = s_socket
        self._connect_request_pool = Recv()
        self._recv_connect_thread = Thread(target=self._recv_connect, name="SockerIO.Server.RecvConnect", daemon=True)

        self._address = None
        self._backlog = None

    def _start_thread(self):
        try:
            self._recv_connect_thread.start()
        except RuntimeError:
            self._recv_connect_thread.join(10)
            self._recv_connect_thread = Thread(target=self._recv_connect, name="SockerIO.Server.RecvConnect",
                                               daemon=True)
            self._recv_connect_thread.start()

    def _recv_connect(self):
        while self._running:
            try:
                connect = self._s_socket.accept()
            except OSError:
                break
            self._connect_request_pool.put(connect)

    def get(self, timeout: Union[Real, None] = None) -> Tuple[socket.socket, Tuple[str, int]]:
        if not self._recv_connect_thread.is_alive():
            raise threading.ThreadError("Recv Connect Thread is not alive!")

        return self._connect_request_pool.get(timeout=timeout)

    def get_que(self):
        return self._connect_request_pool

    def start(self):
        self._running = True
        self._start_thread()

    def stop(self):
        self._running = False
        self._s_socket.close()

    def bind(self, address: Union[Address, tuple[Any, ...], str, bytes]):
        if isinstance(address, Address):
            address = address.get()
        self._address = address
        self._s_socket.bind(self._address)

    def listen(self, _backlog: int):
        self._backlog = _backlog
        self._s_socket.listen(self._backlog)

    def is_alive(self):
        return self._recv_connect_thread.is_alive()

    def join(self, timeout=None):
        self._recv_connect_thread.join(timeout=timeout)

    def restart(self, init_socket: Union[tuple, socket.socket]):
        if type(init_socket) is tuple:
            self._s_socket = socket.socket(*init_socket)
        else:
            self._s_socket = init_socket

        if self._address is None:
            raise AttributeError("address not find")
        if self._backlog is None:
            raise AttributeError("backlog not find")
        self.bind(self._address)
        self.listen(self._backlog)
        self.start()


def main():
    pass


if __name__ == '__main__':
    main()

__all__ = ("Address", "Recv", "SocketIo", "Server")
