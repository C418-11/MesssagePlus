# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"


import importlib


def import_from(module, name):
    module = importlib.import_module(module)
    return getattr(module, name)


def main():
    type_ = input("1: Server, 2.Client, 3: Exit\n")
    match int(type_):
        case 1:
            import_from("AuthenticationSystem.web.Server", "main")()
        case 2:
            import_from("AuthenticationSystem.web.Client", "main")()
        case 3:
            exit()
        case _:
            print("Unknown type")


if __name__ == "__main__":
    main()
