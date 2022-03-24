# pylint: disable=too-few-public-methods
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

from time import strftime, localtime
from abc import ABCMeta, abstractmethod
from typing import Union

DEF_FMT_1 = "{0}"
DEF_FMT_2 = "{0}{1}"


class AttrValue(metaclass=ABCMeta):
    """Attr Value"""

    def __init__(self):
        self._fmt = DEF_FMT_1

    @property
    def fmt(self):
        return self._fmt

    @fmt.setter
    def fmt(self, value):
        self._fmt = value

    @abstractmethod
    def value(self) -> Union[int, str]:
        pass


class StrValue(AttrValue):

    def __init__(self, val: str):
        super().__init__()
        self.val = val

    def value(self) -> str:
        return self.val

    def __repr__(self) -> str:
        return self.fmt.format(self.val)


class IntValue(AttrValue):

    def __init__(self, val: int):
        super().__init__()
        self.val = val

    def value(self) -> int:
        return self.val

    def __repr__(self) -> str:
        return self.fmt.format(self.value())


class IntUnitValue(IntValue):

    def __init__(self, val: int, unit: str):
        super().__init__(val)
        self._unit = unit

    def unit(self) -> str:
        return self._unit

    def __repr__(self) -> str:
        return self.fmt.format(self.value(), self.unit())


ValueType = Union[IntValue, IntUnitValue, StrValue]


class Attr:

    def __init__(self, name, value: ValueType):
        self._name = name
        self._value = value
        self._name_len = len(name)
        self._value_len = len(repr(value))
        self._width = max(self._name_len, self._value_len, 12)

    def __repr__(self) -> str:
        return f"{self._name}:{self._value}"

    @property
    def name(self) -> str:
        return self._name

    def name_str(self) -> str:
        return f"{self._name:>{self._width}s}"

    def value_str(self) -> str:
        return f"{repr(self._value):>{self._width}s}"

    @property
    def value(self) -> AttrValue:
        return self._value

    def set_value_fmt(self, fmt: str):
        self._value.fmt = fmt


EmptyValue = StrValue("")
EmptyIntValue = IntValue(0)
EmptyIntUnitValue = IntUnitValue(0, "kB")
EmptyAttr = Attr("EmptyAttr", EmptyValue)


def parse_int_val(name: str, value: str) -> Attr:
    return Attr(name, IntValue(int(value.strip())))


def parse_int_unit_val(name: str, value: str) -> Attr:
    values = value.strip().split(" ")
    return Attr(name, IntUnitValue(int(values[0]), values[1]))


def parse_str_val(name: str, value: str) -> Attr:
    return Attr(name, StrValue(value.strip()))


def current_time_attr() -> Attr:
    return Attr("TIME", StrValue(strftime("%H:%M:%S", localtime())))
