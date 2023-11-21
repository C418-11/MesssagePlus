# -*- coding: utf-8 -*-
# cython: language_level = 3

__author__ = "C418____11 <553515788@qq.com>"
__version__ = "0.1"

import functools
from itertools import zip_longest
from typing import Self
from typing import Union

MAX_LEN = 30
DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ".lower()
MAX_BASE = len(DIGITS)


def check_value(base=None, type_="self", index=0):
    def wrapper(func):
        nonlocal type_, index, base
        if type_ == "self":
            @functools.wraps(func)
            def decoder_self(self, *args, **kwargs):
                nonlocal index, base
                cls = type(self)
                cls: type[Base]

                value = args[index]

                if base is None:
                    base = self._BASE

                if isinstance(value, cls):
                    if value.base != self.base:
                        raise ValueError(f"self.base is not eq value.base (self={self.base}, value={value.base})")
                    return func(self, *args, **kwargs)

                elif any([isinstance(value, x) for x in (float, int)]):
                    value = cls.from_int(value, base)
                elif isinstance(value, str):
                    value = cls(value, base)
                else:
                    return NotImplemented

                args_ls = list(args)
                args_ls[index] = value

                return func(self, *args_ls, **kwargs)

            return decoder_self

    return wrapper


class Base:
    """
    N 进制的数值 (大小写忽略)
    """

    _DIGITS = DIGITS
    _MAX_LEN = MAX_LEN

    _BASE: int
    _DIGITS: str
    _MAX_LEN: int

    def __init__(self, value: Union[str, "Base"], base: int):
        if isinstance(value, type(self)):
            value = str(value)

        if value == '' or value is None:
            value = self._DIGITS[0]
        if (value != self._DIGITS[0] and
                any([value.startswith(x) for x in (f"-{self._DIGITS[0]}", self._DIGITS[0])])):
            raise ValueError(f"The value can't start with {self._DIGITS[0]} or -{self._DIGITS[0]}")
        if value == '-':
            raise ValueError("Unable to convert a negative number just have '-'")

        if isinstance(value, str):
            if '.' in value:
                raise ValueError("The input parameter cannot be a decimal number")
            self._value = value.lower()
        else:
            raise TypeError(f"{type(value)} is not instance str")

        self._BASE = base

    @property
    def base(self) -> int:
        return self._BASE

    @classmethod
    def from_int(cls, n: int, base) -> Self:
        if n == 0:
            return cls(cls._DIGITS[0], base)

        neg = False
        if n < 0:
            n = -n
            neg = True
        s = ""
        len_ = 0
        while n > 0:
            s = cls._DIGITS[n % base] + s
            n = n // base
            len_ += 1
            if len_ > cls._MAX_LEN:  # 限制最大位数
                raise ValueError(f"Number of digits exceeds maximum allowed value. (max={cls._MAX_LEN})")
        if neg:
            s = '-' + s

        return cls(s, base)

    @classmethod
    def from_index_ls(cls, index_ls: list[int], to: int) -> Self:
        txt = []
        for i in index_ls:
            if i == '-':
                txt += '-'
                continue
            txt += cls._DIGITS[int(i)]
        return cls(''.join(reversed(txt)), to)

    @classmethod
    def dec_to(cls, n: "Base", to: int) -> Self:
        if n.base != 10:
            raise ValueError(f"n's base is not 10")

        to = cls.from_int(to, 10)
        if to == cls.from_int(10, 10):
            return n

        result = ""
        while n > 0:
            result = cls._DIGITS[int(n % to)] + result
            n = n // to
        return cls(result, int(to))

    def __len__(self) -> int:
        return len(self._value)

    def __getitem__(self, item):
        return type(self)(self._value[item], self._BASE)

    def __str__(self) -> str:
        return self._value

    def __iter__(self):
        return iter(self._value)

    def __reversed__(self):
        return reversed(self._value)

    def __abs__(self):
        v = self._value
        if v.startswith('-'):
            v = v[1:]
        return type(self)(v, self._BASE)

    def __neg__(self):
        neg = self._value.startswith('-')
        value = self._value.replace('-', '')
        set_neg = not neg
        if set_neg:
            return type(self)('-' + value, self._BASE)
        else:
            return type(self)(value, self._BASE)

    def __int__(self) -> int:
        n = 0

        neg = False
        if self._value.startswith('-'):
            neg = True

        txt = str(self)
        len_ = len(txt)

        if neg:
            txt = txt[1:]
            len_ -= 1

        for i in range(len_):
            n = n * self._BASE + self._DIGITS.index(txt[i])

        if neg:
            n *= -1

        return n

    @check_value()
    def __add__(self, other):
        cls = type(self)
        negative = False
        x, y = self, other
        if str(other).startswith('-') and str(self).startswith('-'):
            x, y = -x, -y
            negative = True

        elif str(other).startswith('-'):
            return self - (-other)
        elif str(self).startswith('-'):
            return other - (-self)

        result = []
        carry = 0
        for a, b in zip_longest(reversed(x), reversed(y), fillvalue=self._DIGITS[0]):
            sum_ = int(cls(str(a), self._BASE)) + int(cls(str(b), self._BASE)) + carry
            result.append(sum_ % self._BASE)
            carry = sum_ // self._BASE
        if carry > 0:
            result.append(carry)
        if negative:
            result.append('-')
        return type(self).from_index_ls(result, self._BASE)

    @check_value()
    def __sub__(self, other):
        cls = type(self)
        if self == other:
            return self.from_int(0, self._BASE)

        if other == self.from_int(0, self._BASE):
            return self

        if self == self.from_int(0, self._BASE):
            return -other

        result = []
        negative = False
        x, y = self, other
        if self < other:
            negative = not negative
            x, y = y, x

        if str(y).startswith('-'):
            return -(x + -y)

        if str(self).startswith('-') and str(other).startswith('-'):
            negative = False

        x = abs(x)
        y = abs(y)

        carry = 0

        for i, (a, b) in enumerate(zip_longest(reversed(x), reversed(y), fillvalue=self._DIGITS[0])):
            diff = int(cls(str(a), self._BASE)) - int(cls(str(b), self._BASE)) - carry
            carry = 0
            if diff < 0:
                diff += self._BASE
                carry += 1
            result.append(diff)
        while True:
            try:
                if result[-1] == 0:
                    result.pop()
                else:
                    break
            except IndexError:
                result.append(0)
                break

        if negative and (result != [0]):
            result.append('-')

        return type(self).from_index_ls(result, self._BASE)

    @check_value()
    def __mul__(self, other):
        i = type(self)(other, self._BASE)
        sum_ = self.from_int(0, self._BASE)
        while i > self.from_int(0, self._BASE):
            i -= self.from_int(1, self._BASE)
            sum_ = sum_ + self
        return sum_

    @check_value()
    def __truediv__(self, other):
        if self == self.from_int(0, self._BASE) or other == self.from_int(0, other.base):
            raise ZeroDivisionError("division by zero")
        cls = type(self)
        i = cls.from_int(0, self._BASE)
        last = self - other
        while last >= self.from_int(0, self._BASE):
            i += self.from_int(1, self._BASE)
            last -= other
        return i

    @check_value()
    def __floordiv__(self, other):
        return self / other

    @check_value()
    def __mod__(self, other):
        if self._value == self.from_int(0, self._BASE) or other == other.from_int(0, other.base):
            raise ZeroDivisionError("division by zero")
        x = self // other
        result = self - (x * other)
        return result

    @check_value()
    def compare(self, other) -> float:
        """负值左边小 正值右边小"""
        neg = 1
        if str(self).startswith('-') and str(other).startswith('-'):
            neg *= -1
        elif str(self).startswith('-'):
            return -float("inf")
        elif str(other).startswith('-'):
            return float("inf")

        if len(self) != len(other):
            return (len(self) - len(other)) * neg

        if str(self) == str(other):
            return 0

        for a, b in zip(str(self), str(other)):
            if a != b:
                return (self._DIGITS.index(a) - self._DIGITS.index(b)) * neg

        return 0

    def lower(self) -> str:
        return self._value.lower()

    def upper(self) -> str:
        return self._value.upper()

    @classmethod
    def load(cls, data: dict) -> Self:
        return cls(data["value"], data["base"])

    def dump(self) -> dict:
        return {
            "base": self._BASE,
            "value": self._value
        }

    def encode(self, encoding: str, errors: str) -> bytes:
        return self._value.encode(encoding=encoding, errors=errors)

    @check_value()
    def __eq__(self, other) -> bool:
        return self.compare(other) == 0

    @check_value()
    def __ne__(self, other) -> bool:
        return self.compare(other) != 0

    def __hash__(self) -> int:
        return hash(self._value)

    @check_value()
    def __lt__(self, other) -> bool:
        return self.compare(other) < 0

    @check_value()
    def __le__(self, other) -> bool:
        return self.compare(other) <= 0

    @check_value()
    def __gt__(self, other) -> bool:
        return self.compare(other) > 0

    @check_value()
    def __ge__(self, other) -> bool:
        return self.compare(other) >= 0


def main():
    pass


if __name__ == "__main__":
    main()

__all__ = ("MAX_LEN", "MAX_BASE", "DIGITS", "Base")
