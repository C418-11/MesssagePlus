# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"


from Config import ServerConfig
from Lib.SocketIO import Address

config = ServerConfig.Server


def main():
    from web.Server import Server

    s = Server()

    s.bind(Address(*config.address))
    s.listen(config.max_connections)
    s.start()
    while input("STOP? (T/F)\n\r") != 'T':
        pass

    s.stop()
    s.join(10)


if __name__ == "__main__":
    main()
