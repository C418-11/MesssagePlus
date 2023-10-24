# -*- coding: utf-8 -*-
# cython: language_level = 3
import sys

from tqdm import tqdm

from Lib.global_thread_lock import OutputLock

TOTAL_CONFIG_FILE = 0

ProgressBar = tqdm(
        total=-1,
        leave=True,
        unit="file",
        desc="ConfigFiles",
        file=sys.stdout,
)


ProgressBar.set_lock(OutputLock)


def update(n=1, refresh=True):
    ProgressBar.update(n)
    if refresh:
        ProgressBar.refresh()


def close():
    # warn 记得close这玩意!!!!!!!!!!!!!!!!!!!!!
    ProgressBar.close()


def config_counter(__cls=None, *, count: int = None):
    def _add_count(cls):
        def set_max(add):
            global TOTAL_CONFIG_FILE
            TOTAL_CONFIG_FILE += add
            _last_n = ProgressBar.n
            ProgressBar.reset(TOTAL_CONFIG_FILE)
            ProgressBar.n = _last_n
            ProgressBar.refresh()

        def check_count(*_, num):
            nonlocal count
            nonlocal cls
            if count != cls.profile_number:
                raise ValueError(f"count is not equal to {cls.__name__}.profile_number"
                                 f" (count: {count}, profile_number: {attr_value})")
            if count is not None and count != num:
                raise ValueError(f"num is not equal to count"
                                 f" (num: {num}, count: {count})")
            elif count != num:
                set_max(num)
        cls.check_count = check_count

        global TOTAL_CONFIG_FILE
        global ProgressBar
        nonlocal count
        attr_value = None
        try:
            attr_value = cls.profile_number
        except AttributeError:
            pass

        if (count is not None) and (attr_value is not None):
            if count != attr_value:
                raise ValueError(f"count is not equal to {cls.__name__}.profile_number"
                                 f" (count: {count}, profile_number: {attr_value})")

        count = count or attr_value

        if count is not None:
            set_max(count)

        ProgressBar.refresh()
        cls.profile_number = count

    if __cls is None:
        def decorator(cls):
            _add_count(cls)
            return cls
        return decorator

    _add_count(__cls)
    return __cls


__all__ = ("ProgressBar", "config_counter", "update")
