import re
from typing import List, NamedTuple

from xproc.value import (
    Attr,
    FloatValue,
    IntValue,
    current_time_attr,
)


class Loadavg(NamedTuple):
    load_1: float
    load_5: float
    load_15: float
    nr_running: int
    nr_total: int
    last_pid: int

    def get_attrs(self) -> List[Attr]:
        attrs = []
        attrs.append(current_time_attr())
        attrs.append(Attr("LOAD_1_MIN", FloatValue(self.load_1)))
        attrs.append(Attr("LOAD_5_MIN", FloatValue(self.load_5)))
        attrs.append(Attr("LOAD_15_MIN", FloatValue(self.load_15)))
        attrs.append(Attr("NR_RUNNING", IntValue(self.nr_running)))
        attrs.append(Attr("NR_TOTAL", IntValue(self.nr_total)))
        attrs.append(Attr("LAST_PID", IntValue(self.last_pid)))
        return attrs


EmptyLoadavg = Loadavg(0, 0, 0, 0, 0, 0)

LOAD_PATTERN = re.compile(r"^(?P<load_1>[0-9]+\.[0-9]+)\s+"
                          r"(?P<load_5>[0-9]+\.[0-9]+)\s+"
                          r"(?P<load_15>[0-9]+\.[0-9]+)\s+"
                          r"(?P<nr_running>[0-9]+)/(?P<nr_total>[0-9]+)\s+"
                          r"(?P<last_pid>[0-9]+)\s?$")


def current_loadavg() -> Loadavg:
    # 0.24 0.16 0.06 1/296 1968353
    with open("/proc/loadavg", mode="r", encoding="utf-8") as load:
        line = load.readlines()[0]
    match = re.match(LOAD_PATTERN, line)
    if not match:
        return EmptyLoadavg
    return Loadavg(load_1=float(match.group("load_1")),
                   load_5=float(match.group("load_5")),
                   load_15=float(match.group("load_15")),
                   nr_running=int(match.group("nr_running")),
                   nr_total=int(match.group("nr_total")),
                   last_pid=int(match.group("last_pid")))
