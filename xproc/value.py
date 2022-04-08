from time import strftime, localtime
from abc import ABCMeta, abstractmethod
from typing import List, Union
import re

DEF_FMT_1 = "{0}"
DEF_FMT_2 = "{0}{1}"


class Value(metaclass=ABCMeta):
    """Value"""

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


class StrValue(Value):

    def __init__(self, val: str):
        super().__init__()
        self.val = val

    def value(self) -> str:
        return self.val

    def __repr__(self) -> str:
        return self.fmt.format(self.val)


class IntValue(Value):

    def __init__(self, val: int):
        super().__init__()
        self.val = val

    def value(self) -> int:
        return self.val

    def __repr__(self) -> str:
        return self.fmt.format(self.value())


class FloatValue(Value):

    def __init__(self, val: float):
        super().__init__()
        self.val = val

    def value(self) -> float:
        return self.val

    def __repr__(self) -> str:
        return self.fmt.format(self.value())


class IntUnitValue(IntValue):

    def __init__(self, val: int, unit: str):
        super().__init__(val)
        self._unit = unit
        self._fmt = DEF_FMT_2

    def unit(self) -> str:
        return self._unit

    def __repr__(self) -> str:
        return self.fmt.format(self.value(), self.unit())


class ListValue(metaclass=ABCMeta):
    """List Value"""

    @abstractmethod
    def value(self) -> List:
        pass


class ListIntValue(ListValue):

    def __init__(self, val: List[int]):
        super().__init__()
        self._val = val
        self.fmt = ""    # placeholder

    def value(self) -> List[int]:
        return self._val

    def __repr__(self) -> str:
        return " ".join([str(i) for i in self._val])


ValueType = Union[IntValue, IntUnitValue, StrValue, FloatValue, ListIntValue]


class Attr:

    def __init__(self, name: str, value: ValueType):
        self._name = name
        self._value = value

    def __repr__(self) -> str:
        return f"{self._name}:{self._value}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> ValueType:
        return self._value

    def set_value_fmt(self, fmt: str):
        self._value.fmt = fmt


EmptyValue = StrValue("")
EmptyIntValue = IntValue(0)
EmptyIntUnitValue = IntUnitValue(0, "kB")
EmptyAttr = Attr("EmptyAttr", EmptyValue)
EmptyIntAttr = Attr("EmptyAttr", EmptyIntValue)


def parse_int_val(name: str, value: str) -> Attr:
    return Attr(name, IntValue(int(value.strip())))


def parse_int_unit_val(name: str, value: str) -> Attr:
    values = value.strip().split(" ")
    return Attr(name, IntUnitValue(int(values[0]), values[1]))


def parse_str_val(name: str, value: str) -> Attr:
    return Attr(name, StrValue(value.strip()))


def parse_list_int_val(name: str, value: str) -> Attr:
    vals = []
    for i in re.split(r"\s+", value):
        if i:
            vals.append(int(i))
    return Attr(name, ListIntValue(vals))


def current_time_attr() -> Attr:
    return Attr("TIME", StrValue(strftime("%H:%M:%S", localtime())))
