# -*- coding: utf-8 -*-
from typing import Union

from .ABC import Event
from .ABC import RegEvent
from .ABC import RunFailed
from ..ABC import ABCDataBase
from ..ABC import ABCServer
from ..ABC import ABCStore
from ..ABC import NameList


class StoreEvent(Event):

    def __init__(self, database_name, store_name):
        self.database_name = database_name
        self.store_name = store_name

    def db_obj(self, __server: ABCServer) -> ABCDataBase:
        return __server[self.database_name]

    def store_obj(self, __server: ABCServer) -> ABCStore:
        db_obj = self.db_obj(__server)
        return db_obj[self.store_name]


@RegEvent
class CreateStore(StoreEvent):
    raw = "STORE.CREATE_STORE"

    def __init__(self, database_name, store_type, name):
        super().__init__(database_name, name)
        self.store_type = store_type

    def func(self, server: ABCServer, **_kwargs):
        self.db_obj(server).create(self.store_type, self.store_name)


CREATE = CreateStore


@RegEvent
class SetStoreFormat(StoreEvent):
    raw = "STORE.SET_STORE_FORMAT"

    def __init__(self, database, store, format_: NameList):
        super().__init__(database, store)
        self.format_ = format_

    def func(self, server: ABCServer, **_kwargs):
        self.store_obj(server).set_format(self.format_)


SET_FORMAT = SetStoreFormat


@RegEvent
class SetHistoryFormat(StoreEvent):
    raw = "STORE.SET_HISTORY_FORMAT"

    def __init__(self, database, store, format_: str):
        super().__init__(database, store)
        self.format_ = format_

    def func(self, server: ABCServer, **_kwargs):
        self.store_obj(server).set_history_format(self.format_)


SET_HISTORY_FORMANT = SetHistoryFormat


@RegEvent
class Append(StoreEvent):
    raw = "STORE.APPEND"

    def __init__(self, database, store, line: NameList):
        super().__init__(database, store)
        self.line = line

    def func(self, server: ABCServer, **_kwargs):
        self.store_obj(server).append(self.line)


APPEND = Append


@RegEvent
class GetLine(StoreEvent):
    raw = "STORE.GET_LINE"

    def __init__(self, database, store, index):
        super().__init__(database, store)
        self.index = index

    def func(self, server: ABCServer, **_kwargs):
        return self.store_obj(server)[self.index]


GET_LINE = GetLine


@RegEvent
class SetLine(StoreEvent):
    raw = "STORE.SET_LINE"

    def __init__(self, database, store, index: int, line: NameList):
        super().__init__(database, store)
        self.index = index
        self.line = line

    def func(self, server: ABCServer, **_kwargs):
        self.store_obj(server)[self.index] = self.line.ToDict()


SET_LINE = SetLine


@RegEvent
class DelLine(StoreEvent):
    raw = "STORE.DEL_LINE"

    def __init__(self, database, store, index: int):
        super().__init__(database, store)
        self.index = index

    def func(self, server: ABCServer, **_kwargs):
        del self.store_obj(server)[self.index]


DEL_LINE = DelLine


@RegEvent
class LocateLine(StoreEvent):
    raw = "STORE.LOCATE_LINE"

    def __init__(self, database, store, line: NameList):
        super().__init__(database, store)
        self.line = line

    def func(self, server: ABCServer, **_kwargs):
        return self.store_obj(server).locate(self.line)


LOCATE = LocateLine


@RegEvent
class SearchLine(StoreEvent):
    raw = "STORE.SEARCH_LINE"

    def __init__(self, database, store, keyword: Union[str, tuple[str]], value):
        super().__init__(database, store)
        self.keyword = keyword
        self.value = value

    def func(self, server: ABCServer, **_kwargs):
        return self.store_obj(server).search(self.keyword, self.value)


SEARCH = SearchLine


class KeyNotFind(RunFailed):
    raw = "STORE.KET_NOT_FIND"


KEY_NOT_FIND = KeyNotFind()


class LineNotFind(RunFailed):
    raw = "STORE.LINE_NOT_FIND"


LINE_NOT_FIND = LineNotFind()


__all__ = (
    "CREATE",
    "SET_FORMAT",
    "SET_HISTORY_FORMANT",
    "APPEND",
    "GET_LINE",
    "SET_LINE",
    "DEL_LINE",
    "LOCATE",
    "SEARCH",
    "KEY_NOT_FIND",
    "LINE_NOT_FIND"
)
