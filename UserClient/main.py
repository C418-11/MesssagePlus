# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"


from UserClient.login import LoginAuthenticationSystem, ReCallFunc


def main():
    login = LoginAuthenticationSystem()
    try:
        login.login()
    except ReCallFunc:
        login.login()


if __name__ == "__main__":
    main()
